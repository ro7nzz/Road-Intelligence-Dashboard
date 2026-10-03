from pathlib import Path
import shutil

SOURCE_IMAGES = Path("ml/datasets/roadai_yolo/images/train")
SOURCE_LABELS = Path("ml/datasets/roadai_yolo/labels/train")

TARGET_IMAGES = Path("ml/datasets/roadai_yolo/images/train_balanced")
TARGET_LABELS = Path("ml/datasets/roadai_yolo/labels/train_balanced")

D10_EXTRA_COPIES = 3


def contains_d10(label_file):
    for line in label_file.read_text().splitlines():
        if line.strip() and line.split()[0] == "1":
            return True
    return False


TARGET_IMAGES.mkdir(parents=True, exist_ok=True)
TARGET_LABELS.mkdir(parents=True, exist_ok=True)

# Copy the original training dataset
image_files = list(SOURCE_IMAGES.glob("*"))

copied = 0
d10_images = 0

for image_path in image_files:
    label_path = SOURCE_LABELS / f"{image_path.stem}.txt"

    if not label_path.exists():
        continue

    shutil.copy2(
        image_path,
        TARGET_IMAGES / image_path.name
    )

    shutil.copy2(
        label_path,
        TARGET_LABELS / label_path.name
    )

    copied += 1

    # Oversample D10 only
    if contains_d10(label_path):
        d10_images += 1

        for i in range(1, D10_EXTRA_COPIES + 1):
            new_image_name = f"{image_path.stem}_d10x{i}{image_path.suffix}"
            new_label_name = f"{label_path.stem}_d10x{i}.txt"

            shutil.copy2(
                image_path,
                TARGET_IMAGES / new_image_name
            )

            shutil.copy2(
                label_path,
                TARGET_LABELS / new_label_name
            )


print("=" * 60)
print("ROADAI — D10 BALANCED TRAINING SET")
print("=" * 60)
print(f"Original training images copied : {copied}")
print(f"D10 images found                : {d10_images}")
print(f"Extra D10 copies per image      : {D10_EXTRA_COPIES}")
print(f"Balanced training images        : {len(list(TARGET_IMAGES.glob('*')))}")
print("=" * 60)