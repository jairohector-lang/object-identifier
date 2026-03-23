import base64
import io
import os
import re

import anthropic
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Object Identifier", page_icon="🔍", layout="centered")

OBJECT_ICONS = {
    "person": "🧑", "people": "👥", "man": "👨", "woman": "👩", "child": "🧒",
    "dog": "🐶", "cat": "🐱", "bird": "🐦", "horse": "🐴", "fish": "🐟",
    "car": "🚗", "truck": "🚚", "bus": "🚌", "bicycle": "🚲", "motorcycle": "🏍️", "plane": "✈️",
    "phone": "📱", "laptop": "💻", "computer": "🖥️", "keyboard": "⌨️", "screen": "🖥️",
    "book": "📚", "bottle": "🍾", "cup": "☕", "chair": "🪑", "table": "🪑", "desk": "🪑",
    "tree": "🌳", "flower": "🌸", "grass": "🌿", "sky": "🌤️", "sun": "☀️", "cloud": "☁️",
    "building": "🏢", "house": "🏠", "road": "🛣️", "window": "🪟", "door": "🚪",
    "food": "🍽️", "pizza": "🍕", "apple": "🍎", "banana": "🍌", "coffee": "☕",
    "ball": "⚽", "clock": "🕐", "bag": "👜", "hat": "🎩", "glasses": "👓",
    "shoe": "👟", "shirt": "👕", "plant": "🪴", "lamp": "💡", "key": "🔑",
    "pen": "🖊️", "paper": "📄", "box": "📦", "water": "💧", "fire": "🔥",
}

def get_icon(name):
    name_lower = name.lower()
    for key, icon in OBJECT_ICONS.items():
        if key in name_lower:
            return icon
    return "◈"

