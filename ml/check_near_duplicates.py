from pathlib import Path
from PIL import Image
import imagehash

# ============================================================
# ROADAI — NEAR-DUPLICATE IMAGE CHECK
# ============================================================

IMAGE_DIR = Path("ml/datasets/raw/rdd2020_india/train/India/images")
OUTPUT_FILE = Path("ml/near_duplicate_results.txt")

# Hamming distance threshold
# 0 = perceptually identical
# Smaller value = more similar
THRESHOLD = 5


def main():
    if not IMAGE_DIR.exists():
        print("ERROR: Image directory not found:")
        print(IMAGE_DIR.resolve())
        return

    image_files = sorted(IMAGE_DIR.glob("*.jpg"))

    print("=" * 60)
    print("ROADAI — NEAR-DUPLICATE IMAGE CHECK")
    print("=" * 60)
    print(f"Image directory : {IMAGE_DIR}")
    print(f"Images found    : {len(image_files)}")
    print(f"Threshold       : {THRESHOLD}")
    print()

    if not image_files:
        print("ERROR: No JPG images found.")
        return

    # --------------------------------------------------------
    # Step 1: Generate perceptual hashes
    # --------------------------------------------------------

    hashes = {}

    print("Generating perceptual hashes...")

    for i, image_path in enumerate(image_files, start=1):
        try:
            with Image.open(image_path) as img:
                img = img.convert("RGB")
                hashes[image_path.name] = imagehash.phash(img)

        except Exception as e:
            print(f"ERROR reading {image_path.name}: {e}")

        if i % 500 == 0 or i == len(image_files):
            print(f"Processed: {i}/{len(image_files)}")

    print()
    print(f"Successfully hashed: {len(hashes)} images")
    print()

    # --------------------------------------------------------
    # Step 2: Find near-duplicate pairs
    # --------------------------------------------------------

    print("Searching for near-duplicate pairs...")
    print("This may take some time.")
    print()

    near_duplicates = []

    hash_items = list(hashes.items())

    total_comparisons = len(hash_items) * (len(hash_items) - 1) // 2
    comparison_count = 0

    for i in range(len(hash_items)):
        name1, hash1 = hash_items[i]

        for j in range(i + 1, len(hash_items)):
            name2, hash2 = hash_items[j]

            distance = hash1 - hash2

            if distance <= THRESHOLD:
                near_duplicates.append(
                    (name1, name2, distance)
                )

            comparison_count += 1

        if (i + 1) % 500 == 0 or i == len(hash_items) - 1:
            print(
                f"Compared approximately "
                f"{comparison_count:,}/{total_comparisons:,} pairs"
            )

    # --------------------------------------------------------
    # Step 3: Save results
    # --------------------------------------------------------

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("ROADAI — NEAR-DUPLICATE IMAGE CHECK\n")
        f.write("=" * 60 + "\n\n")

        f.write(f"Images scanned: {len(hashes)}\n")
        f.write(f"Hamming distance threshold: {THRESHOLD}\n")
        f.write(
            f"Near-duplicate pairs found: "
            f"{len(near_duplicates)}\n\n"
        )

        if near_duplicates:
            f.write("NEAR-DUPLICATE PAIRS\n")
            f.write("-" * 60 + "\n")

            for name1, name2, distance in near_duplicates:
                f.write(
                    f"{name1} <--> {name2} "
                    f"(distance={distance})\n"
                )
        else:
            f.write(
                "No near-duplicate pairs were found "
                f"at threshold {THRESHOLD}.\n"
            )

    # --------------------------------------------------------
    # Final summary
    # --------------------------------------------------------

    print("=" * 60)
    print("CHECK COMPLETE")
    print("=" * 60)
    print(f"Images scanned        : {len(hashes)}")
    print(f"Near-duplicate pairs  : {len(near_duplicates)}")
    print(f"Results saved to      : {OUTPUT_FILE}")
    print()
    print("IMPORTANT:")
    print("A near-duplicate pair does NOT automatically mean")
    print("data leakage. We will inspect the results first.")
    print("=" * 60)


if __name__ == "__main__":
    main()
