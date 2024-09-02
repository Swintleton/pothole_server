import os
import sys
from pathlib import Path
import torch

# Add YOLOv5 to the PATH
YOLOv5_PATH = Path("yolov5")  # Replace with your YOLOv5 directory path
sys.path.insert(0, str(YOLOv5_PATH))

from models.common import DetectMultiBackend
from utils.dataloaders import LoadImages
from utils.general import non_max_suppression, scale_boxes
from utils.plots import save_one_box
from utils.torch_utils import select_device

def detect_potholes(image_path, weights_path, img_size=640, conf_thres=0.65):
    device = select_device('')
    model = DetectMultiBackend(weights_path, device=device)
    dataset = LoadImages(image_path, img_size=img_size)
    
    for path, img, im0s, vid_cap, s in dataset:
        img = torch.from_numpy(img).to(device)
        img = img.float()  # uint8 to fp16/32
        img /= 255.0  # 0 - 255 to 0.0 - 1.0
        if len(img.shape) == 3:
            img = img[None]  # expand for batch dim

        pred = model(img, augment=False, visualize=False)
        pred = non_max_suppression(pred, conf_thres, 0.45, max_det=1000)

        detected_potholes = False
        for i, det in enumerate(pred):  # per image
            if len(det):
                detected_potholes = True

        return detected_potholes

if __name__ == "__main__":
    image_path = sys.argv[1]
    weights_path = sys.argv[2]
    detected = detect_potholes(image_path, weights_path)
    print("Detected" if detected else "Not detected")
