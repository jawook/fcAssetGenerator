#%% Import Packages
import io
import datetime
from PIL import Image, ImageOps, ImageDraw, ImageFont
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader
from zoneinfo import ZoneInfo

#%% Key inputs

TITLE_FONT_PATH = "Aptos-ExtraBold.ttf"
BODY_FONT_PATH = "Aptos-Display.ttf"
logo_img = Image.open("Forever Canadian No Background.png").convert("RGBA")
bg = Image.open("background.png").convert("RGB")
qr_img = Image.open('qrcode.png').convert("RGBA")    
site_address = 'Forever-Canadian.ca'
question1 = 'Sign the Petition:'
question2 = 'Do you agree that Alberta should remain in Canada?'
APP_TZ = ZoneInfo("America/Edmonton")  # <- change if needed
font_size_title = 300
font_size_subtitle = 130
font_size_body = 90

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

def fit_font_to_width(draw, text, font_path, target_size, max_width, min_size=60):
    """
    Returns a PIL ImageFont that will render `text` no wider than `max_width`.
    Starts at `target_size` and scales down (one-pass estimate + small refine loop).
    """
    # Start at target size
    font = load_font(font_path, target_size)

    # Fast estimate: font size scales ~linearly with text width
    bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
    text_w = bbox[2] - bbox[0]
    if text_w > 0 and text_w > max_width:
        scale = max_width / text_w
        new_size = max(min_size, int(target_size * scale))
        font = load_font(font_path, new_size)

    # Refine to be safe
    while True:
        bbox = draw.textbbox((0, 0), text, font=font, anchor="lt")
        text_w = bbox[2] - bbox[0]
        if text_w <= max_width or font.size <= min_size:
            break
        font = load_font(font.path if hasattr(font, "path") else font_path, font.size - 2)

    return font

