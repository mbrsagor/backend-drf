import io
import qrcode
import re, time, base64, os
from io import BytesIO
from PIL import Image

# Generate QR code
def generate_qr_code(data, size=10, border=0):
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=size, border=border)
    qr.add_data(data)
    qr.make(fit=True)
    img = qr.make_image()
    return img


# The function will use/call for the API
def generate_qr(url_text):
    generated_code = generate_qr_code(data=url_text, size=10, border=1)  # call the function
    bio = io.BytesIO()
    img_save = generated_code.save(bio)
    png_qr = bio.getvalue()
    base64qr = base64.b64encode(png_qr)
    img_name = base64qr.decode("utf-8")
    return img_name
