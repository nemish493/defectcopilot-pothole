import streamlit as st
import numpy as np
import cv2
from PIL import Image
from streamlit_drawable_canvas import st_canvas

def draw_bbox_overlay(img: np.ndarray, bbox: tuple[int, int, int, int]) -> np.ndarray:
    x1, y1, x2, y2 = bbox
    out = img.copy()
    cv2.rectangle(out, (x1, y1), (x2, y2), (0, 255, 0), 3)  # green box
    return out

def compute_bbox_metrics(img_shape: tuple[int, int, int], bbox: tuple[int, int, int, int]) -> dict:
    h, w = img_shape[:2]
    x1, y1, x2, y2 = bbox
    bw = max(0, x2 - x1)
    bh = max(0, y2 - y1)
    area_px = bw * bh
    area_ratio = area_px / float(h * w) if h*w else 0.0

    cx = x1 + bw / 2.0
    cy = y1 + bh / 2.0
    center_dist_norm = float(np.sqrt(((cx - w/2)**2 + (cy - h/2)**2)) / np.sqrt((w/2)**2 + (h/2)**2))

    return {
        "bbox": {"x1": x1, "y1": y1, "x2": x2, "y2": y2},
        "bbox_width_px": int(bw),
        "bbox_height_px": int(bh),
        "area_px": int(area_px),
        "area_ratio": round(area_ratio, 6),
        "center_distance_norm": round(center_dist_norm, 4),
        "notes": "These metrics are from a bounding box (coarse). SAM2 mask metrics will replace this later."
    }

st.set_page_config(page_title="DefectCopilot - Pothole", layout="wide")
st.title("DefectCopilot – Pothole Inspection (MVP)")

uploaded = st.file_uploader("Upload a road image", type=["jpg", "jpeg", "png"])
question = st.text_input("Ask a question (DE or EN)", value="Is this pothole severe and what should be done?")

if uploaded is None:
    st.info("Upload an image to begin.")
    st.stop()

img_pil = Image.open(uploaded).convert("RGB")
img = np.array(img_pil)
h, w = img.shape[:2]

st.caption("Draw a rectangle around the pothole. This is **coarse grounding** (mask comes later with SAM2).")

# Canvas setup
canvas_result = st_canvas(
    fill_color="rgba(0, 0, 0, 0)",
    stroke_width=3,
    stroke_color="#00FF00",
    background_image=img_pil,
    update_streamlit=True,
    height=min(650, h),
    width=min(900, w),
    drawing_mode="rect",
    key="canvas",
)

bbox = None
if canvas_result.json_data and "objects" in canvas_result.json_data and len(canvas_result.json_data["objects"]) > 0:
    # Take the last drawn rectangle
    rect = canvas_result.json_data["objects"][-1]
    left = int(rect["left"])
    top = int(rect["top"])
    bw = int(rect["width"])
    bh = int(rect["height"])
    x1, y1 = max(0, left), max(0, top)
    x2, y2 = min(w - 1, left + bw), min(h - 1, top + bh)
    if x2 > x1 and y2 > y1:
        bbox = (x1, y1, x2, y2)

col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Overlay")
    if bbox:
        overlay = draw_bbox_overlay(img, bbox)
        st.image(overlay, use_column_width=True)
    else:
        st.image(img, use_column_width=True)
        st.warning("Draw a rectangle to continue.")

with col2:
    st.subheader("Metrics (coarse)")
    if bbox:
        metrics = compute_bbox_metrics(img.shape, bbox)
        st.json(metrics)
        st.subheader("Your question")
        st.write(question)
    else:
        st.info("Metrics will appear after you draw a rectangle.")