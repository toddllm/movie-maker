import os
import base64
import time
from dotenv import load_dotenv
from openai import OpenAI
import openai

# Load environment variables
load_dotenv()
api_key = os.getenv('OPENAI_API_KEY')
if not api_key:
    raise ValueError('OPENAI_API_KEY environment variable not set.')
client = OpenAI(api_key=api_key)

# Test prompt and models to try
PROMPT = (
    'A low-poly style animated scene of Mary and Super Dog standing together on a cliff at sunrise.'
)
MODELS = ['gpt-image-1', 'dall-e-2']
SIZE = '1024x1024'
QUALITY = 'low'
OUTPUT_FILE = 'test_image.png'


def generate_test_image(prompt, attempts=3, delay=60):
    """Try generating an image, falling back to the next model on PermissionDenied errors."""
    for model in MODELS:
        print(f"== Trying model: {model} ==")
        for attempt in range(1, attempts + 1):
            try:
                print(f"Attempt {attempt}/{attempts} with {model}...")
                # Build parameters dynamically
                params = {
                    'model': model,
                    'prompt': prompt,
                    'size': SIZE,
                }
                # Only gpt-image-1 supports 'quality'
                if model == 'gpt-image-1':
                    params['quality'] = QUALITY
                resp = client.images.generate(**params)
                img_data = resp.data[0].b64_json
                img_bytes = base64.b64decode(img_data)
                with open(OUTPUT_FILE, 'wb') as f:
                    f.write(img_bytes)
                print(f"Success with {model}! Saved to {OUTPUT_FILE}.")
                return
            except openai.PermissionDeniedError as e:
                print(f"PermissionDeniedError using {model}: {e}")
                # Move to next model
                break
            except Exception as e:
                print(f"Error on attempt {attempt} with {model}: {e}")
                if attempt < attempts:
                    print(f"Waiting {delay}s before retry...")
                    time.sleep(delay)
                else:
                    print(f"Failed {attempts} attempts with {model}.")
        print(f"Falling back from {model} to next model.\n")
    raise RuntimeError('All models failed to generate image.')


if __name__ == '__main__':
    generate_test_image(PROMPT) 