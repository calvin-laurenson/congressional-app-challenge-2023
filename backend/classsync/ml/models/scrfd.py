import numpy as np
import os.path as osp
import sys
import onnxruntime
from classsync.ml.image_utils import Box, DetectedFace, KeyPoint, draw_bboxes
from numpy.typing import NDArray
from PIL import Image
def softmax(z):
    assert len(z.shape) == 2
    s = np.max(z, axis=1)
    s = s[:, np.newaxis] 
    e_x = np.exp(z - s)
    div = np.sum(e_x, axis=1)
    div = div[:, np.newaxis] 
    return e_x / div


def distance2bbox(points, distance, max_shape=None):
    """Decode distance prediction to bounding box.

    Args:
        points (Tensor): Shape (n, 2), [x, y].
        distance (Tensor): Distance from the given point to 4
            boundaries (left, top, right, bottom).
        max_shape (tuple): Shape of the image.

    Returns:
        Tensor: Decoded bboxes.
    """
    x1 = points[:, 0] - distance[:, 0]
    y1 = points[:, 1] - distance[:, 1]
    x2 = points[:, 0] + distance[:, 2]
    y2 = points[:, 1] + distance[:, 3]
    if max_shape is not None:
        x1 = x1.clamp(min=0, max=max_shape[1])
        y1 = y1.clamp(min=0, max=max_shape[0])
        x2 = x2.clamp(min=0, max=max_shape[1])
        y2 = y2.clamp(min=0, max=max_shape[0])
    return np.stack([x1, y1, x2, y2], axis=-1)


def distance2kps(points, distance, max_shape=None):
    """Decode distance prediction to bounding box.

    Args:
        points (Tensor): Shape (n, 2), [x, y].
        distance (Tensor): Distance from the given point to 4
            boundaries (left, top, right, bottom).
        max_shape (tuple): Shape of the image.

    Returns:
        Tensor: Decoded bboxes.
    """
    preds = []
    for i in range(0, distance.shape[1], 2):
        px = points[:, i % 2] + distance[:, i]
        py = points[:, i % 2 + 1] + distance[:, i + 1]
        if max_shape is not None:
            px = px.clamp(min=0, max=max_shape[1])
            py = py.clamp(min=0, max=max_shape[0])
        preds.append(px)
        preds.append(py)
    return np.stack(preds, axis=-1)


