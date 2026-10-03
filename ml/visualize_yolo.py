from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
import random

ROOT = Path("ml/datasets/roadai_yolo")
OUT = Path("ml/yolo_visualization")
OUT.mkdir(parents=True, exist_ok=True)

CLASS_NAMES = {
    0: "D00 - Longitudinal Crack",
    1: "D10 - Transverse Crack",
    2: "D20 - Alligator Crack",
    3: "D40 - Pothole",
}

random.seed(42)

samples_per_split = 3

for split in ["train", "val", "test"]:
    image_dir = ROOT / "images" / split
    label_dir = ROOT / "labels" / split

    images = list(image_dir.glob("*.jpg"))
    random.shuffle(images)

    selected = images[:samples_per_split]

    for image_path in selected:
        label_path = label_dir / f"{image_path.stem}.txt"

        image = Image.open(image_path).convert("RGB")
        draw = ImageDraw.Draw(image)

        width, height = image.size

        if label_path.exists():
            text = label_path.read_text(encoding="utf-8").strip()

            if text:
                for line in text.splitlines():
                    parts = line.split()

                    if len(parts) != 5:
                        continue

                    class_id = int(parts[0])
                    x_center, y_center, box_width, box_height = map(float, parts[1:])

                    x_center *= width
                    y_center *= height
                    box_width *= width
                    box_height *= height

                    x1 = int(x_center - box_width / 2)
                    y1 = int(y_center - box_height / 2)
                    x2 = int(x_center + box_width / 2)
                    y2 = int(y_center + box_height / 2)

                    draw.rectangle([x1, y1, x2, y2], outline="red", width=3)
                    draw.text(
                        (x1, max(0, y1 - 18)),
                        CLASS_NAMES.get(class_id, f"Class {class_id}"),
                        fill="red"
                    )

        output_path = OUT / f"{split}_{image_path.stem}.jpg"
        image.save(output_path, quality=95)

        print(f"Created: {output_path}")

print("\n" + "=" * 70)
print("YOLO VISUALIZATION COMPLETE")
print("=" * 70)
print(f"Output folder: {OUT.resolve()}")
