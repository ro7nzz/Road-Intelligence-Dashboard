from pathlib import Path
from collections import defaultdict
import xml.etree.ElementTree as ET
import numpy as np

from scipy.optimize import milp, Bounds, LinearConstraint

SEED = 42

ROOT = Path(__file__).resolve().parent.parent

RAW_IMAGES = ROOT / "ml" / "datasets" / "raw" / "rdd2020_india" / "train" / "India" / "images"
RAW_XML = ROOT / "ml" / "datasets" / "raw" / "rdd2020_india" / "train" / "India" / "annotations" / "xmls"
NEAR_DUP = ROOT / "ml" / "near_duplicate_results.txt"
OUT_DIR = ROOT / "ml" / "split_manifests"

TARGET_CLASSES = ["D00", "D10", "D20", "D40"]
SPLITS = ["train", "val", "test"]


def read_labels(xml_path):
    labels = set()
    root = ET.parse(xml_path).getroot()

    for obj in root.findall("object"):
        name = obj.find("name")

        if name is not None and name.text:
            value = name.text.strip()

            if value in TARGET_CLASSES:
                labels.add(value)

    return frozenset(labels)


def load_metadata():
    metadata = {}

    images = sorted(RAW_IMAGES.glob("*.jpg"))

    if len(images) != 7706:
        raise RuntimeError(
            f"Expected 7706 JPG images, found {len(images)}"
        )

    for image in images:
        xml = RAW_XML / f"{image.stem}.xml"

        if not xml.exists():
            raise RuntimeError(
                f"Missing XML: {xml.name}"
            )

        metadata[image.name] = read_labels(xml)

    return metadata


def load_near_duplicate_groups(all_images):
    parent = {x: x for x in all_images}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    def union(a, b):
        ra = find(a)
        rb = find(b)

        if ra != rb:
            parent[rb] = ra

    pairs = 0

    with NEAR_DUP.open("r", encoding="utf-8") as f:

        for line in f:

            parts = line.replace(",", " ").split()

            jpgs = [
                p.strip("()[]{}:;")
                for p in parts
                if p.lower().endswith(".jpg")
            ]

            if len(jpgs) < 2:
                continue

            a, b = jpgs[0], jpgs[1]

            if a in parent and b in parent and a != b:
                union(a, b)
                pairs += 1

    components = defaultdict(list)

    for image in all_images:
        components[find(image)].append(image)

    groups = [
        sorted(v)
        for v in components.values()
    ]

    groups.sort(
        key=lambda x: (-len(x), x[0])
    )

    return groups, pairs


