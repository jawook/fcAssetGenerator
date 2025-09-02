# fcBlankSpacePoster – READY-TO-RUN STREAMLIT APP
# -------------------------------------------------
# What this does
# - Renders a portrait poster with a thick red border
# - A red horizontal divider splits the page in half
# - TOP HALF: free writing text, word-wrapped and auto-sized up to 300px
# - BOTTOM HALF: Forever Canadian logo on the left; QR code + website right
# - Download button to save the poster as PNG
#
# How to run:
#   streamlit run fcBlankSpacePoster_ready_to_run.py
#
# You can upload your logo and QR in the sidebar, and set the website text there too.

import io
from typing import Tuple

import streamlit as st
from PIL import Image, ImageDraw, ImageFont

# --------------------
# Global poster settings
# --------------------
POSTER_WIDTH = 3300    # ~8.5" at 300dpi
POSTER_HEIGHT = 2550   # ~11" at 300dpi
BACKGROUND_COLOR = (255, 255, 255)
BORDER_COLOR = (255, 0, 0)
TEXT_COLOR = (0, 0, 0)
BORDER_WIDTH = 100
DIVIDER_WIDTH = 20
INNER_PAD = 160  # space inside border before content begins

# Default font search order (bold first)
DEFAULT_FONTS = [
"DejaVuSans-Bold.ttf",
"/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
"/Library/Fonts/Arial Bold.ttf",
"/System/Library/Fonts/Supplemental/Arial Bold.ttf",
"/Library/Fonts/Arial.ttf",
]

custom_font = None

site_text = "forever-canadian.ca"
logo_img = Image.open("Forever Canadian No Background.png").convert("RGBA")
qr_img = Image.open("qrcode.png").convert("RGBA")

def load_font_from_upload(font_file, size: int) -> ImageFont.FreeTypeFont:
    if font_file is None:
        return load_font_auto(size)
    try:
        # Read bytes and create a font
        data = font_file.read()
        return ImageFont.truetype(io.BytesIO(data), size=size)
    except Exception:
        return load_font_auto(size)


def load_font_auto(size: int) -> ImageFont.FreeTypeFont:
    for path in DEFAULT_FONTS:
        try:
            return ImageFont.truetype(path, size=size)
        except Exception:
            continue
    # Last resort bitmap font (not ideal, but avoids crashing)
    return ImageFont.load_default()


def draw_safe_paste(base: Image.Image, overlay: Image.Image, xy: Tuple[int, int]):
    """Paste RGBA/LA with alpha preserved when possible."""
    if overlay.mode in ("RGBA", "LA"):
        base.paste(overlay, xy, mask=overlay)
    else:
        base.paste(overlay, xy)


# --------------------
# Text wrapping & auto-fit
# --------------------

def wrap_lines(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.ImageFont, max_width: int):
    """Greedy space-based wrap so each line <= max_width pixels."""
    words = (text or "").split()
    if not words:
        return [""]
    lines, line = [], ""
    for w in words:
        trial = f"{line} {w}".strip()
        if draw.textlength(trial, font=font) <= max_width or not line:
            line = trial
        else:
            lines.append(line)
            line = w
    if line:
        lines.append(line)
    return lines


def fit_text_to_box(
    draw: ImageDraw.ImageDraw,
    text: str,
    font_file,
    max_width: int,
    max_height: int,
    max_font_size: int = 300,
    min_font_size: int = 16,
    line_gap: float = 0.15,
):
    """
    Binary-search the largest font size so wrapped text fits inside (max_width x max_height).
    Returns (font, lines, line_height_px, line_gap_px).
    """
    lo, hi = min_font_size, max_font_size
    best = None

    while lo <= hi:
        mid = (lo + hi) // 2
        font = load_font_from_upload(font_file, mid)
        lines = wrap_lines(draw, text, font, max_width)

        # Measure height
        if not lines:
            total_h = 0
            line_h = 0
        else:
            bbox = draw.textbbox((0, 0), lines[0], font=font, anchor="lt")
            line_h = bbox[3] - bbox[1]
            gap_px = int(line_h * line_gap)
            total_h = line_h * len(lines) + gap_px * (len(lines) - 1)

        if total_h <= max_height:
            best = (font, lines, line_h, int(line_h * line_gap))
            lo = mid + 1
        else:
            hi = mid - 1

    if best is None:
        # Fallback to smallest font
        font = load_font_from_upload(font_file, min_font_size)
        lines = wrap_lines(draw, text, font, max_width)
        bbox = draw.textbbox((0, 0), lines[0] if lines else " ", font=font, anchor="lt")
        line_h = bbox[3] - bbox[1]
        return font, lines, line_h, int(line_h * line_gap)

    return best


