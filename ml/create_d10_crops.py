from pathlib import Path
from PIL import Image

IMAGE_DIR = Path("ml/datasets/roadai_yolo/images/train")
LABEL_DIR = Path("ml/datasets/roadai_yolo/labels/train")
OUTPUT_DIR = Path("ml/d10_crops")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

count = 0

for image_path in IMAGE_DIR.glob("*.jpg"):
    label_path = LABEL_DIR / f"{image_path.stem}.txt"

    if not label_path.exists():
        continue

    image = Image.open(image_path)
    width, height = image.size

    for i, line in enumerate(label_path.read_text().splitlines()):
        parts = line.split()

        if len(parts) != 5:
            continue

        class_id, cx, cy, bw, bh = parts

        if class_id != "1":
            continue

        cx = float(cx)
        cy = float(cy)
        bw = float(bw)
        bh = float(bh)

        x1 = max(0, int((cx - bw * 1.5) * width))
        y1 = max(0, int((cy - bh * 3) * height))
        x2 = min(width, int((cx + bw * 1.5) * width))
        y2 = min(height, int((cy + bh * 3) * height))

        crop = image.crop((x1, y1, x2, y2))
        crop = crop.resize((600, 600))

        output_path = OUTPUT_DIR / f"{image_path.stem}_d10_{i}.jpg"
        crop.save(output_path)

        count += 1

print(f"D10 crops created: {count}")
print(f"Folder: {OUTPUT_DIR.resolve()}")