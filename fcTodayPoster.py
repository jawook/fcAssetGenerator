#%% Import Packages
import io
import datetime
from PIL import Image, ImageDraw, ImageFont
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

#%% Key inputs

TITLE_FONT_PATH = "Aptos-ExtraBold.ttf"
BODY_FONT_PATH = "Aptos-Display.ttf"
logo_img = Image.open("Forever Canadian No Background.png").convert("RGBA")
qr_img = Image.open('qrcode.png').convert("RGBA")    
site_address = 'Forever-Canadian.ca'
lMargin = 80

POSTER_WIDTH, POSTER_HEIGHT = 2550, 3300  # 8.5x11 in @ ~300 DPI

#%% Function definition

def load_font(path, size):
    try:
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.truetype("DejaVuSans.ttf", size)

def load_background_canvas(w=POSTER_WIDTH, h=POSTER_HEIGHT):
    return Image.new("RGB", (w, h), "white")
    
def place_centered_text(draw, text, y, font, fill, w=POSTER_WIDTH):
    bbox = draw.textbbox((0,0), text, font=font, anchor="lt")
    text_w = bbox[2]-bbox[0]
    x = (w - text_w) // 2
    draw.text((x, y), text, font=font, fill=fill)
    return y + (bbox[3]-bbox[1])

def render_poster(date_str1, date_str2):
    
    img = load_background_canvas()
    draw = ImageDraw.Draw(img)

    # Load fonts
    title_font = load_font(TITLE_FONT_PATH, 190)
    subtitle_font = load_font(TITLE_FONT_PATH, 90)
    body_font = load_font(BODY_FONT_PATH, 70)
    site_font = load_font(TITLE_FONT_PATH, 75)

    # Top logo (optional)
    top_y = int(POSTER_HEIGHT*0.07)
    max_w = int(POSTER_WIDTH*0.40)
    ratio = min(max_w/logo_img.width, (POSTER_HEIGHT*0.40)/logo_img.height)
    logo = logo_img.resize((int(logo_img.width*ratio), int(logo_img.height*ratio)))
    img.paste(logo, ((POSTER_WIDTH - logo.width)//2, top_y), mask=logo if logo.mode=="RGBA" else None)
    top_y += logo.height + 20

    # Today
    today_y = top_y + 80
    today_text = "TODAY'S DATE IS:"
    draw.text((POSTER_WIDTH//2, today_y), today_text, font=title_font, 
              fill="black", anchor="ma")
    today_y += 190

    # line 1
    line1_y = today_y + 50
    draw.line([(lMargin, line1_y), (img.size[0]-lMargin, line1_y)], fill=(255,0,0),
              width=18)
    
    # Date1
    date_y = line1_y + 50
    draw.text((POSTER_WIDTH//2, date_y), date_str1, font=title_font, 
              fill=(255,0,0), anchor="ma")
    date_y += 190
    
    # Date2
    date_y = date_y + 100
    draw.text((POSTER_WIDTH//2, date_y), date_str2, font=title_font, 
              fill=(255,0,0), anchor="ma")
    date_y += 190    
    
    # Line 2
    line2_y = date_y + 50
    draw.line([(lMargin, line2_y), (img.size[0]-lMargin, line2_y)], 
              fill=(255,0,0), width=18)
    
    # Thanks
    thks_y = line2_y + 50
    thks_text = "Thanks for agreeing that Alberta should remain in Canada."
    draw.text((POSTER_WIDTH//2, thks_y), thks_text, font=subtitle_font, fill="black", anchor="ma")
    thks_y = thks_y + 90

    # Site
    draw.text((POSTER_WIDTH//2, int(POSTER_HEIGHT*0.8)), site_address, 
              font=site_font, fill="black", anchor="ma")

    # QR Code
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
st.title("Generate your Own 'Today's Date' Poster")
st.write("""Click on 'Generate Poster.'""")
st.write("""Download buttons will appear beneath the preview image allowing you to 
         download in png or pdf format.""")
st.write("""PNG files are great for social media posts, PDF files are great for
         printing.""")

date_input = st.date_input("Today's Date", value="today", disabled=True)
date_str1 = datetime.datetime.strftime(date_input, "%A, %B %d, %Y") if date_input else ""
date_str2 = datetime.datetime.strftime(date_input, "%m/%d/%Y") if date_input else ""
date_strName = date_str2.replace('/','')
if st.button("Generate Poster"):
    poster = render_poster(date_str1, date_str2)         

if poster != None:
    st.image(poster, caption="Preview (PNG)")
    # Download buttons
    png_buf = io.BytesIO()
    poster.save(png_buf, format="PNG", optimize=True)
    png_buf.seek(0)
    st.download_button("Download PNG (high-res)", data=png_buf, file_name=f"{date_strName}_Date_Poster.png", mime="image/png")
    
    pdf_buf = to_pdf_bytes_flat(poster)
    st.download_button("Download PDF (print-ready)", data=pdf_buf, file_name=f"{date_strName}_Date_Poster.pdf", mime="application/pdf")