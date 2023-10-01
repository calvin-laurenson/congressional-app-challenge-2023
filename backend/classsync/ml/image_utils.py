import numpy as np
from numpy.typing import NDArray
from dataclasses import dataclass
from PIL import Image, ImageDraw, ImageFont


@dataclass
class Box:
    x1: int
    y1: int
    x2: int
    y2: int
    score: float


@dataclass
class KeyPoint:
    x: int
    y: int


@dataclass
class DetectedFace:
    bbox: Box
    kps: list[KeyPoint] | None


def draw_bboxes(img, faces, draw_size=1):
    draw = ImageDraw.Draw(img)
    font = ImageFont.load_default()  # Use the system default font

    for face in faces:
        x1 = face.bbox.x1
        y1 = face.bbox.y1
        x2 = face.bbox.x2
        y2 = face.bbox.y2

        draw.rectangle([x1, y1, x2, y2], outline=(255, 0, 0), width=draw_size)
        text = f"{round(face.bbox.score * 100, 1)}%"
        draw.text((x1, y1), text, fill=(0, 255, 0), font=font)

        if face.kps is not None:
            for kp in face.kps:
                draw.ellipse(
                    [
                        (kp.x - draw_size, kp.y - draw_size),
                        (kp.x + draw_size, kp.y + draw_size),
                    ],
                    outline=(0, 0, 255),
                    width=1,
                )

    return img


def extract_face_images(
    img: Image.Image, faces: list[DetectedFace], align=True
) -> list[NDArray]:
    face_images = []

    for face in faces:
        if face.kps is None or not align:
            face_bbox = (face.bbox.x1, face.bbox.y1, face.bbox.x2, face.bbox.y2)
            face_img = img.crop(face_bbox)
            face_images.append(np.array(face_img))
        else:
            left_eye = face.kps[1]
            right_eye = face.kps[0]
            y_diff = right_eye.y - left_eye.y
            x_diff = right_eye.x - left_eye.x
            angle = np.degrees(np.arctan2(y_diff, x_diff)) - 180
            eyes_center = (
                (left_eye.x + right_eye.x) // 2,
                (left_eye.y + right_eye.y) // 2,
            )

            # Rotate the image
            rotated_img = img.rotate(
                angle, center=eyes_center, resample=Image.BILINEAR, expand=True
            )

            # Crop the aligned face
            face_bbox = (face.bbox.x1, face.bbox.y1, face.bbox.x2, face.bbox.y2)
            face_img = rotated_img.crop(face_bbox)

            face_images.append(np.array(face_img))

    return face_images


def nms(faces: list[DetectedFace], thresh=0.3) -> list[DetectedFace]:
    x1 = np.array([f.bbox.x1 for f in faces])
    y1 = np.array([f.bbox.y1 for f in faces])
    x2 = np.array([f.bbox.x2 for f in faces])
    y2 = np.array([f.bbox.y2 for f in faces])
    scores = np.array([f.bbox.score for f in faces])

    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    order = scores.argsort()[::-1]

    keep = []
    while order.size > 0:
        i = order[0]
        keep.append(i)
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        inter = w * h
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        inds = np.where(ovr <= thresh)[0]
        order = order[inds + 1]

    return [face for i, face in enumerate(faces) if i in keep]