api_key = os.environ.get("ANTHROPIC_API_KEY", "")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

    * { font-family: 'DM Sans', sans-serif; }

    /* Animated gradient background */
    .stApp {
        background: linear-gradient(130deg, #020818, #0a1a4e, #0d2157, #0a3080, #071440);
        background-size: 400% 400%;
        animation: gradientShift 10s ease infinite;
        min-height: 100vh;
        overflow: hidden;
    }

    @keyframes gradientShift {
        0%   { background-position: 0% 50%; }
        50%  { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* Particle stars */
    .stApp::before {
        content: '';
        position: fixed;
        top: 0; left: 0;
        width: 100%; height: 100%;
        background-image:
            radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.6) 0%, transparent 100%),
            radial-gradient(1px 1px at 25% 40%, rgba(255,255,255,0.4) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 40% 10%, rgba(255,255,255,0.5) 0%, transparent 100%),
            radial-gradient(1px 1px at 55% 60%, rgba(255,255,255,0.3) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 70% 25%, rgba(255,255,255,0.5) 0%, transparent 100%),
            radial-gradient(1px 1px at 80% 80%, rgba(255,255,255,0.4) 0%, transparent 100%),
            radial-gradient(1px 1px at 90% 45%, rgba(255,255,255,0.3) 0%, transparent 100%),
            radial-gradient(1px 1px at 15% 75%, rgba(255,255,255,0.4) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 60% 90%, rgba(255,255,255,0.5) 0%, transparent 100%),
            radial-gradient(1px 1px at 35% 55%, rgba(255,255,255,0.3) 0%, transparent 100%),
            radial-gradient(1px 1px at 50% 30%, rgba(99,149,255,0.6) 0%, transparent 100%),
            radial-gradient(1px 1px at 85% 15%, rgba(99,149,255,0.4) 0%, transparent 100%),
            radial-gradient(1.5px 1.5px at 5% 90%, rgba(99,149,255,0.5) 0%, transparent 100%);
        animation: twinkle 6s ease-in-out infinite alternate;
        pointer-events: none;
        z-index: 0;
    }

    @keyframes twinkle {
        0%   { opacity: 0.6; }
        100% { opacity: 1; }
    }

    header, [data-testid="stToolbar"] { visibility: hidden; }

    /* Main card with glow */
    .main-card {
        background: linear-gradient(160deg, rgba(10,26,78,0.9) 0%, rgba(13,33,87,0.85) 100%);
        backdrop-filter: blur(40px);
        -webkit-backdrop-filter: blur(40px);
        border: 1px solid rgba(99,149,255,0.3);
        border-radius: 28px;
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        box-shadow:
            0 0 0 1px rgba(99,149,255,0.1),
            0 32px 80px rgba(0,0,0,0.5),
            0 0 60px rgba(37,99,235,0.15),
            inset 0 1px 0 rgba(255,255,255,0.08);
        margin: 2rem auto;
        position: relative;
        z-index: 1;
    }

    /* Animated scan title */
    .app-title {
        font-family: 'Syne', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        letter-spacing: -0.02em;
        background: linear-gradient(90deg, #fff 0%, #93c5fd 50%, #fff 100%);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: shimmer 4s linear infinite;
        text-shadow: none;
        margin-bottom: 0.2rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    @keyframes shimmer {
        0%   { background-position: 0% center; }
        100% { background-position: 200% center; }
    }

    /* Pulsing scan dot */
    .scan-dot {
        display: inline-block;
        width: 14px;
        height: 14px;
        border-radius: 50%;
        background: #3b82f6;
        box-shadow: 0 0 0 0 rgba(59,130,246,0.6);
        animation: pulse 2s ease-out infinite;
        vertical-align: middle;
        margin-right: 0.4rem;
    }

    @keyframes pulse {
        0%   { box-shadow: 0 0 0 0 rgba(59,130,246,0.7); }
        70%  { box-shadow: 0 0 0 12px rgba(59,130,246,0); }
        100% { box-shadow: 0 0 0 0 rgba(59,130,246,0); }
    }

    .app-subtitle {
        font-size: 1.05rem;
        color: rgba(255,255,255,0.5);
        margin-bottom: 2rem;
    }

    /* Tab buttons */
    [data-testid="stTabs"] [role="tablist"] {
        gap: 0.75rem;
        border-bottom: none !important;
        margin-bottom: 1.25rem;
    }
    [data-testid="stTabs"] [role="tablist"]::after,
    [data-testid="stTabs"] [role="tablist"]::before { display: none !important; }

    [data-testid="stTabs"] [role="tab"] {
        font-family: 'DM Sans', sans-serif;
        font-size: 1rem;
        font-weight: 600;
        color: rgba(255,255,255,0.55);
        background: rgba(255,255,255,0.06);
        border: 1px solid rgba(99,149,255,0.2) !important;
        border-radius: 50px !important;
        padding: 0.55rem 1.75rem !important;
        transition: all 0.2s;
    }
    [data-testid="stTabs"] [role="tab"]:hover {
        background: rgba(99,149,255,0.15);
        color: #fff;
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"] {
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: #fff !important;
        border: none !important;
        box-shadow: 0 4px 20px rgba(37,99,235,0.5);
    }
    [data-testid="stTabs"] [role="tab"][aria-selected="true"]:after,
    [data-testid="stTabs"] [role="tab"][aria-selected="true"]:before {
        display: none !important;
        background: none !important;
    }
    [data-testid="stTabs"] [role="tab"] p {
        border-bottom: none !important;
        color: inherit !important;
    }

    /* Upload/camera zones */
    [data-testid="stFileUploader"] {
        background: #0d2157;
        border: 2px dashed rgba(99,149,255,0.5);
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: rgba(99,149,255,0.9);
        background: #0f2a6e;
    }
    [data-testid="stFileUploader"] label,
    [data-testid="stFileUploader"] p,
    [data-testid="stFileUploader"] span,
    [data-testid="stFileUploader"] small,
    [data-testid="stFileUploader"] div,
    [data-testid="stFileUploaderDropzoneInstructions"] {
        color: rgba(255,255,255,0.9) !important;
    }
    [data-testid="stCameraInput"] {
        background: #0d2157;
        border: 2px dashed rgba(99,149,255,0.5);
        border-radius: 16px;
        padding: 1rem;
    }
    [data-testid="stCameraInput"] button {
        background: linear-gradient(90deg, #2563eb, #1d4ed8) !important;
        color: #fff !important;
        border: none !important;
        border-radius: 50px !important;
        font-weight: 600 !important;
        padding: 0.5rem 1.5rem !important;
        box-shadow: 0 4px 16px rgba(37,99,235,0.4) !important;
    }
    [data-testid="stCameraInput"] p,
    [data-testid="stCameraInput"] span {
        color: rgba(255,255,255,0.8) !important;
    }

    /* Image display */
    [data-testid="stImage"] img {
        border-radius: 16px;
        box-shadow: 0 8px 40px rgba(0,0,0,0.4), 0 0 30px rgba(37,99,235,0.2);
        margin-top: 1.25rem;
    }

    /* Fade-in animation for results */
    .result-card {
        background: rgba(13,33,87,0.6);
        border: 1px solid rgba(99,149,255,0.3);
        border-radius: 20px;
        padding: 1.5rem 1.75rem;
        margin-top: 1.5rem;
        animation: fadeInUp 0.5s ease forwards;
        box-shadow: 0 0 30px rgba(37,99,235,0.1);
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(16px); }
        to   { opacity: 1; transform: translateY(0); }
    }

    .result-chip {
        display: inline-block;
        background: linear-gradient(90deg, #2563eb, #1d4ed8);
        color: #fff;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        padding: 0.3rem 0.9rem;
        border-radius: 999px;
        box-shadow: 0 2px 10px rgba(37,99,235,0.4);
        margin-bottom: 1rem;
    }

    .result-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #fff;
        letter-spacing: -0.02em;
        margin-bottom: 1rem;
    }

    /* Object tags */
    .tags-wrap {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-bottom: 1.25rem;
    }
    .obj-tag {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        background: rgba(37,99,235,0.2);
        border: 1px solid rgba(99,149,255,0.35);
        border-radius: 999px;
        padding: 0.35rem 0.9rem;
        font-size: 0.92rem;
        font-weight: 500;
        color: #e0eaff;
        transition: all 0.2s;
    }
    .obj-tag:hover {
        background: rgba(37,99,235,0.4);
        border-color: rgba(99,149,255,0.7);
    }

    /* Object detail cards with confidence bars */
    .objects-list {
        display: flex;
        flex-direction: column;
        gap: 0.7rem;
        margin-top: 1rem;
    }
    .object-row {
        background: rgba(255,255,255,0.05);
        border: 1px solid rgba(99,149,255,0.2);
        border-radius: 14px;
        padding: 0.8rem 1.1rem;
        animation: fadeInUp 0.4s ease forwards;
    }
    .object-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 0.35rem;
    }
    .object-name {
        font-size: 1rem;
        font-weight: 600;
        color: #fff;
    }
    .object-confidence {
        font-size: 0.8rem;
        font-weight: 600;
        color: #60a5fa;
    }
    .conf-bar-bg {
        background: rgba(255,255,255,0.08);
        border-radius: 999px;
        height: 5px;
        width: 100%;
        margin-bottom: 0.4rem;
        overflow: hidden;
    }
    .conf-bar-fill {
        height: 100%;
        border-radius: 999px;
        background: linear-gradient(90deg, #2563eb, #60a5fa);
        box-shadow: 0 0 6px rgba(96,165,250,0.5);
    }
    .object-desc {
        font-size: 0.88rem;
        color: rgba(255,255,255,0.55);
        line-height: 1.5;
        margin-top: 0.2rem;
    }

    /* Spinner */
    .stSpinner > div { border-top-color: #3b82f6 !important; }
</style>
""", unsafe_allow_html=True)

if not api_key:
    st.error("ANTHROPIC_API_KEY is not set. Run: export ANTHROPIC_API_KEY=your-key")
    st.stop()

st.markdown("""
<div class="main-card">
    <div class="app-title"><span class="scan-dot"></span>Object Identifier</div>
    <div class="app-subtitle">Point your camera or upload a photo — AI will identify what it sees</div>
""", unsafe_allow_html=True)

tab1, tab2 = st.tabs(["Camera", "Upload"])
with tab1:
    camera_photo = st.camera_input("", label_visibility="collapsed")
with tab2:
    uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")

source = camera_photo or uploaded_file

if source:
    image = Image.open(source)
    st.image(image, use_container_width=True)

    with st.spinner("Scanning image..."):
        img = image.convert("RGB")
        img.thumbnail((1568, 1568))
        buffer = io.BytesIO()
        img.save(buffer, format="JPEG", quality=85)
        image_data = base64.standard_b64encode(buffer.getvalue()).decode("utf-8")

        client = anthropic.Anthropic(api_key=api_key)
        try:
            response = client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": [
                        {
                            "type": "image",
                            "source": {
                                "type": "base64",
                                "media_type": "image/jpeg",
                                "data": image_data,
                            },
                        },
                        {
                            "type": "text",
                            "text": (
                                "List every distinct object you can see in this image.\n"
                                "Format your response exactly as follows:\n"
                                "TITLE: a short overall scene title (1 line)\n"
                                "OBJECTS:\n"
                                "- Object name [confidence%]: one sentence describing it\n"
                                "Example: - Coffee Cup [92%]: A white ceramic mug filled with dark coffee.\n"
                                "Estimate confidence as a percentage (50-99%) for each object."
                            ),
                        },
                    ],
                }],
            )
        except anthropic.BadRequestError as e:
            st.error(f"Could not process image: {e}")
            st.stop()

    raw = response.content[0].text.strip()

    title = ""
    objects = []
    for line in raw.splitlines():
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.strip().startswith("-"):
            objects.append(line.strip()[1:].strip())

    # Build tags row
    tags_html = '<div class="tags-wrap">'
    for o in objects:
        name = o.split("[")[0].strip().split(":")[0].strip()
        icon = get_icon(name)
        tags_html += f'<span class="obj-tag">{icon} {name}</span>'
    tags_html += '</div>'

    # Build detail cards with confidence bars
    cards_html = '<div class="objects-list">'
    for o in objects:
        conf_match = re.search(r'\[(\d+)%\]', o)
        conf = int(conf_match.group(1)) if conf_match else 75
        clean = re.sub(r'\[\d+%\]', '', o)
        parts = clean.split(":", 1)
        name = parts[0].strip()
        desc = parts[1].strip() if len(parts) > 1 else ""
        icon = get_icon(name)
        cards_html += f"""
        <div class="object-row">
            <div class="object-header">
                <span class="object-name">{icon} {name}</span>
                <span class="object-confidence">{conf}%</span>
            </div>
            <div class="conf-bar-bg">
                <div class="conf-bar-fill" style="width:{conf}%"></div>
            </div>
            <div class="object-desc">{desc}</div>
        </div>"""
    cards_html += '</div>'

    st.markdown(f"""
    <div class="result-card">
        <div class="result-chip">AI Analysis</div>
        <div class="result-title">{title}</div>
        {tags_html}
        {cards_html}
    </div>
    """, unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)
