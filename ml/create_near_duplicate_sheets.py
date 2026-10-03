from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

# ============================================================
# ROADAI — NEAR-DUPLICATE VISUAL INSPECTION SHEET
# ============================================================

IMAGE_DIR = Path("ml/datasets/raw/rdd2020_india/train/India/images")
RESULT_FILE = Path("ml/near_duplicate_results.txt")
OUTPUT_DIR = Path("ml/near_duplicate_inspection")

THUMB_WIDTH = 240
THUMB_HEIGHT = 240
LABEL_HEIGHT = 55
PAIRS_PER_SHEET = 10


def read_pairs():
    pairs = []

    if not RESULT_FILE.exists():
        print(f"ERROR: Results file not found: {RESULT_FILE}")
        return pairs

    with open(RESULT_FILE, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()

            if "<-->" not in line:
                continue

            try:
                left, right = line.split("<-->", 1)

                name1 = left.strip()
                right = right.strip()

                name2 = right.split("(distance=", 1)[0].strip()
                distance = int(
                    right.split("(distance=", 1)[1].split(")", 1)[0]
                )

                pairs.append((name1, name2, distance))

            except Exception:
                continue

    return pairs


def make_sheet(pairs, sheet_number):
    columns = 2
    rows = len(pairs)

    sheet_width = columns * THUMB_WIDTH
    sheet_height = rows * (THUMB_HEIGHT + LABEL_HEIGHT)

    sheet = Image.new("RGB", (sheet_width, sheet_height), "white")
    draw = ImageDraw.Draw(sheet)

    for row, (name1, name2, distance) in enumerate(pairs):

        y = row * (THUMB_HEIGHT + LABEL_HEIGHT)

        for col, filename in enumerate([name1, name2]):

            x = col * THUMB_WIDTH
            image_path = IMAGE_DIR / filename

            try:
                with Image.open(image_path) as img:
                    img = img.convert("RGB")
                    img.thumbnail((THUMB_WIDTH - 10, THUMB_HEIGHT - 10))

                    paste_x = x + (THUMB_WIDTH - img.width) // 2
                    paste_y = y + (THUMB_HEIGHT - img.height) // 2

                    sheet.paste(img, (paste_x, paste_y))

            except Exception as e:
                draw.text(
                    (x + 10, y + 10),
                    f"ERROR\n{filename}\n{e}",
                    fill="black"
                )

            draw.text(
                (x + 5, y + THUMB_HEIGHT + 5),
                filename,
                fill="black"
            )

        draw.text(
            (sheet_width // 2 - 60, y + THUMB_HEIGHT + 5),
            f"Distance: {distance}",
            fill="black"
        )

    output_file = OUTPUT_DIR / f"sheet_{sheet_number:02d}.jpg"
    sheet.save(output_file, quality=95)

    return output_file


def main():
    print("=" * 60)
    print("ROADAI — NEAR-DUPLICATE VISUAL INSPECTION")
    print("=" * 60)

    pairs = read_pairs()

    print(f"Near-duplicate pairs loaded: {len(pairs)}")

    if not pairs:
        print("ERROR: No near-duplicate pairs found.")
        return

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    sheet_number = 1

    for start in range(0, len(pairs), PAIRS_PER_SHEET):

        batch = pairs[start:start + PAIRS_PER_SHEET]

        output_file = make_sheet(batch, sheet_number)

        print(f"Created: {output_file}")

        sheet_number += 1

    print()
    print("=" * 60)
    print("VISUAL INSPECTION SHEETS CREATED")
    print("=" * 60)
    print(f"Total pairs : {len(pairs)}")
    print(f"Sheets      : {sheet_number - 1}")
    print(f"Folder      : {OUTPUT_DIR}")
    print()
    print("No original dataset files were modified.")
    print("=" * 60)


if __name__ == "__main__":
    main()
