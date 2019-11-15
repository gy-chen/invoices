import base64
from PIL import Image
from io import BytesIO


def decode_base64_image(base64_content):
    """decode base64 image

    expect base64_contnet startswith data:image/jpg;base64.

    Args:
        base64_content

    Returns:
        pillow Image
    """
    prefix = "data:image/jpg;base64."
    if not base64_content.startswith(prefix):
        raise ValueError("only support data:image/jpg;base64.")
    img_base64_content = base64_content[len(prefix) :]
    return Image.open(BytesIO(base64.b64decode(img_base64_content)))
