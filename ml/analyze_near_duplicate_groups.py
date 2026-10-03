from pathlib import Path
import re

RESULT_FILE = Path("ml/near_duplicate_results.txt")

SPLIT_ROOTS = {
    "train": Path("ml/datasets/roadai_yolo/images/train"),
    "val": Path("ml/datasets/roadai_yolo/images/val"),
    "test": Path("ml/datasets/roadai_yolo/images/test"),
}

pairs = []

with open(RESULT_FILE, "r", encoding="utf-8") as f:
    for line in f:
        match = re.search(
            r"(India_\d+\.jpg)\s+<-->\s+(India_\d+\.jpg)\s+\(distance=(\d+)\)",
            line
        )

        if match:
            pairs.append(
                (
                    match.group(1),
                    match.group(2),
                    int(match.group(3))
                )
            )


# ------------------------------------------------------------
# Union-Find / Disjoint Set
# ------------------------------------------------------------

parent = {}
rank = {}


def make_set(x):
    if x not in parent:
        parent[x] = x
        rank[x] = 0


def find(x):
    if parent[x] != x:
        parent[x] = find(parent[x])
    return parent[x]


def union(a, b):
    root_a = find(a)
    root_b = find(b)

    if root_a == root_b:
        return

    if rank[root_a] < rank[root_b]:
        parent[root_a] = root_b
    elif rank[root_a] > rank[root_b]:
        parent[root_b] = root_a
    else:
        parent[root_b] = root_a
        rank[root_a] += 1


# Create sets and connect every near-duplicate pair
for image1, image2, distance in pairs:
    make_set(image1)
    make_set(image2)
    union(image1, image2)


# ------------------------------------------------------------
# Build groups
# ------------------------------------------------------------

groups = {}

for image in parent:
    root = find(image)
    groups.setdefault(root, []).append(image)

groups = list(groups.values())

groups.sort(key=lambda x: (-len(x), x))


# ------------------------------------------------------------
# Find dataset split
# ------------------------------------------------------------

def get_split(image_name):
    for split, root in SPLIT_ROOTS.items():
        if (root / image_name).exists():
            return split
    return "NOT_FOUND"


# ------------------------------------------------------------
# Analyze leakage
# ------------------------------------------------------------

cross_split_groups = []

for i, group in enumerate(groups, start=1):

    split_map = {}

    for image in sorted(group):
        split = get_split(image)
        split_map.setdefault(split, []).append(image)

    real_splits = set(split_map.keys()) - {"NOT_FOUND"}

    if len(real_splits) > 1:
        cross_split_groups.append(
            (i, split_map)
        )


# ------------------------------------------------------------
# Display results
# ------------------------------------------------------------

print("=" * 70)
print("ROADAI — NEAR-DUPLICATE SPLIT / LEAKAGE ANALYSIS")
print("=" * 70)

print(f"Near-duplicate pairs : {len(pairs)}")
print(f"Images involved      : {len(parent)}")
print(f"Groups found         : {len(groups)}")
print()

print("=" * 70)
print("SPLIT DISTRIBUTION")
print("=" * 70)

split_counts = {
    "train": 0,
    "val": 0,
    "test": 0,
    "NOT_FOUND": 0
}

for image in parent:
    split_counts[get_split(image)] += 1

for split, count in split_counts.items():
    print(f"{split:12}: {count}")

print()

print("=" * 70)
print("CROSS-SPLIT NEAR-DUPLICATE GROUPS")
print("=" * 70)

if not cross_split_groups:
    print("NONE FOUND")
    print()
    print("No near-duplicate group contains images from")
    print("more than one dataset split.")
else:
    print(f"Potential leakage groups: {len(cross_split_groups)}")
    print()

    for group_id, split_map in cross_split_groups:

        print(f"GROUP {group_id}")

        for split, images in sorted(split_map.items()):

            print(f"  [{split}]")

            for image in images:
                print(f"    {image}")

        print()

print("=" * 70)
print("FINAL RESULT")
print("=" * 70)

if not cross_split_groups:
    print("DATASET STATUS: NO CROSS-SPLIT NEAR-DUPLICATES FOUND")
else:
    print("DATASET STATUS: POTENTIAL CROSS-SPLIT LEAKAGE FOUND")

print("=" * 70)