class SCRFD:
    def __init__(self, model_file: str | None = None, session: str | None = None, nms_thresh: float = 0.4):
        self.model_file = model_file
        self.center_cache = {}
        self.nms_thresh = nms_thresh
        if session is None:
            assert self.model_file is not None
            assert osp.exists(self.model_file)
            self.session = onnxruntime.InferenceSession(self.model_file, None, providers=["CPUExecutionProvider"])
        else:
            self.session = session
        input_cfg = self.session.get_inputs()[0]
        input_shape = input_cfg.shape
        if isinstance(input_shape[2], str):
            self.input_size = None
        else:
            self.input_size = tuple(input_shape[2:4][::-1])
        outputs = self.session.get_outputs()
        self.batched = len(outputs[0].shape) == 3
        self.input_name = input_cfg.name
        self.output_names = [o.name for o in outputs]
        self.use_kps = False
        self._num_anchors = 1
        if len(outputs) == 6:
            self.fmc = 3
            self._feat_stride_fpn = [8, 16, 32]
            self._num_anchors = 2
        elif len(outputs) == 9:
            self.fmc = 3
            self._feat_stride_fpn = [8, 16, 32]
            self._num_anchors = 2
            self.use_kps = True
        elif len(outputs) == 10:
            self.fmc = 5
            self._feat_stride_fpn = [8, 16, 32, 64, 128]
            self._num_anchors = 1
        elif len(outputs) == 15:
            self.fmc = 5
            self._feat_stride_fpn = [8, 16, 32, 64, 128]
            self._num_anchors = 1
            self.use_kps = True
        

    def forward(self, img: NDArray, thresh):
        scores_list = []
        bboxes_list = []
        kpss_list = []
        input_size = tuple(img.shape[0:2][::-1])
        
        img = img.astype(np.float32)
        img = ((img / 255.0) - 0.5) / 0.5
        img = img.transpose((2, 0, 1))
        img = img.reshape(1, 3, input_size[1], input_size[0])

        net_outs = self.session.run(self.output_names, {self.input_name: img})

        input_height = img.shape[2]
        input_width = img.shape[3]
        fmc = self.fmc
        for idx, stride in enumerate(self._feat_stride_fpn):
            # If model support batch dim, take first output
            if self.batched:
                scores = net_outs[idx][0]
                bbox_preds = net_outs[idx + fmc][0]
                bbox_preds = bbox_preds * stride
                if self.use_kps:
                    kps_preds = net_outs[idx + fmc * 2][0] * stride
            # If model doesn't support batching take output as is
            else:
                scores = net_outs[idx]
                bbox_preds = net_outs[idx + fmc]
                bbox_preds = bbox_preds * stride
                if self.use_kps:
                    kps_preds = net_outs[idx + fmc * 2] * stride

            height = input_height // stride
            width = input_width // stride
            K = height * width
            key = (height, width, stride)
            if key in self.center_cache:
                anchor_centers = self.center_cache[key]
            else:
                anchor_centers = np.stack(
                    np.mgrid[:height, :width][::-1], axis=-1
                ).astype(np.float32)

                anchor_centers = (anchor_centers * stride).reshape((-1, 2))
                if self._num_anchors > 1:
                    anchor_centers = np.stack(
                        [anchor_centers] * self._num_anchors, axis=1
                    ).reshape((-1, 2))
                if len(self.center_cache) < 100:
                    self.center_cache[key] = anchor_centers

            pos_inds = np.where(scores >= thresh)[0]
            bboxes = distance2bbox(anchor_centers, bbox_preds)
            pos_scores = scores[pos_inds]
            pos_bboxes = bboxes[pos_inds]
            scores_list.append(pos_scores)
            bboxes_list.append(pos_bboxes)
            if self.use_kps:
                kpss = distance2kps(anchor_centers, kps_preds)
                kpss = kpss.reshape((kpss.shape[0], -1, 2))
                pos_kpss = kpss[pos_inds]
                kpss_list.append(pos_kpss)
        return scores_list, bboxes_list, kpss_list

    def detect(
        self, img: Image.Image, thresh=0.5, input_size=None
    ) -> list[DetectedFace]:
        if input_size is None and self.input_size is None:
            input_size = (img.width, img.height)
        elif input_size is None:
            input_size = self.input_size
        else:
            # input_size is defined
            ...

        original_size = (img.width, img.height)

        # Resize the image to the calculated size
        img = img.resize(input_size)
        img = img.convert("RGB")
        img_array = np.array(img)
        img_array = img_array[:, :, ::-1]

        scores_list, bboxes_list, kpss_list = self.forward(img_array, thresh)

        img_scale_x = original_size[0] / input_size[0]
        img_scale_y = original_size[1] / input_size[1]

        scores = np.vstack(scores_list)
        scores_ravel = scores.ravel()
        order = scores_ravel.argsort()[::-1]
        bboxes = np.vstack(bboxes_list)
        
        # Scale the bounding boxes correctly to the original image size
        bboxes = bboxes * np.array([img_scale_x, img_scale_y, img_scale_x, img_scale_y])

        if self.use_kps:
            kpss = np.vstack(kpss_list)
            # Scale the keypoints correctly to the original image size
            kpss[:, :, 0] *= img_scale_x
            kpss[:, :, 1] *= img_scale_y

        pre_det = np.hstack((bboxes, scores)).astype(np.float32, copy=False)
        pre_det = pre_det[order, :]
        keep = self.nms(pre_det)
        det = pre_det[keep, :]
        if self.use_kps:
            kpss = kpss[order, :, :]
            kpss = kpss[keep, :, :]
        else:
            kpss = None
        faces = []
        if kpss is None:
            kpss = [None for _ in det]
        for face, kps in zip(det, kpss, strict=True):
            face = Box(
                int(face[0]), int(face[1]), int(face[2]), int(face[3]), float(face[4])
            )
            faces.append(
                DetectedFace(
                    face,
                    [KeyPoint(kp[0], kp[1]) for kp in kps] if kps is not None else None,
                )
            )
        return faces


    def nms(self, dets):
        thresh = self.nms_thresh
        x1 = dets[:, 0]
        y1 = dets[:, 1]
        x2 = dets[:, 2]
        y2 = dets[:, 3]
        scores = dets[:, 4]

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

        return keep


if __name__ == "__main__":
    import glob

    # detector = SCRFD(model_file='./det.onnx')
    detector = SCRFD(model_file="./scrfd-10g-kps.onnx")
    img_path = sys.argv[1]
    img = Image.open(img_path)
    faces = detector.detect(img, 0.6, (640, 640))

    draw_bboxes(img, faces)
    filename = img_path.split("/")[-1]
    img.save("./done-%s" % filename)

