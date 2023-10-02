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

def nms(faces: list[DetectedFace], thresh=0.3):
    """
    Perform Non-Maximum Suppression (NMS) on a list of detected faces.

    Parameters:
    faces (list[DetectedFace]): A list of DetectedFace objects containing bounding box information.
    thresh (float, optional): The threshold value for IoU (Intersection over Union) to retain faces.
                              Defaults to 0.3.

    Returns:
    list[DetectedFace]: A list of DetectedFace objects after NMS has been applied.
    """
    # Extract the coordinates (x1, y1, x2, y2) and scores of each detected face
    x1 = np.array([f.bbox.x1 for f in faces])
    y1 = np.array([f.bbox.y1 for f in faces])
    x2 = np.array([f.bbox.x2 for f in faces])
    y2 = np.array([f.bbox.y2 for f in faces])
    scores = np.array([f.bbox.score for f in faces])

    # Calculate the areas of the bounding boxes
    areas = (x2 - x1 + 1) * (y2 - y1 + 1)
    
    # Sort the faces in descending order of their scores and get the corresponding indices
    order = scores.argsort()[::-1]

    # Initialize a list 'keep' to store the indices of the faces to be retained after NMS
    keep = []
    
    # Perform non-maximum suppression
    while order.size > 0:
        i = order[0]  # Select the face with the highest score
        keep.append(i)  # Add its index to the 'keep' list
        
        # Calculate the intersection coordinates and dimensions of the selected face and other faces
        xx1 = np.maximum(x1[i], x1[order[1:]])
        yy1 = np.maximum(y1[i], y1[order[1:]])
        xx2 = np.minimum(x2[i], x2[order[1:]])
        yy2 = np.minimum(y2[i], y2[order[1:]])

        # Calculate the width and height of the intersection area (clipped to zero if no overlap)
        w = np.maximum(0.0, xx2 - xx1 + 1)
        h = np.maximum(0.0, yy2 - yy1 + 1)
        
        # Calculate the intersection area
        inter = w * h
        
        # Calculate the overlap ratio (IoU) between the selected face and other faces
        ovr = inter / (areas[i] + areas[order[1:]] - inter)

        # Find the indices of faces with IoU less than or equal to the threshold
        inds = np.where(ovr <= thresh)[0]
        
        # Update the 'order' array to exclude faces that are too similar to the selected face
        order = order[inds + 1]

    # Return the list of faces that survived non-maximum suppression
    return [face for i, face in enumerate(faces) if i in keep]
