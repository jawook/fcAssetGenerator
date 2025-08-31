#%% Import Packages
import io
import datetime
from PIL import Image, ImageOps, ImageDraw, ImageFont
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

#%% Key inputs

TITLE_FONT_PATH = "DejaVuSans-Bold.ttf"
BODY_FONT_PATH = "DejaVuSans.ttf"
logo_img = Image.open("Forever Canadian No Background.png").convert("RGBA")
bg = Image.open("background.png").convert("RGB")
qr_img = Image.open('qrcode.png').convert("RGBA")    
site_address = 'Forever-Canadian.ca'
question1 = 'Sign the Petition:'
question2 = 'Do you agree that Alberta should remain in Canada?'

POSTER_WIDTH, POSTER_HEIGHT = 2550, 3300  # 8.5x11 in @ ~300 DPI

#%% Function definition

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype("DejaVuSans.ttf", size)

def load_background_canvas(path="background.png", w=POSTER_WIDTH, h=POSTER_HEIGHT):
    """
    Load 'background.png' and fill the 2550x3300 canvas.
    Uses a center-crop to preserve aesthetics and avoid stretching.
    """
    bg_fitted = ImageOps.fit(bg, (w, h), method=Image.Resampling.LANCZOS, centering=(0.5, 0.5))
    return bg_fitted

def place_centered_text(draw, text, y, font, fill, w=POSTER_WIDTH):
    bbox = draw.textbbox((0,0), text, font=font, anchor="lt")
    text_w = bbox[2]-bbox[0]
    x = (w - text_w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + (bbox[3]-bbox[1])

def render_poster(city, address_line1, address_line2, date_str, time_str):
    
    img = load_background_canvas()
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font = load_font(TITLE_FONT_PATH, 190)
    subtitle_font = load_font(TITLE_FONT_PATH, 90)
    body_font = load_font(BODY_FONT_PATH, 70)
    site_font = load_font(TITLE_FONT_PATH, 75)

    # Top logo (optional)
    top_y = int(POSTER_HEIGHT*0.07)
    max_w = int(POSTER_WIDTH*0.24)
    ratio = min(max_w/logo_img.width, (POSTER_HEIGHT*0.15)/logo_img.height)
    logo = logo_img.resize((int(logo_img.width*ratio), int(logo_img.height*ratio)))
    img.paste(logo, ((POSTER_WIDTH - logo.width)//2, top_y), mask=logo if logo.mode=="RGBA" else None)
    top_y += logo.height + 20

    # CITY (big red)
    city_y = top_y + 40
    city_text = city.upper()
    draw.text((POSTER_WIDTH//2, city_y), city_text, font=title_font, fill="#E53935", anchor="ma")
    city_bbox = draw.textbbox((POSTER_WIDTH//2, city_y), city_text, font=title_font, anchor="ma")
    y = city_bbox[3] + 60

    # Date
    draw.text((POSTER_WIDTH//2, y), date_str, font=subtitle_font, fill="white", anchor="ma")
    y += 120

    # Address (two lines: 1) full address 2) postal)
    draw.text((POSTER_WIDTH//2, y), address_line1, font=body_font, 
              fill="white", anchor="ma")
    y += 85
    draw.text((POSTER_WIDTH//2, y), address_line2, font=body_font, 
              fill="white", anchor="ma")
    y += 85
    
    # Time
    y += 20
    draw.text((POSTER_WIDTH//2, y), time_str, font=subtitle_font, fill="white", anchor="ma")

    # Petition Question
    y += 400
    draw.text((POSTER_WIDTH//2, y), question1, font=subtitle_font, fill=(255,0,0), anchor="ma")
    y += 115
    draw.text((POSTER_WIDTH//2, y), question2, font=body_font, fill=(255,0,0), anchor="ma")
    
    # Site (bottom, above grass)
    draw.text((POSTER_WIDTH//2, int(POSTER_HEIGHT*0.8)), site_address, 
              font=site_font, fill="black", anchor="ma")

    # Add QR Code
    top_y = int(POSTER_HEIGHT*0.85)
    max_w = int(POSTER_WIDTH*0.15)
    ratio = min(max_w/qr_img.width, (POSTER_HEIGHT*0.15)/qr_img.height)
    qr = qr_img.resize((int(qr_img.width*ratio), int(qr_img.height*ratio)))
    img.paste(qr, ((POSTER_WIDTH - qr.width)//2, top_y), mask=qr if qr.mode=="RGBA" else None)

    return img

def to_pdf_bytes_flat(poster_img):
    # Flatten the already-rendered PIL poster image into a single-page PDF.

    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=letter)
    W, H = letter  # 612 x 792 points

    # Draw the PIL image as-is to fill the page
    c.drawImage(ImageReader(poster_img.convert("RGB")), 0, 0, width=W, height=H)

    c.showPage()
    c.save()
    buf.seek(0)
    return buf

#%% Streamlit Interface

poster = None
st.set_page_config(page_title="Poster Generator", page_icon="🖼️", layout="centered")

st.image(logo_img)
st.title("Generate your Own Event Details Poster")
st.write("""Enter the relevant information below and then click on 'Generate 
         Poster.'""")
st.write("""Wait for 'RUNNING...' in the upper left corner to disappear.""")
st.write("""Download buttons will appear beneath the preview image allowing you to 
         download in png or pdf format.""")
st.write("""PNG files are great for social media posts, PDF files are great for
         printing.""")

col1, col2 = st.columns(2)
with col1:
    city = st.text_input("City (e.g., Sherwood Park)", 
                         "Municipality Name")
    date_input = st.date_input("Event Date")
    time_start = st.time_input("Start Time")
    time_end = st.time_input("End Time", 
                             value = datetime.datetime.combine(
                                 datetime.date.today(),
                                 time_start
                                 ) + datetime.timedelta(hours=2)
                             )
with col2:
    address_line1 = st.text_input("Address line 1", 
                                  "Address Line 1")
    address_line2 = st.text_input("Address line 2 (optional)", 
                                  "")
    date_str = datetime.datetime.strftime(date_input, "%A, %B %d, %Y") if date_input else ""
    time_str = (
        f"{time_start.strftime('%I:%M %p').lstrip('0')} – {time_end.strftime('%I:%M %p').lstrip('0')}"
        if time_start and time_end else ""
    )
    if st.button("Generate Poster"):
        poster = render_poster(city, address_line1, address_line2, date_str, 
                               time_str)         

if poster != None:
    st.image(poster, caption="Preview (PNG)")
    # Download buttons
    png_buf = io.BytesIO()
    poster.save(png_buf, format="PNG", optimize=True)
    png_buf.seek(0)
    st.download_button("Download PNG (high-res)", data=png_buf, file_name=f"{city}_poster.png", mime="image/png")
    
    pdf_buf = to_pdf_bytes_flat(poster)
    st.download_button("Download PDF (print-ready)", data=pdf_buf, file_name=f"{city}_poster.pdf", mime="application/pdf")