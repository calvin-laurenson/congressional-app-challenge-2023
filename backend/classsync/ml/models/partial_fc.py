import os.path as osp
import numpy as np
import numpy.typing as npt
import onnxruntime as ort
import sys
from PIL import Image


class PartialFC:
    session: ort.InferenceSession
    input_name: str
    output_name: str

    def __init__(
        self, model_file: str | None = None, session: ort.InferenceSession | None = None
    ):
        self.session = session
        if self.session is None:
            assert model_file is not None
            assert osp.exists(model_file)
            self.session = ort.InferenceSession(model_file, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.output_name = self.session.get_outputs()[0].name

    def forward(self, img: npt.NDArray) -> npt.NDArray[np.float64]:
        assert img.shape == (112, 112, 3)
        img = img.astype(np.float32)
        img = ((img / 255.0) - 0.5) / 0.5
        img = img.transpose((2, 0, 1))
        img = img.reshape(1, 3, 112, 112)
        output = self.session.run([self.output_name], {self.input_name: img})
        return output[0][0]

    def recognize(self, img: Image.Image) -> npt.NDArray[np.float64]:
        img = img.convert("RGB")
        img = img.resize((112, 112))
        img_array = np.array(img)
        # RGB -> BGR
        img_array = img_array[:, :, ::-1]
        return self.forward(img_array)
        

if __name__ == "__main__":
    pfc = PartialFC("pfc.onnx")
    image_path = sys.argv[1]
    img = Image.open(image_path)
    print(str(pfc.recognize(img).tolist())[1:-1])
