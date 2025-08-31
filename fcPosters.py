import streamlit as st
import streamlit.components.v1 as components

FOLDER_ID = "1CwxvuPeAJHhpIn6ZkvSvla6Hyj0OgKkO"
embed_url = f"https://drive.google.com/embeddedfolderview?id={FOLDER_ID}#grid"  # or #list

st.markdown("_If you are on mobile, look for >> in the top left for all options._")
st.title("Pre-Made Posters")
st.write("""Click the below folders to be taken to a Google Drive link with 
         posters that were made with inspiration from the images seen so far.
         If you are looking for additional assets (or would like to add some 
         to the library), please feel free to email requests to 
         jamieforevercanada@gmail.com . They are available in both pdf and 
         editable (ppt) formats.""")
components.iframe(embed_url, height=600, scrolling=True)
