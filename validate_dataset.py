from pathlib import Path
import xml.etree.ElementTree as ET
from PIL import Image

BASE = Path(r".\ml\datasets\raw\rdd2020_india\train\India")
IMAGE_DIR = BASE / "images"
XML_DIR = BASE / "annotations" / "xmls"

TARGET_CLASSES = {"D00", "D10", "D20", "D40"}
ALL_KNOWN_EXTRA = {"D01", "D0w0", "D11", "D43", "D44", "D50"}

images = {p.stem: p for p in IMAGE_DIR.glob("*.jpg")}
xmls = {p.stem: p for p in XML_DIR.glob("*.xml")}

missing_xml = sorted(set(images) - set(xmls))
missing_images = sorted(set(xmls) - set(images))

empty_xml = []
invalid_boxes = []
out_of_bounds = []
invalid_classes = []
broken_images = []
dimensions = {}

for stem, img_path in images.items():
    try:
        with Image.open(img_path) as img:
            img.verify()

        with Image.open(img_path) as img:
            dimensions.setdefault(img.size, 0)
            dimensions[img.size] += 1

    except Exception as e:
        broken_images.append((img_path.name, str(e)))

for stem, xml_path in xmls.items():
    try:
        root = ET.parse(xml_path).getroot()
        objects = root.findall(".//object")

        if not objects:
            empty_xml.append(xml_path.name)
            continue

        img_path = images.get(stem)

        if img_path and img_path.exists():
            with Image.open(img_path) as img:
                width, height = img.size
        else:
            width = height = None

        for obj in objects:
            name = obj.find("name")

            if name is None or not name.text:
                invalid_classes.append((xml_path.name, "MISSING_CLASS"))
                continue

            label = name.text.strip()

            if label not in TARGET_CLASSES and label not in ALL_KNOWN_EXTRA:
                invalid_classes.append((xml_path.name, label))

            box = obj.find("bndbox")

            if box is None:
                invalid_boxes.append((xml_path.name, label, "MISSING_BBOX"))
                continue

            try:
                xmin = float(box.find("xmin").text)
                ymin = float(box.find("ymin").text)
                xmax = float(box.find("xmax").text)
                ymax = float(box.find("ymax").text)
            except Exception:
                invalid_boxes.append((xml_path.name, label, "NON_NUMERIC"))
                continue

            if xmin >= xmax or ymin >= ymax:
                invalid_boxes.append(
                    (xml_path.name, label, f"INVALID_COORDS [{xmin},{ymin},{xmax},{ymax}]")
                )

            if width is not None and height is not None:
                if xmin < 0 or ymin < 0 or xmax > width or ymax > height:
                    out_of_bounds.append(
                        (xml_path.name, label, f"BOX [{xmin},{ymin},{xmax},{ymax}] IMAGE [{width},{height}]")
                    )

    except Exception as e:
        invalid_boxes.append((xml_path.name, "XML_ERROR", str(e)))

print("\n========== ROADAI DATASET INTEGRITY REPORT ==========\n")

print("Images found:", len(images))
print("XML files found:", len(xmls))

print("\n--- IMAGE / XML MATCHING ---")
print("Missing XML files:", len(missing_xml))
print("Missing image files:", len(missing_images))

print("\n--- ANNOTATIONS ---")
print("Empty XML files:", len(empty_xml))
print("Invalid class entries:", len(invalid_classes))
print("Invalid bounding boxes:", len(invalid_boxes))
print("Out-of-bounds bounding boxes:", len(out_of_bounds))

print("\n--- IMAGE HEALTH ---")
print("Broken/unreadable images:", len(broken_images))

print("\n--- IMAGE DIMENSIONS ---")
for size, count in sorted(dimensions.items()):
    print(size, ":", count)

print("\n======================================================")

if not missing_xml and not missing_images and not empty_xml and not invalid_boxes and not out_of_bounds and not broken_images:
    print("\nCORE DATASET INTEGRITY: PASS")
else:
    print("\nCORE DATASET INTEGRITY: REVIEW REQUIRED")

if invalid_classes:
    print("\nExtra/unknown labels detected:", len(invalid_classes))
    print("(Known extra RDD2020 labels are expected and will be filtered during YOLO conversion.)")

print("\n======================================================")
