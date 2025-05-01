import os
import re
import ast
from dotenv import load_dotenv
from openai import OpenAI
import argparse

load_dotenv()
client = OpenAI()

def extract_dict_from_code(code, dict_name):
    match = re.search(rf'{dict_name}\s*=\s*(\{{[\s\S]*?\}})', code)
    if not match:
        return {}
    dict_str = match.group(1)
    try:
        return ast.literal_eval(dict_str)
    except Exception:
        return {}

def update_character_description(character, instruction, desc_path="character_descriptions.py", model="gpt-4.1-2025-04-14"):
    # Load current descriptions
    with open(desc_path, "r", encoding="utf-8") as f:
        code = f.read()
    descriptions = extract_dict_from_code(code, "CHARACTER_DESCRIPTIONS")
    if character not in descriptions:
        raise ValueError(f"Character '{character}' not found in CHARACTER_DESCRIPTIONS.")

    current_desc = descriptions[character]

    # Build LLM prompt with explicit warning about image generation model
    prompt = f"""
You are an expert at editing character descriptions for visual consistency in animation and illustration.

Below is the current canonical description for the character '{character}':
---
{current_desc}
---

Instruction: {instruction}

IMPORTANT: The image generation model often adds a mouth to characters even when not described. It is CRUCIAL that the updated description is extremely clear and explicit that the character should have NO MOUTH. Use strong, unambiguous language and repeat this detail if necessary to prevent a mouth from being generated. Make sure the description would be understood by an AI image model as a strict prohibition against any visible mouth, lips, or mouth-like features.

Please return ONLY the updated description as a Python triple-quoted string, keeping all other details the same except for the requested change.
"""

    # Get updated description from LLM
    result = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=800,
    )
    updated_desc = result.choices[0].message.content.strip()
    # Remove code fences if present
    if updated_desc.startswith("```") and updated_desc.endswith("```"):
        updated_desc = updated_desc.strip("`").strip()
    # Remove possible variable assignment
    updated_desc = re.sub(r'^[a-zA-Z_0-9]+\s*=\s*', '', updated_desc).strip()
    # Remove triple quotes if present
    updated_desc = updated_desc.strip('"""').strip("'").strip()

    # Update and save
    descriptions[character] = updated_desc
    with open(desc_path, "w", encoding="utf-8") as f:
        f.write("CHARACTER_DESCRIPTIONS = ")
        f.write(repr(descriptions))
    print(f"Updated description for {character} and saved to {desc_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Update a single character description using the LLM.")
    parser.add_argument("character", type=str, help="Character name (must match key in CHARACTER_DESCRIPTIONS)")
    parser.add_argument("instruction", type=str, help="Instruction for the LLM (e.g., 'Billy should have no mouth')")
    parser.add_argument("--desc_path", type=str, default="character_descriptions.py", help="Path to character_descriptions.py")
    parser.add_argument("--model", type=str, default="gpt-4.1-2025-04-14", help="OpenAI model to use")
    args = parser.parse_args()
    update_character_description(args.character, args.instruction, args.desc_path, args.model) 