import os
import base64
import json
from dotenv import load_dotenv
from openai import OpenAI
import openai
from moviepy.video.VideoClip import ImageClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
from moviepy.video.compositing.CompositeVideoClip import concatenate_videoclips
from PIL import Image as PILImage, ImageDraw, ImageFont
import textwrap

# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OPENAI_API_KEY environment variable is not set.")
client = OpenAI(api_key=api_key)

# File paths
SCRIPT_PATH = os.path.join("the-dog-who-save-her-life", "script.txt")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)
# Threshold in bytes below which an image is considered placeholder and should be regenerated
IMG_SIZE_THRESHOLD = 20 * 1024  # 20 KB

# Read the full script
with open(SCRIPT_PATH, "r", encoding="utf-8") as f:
    script_text = f.read().strip()

# Cache parsed scenes to avoid re-parsing
SCENES_CACHE = os.path.join(OUTPUT_DIR, "scenes.json")
if os.path.exists(SCENES_CACHE):
    with open(SCENES_CACHE, "r", encoding="utf-8") as f:
        scenes = json.load(f)["scenes"]
    print(f"Loaded {len(scenes)} scenes from cache at {SCENES_CACHE}.")
else:
    print("Parsing script into scenes...")
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a helpful assistant that splits a movie script into discrete scenes. "
                    "Return strictly a JSON object with one key 'scenes', which is an array of objects. "
                    "Each scene object must have 'id' (integer), 'description' (concise prompt for image generation), "
                    "and 'text' (narration for that scene). Do not include any extra fields or text."
                )
            },
            {"role": "user", "content": script_text}
        ]
    )
    scenes = json.loads(response.choices[0].message.content)["scenes"]
    print(f"Parsed {len(scenes)} scenes.")
    with open(SCENES_CACHE, "w", encoding="utf-8") as f:
        json.dump({"scenes": scenes}, f, indent=2)
    print(f"Saved scenes to cache at {SCENES_CACHE}.")

# Instructions for TTS voice
TTS_INSTRUCTIONS = (
    "Voice Affect: Calm, measured, and warmly engaging; convey awe and quiet reverence for the story.\n"
    "Tone: Even and steady with natural pauses.\n"
    "Emotion: Subtle empathy and wonder without being overly dramatic."
)

# Sanitization helper to create child-friendly prompts
def sanitize_prompt(text):
    """Use the LLM to sanitize a scene description into a child-friendly illustration prompt."""
    system_msg = (
        "You are a helpful assistant that transforms a scene description into a safe, "
        "child-friendly illustration prompt. Remove references to violence, gore, scary themes, "
        "and keep the tone cheerful and whimsical."
    )
    resp = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": text},
        ],
    )
    return resp.choices[0].message.content.strip()

# Generate image and narration per scene, and build video clips list
tclips = []
for scene in scenes:
    sid = scene["id"]
    prompt = scene["description"]
    narration = scene["text"]

    # Image caching: skip if file exists and size is above threshold
    img_path = os.path.join(OUTPUT_DIR, f"scene_{sid}.png")
    if os.path.exists(img_path) and os.path.getsize(img_path) > IMG_SIZE_THRESHOLD:
        print(f"Scene {sid}: valid image exists (>{IMG_SIZE_THRESHOLD} bytes), skipping generation.")
    else:
        # Sanitize prompt once for child-friendly illustration
        print(f"Scene {sid}: sanitizing prompt for child-friendly image...")
        safe_prompt = sanitize_prompt(prompt)
        image_models = [("gpt-image-1", True), ("dall-e-2", False)]
        for imodel, has_quality in image_models:
            try:
                print(f"Scene {sid}: generating image with model {imodel}...")
                # Always request b64_json response format for reliable decoding
                params = {"model": imodel, "prompt": safe_prompt, "size": "1024x1024", "response_format": "b64_json"}
                if has_quality:
                    params["quality"] = "low"
                # Generate image and decode the base64 JSON
                img_resp = client.images.generate(**params)
                b64 = img_resp.data[0].b64_json
                img_bytes = base64.b64decode(b64)
                with open(img_path, "wb") as img_f:
                    img_f.write(img_bytes)
                print(f"Scene {sid}: image saved with {imodel}.")
                break
            except openai.BadRequestError as e:
                print(f"Scene {sid}: model {imodel} blocked by safety: {e}")
                continue
            except Exception as e:
                print(f"Scene {sid}: error with {imodel}: {e}")
                continue
        else:
            print(f"Scene {sid}: all image models failed; creating text placeholder.")
            # Create a white background
            placeholder = PILImage.new('RGB', (1024, 1024), color=(255, 255, 255))
            draw = ImageDraw.Draw(placeholder)
            # Prepare text: show scene id and description
            text = f"Scene {sid}: {prompt}"
            lines = textwrap.wrap(text, width=40)
            # Load default font
            font = ImageFont.load_default()
            # Draw each line
            y = 50
            for line in lines:
                draw.text((50, y), line, fill=(0, 0, 0), font=font)
                y += font.getsize(line)[1] + 5
            placeholder.save(img_path)

    # TTS caching: skip if audio exists
    audio_path = os.path.join(OUTPUT_DIR, f"scene_{sid}.wav")
    if os.path.exists(audio_path):
        print(f"Scene {sid}: narration already exists, skipping generation.")
    else:
        print(f"Scene {sid}: generating narration audio...")
        audio_resp = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="echo",
            instructions=TTS_INSTRUCTIONS,
            input=narration,
            response_format="wav"
        )
        with open(audio_path, "wb") as audio_f:
            audio_f.write(audio_resp.content)

    # Create a video clip for this scene using new API
    audio_clip = AudioFileClip(audio_path)
    duration = audio_clip.duration
    img_clip = ImageClip(img_path).with_duration(duration)
    clip = img_clip.with_audio(audio_clip)
    tclips.append(clip)

# Concatenate all scene clips into the final movie
print("Assembling final video...")
final_video = concatenate_videoclips(tclips, method="compose")
output_path = os.path.join(OUTPUT_DIR, "final_movie.mp4")
final_video.write_videofile(output_path, fps=24)
print(f"Video saved to {output_path}.") 