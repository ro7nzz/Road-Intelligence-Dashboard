from pathlib import Path
from collections import Counter

ROOT = Path("ml/datasets/roadai_yolo")
SPLITS = ["train", "val", "test"]
CLASS_NAMES = {
    0: "D00",
    1: "D10",
    2: "D20",
    3: "D40",
}

total_images = 0
total_labels = 0
total_boxes = 0
total_empty = 0
total_errors = 0
global_counts = Counter()

print("RoadAI - YOLO Dataset Validation")
print("=" * 70)

for split in SPLITS:
    image_dir = ROOT / "images" / split
    label_dir = ROOT / "labels" / split

    images = sorted(image_dir.glob("*.jpg"))
    labels = sorted(label_dir.glob("*.txt"))

    image_stems = {p.stem for p in images}
    label_stems = {p.stem for p in labels}

    missing_labels = image_stems - label_stems
    extra_labels = label_stems - image_stems

    split_boxes = 0
    split_empty = 0
    split_counts = Counter()
    split_errors = []

    for image in images:
        label_file = label_dir / f"{image.stem}.txt"

        if not label_file.exists():
            continue

        total_labels += 1

        text = label_file.read_text(encoding="utf-8").strip()

        if not text:
            split_empty += 1
            total_empty += 1
            continue

        for line_no, line in enumerate(text.splitlines(), 1):
            parts = line.split()

            if len(parts) != 5:
                split_errors.append(
                    f"{label_file.name}:{line_no} -> expected 5 values, got {len(parts)}"
                )
                continue

            try:
                class_id = int(parts[0])
                values = [float(x) for x in parts[1:]]
            except ValueError:
                split_errors.append(
                    f"{label_file.name}:{line_no} -> non-numeric value"
                )
                continue

            if class_id not in CLASS_NAMES:
                split_errors.append(
                    f"{label_file.name}:{line_no} -> invalid class ID {class_id}"
                )
                continue

            if not all(0.0 <= x <= 1.0 for x in values):
                split_errors.append(
                    f"{label_file.name}:{line_no} -> normalized value outside [0,1]"
                )
                continue

            split_boxes += 1
            split_counts[class_id] += 1
            global_counts[class_id] += 1

    split_images = len(images)
    total_images += split_images
    total_boxes += split_boxes
    total_errors += len(split_errors)

    print(f"\n{split.upper()}")
    print("-" * 70)
    print(f"Images:          {split_images}")
    print(f"Label files:     {len(labels)}")
    print(f"Empty labels:    {split_empty}")
    print(f"Bounding boxes:  {split_boxes}")
    print(f"D00:             {split_counts[0]}")
    print(f"D10:             {split_counts[1]}")
    print(f"D20:             {split_counts[2]}")
    print(f"D40:             {split_counts[3]}")
    print(f"Missing labels:  {len(missing_labels)}")
    print(f"Extra labels:    {len(extra_labels)}")
    print(f"Errors:          {len(split_errors)}")

    if missing_labels:
        print("  Missing label examples:", sorted(missing_labels)[:5])

    if extra_labels:
        print("  Extra label examples:", sorted(extra_labels)[:5])

    if split_errors:
        print("  Error examples:")
        for error in split_errors[:5]:
            print("   ", error)

print("\n" + "=" * 70)
print("OVERALL VALIDATION")
print("=" * 70)

print(f"Total images:    {total_images}")
print(f"Total labels:    {total_labels}")
print(f"Empty labels:    {total_empty}")
print(f"Total boxes:     {total_boxes}")
print(f"D00 boxes:       {global_counts[0]}")
print(f"D10 boxes:       {global_counts[1]}")
print(f"D20 boxes:       {global_counts[2]}")
print(f"D40 boxes:       {global_counts[3]}")
print(f"Validation errors: {total_errors}")

expected = {
    0: 1555,
    1: 68,
    2: 2021,
    3: 3187,
}

print("\nExpected target box counts:")
for class_id, expected_count in expected.items():
    actual = global_counts[class_id]
    status = "PASS" if actual == expected_count else "FAIL"
    print(f"  {CLASS_NAMES[class_id]}: {actual} / {expected_count} -> {status}")

expected_total = sum(expected.values())

print(f"\nExpected total boxes: {expected_total}")
print(f"Actual total boxes:   {total_boxes}")

if (
    total_images == 7706
    and total_labels == 7706
    and total_boxes == expected_total
    and total_errors == 0
    and all(global_counts[k] == v for k, v in expected.items())
):
    print("\n" + "=" * 70)
    print("VALIDATION PASSED")
    print("=" * 70)
else:
    print("\n" + "=" * 70)
    print("VALIDATION FAILED - INVESTIGATION REQUIRED")
    print("=" * 70)
