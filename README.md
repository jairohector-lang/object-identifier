# Object Identifier

An AI-powered web app that identifies and describes objects in photos using Claude Vision. Upload an image or take a photo with your camera, and the AI will detect every object it sees — complete with descriptions and confidence scores.

## Features

- **Camera input** — take a photo directly from your browser
- **Image upload** — drag and drop any JPG or PNG
- **Multi-object detection** — identifies every distinct object in the image
- **Confidence bars** — shows how certain the AI is for each object
- **Object tags** — quick visual summary with emoji icons
- **Animated UI** — dark blue theme with smooth animations

## Demo

![App Screenshot](assets/screenshot.png)

## Requirements

- Python 3.9+
- An [Anthropic API key](https://console.anthropic.com)

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/jairohector-lang/object-identifier.git
   cd object-identifier
   ```

2. Create a virtual environment and install dependencies:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

3. Set your Anthropic API key:
   ```bash
   export ANTHROPIC_API_KEY="your-key-here"
   ```

4. Run the app:
   ```bash
   streamlit run app.py
   ```

5. Open your browser at `http://localhost:8501`

## How It Works

1. You upload a photo or take one with your camera
2. The image is sent to Claude (Anthropic's AI) via the API
3. Claude analyzes the image and returns a list of detected objects with descriptions and confidence levels
4. The results are displayed in a clean card with tags and confidence bars

## Tech Stack

| Layer | Technology |
|-------|-----------|
| UI | Streamlit |
| AI | Claude Haiku (Anthropic) |
| Image processing | Pillow |
| Language | Python |

## Cost

Each image analysis costs approximately **$0.01–0.02** using the Claude Haiku model. New Anthropic accounts receive free credits to get started.

## License

MIT
