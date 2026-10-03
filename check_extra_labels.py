import xml.etree.ElementTree as ET
import glob
import os

target = {"D00", "D10", "D20", "D40"}
found = {}

files = glob.glob(
    r".\ml\datasets\raw\rdd2020_india\train\India\annotations\xmls\*.xml"
)

for f in files:
    root = ET.parse(f).getroot()

    for obj in root.findall(".//object"):
        label = obj.find("name").text

        if label not in target and label not in found:
            found[label] = os.path.basename(f)

print("First example file for each extra label:")

for label, filename in sorted(found.items()):
    print(label, ":", filename)