def main():

    print()
    print("RoadAI - Final Leakage-Aware MILP Split")
    print("=" * 70)

    print()
    print("Reading annotations...")

    metadata = load_metadata()
    all_images = sorted(metadata)

    print(f"Images: {len(all_images)}")

    print()
    print("Loading near-duplicate groups...")

    groups, pairs = load_near_duplicate_groups(
        all_images
    )

    multi_groups = [
        g for g in groups
        if len(g) > 1
    ]

    singleton_groups = [
        g for g in groups
        if len(g) == 1
    ]

    print(f"Near-duplicate pairs: {pairs}")
    print(f"Near-duplicate groups: {len(multi_groups)}")
    print(f"Total groups: {len(groups)}")
    print(f"Multi-image groups: {len(multi_groups)}")
    print(f"Singleton images: {len(singleton_groups)}")

    # ------------------------------------------------------------
    # Singleton categories
    # ------------------------------------------------------------

    category_members = defaultdict(list)

    for group in singleton_groups:
        image = group[0]
        category_members[metadata[image]].append(image)

    categories = sorted(
        category_members.keys(),
        key=lambda x: (
            len(x),
            tuple(sorted(x))
        )
    )

    print(f"Singleton categories: {len(categories)}")

    # ------------------------------------------------------------
    # Targets
    # ------------------------------------------------------------

    total_images = len(all_images)

    image_targets = {
        "train": int(total_images * 0.70),
        "val": int(total_images * 0.15),
    }

    image_targets["test"] = (
        total_images
        - image_targets["train"]
        - image_targets["val"]
    )

    class_total = {
        cls: sum(
            1
            for image in all_images
            if cls in metadata[image]
        )
        for cls in TARGET_CLASSES
    }

    negative_total = sum(
        1
        for image in all_images
        if not metadata[image]
    )

    class_targets = {}

    for cls in TARGET_CLASSES:

        train = round(class_total[cls] * 0.70)
        val = round(class_total[cls] * 0.15)

        class_targets[cls] = {
            "train": train,
            "val": val,
            "test": class_total[cls] - train - val,
        }

    negative_targets = {
        "train": round(negative_total * 0.70),
        "val": round(negative_total * 0.15),
    }

    negative_targets["test"] = (
        negative_total
        - negative_targets["train"]
        - negative_targets["val"]
    )

    print()
    print("Target image counts:")
    print(image_targets)

    print()
    print("Target negative counts:")
    print(negative_targets)

    print()
    print("Target class image counts:")

    for cls in TARGET_CLASSES:
        print(
            f"  {cls}: {class_targets[cls]}"
        )

    # ------------------------------------------------------------
    # Variables
    #
    # x[g,s] = binary assignment of multi group
    # y[c,s] = number of singleton images from category c
    # d[m,s] = absolute deviation
    # ------------------------------------------------------------

    G = len(multi_groups)
    C = len(categories)

    x_count = G * 3
    y_count = C * 3

    metrics = [
        ("class", cls)
        for cls in TARGET_CLASSES
    ]

    metrics.append(
        ("negative", "negative")
    )

    deviation_keys = [
        (metric_type, metric_name, split)
        for metric_type, metric_name in metrics
        for split in SPLITS
    ]

    deviation_start = x_count + y_count
    total_variables = (
        deviation_start + len(deviation_keys)
    )

    c = np.zeros(total_variables)

    # Strong D10 priority.
    weights = {
        "D00": 5.0,
        "D10": 30.0,
        "D20": 5.0,
        "D40": 5.0,
        "negative": 4.0,
    }

    deviation_index = {}

    for i, key in enumerate(deviation_keys):
        idx = deviation_start + i
        deviation_index[key] = idx
        c[idx] = weights[key[1]]

    # Tiny deterministic tie-break.
    for i in range(x_count + y_count):
        c[i] += (i + 1) * 1e-9

    lower = np.zeros(total_variables)
    upper = np.full(total_variables, np.inf)
    integrality = np.zeros(total_variables)

    # x = binary.
    for i in range(x_count):
        upper[i] = 1
        integrality[i] = 1

    # y = integer, bounded by category size.
    for k, category in enumerate(categories):
        count = len(category_members[category])

        for s in range(3):
            idx = x_count + k * 3 + s
            upper[idx] = count
            integrality[idx] = 1

    bounds = Bounds(
        lower,
        upper
    )

    rows = []
    lb = []
    ub = []

    # ------------------------------------------------------------
    # 1. Every multi-image group goes to exactly one split.
    # ------------------------------------------------------------

    for g in range(G):

        row = np.zeros(total_variables)

        for s in range(3):
            row[g * 3 + s] = 1

        rows.append(row)
        lb.append(1)
        ub.append(1)

    # ------------------------------------------------------------
    # 2. Every singleton category is fully distributed.
    # ------------------------------------------------------------

    for k, category in enumerate(categories):

        count = len(category_members[category])

        row = np.zeros(total_variables)

        for s in range(3):
            row[x_count + k * 3 + s] = 1

        rows.append(row)
        lb.append(count)
        ub.append(count)

    # ------------------------------------------------------------
    # 3. Exact total image count per split.
    # ------------------------------------------------------------

    for s, split in enumerate(SPLITS):

        row = np.zeros(total_variables)

        # Multi groups contribute their full size.
        for g, group in enumerate(multi_groups):
            row[g * 3 + s] = len(group)

        # Singleton categories contribute their count.
        for k, category in enumerate(categories):
            row[x_count + k * 3 + s] = 1

        rows.append(row)

        lb.append(image_targets[split])
        ub.append(image_targets[split])

    # ------------------------------------------------------------
    # 4. Absolute deviation constraints for class/negative counts.
    # ------------------------------------------------------------

    for metric_type, metric_name in metrics:

        for s, split in enumerate(SPLITS):

            actual = np.zeros(total_variables)

            # Multi groups.
            for g, group in enumerate(multi_groups):

                if metric_name == "negative":
                    value = (
                        len(group)
                        if all(
                            not metadata[image]
                            for image in group
                        )
                        else 0
                    )

                else:
                    value = (
                        1
                        if any(
                            metric_name in metadata[image]
                            for image in group
                        )
                        else 0
                    )

                actual[g * 3 + s] = value

            # Singleton categories.
            for k, category in enumerate(categories):

                idx = x_count + k * 3 + s

                if metric_name == "negative":
                    value = (
                        1
                        if len(category) == 0
                        else 0
                    )
                else:
                    value = (
                        1
                        if metric_name in category
                        else 0
                    )

                actual[idx] = value

            d = deviation_index[
                (metric_type, metric_name, split)
            ]

            target = (
                negative_targets[split]
                if metric_name == "negative"
                else class_targets[metric_name][split]
            )

            # actual - deviation <= target
            row1 = actual.copy()
            row1[d] = -1

            rows.append(row1)
            lb.append(-np.inf)
            ub.append(target)

            # actual + deviation >= target
            row2 = actual.copy()
            row2[d] = 1

            rows.append(row2)
            lb.append(target)
            ub.append(np.inf)

    A = np.vstack(rows)

    constraints = LinearConstraint(
        A,
        np.array(lb),
        np.array(ub)
    )

    print()
    print(f"MILP variables: {total_variables}")
    print(f"MILP constraints: {len(rows)}")

    print()
    print("Solving MILP...")
    print("Please wait...")

    result = milp(
        c=c,
        integrality=integrality,
        bounds=bounds,
        constraints=constraints,
        options={
            "time_limit": 180,
            "mip_rel_gap": 0.0,
            "presolve": True,
        },
    )

    if not result.success:
        raise RuntimeError(
            "MILP failed.\n"
            f"Status: {result.status}\n"
            f"Message: {result.message}"
        )

    print()
    print("MILP solution found.")

    solution = result.x

    assignments = {
        split: []
        for split in SPLITS
    }

    # Multi groups.
    for g, group in enumerate(multi_groups):

        values = [
            solution[g * 3 + s]
            for s in range(3)
        ]

        selected = int(
            np.argmax(values)
        )

        assignments[
            SPLITS[selected]
        ].extend(group)

    # Singleton categories.
    for k, category in enumerate(categories):

        members = list(
            category_members[category]
        )

        offset = x_count + k * 3

        start = 0

        for s, split in enumerate(SPLITS):

            count = int(
                round(solution[offset + s])
            )

            assignments[split].extend(
                members[start:start + count]
            )

            start += count

    # ------------------------------------------------------------
    # Validation
    # ------------------------------------------------------------

    print()
    print("Validating final split...")

    assigned = []

    for split in SPLITS:
        assigned.extend(assignments[split])

    if len(assigned) != total_images:
        raise RuntimeError(
            f"Assigned {len(assigned)} images, expected {total_images}."
        )

    if len(set(assigned)) != total_images:
        raise RuntimeError(
            "Duplicate image assignment detected."
        )

    if set(assigned) != set(all_images):
        raise RuntimeError(
            "Assigned image set does not match dataset."
        )

    image_split = {}

    for split in SPLITS:
        for image in assignments[split]:
            image_split[image] = split

    crossing = []

    for group in groups:

        used = {
            image_split[image]
            for image in group
        }

        if len(used) > 1:
            crossing.append(group)

    if crossing:
        raise RuntimeError(
            f"{len(crossing)} near-duplicate groups cross splits."
        )

    # ------------------------------------------------------------
    # Report
    # ------------------------------------------------------------

    OUT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    report = []

    report.append(
        "RoadAI Final Leakage-Aware Dataset Split"
    )
    report.append("=" * 70)
    report.append(f"Seed: {SEED}")
    report.append(
        f"Total images: {total_images}"
    )
    report.append(
        f"Near-duplicate pairs: {pairs}"
    )
    report.append(
        f"Near-duplicate groups: {len(multi_groups)}"
    )
    report.append("")

    for split in SPLITS:

        imgs = assignments[split]

        negatives = sum(
            1
            for image in imgs
            if not metadata[image]
        )

        positives = len(imgs) - negatives

        report.append(split.upper())
        report.append("-" * 30)
        report.append(
            f"Images: {len(imgs)} "
            f"({len(imgs) / total_images * 100:.2f}%)"
        )
        report.append(
            f"Positive images: {positives}"
        )
        report.append(
            f"Negative images: {negatives}"
        )

        for cls in TARGET_CLASSES:

            count = sum(
                1
                for image in imgs
                if cls in metadata[image]
            )

            target = class_targets[cls][split]

            report.append(
                f"{cls}: {count} "
                f"(target {target}, "
                f"diff {count - target:+d})"
            )

        report.append("")

    report.append(
        f"Near-duplicate groups crossing splits: {len(crossing)}"
    )
    report.append(
        f"Images assigned: {len(assigned)}/{total_images}"
    )
    report.append(
        "Raw dataset modified: NO"
    )
    report.append(
        "Validation: PASSED"
    )

    report_text = "\n".join(report)

    print()
    print(report_text)

    # Manifests.
    for split in SPLITS:

        path = OUT_DIR / f"{split}.txt"

        with path.open(
            "w",
            encoding="utf-8"
        ) as f:

            for image in sorted(assignments[split]):
                f.write(image + "\n")

    (OUT_DIR / "split_report.txt").write_text(
        report_text,
        encoding="utf-8"
    )

    print()
    print("Split completed successfully.")
    print(
        f"Manifests written to: {OUT_DIR}"
    )


if __name__ == "__main__":
    main()
