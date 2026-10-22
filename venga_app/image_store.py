import io
import os
import uuid

from flask import current_app
from PIL import (
    Image,
    ImageOps,
    UnidentifiedImageError,
)

MAX_FILE_SIZE = 800_000  # 0.8 MB (800 KB)
MAX_DIMENSION = 1600
MIN_DIMENSION = 320

ALLOWED_FORMATS = {
    "JPEG": "jpg",
    "PNG": "png",
    "WEBP": "webp",
}


def _compress_image(image):
    """Resize and compress until the saved image is at most 800 KB."""

    image.thumbnail(
        (1600, 1600),
        Image.Resampling.LANCZOS,
    )

    if image.mode in ("RGBA", "LA") or (
        image.mode == "P" and "transparency" in image.info
    ):
        rgba = image.convert("RGBA")
        background = Image.new("RGB", rgba.size, "white")
        background.paste(rgba, mask=rgba.getchannel("A"))
        image = background
    else:
        image = image.convert("RGB")

    max_bytes = 800_000
    min_dimension = 400

    while True:
        buffer = io.BytesIO()

        image.save(
            buffer,
            format="JPEG",
            quality=80,
            optimize=True,
        )

        data = buffer.getvalue()

        if len(data) <= max_bytes:
            return data

        width, height = image.size

        if max(width, height) <= min_dimension:
            # Return the smallest result we could produce.
            # The 800 KB target is a goal, not a hard rejection.
            return data

        # Reduce both dimensions by 20%, preserving aspect ratio.
        image = image.resize(
            (
                max(1, int(width * 0.8)),
                max(1, int(height * 0.8)),
            ),
            Image.Resampling.LANCZOS,
        )


def save_boulder_photo(upload):
    """Validate, resize, compress, and save an uploaded photo.

    Returns a path relative to Flask's static directory.
    """

    if not upload or not upload.filename:
        raise ValueError("Please select a photo.")

    try:
        upload.stream.seek(0)

        with Image.open(upload.stream) as image:
            if image.format not in ALLOWED_FORMATS:
                raise ValueError(
                    "Please upload a JPG, PNG, or WebP image."
                )

            image.verify()

        # Reopen after verify(), then correct phone-camera orientation.
        upload.stream.seek(0)

        with Image.open(upload.stream) as image:
            image = ImageOps.exif_transpose(image)
            image.load()

            image_data = _compress_image(image)

    except ValueError:
        raise
    except (
        UnidentifiedImageError,
        OSError,
        Image.DecompressionBombError,
    ):
        raise ValueError(
            "The uploaded file is not a valid or supported image."
        ) from None

    # Final size check before writing to disk.
    if len(image_data) > MAX_FILE_SIZE:
        raise ValueError("The compressed image exceeds 800 KB.")

    relative_directory = os.path.join("uploads", "boulders")
    upload_directory = os.path.join(
        current_app.static_folder,
        relative_directory,
    )

    os.makedirs(upload_directory, exist_ok=True)

    filename = f"{uuid.uuid4().hex}.jpg"
    destination = os.path.join(upload_directory, filename)

    with open(destination, "wb") as output:
        output.write(image_data)

    return os.path.join(
        relative_directory,
        filename,
    ).replace("\\", "/")
