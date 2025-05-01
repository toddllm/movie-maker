import base64
from openai import OpenAI
from character_descriptions import CHARACTER_DESCRIPTIONS
import os

client = OpenAI()

def generate_scene_image(scene_prompt, character_names, out_path):
    # Build the full prompt with character descriptions
    char_descs = "\n".join(
        [f"{name}: {CHARACTER_DESCRIPTIONS[name].strip()}" for name in character_names]
    )
    full_prompt = f"{scene_prompt}\n\nCharacters present:\n{char_descs}"

    # Load reference images for all characters
    ref_images = []
    for name in character_names:
        ref_path = f"character_refs/{name.lower()}.png"
        ref_images.append(open(ref_path, "rb"))

    # Use the edit endpoint with references for consistency
    result = client.images.edit(
        model="gpt-image-1",
        image=ref_images,
        prompt=full_prompt,
        size="1024x1024",
        background="transparent",
        quality="high",
    )
    image_base64 = result.data[0].b64_json
    image_bytes = base64.b64decode(image_base64)
    with open(out_path, "wb") as f:
        f.write(image_bytes)
    print(f"Saved scene image to {out_path}")

if __name__ == "__main__":
    # Example test: Billy and Bob in the App District
    test_scene = "Billy and Bob are racing through the App District, laughing."
    generate_scene_image(
        test_scene,
        ["Billy", "Bob"],
        "scene_test_app_district.png"
    ) 