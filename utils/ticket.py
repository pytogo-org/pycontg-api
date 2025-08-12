
import qrcode
import os
import cloudinary
import cloudinary.uploader
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A6
from PIL import Image, ImageDraw, ImageFont

from dotenv import load_dotenv


load_dotenv()


# Cloudinary setup
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET")
)



FONT_PATH = "static/fonts/Roboto-VariableFont_wdth,wght.ttf" 
font_title = ImageFont.truetype(FONT_PATH, 50)
font_text = ImageFont.truetype(FONT_PATH, 30)

from PIL import Image, ImageDraw, ImageFont
import qrcode


def generate_ticket_image(data, name, ref, organization, country_city="Togo/Lomé"):
    width, height = 1200, 600
    bg_color = (255, 255, 255)
    img = Image.new("RGB", (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    draw.text((width//2 - 250, 30), "Ticket - PyCon Togo 2025", fill="black", font=font_title)
    draw.text((50, 120), f"Name : {name}", fill="black", font=font_text)
    draw.text((50, 180), f"Reference : {ref}", fill="black", font=font_text)
    draw.text((50, 240), f"Country/City : {country_city}", fill="black", font=font_text)
    if organization:
        draw.text((50, 300), f"Company/Community : {organization}", fill="black", font=font_text)


    qr = qrcode.make(data).resize((230, 230))
    img.paste(qr, (900, 150))

    draw.line((50, 400, 1150, 400), fill="black", width=2)

    logo_paths = [
        ("static/images/pythontogo.png", "Python Togo"),
        ("static/images/psf.png", "PSF"),
        ("static/images/afpy.png", "AFPy"),
        ("static/images/bpd_stacked_us5ika.png", "BPD"),
        ("static/images/tahaga.png", "TAHAGA"),
        ("static/images/django-logo-positive.png", "Django"),
        ("static/images/github-logo.png", "GitHub")
    ]

    custom_sizes = {
        "PSF": (300, 70),
        "Python Togo": (180, 180)
    }

    default_size = (110, 60)
    resized_logos = []

    for path, name in logo_paths:
        logo = Image.open(path).convert("RGBA")
        target_width, target_height = custom_sizes.get(name, default_size)
        ratio = min(target_width / logo.width, target_height / logo.height)
        new_size = (int(logo.width * ratio), int(logo.height * ratio))
        resized_logos.append(logo.resize(new_size, Image.LANCZOS))

    total_width = sum(logo.width for logo in resized_logos) + (len(resized_logos) - 1) * 40
    start_x = (width - total_width) // 2
    y_position = 460

    x = start_x
    for logo in resized_logos:
        y = y_position + (70 - logo.height) // 2
        img.paste(logo, (x, y), logo)
        x += logo.width + 40

    return img


def upload_ticket_to_cloudinary(pil_img, filename):
    buffer = BytesIO()
    pil_img.save(buffer, format="PNG")
    buffer.seek(0)
    result = cloudinary.uploader.upload(buffer, public_id=f"tickets/{filename}", folder="pycon2025", resource_type="image")
    return result["secure_url"]



def ticket_system(data=None, name=None, organization=None, country_city="Togo/Lomé"):
    ref = generate_ticket_reference(data)
    ticket_img = generate_ticket_image(data, name, ref, organization, country_city)
    ticket_url = upload_ticket_to_cloudinary(ticket_img, ref)
    return ticket_url

def generate_ticket_reference(participant_id):
    short_part = str(participant_id).split("-")[0][:6].upper()  
    return f"PYCONTG-2025-{short_part}"

