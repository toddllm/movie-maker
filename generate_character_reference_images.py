import base64
from openai import OpenAI
from character_descriptions import CHARACTER_DESCRIPTIONS
import os

client = OpenAI()

os.makedirs("character_refs", exist_ok=True)

def generate_reference_image(character_name, description, out_path):
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
    for name, desc in CHARACTER_DESCRIPTIONS.items():
        out_file = f"character_refs/{name.lower()}.png"
        generate_reference_image(name, desc, out_file) 