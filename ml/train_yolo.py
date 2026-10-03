from ultralytics import YOLO

MODEL = "yolo11n.pt"
DATA = "ml/datasets/roadai_yolo/dataset_balanced.yaml"

model = YOLO(MODEL)

model.train(
    data=DATA,
    epochs=30,
    imgsz=320,
    batch=2,
    device="cpu",
    workers=0,
    patience=10,
    pretrained=True,
    project="ml/runs",
    name="roadai_yolo11n_320_d10_balanced",
    exist_ok=True,
    plots=True,
    save=True,
    seed=42
)