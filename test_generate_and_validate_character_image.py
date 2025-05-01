import base64
import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from character_descriptions import CHARACTER_DESCRIPTIONS
import argparse
from pydantic import BaseModel
from typing import Optional

load_dotenv()
client = OpenAI()

os.makedirs("character_refs", exist_ok=True)

class VisionQAResult(BaseModel):
    error_detected: bool
    analysis: str
    edit_prompt: Optional[str] = None

def generate_reference_image(character_name, out_path):
    description = CHARACTER_DESCRIPTIONS[character_name]
    prompt = f"Character reference: {description.strip()}"
    result = client.images.generate(
        model="gpt-image-1",
        prompt=prompt,
        size="1024x1024",
        background="transparent",
        quality="high",
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    print(f"Saved {character_name} reference image to {out_path}")
    return out_path

def vision_check_and_edit_prompt(image_path, character_name):
    description = CHARACTER_DESCRIPTIONS[character_name]
    with open(image_path, "rb") as img_file:
        image_bytes = img_file.read()
    vision_prompt = (
        f"Below is the canonical description for the character '{character_name}':\n"
        f"{description}\n\n"
        "You are an expert at visual QA for AI-generated character images. "
        "Analyze the attached image and compare it to the description. "
        "If you see any errors (for example, if the character has a mouth but the description says they should have no mouth), "
        "return a JSON object with: error_detected (true/false), analysis (string), and edit_prompt (string or null). "
        "If the image is correct, set error_detected to false, provide a brief analysis, and set edit_prompt to null."
    )
    response = client.chat.completions.create(
        model="gpt-4.1-2025-04-14",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": vision_prompt},
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{base64.b64encode(image_bytes).decode()}"}}
                ]
            }
        ],
        response_format={"type": "json_object"},
        max_tokens=800,
    )
    result = json.loads(response.choices[0].message.content)
    print("\n--- Vision Model Analysis ---\n")
    print(result["analysis"])
    if result["error_detected"] and result["edit_prompt"]:
        print("\n--- Edit Prompt Detected ---\n", result["edit_prompt"])
        return result["edit_prompt"]
    else:
        print("\nNo edit needed according to the vision model.")
        return None

def edit_image(image_path, edit_prompt, out_path):
    with open(image_path, "rb") as img_file:
        result = client.images.edit(
            model="gpt-image-1",
            image=img_file,
            prompt=edit_prompt,
            size="1024x1024",
            quality="high",
        )
        image_base64 = result.data[0].b64_json
        image_bytes = base64.b64decode(image_base64)
        with open(out_path, "wb") as f:
            f.write(image_bytes)
        print(f"Saved edited image to {out_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate and validate a character reference image.")
    parser.add_argument("character", type=str, help="Name of the character (must match key in CHARACTER_DESCRIPTIONS)")
    args = parser.parse_args()
    out_file = f"character_refs/{args.character.replace(' ', '_').lower()}.png"
    generate_reference_image(args.character, out_file)
    edit_prompt = vision_check_and_edit_prompt(out_file, args.character)
    if edit_prompt:
        edited_out_file = out_file.replace(".png", "_edited.png")
        edit_image(out_file, edit_prompt, edited_out_file) 