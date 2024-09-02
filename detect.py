import torch
from models.common import DetectMultiBackend
from utils.general import non_max_suppression, scale_coords
from utils.augmentations import letterbox
import cv2
import numpy as np

# Load model
model = DetectMultiBackend('yolov5s.pt', device='cuda')
model.eval()

# Load image
img = cv2.imread('potholes.png')
img = letterbox(img, new_shape=640)[0]
img = img[:, :, ::-1].transpose(2, 0, 1)
img = np.ascontiguousarray(img)

# Inference
img_tensor = torch.from_numpy(img).to('cuda').float()
img_tensor /= 255.0
if img_tensor.ndimension() == 3:
    img_tensor = img_tensor.unsqueeze(0)

pred = model(img_tensor, augment=False, visualize=False)

# Apply NMS
pred = non_max_suppression(pred, 0.25, 0.45, None, False, max_det=1000)

# Process detections
for i, det in enumerate(pred):  # detections per image
    if len(det):
        # Rescale boxes from img_size to im0 size
        det[:, :4] = scale_coords(img_tensor.shape[2:], det[:, :4], img.shape).round()

        # Print results
        for *xyxy, conf, cls in reversed(det):
            c = int(cls)  # integer class
            label = f'{model.names[c]} {conf:.2f}'
            print(label, xyxy)