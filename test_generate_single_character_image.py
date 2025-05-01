import base64
import os
from openai import OpenAI
from character_descriptions import CHARACTER_DESCRIPTIONS
import argparse
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()

os.makedirs("character_refs", exist_ok=True)

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a single character reference image.")
    parser.add_argument("character", type=str, help="Name of the character (must match key in CHARACTER_DESCRIPTIONS)")
    args = parser.parse_args()
    out_file = f"character_refs/{args.character.replace(' ', '_').lower()}.png"
    generate_reference_image(args.character, out_file) 