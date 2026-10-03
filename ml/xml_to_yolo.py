from pathlib import Path
import shutil
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent

RAW_IMAGES = ROOT / "ml" / "datasets" / "raw" / "rdd2020_india" / "train" / "India" / "images"
RAW_XML = ROOT / "ml" / "datasets" / "raw" / "rdd2020_india" / "train" / "India" / "annotations" / "xmls"

MANIFEST_DIR = ROOT / "ml" / "split_manifests"
OUT_DIR = ROOT / "ml" / "datasets" / "roadai_yolo"

CLASS_MAP = {
    "D00": 0,
    "D10": 1,
    "D20": 2,
    "D40": 3,
}

CLASS_NAMES = [
    "D00_Longitudinal_Crack",
    "D10_Transverse_Crack",
    "D20_Alligator_Crack",
    "D40_Pothole",
]


def convert_box(obj, image_width, image_height):

    name = obj.find("name")

    if name is None or not name.text:
        return None

    class_name = name.text.strip()

    if class_name not in CLASS_MAP:
        return None

    box = obj.find("bndbox")

    if box is None:
        return None

    xmin = float(box.findtext("xmin"))
    ymin = float(box.findtext("ymin"))
    xmax = float(box.findtext("xmax"))
    ymax = float(box.findtext("ymax"))

    # Clamp coordinates to image boundaries.
    xmin = max(0.0, min(xmin, image_width))
    xmax = max(0.0, min(xmax, image_width))
    ymin = max(0.0, min(ymin, image_height))
    ymax = max(0.0, min(ymax, image_height))

    if xmax <= xmin or ymax <= ymin:
        raise ValueError(
            f"Invalid bounding box for {class_name}: "
            f"{xmin},{ymin},{xmax},{ymax}"
        )

    x_center = ((xmin + xmax) / 2.0) / image_width
    y_center = ((ymin + ymax) / 2.0) / image_height

    width = (xmax - xmin) / image_width
    height = (ymax - ymin) / image_height

    values = [
        x_center,
        y_center,
        width,
        height,
    ]

    for value in values:
        if value < 0.0 or value > 1.0:
            raise ValueError(
                f"Normalized value out of range: {value}"
            )

    return (
        CLASS_MAP[class_name],
        x_center,
        y_center,
        width,
        height,
    )


def main():

    print()
    print("RoadAI - VOC XML to YOLO Conversion")
    print("=" * 70)

    if not MANIFEST_DIR.exists():
        raise RuntimeError(
            f"Split manifests not found:\n{MANIFEST_DIR}"
        )

    if OUT_DIR.exists():
        print()
        print("Existing YOLO dataset found.")
        print("Removing previous generated YOLO dataset...")
        shutil.rmtree(OUT_DIR)

    for split in ["train", "val", "test"]:
        (OUT_DIR / "images" / split).mkdir(
            parents=True,
            exist_ok=True
        )
        (OUT_DIR / "labels" / split).mkdir(
            parents=True,
            exist_ok=True
        )

    total_images = 0
    total_target_boxes = 0
    skipped_extra_boxes = 0
    class_counts = {
        cls: 0
        for cls in CLASS_MAP
    }

    print()

    for split in ["train", "val", "test"]:

        manifest = MANIFEST_DIR / f"{split}.txt"

        if not manifest.exists():
            raise RuntimeError(
                f"Missing manifest: {manifest}"
            )

        images = [
            line.strip()
            for line in manifest.read_text(
                encoding="utf-8"
            ).splitlines()
            if line.strip()
        ]

        print(
            f"{split.upper()}: converting {len(images)} images..."
        )

        for image_name in images:

            source_image = RAW_IMAGES / image_name
            source_xml = RAW_XML / (
                Path(image_name).stem + ".xml"
            )

            if not source_image.exists():
                raise RuntimeError(
                    f"Missing image: {source_image}"
                )

            if not source_xml.exists():
                raise RuntimeError(
                    f"Missing XML: {source_xml}"
                )

            tree = ET.parse(source_xml)
            root = tree.getroot()

            size = root.find("size")

            if size is None:
                raise RuntimeError(
                    f"Missing image size in {source_xml.name}"
                )

            image_width = float(
                size.findtext("width")
            )

            image_height = float(
                size.findtext("height")
            )

            if image_width <= 0 or image_height <= 0:
                raise RuntimeError(
                    f"Invalid image dimensions in {source_xml.name}"
                )

            yolo_lines = []

            for obj in root.findall("object"):

                name = obj.find("name")

                if (
                    name is None
                    or not name.text
                ):
                    continue

                class_name = name.text.strip()

                if class_name not in CLASS_MAP:
                    skipped_extra_boxes += 1
                    continue

                converted = convert_box(
                    obj,
                    image_width,
                    image_height,
                )

                if converted is None:
                    continue

                class_id, xc, yc, w, h = converted

                yolo_lines.append(
                    f"{class_id} "
                    f"{xc:.6f} "
                    f"{yc:.6f} "
                    f"{w:.6f} "
                    f"{h:.6f}"
                )

                class_counts[class_name] += 1
                total_target_boxes += 1

            destination_image = (
                OUT_DIR
                / "images"
                / split
                / image_name
            )

            destination_label = (
                OUT_DIR
                / "labels"
                / split
                / (
                    Path(image_name).stem
                    + ".txt"
                )
            )

            shutil.copy2(
                source_image,
                destination_image
            )

            # Empty label file is intentional for images
            # containing no RoadAI target classes.
            destination_label.write_text(
                "\n".join(yolo_lines),
                encoding="utf-8"
            )

            total_images += 1

    # ------------------------------------------------------------
    # dataset.yaml
    # ------------------------------------------------------------

    yaml_text = f"""path: {OUT_DIR.as_posix()}
train: images/train
val: images/val
test: images/test

names:
  0: {CLASS_NAMES[0]}
  1: {CLASS_NAMES[1]}
  2: {CLASS_NAMES[2]}
  3: {CLASS_NAMES[3]}
"""

    (OUT_DIR / "dataset.yaml").write_text(
        yaml_text,
        encoding="utf-8"
    )

    print()
    print("=" * 70)
    print("CONVERSION COMPLETE")
    print("=" * 70)

    print(f"Images converted: {total_images}")
    print(f"Target boxes: {total_target_boxes}")
    print(f"Extra-label boxes skipped: {skipped_extra_boxes}")

    print()
    print("Target box counts:")

    for cls in CLASS_MAP:
        print(
            f"  {cls}: {class_counts[cls]}"
        )

    print()
    print("YOLO dataset:")
    print(OUT_DIR)

    print()
    print("Raw dataset modified: NO")


if __name__ == "__main__":
    main()
