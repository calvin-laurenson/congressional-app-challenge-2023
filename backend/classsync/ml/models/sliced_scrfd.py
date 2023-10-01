# TODO: Fix this file

from .scrfd import SCRFD
# TODO: Install sahi or replace with built-in slicing
from sahi.slicing import get_slice_bboxes
import sys
from classsync.ml.image_utils import draw_bboxes, DetectedFace, nms, get_faces
from pathlib import Path
import shutil
import os
import numpy as np


class SlicedSCRFD(SCRFD):
    def __init__(self, model_file: str | None = None, session: str | None = None):
        super().__init__(model_file, session)

    def detect(self, img, score_thresh=0.75, slice_thresh=0.75, nms_thresh=0.4, slice_height=640, slice_width=640):
        faces: list[DetectedFace] = []
        assert len(img.shape) == 3
        input_height, input_width, _ = img.shape
        slices = get_slice_bboxes(
            input_height,
            input_width,
            slice_height=slice_height,
            slice_width=slice_width,
        )
        faces.extend(super().detect(img, input_size=(slice_width, slice_height)))
        for slice in slices:
            x1, y1, x2, y2 = slice
            # img = cv2.rectangle(img, (x1, y1), (x2, y2), (255, 0, 0), 3)
            sub_image = img[y1:y2, x1:x2]
            sub_faces = super().detect(
                sub_image, thresh=slice_thresh, input_size=(slice_width, slice_height)
            )
            # draw_bboxes(sub_image, sub_faces)
            # cv2.imshow("a", sub_image)
            # cv2.waitKey()
            for face in sub_faces:
                face.bbox.x1 += x1
                face.bbox.y1 += y1
                face.bbox.x2 += x1
                face.bbox.y2 += y1
                if face.kps is not None:
                    for kp in face.kps:
                        kp.x += x1
                        kp.y += y1
            faces.extend(sub_faces)
        print(f"Before NMS: {len(faces)=}")
        faces = nms(faces, thresh=nms_thresh)
        print(f"After NMS: {len(faces)=}")
        print(f"Before Threshold: {len(faces)=}")
        faces = [face for face in faces if face.bbox.score > score_thresh]
        print(f"After Threshold: {len(faces)=}")
        return faces


if __name__ == "__main__":
    detector = SlicedSCRFD(model_file="./scrfd-10g-kps.onnx")
    detector.prepare(-1)
    img_path = sys.argv[1]
    img = cv2.imread(img_path)
    faces = detector.detect(img, score_thresh=0.9)
    annotated_img = np.copy(img)
    draw_bboxes(annotated_img, faces)
    cv2.imwrite(
        str((Path("./outputs") / Path(img_path).name).absolute()), annotated_img
    )
    face_folder = Path("face-images")
    if face_folder.exists():
        shutil.rmtree(face_folder)
    os.mkdir(face_folder)
    face_images = get_faces(img, faces)
    for i, face_image in enumerate(face_images):
        cv2.imwrite(str((face_folder / f"{i}.jpeg").absolute()), face_image)
