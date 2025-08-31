import streamlit as st
import streamlit.components.v1 as components

FOLDER_ID = "1IHBdFEuPOsO59YeUcUDt4eWQ7BD9sol_"
embed_url = f"https://drive.google.com/embeddedfolderview?id={FOLDER_ID}#grid"  # or #list

st.markdown("_If you are on mobile, look for >> in the top left for all options._")
st.title("Unofficial Logos")
st.write("""Click the below folders to be taken to a Google Drive link with 
         logos that were reprocessed from the website images.  They are made
         for use in your own canvassing assets.  No infringment intended.""")
components.iframe(embed_url, height=600, scrolling=True)
