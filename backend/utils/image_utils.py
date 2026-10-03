import io
from PIL import Image


def load_image_from_bytes(image_bytes: bytes) -> Image.Image:
    """
    Validates and loads an image from raw bytes using Pillow.
    Raises ValueError if the image content is empty or invalid.
    """
    if not image_bytes:
        raise ValueError("Uploaded file is empty.")

    try:
        image = Image.open(io.BytesIO(image_bytes))
        image.verify()  # Verify image integrity
        # Re-open after verify() as verify() can mutate file pointer state
        image = Image.open(io.BytesIO(image_bytes))
        image = image.convert("RGB")
        return image
    except Exception as e:
        raise ValueError(f"Invalid or corrupted image format: {str(e)}")
