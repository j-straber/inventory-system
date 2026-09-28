# __architect__ = "Jason Straber"
# __email__ = "jason@straberstudios.com"
# __version__ = "1.2.0"
# __license__ = "MIT"
# __copyright__ = "Copyright 2026, 5tra83r Studios LLC."
# __status__ = "Production"

"""Utility functions for generating barcodes and QR codes for inventory items.
Both functions return PNG bytes that can be streamed directly in a FastAPI response.
"""

import io
from typing import Tuple

import qrcode
from barcode import Code128
from barcode.writer import ImageWriter
from PIL import Image

def generate_barcode(data: str) -> bytes:
    """Generate a Code128 barcode PNG for the given string.
    Returns raw PNG bytes.
    """
    # ImageWriter creates a Pillow Image object
    barcode_obj = Code128(data, writer=ImageWriter())
    buffer = io.BytesIO()
    barcode_obj.write(buffer, {'format': 'PNG'})
    return buffer.getvalue()

def generate_qr(data: str, size: int = 300) -> bytes:
    """Generate a QR code PNG for the given string.
    `size` is the pixel dimension of the resulting square image.
    Returns raw PNG bytes.
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white").convert("RGB")
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()

def parse_location_string(location: str) -> Tuple[str, str, str, str]:
    """Parse a location string like "House 2, Room 3, Rack A, Shelf 1" into
    a tuple (house, room, rack, shelf). If the format is unexpected, returns
    empty strings for missing parts.
    """
    parts = [p.strip() for p in location.split(',')]
    # Pad to 4 parts
    while len(parts) < 4:
        parts.append("")
    return tuple(parts[:4])
