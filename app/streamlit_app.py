import streamlit as st
from PIL import Image
import numpy as np

st.set_page_config(page_title="DefectCopilot - Pothole", layout="wide")
st.title("DefectCopilot – Pothole Inspection (MVP)")

uploaded = st.file_uploader("Upload a road image", type=["jpg", "jpeg", "png"])

if uploaded is None:
    st.info("Upload an image to begin.")
    st.stop()

img_pil = Image.open(uploaded).convert("RGB")
img = np.array(img_pil)

col1, col2 = st.columns([1, 1])
with col1:
    st.subheader("Input")
    st.image(img, use_container_width=True)
with col2:
    st.subheader("Next")
    st.write("Next step: mark pothole region (ROI) and compute metrics.")
    st.json({"image_shape": list(img.shape)})