import base64
import io
import os

import anthropic
import streamlit as st
from PIL import Image

st.set_page_config(page_title="Object Identifier", page_icon="🔍", layout="centered")

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600;700&display=swap');

    * { font-family: 'DM Sans', sans-serif; }

    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        min-height: 100vh;
    }

    header, [data-testid="stToolbar"] { visibility: hidden; }

    /* Main card */
    .main-card {
        background: rgba(255,255,255,0.97);
        backdrop-filter: blur(20px);
        border-radius: 24px;
        padding: 2.5rem 2.5rem 2rem 2.5rem;
        box-shadow: 0 32px 80px rgba(0,0,0,0.18);
        margin: 2rem auto;
    }

    .app-title {
        font-size: 2.4rem;
        font-weight: 700;
        color: #1a1a2e;
        letter-spacing: -0.03em;
        margin-bottom: 0.3rem;
    }

    .app-subtitle {
        font-size: 1.1rem;
        color: #888;
        margin-bottom: 2rem;
    }

    /* Upload zone */
    [data-testid="stFileUploader"] {
        background: #f7f8fc;
        border: 2px dashed #d0d4f0;
        border-radius: 16px;
        padding: 1rem;
        transition: all 0.2s;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #667eea;
        background: #f0f2ff;
    }

    /* Image display */
    [data-testid="stImage"] img {
        border-radius: 16px;
        box-shadow: 0 8px 32px rgba(0,0,0,0.12);
        margin-top: 1.25rem;
    }

    /* Result card */
    .result-card {
        background: linear-gradient(135deg, #f7f8ff 0%, #f0f2ff 100%);
        border: 1px solid #e0e4ff;
        border-radius: 16px;
        padding: 1.5rem 1.75rem;
        margin-top: 1.5rem;
    }

    .result-chip {
        display: inline-block;
        background: linear-gradient(90deg, #667eea, #764ba2);
        color: white;
        font-size: 0.7rem;
        font-weight: 600;
        letter-spacing: 0.1em;
        text-transform: uppercase;
        padding: 0.3rem 0.85rem;
        border-radius: 999px;
        margin-bottom: 1rem;
    }

    .result-title {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
        letter-spacing: -0.02em;
        margin-bottom: 0.6rem;
    }

    .result-body {
        font-size: 1.1rem;
        color: #555;
        line-height: 1.8;
    }

    /* Object list */
    .objects-list {
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
        margin-top: 0.5rem;
    }
    .object-row {
        display: flex;
        flex-direction: column;
        background: rgba(255,255,255,0.7);
        border-radius: 10px;
        padding: 0.65rem 1rem;
        border: 1px solid #e0e4ff;
    }
    .object-name {
        font-size: 1rem;
        font-weight: 600;
        color: #1a1a2e;
    }
    .object-desc {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.15rem;
        line-height: 1.5;
    }

    /* Spinner */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
</style>
""", unsafe_allow_html=True)

api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not api_key:
    st.error("ANTHROPIC_API_KEY is not set. Run: export ANTHROPIC_API_KEY=your-key")
    st.stop()

st.markdown("""
<div class="main-card">
    <div class="app-title">Object Identifier</div>
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

    with st.spinner("Analyzing your image..."):
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
                                "List every distinct object you can see in this image. "
                                "Format your response as follows:\n"
                                "TITLE: a short overall scene title (1 line)\n"
                                "OBJECTS:\n"
                                "- Object name: one sentence describing it\n"
                                "- Object name: one sentence describing it\n"
                                "(continue for all objects you see)"
                            ),
                        },
                    ],
                }],
            )
        except anthropic.BadRequestError as e:
            st.error(f"Could not process image: {e}")
            st.stop()

    raw = response.content[0].text.strip()

    # Parse title
    title = ""
    objects = []
    for line in raw.splitlines():
        if line.startswith("TITLE:"):
            title = line.replace("TITLE:", "").strip()
        elif line.strip().startswith("-"):
            objects.append(line.strip()[1:].strip())

    # Build objects HTML
    objects_html = "".join(
        f'<div class="object-row"><span class="object-name">{o.split(":")[0].strip()}</span>'
        f'<span class="object-desc">{o.split(":", 1)[1].strip() if ":" in o else ""}</span></div>'
        for o in objects
    )

    st.markdown(f"""
    <div class="result-card">
        <div class="result-chip">AI Analysis</div>
        <div class="result-title">{title}</div>
        <div class="objects-list">{objects_html}</div>
    </div>
    """, unsafe_allow_html=True)

    st.code(raw, language=None)
    st.caption("Use the copy button above to copy the full analysis")

st.markdown('</div>', unsafe_allow_html=True)
