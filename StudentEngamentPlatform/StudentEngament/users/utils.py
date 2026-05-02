# users/utils.py

import qrcode
import io
import base64


def generate_qr(data: str):
    img = qrcode.make(data)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")

    return base64.b64encode(buffer.getvalue()).decode()