def place_centered_text(draw, text, y, font, fill, w=POSTER_WIDTH):
    bbox = draw.textbbox((0,0), text, font=font, anchor="lt")
    text_w = bbox[2]-bbox[0]
    x = (w - text_w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + (bbox[3]-bbox[1])

def render_poster(city, address_line1, address_line2, date_str, time_str,
                  questionText, addlInfo1, addlInfo2):
    
    img = load_background_canvas()
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font = load_font(TITLE_FONT_PATH, font_size_title)
    subtitle_font = load_font(TITLE_FONT_PATH, font_size_subtitle)
    body_font = load_font(BODY_FONT_PATH, font_size_body)

    # Top logo (optional)
    top_y = int(POSTER_HEIGHT*0.04)
    max_w = int(POSTER_WIDTH*0.30)
    ratio = min(max_w/logo_img.width, (POSTER_HEIGHT*0.18)/logo_img.height)
    logo = logo_img.resize((int(logo_img.width*ratio), int(logo_img.height*ratio)))
    img.paste(logo, ((POSTER_WIDTH - logo.width)//2, top_y), mask=logo if logo.mode=="RGBA" else None)
    top_y += logo.height + 20

    # CITY (big red) — auto-fit width
    city_y = top_y + 40
    city_text = city.upper()
    
    side_margin = int(POSTER_WIDTH * 0.05)     # 5% margins on each side
    max_city_width = POSTER_WIDTH - (2 * side_margin)
    
    # choose a min size that still looks bold enough
    title_font = fit_font_to_width(draw, city_text, TITLE_FONT_PATH, font_size_title, max_city_width, min_size=120)
    
    # center draw using 'ma' as before
    draw.text((POSTER_WIDTH//2, city_y), city_text, font=title_font, fill="#E53935", anchor="ma")
    city_bbox = draw.textbbox((POSTER_WIDTH//2, city_y), city_text, font=title_font, anchor="ma")
    y = city_bbox[3] + 60

    # Date
    draw.text((POSTER_WIDTH//2, y), date_str, font=subtitle_font, fill="white", anchor="ma")
    y += font_size_subtitle

    # Address (two lines: 1) full address 2) postal)
    y += 20
    draw.text((POSTER_WIDTH//2, y), address_line1, font=body_font, 
              fill="white", anchor="ma")
    y += font_size_body + 20
    draw.text((POSTER_WIDTH//2, y), address_line2, font=body_font, 
              fill="white", anchor="ma")
    y += font_size_body + 20
    
    # Time
    draw.text((POSTER_WIDTH//2, y), time_str, font=subtitle_font, fill="white", anchor="ma")

    # Petition Question
    y += 400
    if questionText:
        draw.text((POSTER_WIDTH//2, y), question1, font=subtitle_font, fill=(255,0,0), anchor="ma")
        y += font_size_subtitle + 20
        draw.text((POSTER_WIDTH//2, y), question2, font=body_font, fill=(255,0,0), anchor="ma")
    
    # Additional Information
    y += 250
    draw.text((POSTER_WIDTH//2, y), addlInfo1, font=body_font, fill="black",
              anchor="ma")
    y += font_size_body + 20
    draw.text((POSTER_WIDTH//2, y), addlInfo2, font=body_font, fill="black",
              anchor="ma")    
    
    # Site (bottom, above grass)
    draw.text((POSTER_WIDTH//2, int(POSTER_HEIGHT*0.8)), site_address, 
              font=body_font, fill="black", anchor="ma")

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
st.markdown("_If you are on mobile, look for >> in the top left for all options._")
st.title("Generate your Own Event Details Poster")
st.write("""Enter the relevant information below and then click on 'Generate 
         Poster.'""")
st.write("""Wait for the runners, kayakers and cyclists in the upper right 
         corner to finish doing their thing. It takes a minute.  Patience...""")
st.write("""Download buttons will appear beneath the preview image allowing you to 
         download in png or pdf format.""")
st.write("""PNG files are great for social media posts, PDF files are great for
         printing.""")

col1, col2 = st.columns(2)
with col1:
    city = st.text_input("City (e.g., Sherwood Park)", 
                         "Municipality")
    today_local = datetime.datetime.now(APP_TZ).date()
    date_input = st.date_input("Event Date", value=today_local)
    now_local = datetime.datetime.now(APP_TZ)
    default_start = now_local.time().replace(second=0, microsecond=0)
    time_start = st.time_input("Start Time", value=default_start)
    time_end = st.time_input("End Time", 
                             value = datetime.datetime.combine(
                                 today_local,
                                 time_start
                                 ) + datetime.timedelta(hours=2)
                             )
with col2:
    address_line1 = st.text_input("Address line 1", 
                                  "Address Line 1")
    address_line2 = st.text_input("Address line 2 or 'Find us Details' (optional)", 
                                  "")
    date_str = datetime.datetime.strftime(date_input, "%A, %B %d, %Y") if date_input else ""
    time_str = (
        f"{time_start.strftime('%I:%M %p').lstrip('0')} – {time_end.strftime('%I:%M %p').lstrip('0')}"
        if time_start and time_end else ""
    )
    addlInfo1 = st.text_input("Additional information 1 (in black above website, optional)",
                             value="")
    addlInfo2 = st.text_input("Additional information 2 (in black above website, optional)",
                             value="")    
    questionText = st.checkbox("Do you want the question to appear on the poster?",
                               value=True)
    
    if st.button("Generate Poster"):
        poster = render_poster(city, address_line1, address_line2, date_str, 
                               time_str, questionText, addlInfo1, addlInfo2)         

if poster != None:
    st.image(poster, caption="Preview (PNG)")
    # Download buttons
    png_buf = io.BytesIO()
    poster.save(png_buf, format="PNG", optimize=True)
    png_buf.seek(0)
    st.download_button("Download PNG (high-res)", data=png_buf, file_name=f"{city}_poster.png", mime="image/png")
    
    pdf_buf = to_pdf_bytes_flat(poster)
    st.download_button("Download PDF (print-ready)", data=pdf_buf, file_name=f"{city}_poster.pdf", mime="application/pdf")