# --------------------
# Poster rendering
# --------------------

def render_poster(
    free_text: str,
    logo_img: Image.Image | None,
    qr_img: Image.Image | None,
    site_text: str,
    font_file,  # Uploaded font file or None
) -> Image.Image:
    # Base canvas
    img = Image.new("RGB", (POSTER_WIDTH, POSTER_HEIGHT), BACKGROUND_COLOR)
    draw = ImageDraw.Draw(img)

    # Outer border
    draw.rectangle(
        [
            (BORDER_WIDTH // 2, BORDER_WIDTH // 2),
            (POSTER_WIDTH - BORDER_WIDTH // 2, POSTER_HEIGHT - BORDER_WIDTH // 2),
        ],
        outline=BORDER_COLOR,
        width=BORDER_WIDTH,
    )

    # Horizontal divider at mid-page (inside border)
    mid_y = POSTER_HEIGHT // 2
    draw.line(
        [(BORDER_WIDTH, mid_y), (POSTER_WIDTH - BORDER_WIDTH, mid_y)],
        fill=BORDER_COLOR,
        width=DIVIDER_WIDTH,
    )

    # Inner content box (padding inside border)
    inner_left = BORDER_WIDTH + INNER_PAD
    inner_right = POSTER_WIDTH - BORDER_WIDTH - INNER_PAD
    inner_top = BORDER_WIDTH + INNER_PAD
    inner_bottom = POSTER_HEIGHT - BORDER_WIDTH - INNER_PAD

    # ---------------- TOP HALF: auto-wrapped, auto-sized text ----------------
    top_area_top = inner_top
    top_area_bottom = mid_y - INNER_PAD
    top_area_height = max(0, top_area_bottom - top_area_top)
    max_text_width = max(1, inner_right - inner_left)

    if free_text is None:
        free_text = ""

    font, lines, line_h, gap_px = fit_text_to_box(
        draw,
        free_text,
        font_file,
        max_width=max_text_width,
        max_height=top_area_height,
        max_font_size=300,  # <= 300 per requirement
        min_font_size=16,
        line_gap=0.15,
    )

    # --- Draw centered horizontally AND vertically within top area ---
    if lines:
        # measure each line height to get an accurate block height
        line_heights = []
        for ln in lines:
            bbox = draw.textbbox((0, 0), ln, font=font, anchor="lt")
            line_heights.append(bbox[3] - bbox[1])
    
        total_h = sum(line_heights) + gap_px * (len(line_heights) - 1)
        # vertical start so the block is centered in the top half
        y = top_area_top + max(0, (top_area_height - total_h) // 2)
    
        # draw lines centered horizontally
        for i, ln in enumerate(lines):
            w = draw.textlength(ln, font=font)
            x = inner_left + (max_text_width - w) // 2
            draw.text((x, y), ln, font=font, fill=TEXT_COLOR)
            y += line_heights[i] + gap_px
    else:
        # nothing to draw
        pass


    # ---------------- BOTTOM HALF: logo (left) and QR + website (right) ----------------
    bottom_top = mid_y + INNER_PAD
    bottom_bottom = inner_bottom
    bottom_height = max(1, bottom_bottom - bottom_top)

    gutter = 80   # space between logo and QR blocks
    col_width = int((inner_right - inner_left) * 0.35)  # each block ~35% of total width
    
    # total content width (two blocks + gutter)
    total_width = col_width * 2 + gutter
    
    # left margin so the whole block is centered in the bottom half
    start_x = inner_left + ((inner_right - inner_left) - total_width) // 2
    
    left_x = start_x
    right_x = left_x + col_width + gutter

    # 1) Left column: logo
    if logo_img is not None:
        # Fit the logo within left column bounds
        max_logo_w = col_width
        max_logo_h = bottom_height
        ratio = min(max_logo_w / logo_img.width, max_logo_h / logo_img.height, 1.0)
        if ratio <= 0:
            ratio = 1.0
        logo_resized = logo_img.resize((int(logo_img.width * ratio), int(logo_img.height * ratio)))
        logo_y = bottom_top + (bottom_height - logo_resized.height) // 2
        draw_safe_paste(img, logo_resized, (left_x, logo_y))
    else:
        # Placeholder box
        placeholder = Image.new("RGB", (col_width, bottom_height), (245, 245, 245))
        draw_safe_paste(img, placeholder, (left_x, bottom_top))
        draw.rectangle([(left_x, bottom_top), (left_x + col_width, bottom_top + bottom_height)], outline=(200, 200, 200), width=4)
        ph_font = load_font_from_upload(font_file, 60)
        ph_text = "LOGO"
        tw = draw.textlength(ph_text, font=ph_font)
        draw.text((left_x + (col_width - tw)//2, bottom_top + bottom_height//2 - 30), ph_text, font=ph_font, fill=(150, 150, 150))

    # 2) Right column: QR on top-right; website below, right-aligned
    site_font = load_font_from_upload(font_file, 75)
    
    # Measure website width and height
    if site_text:
        site_w = int(round(draw.textlength(site_text, font=site_font)))
        site_bbox = draw.textbbox((0, 0), site_text, font=site_font, anchor="lt")
        site_h = site_bbox[3] - site_bbox[1]
    else:
        site_w = 0
        site_h = 0
    
    if qr_img is not None:
        qr_target_h = int(bottom_height * 0.5)
        qr_target_w = col_width
        ratio_qr = min(qr_target_w / qr_img.width, qr_target_h / qr_img.height, 1.0)
        if ratio_qr <= 0:
            ratio_qr = 1.0
        qr_resized = qr_img.resize((int(qr_img.width * ratio_qr), int(qr_img.height * ratio_qr)))
    
        # total block size
        block_w = max(qr_resized.width, site_w)
        block_h = qr_resized.height + (30 if site_text else 0) + site_h
    
        # center block in column vertically
        block_x = int(right_x + (col_width - block_w) // 2)
        block_y = int(bottom_top + (bottom_height - block_h) // 2)
    
        # Draw QR centered in block
        qr_x = int(block_x + (block_w - qr_resized.width) // 2)
        qr_y = block_y
        draw_safe_paste(img, qr_resized, (qr_x, qr_y))
    
        # Draw site text centered under QR
        if site_text:
            site_x = int(block_x + (block_w - site_w) // 2)
            site_y = int(qr_y + qr_resized.height + 30)
            draw.text((site_x, site_y), site_text, font=site_font, fill=TEXT_COLOR)
    else:
        # Only site text (no QR) -> center it vertically in column
        if site_text:
            site_x = int(right_x + (col_width - site_w) // 2)
            site_y = int(bottom_top + (bottom_height - site_h) // 2)
            draw.text((site_x, site_y), site_text, font=site_font, fill=TEXT_COLOR)

    return img


# --------------------
# Streamlit UI
# --------------------

st.markdown("_If you are on mobile, look for >> in the top left for all options._")
st.title("Free-Writing Forever Canadian Poster")
colA, colB = st.columns(2)
with colA:
    st.write("""
             Top half is free text (auto-sized up to 300px). Bottom half shows 
             logo (left) and QR + website (right).
             """)
    free_text = st.text_area("Top free text", value="", 
                             height=150, 
                             help="""
                             This fills the top half of the poster. 
                             The font will auto-size and wrap (max 300px).
                             """)
    make_btn = st.button("Generate Poster")
with colB:
    st.image("sample_blank_space Poster.png", caption="Sample Generated Poster")

if make_btn:
    st.markdown("## Your Generated Poster")
    poster = render_poster(free_text, logo_img, qr_img, site_text, custom_font)
    st.image(poster, caption="Preview", use_container_width=True)

    # Download as PNG
    buf = io.BytesIO()
    poster.save(buf, format="PNG")
    buf.seek(0)
    st.download_button(
        "Download PNG",
        data=buf,
        file_name="fc_blank_space_poster.png",
        mime="image/png",
    )

    # Download as PDF (single page)
    pdf_buf = io.BytesIO()
    poster_rgb = poster.convert("RGB")  # ensure no alpha
    # Optional: resolution=300.0 embeds DPI metadata for some viewers/printers
    poster_rgb.save(pdf_buf, format="PDF", resolution=300.0)
    pdf_buf.seek(0)
    st.download_button(
        "Download PDF",
        data=pdf_buf,
        file_name="fc_blank_space_poster.pdf",
        mime="application/pdf",
    )
