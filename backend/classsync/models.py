from classsync.ml.models import partial_fc, scrfd
from classsync.ml import image_utils
from PIL import Image


class Models:
    def __init__(self):
        print("Initiating facial recognition models")
        self.detector = scrfd.SCRFD(model_file="./backend/scrfd-10g-kps.onnx")
        self.pfc = partial_fc.PartialFC("./backend/pfc.onnx")

    def find_faces(self, image: Image.Image):
        faces = self.detector.detect(image, 0.6)
        face_images = image_utils.extract_face_images(image, faces)
        recognized_faces: list[list] = [
            self.pfc.recognize(face_image).tolist() for face_image in face_images
        ]
        return recognized_faces
