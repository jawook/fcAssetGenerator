#%% Import Packages
import io
import datetime
from PIL import Image, ImageOps, ImageDraw, ImageFont
import streamlit as st
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

pages = {
    "Pre-Made Assets": [
        st.Page("fcLogos.py", title="Unofficial Logos"),
        st.Page("fcPosters.py", title="Pre-Made Posters")
        ],
    "Asset Builder": [
        st.Page("fcEventPosterGenerator.py", title="Generate an Event Poster"),
        st.Page("fcTodayPoster.py", title="Generate a Today's Date Poster")
        ]
    }

with st.sidebar:
    st.logo("Forever Canadian No Text.svg",size="large")
    pg = st.navigation(pages,expanded=False)
    st.write("""This unofficial resource was built by Jamie Wilkie (a 
             canvasser for Forever Canada) on a volunteer basis.  Use at your 
             own risk.""")  
    st.write("""It is intended to provide helpful assets for canvassers.  No
             infringement is intended.""")
    st.write("For any concerns, contact jamieforevercanada@gmail.com")
pg.run()