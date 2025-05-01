from dotenv import load_dotenv
load_dotenv()

import openai
import os
import sys
import ast
import re

PROMPT_TEMPLATE = '''
You are an expert at analyzing stories and extracting detailed, visually descriptive character profiles for use in consistent image generation.

Below is the script for a story, and a Python dictionary called CHARACTER_DESCRIPTIONS containing canonical descriptions for some characters.

Your task is to:

1. Identify ALL characters in the script, including major, minor, one-off, background, and non-recurring characters. Do not limit yourself to recurring or main characters—include every named or visually distinct character, even if they appear only once.
2. Compare the list of all characters you find to the provided CHARACTER_DESCRIPTIONS. For any character that is NOT already present in CHARACTER_DESCRIPTIONS, write a detailed, canonical visual description that includes:
   - Physical appearance (shape, color, distinguishing features, accessories, etc.)
   - Personality traits that might influence their visual style or expression
   - Any other details that would help an artist or AI generate consistent images of this character in different scenes
3. Output ONLY a Python dictionary called CHARACTER_DESCRIPTIONS_NEW, where each key is the name of a missing character and the value is a multi-line string with the description. If all characters are already described, output an empty dictionary.

Purpose:  
These descriptions will be used as the canonical reference for generating images of each character using an AI image generation API. The same description will be reused for every image prompt involving that character, and reference images will be generated and stored for each character to ensure visual consistency throughout the project.

Script:
{script}

Current CHARACTER_DESCRIPTIONS:
{existing_descriptions}
'''

def build_prompt(script_path, existing_descriptions_path):
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    if os.path.exists(existing_descriptions_path):
        with open(existing_descriptions_path, "r", encoding="utf-8") as f:
            existing = f.read()
    else:
        existing = "CHARACTER_DESCRIPTIONS = {}"
    return PROMPT_TEMPLATE.format(script=script, existing_descriptions=existing)

def get_character_descriptions_from_llm(prompt, model="gpt-4.1-2025-04-14"):
    client = openai.OpenAI()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,
        max_tokens=4096,
    )
    return response.choices[0].message.content

def extract_dict_from_code(code, dict_name):
    # Use regex to extract the dictionary assignment
    match = re.search(rf'{dict_name}\s*=\s*(\{{[\s\S]*?\}})', code)
    if not match:
        return {}
    dict_str = match.group(1)
    try:
        return ast.literal_eval(dict_str)
    except Exception:
        return {}

def merge_and_save_descriptions(new_output_path, existing_path):
    # Read existing CHARACTER_DESCRIPTIONS
    if os.path.exists(existing_path):
        with open(existing_path, "r", encoding="utf-8") as f:
            existing_code = f.read()
        existing_dict = extract_dict_from_code(existing_code, "CHARACTER_DESCRIPTIONS")
    else:
        existing_dict = {}
    # Read new CHARACTER_DESCRIPTIONS_NEW
    with open(new_output_path, "r", encoding="utf-8") as f:
        new_code = f.read()
    new_dict = extract_dict_from_code(new_code, "CHARACTER_DESCRIPTIONS_NEW")
    # Merge
    updated = False
    for k, v in new_dict.items():
        if k not in existing_dict:
            existing_dict[k] = v
            updated = True
    # Save only if there are updates
    if updated:
        with open(existing_path, "w", encoding="utf-8") as f:
            f.write("CHARACTER_DESCRIPTIONS = ")
            f.write(repr(existing_dict))
        print(f"Merged and updated CHARACTER_DESCRIPTIONS in {existing_path}")
    else:
        print("No new characters found. No update needed.")

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Extract character descriptions from a script using LLM.")
    parser.add_argument("--script", type=str, default="script.txt", help="Path to the input script file.")
    parser.add_argument("--output", type=str, default="character_descriptions.py", help="Path to save the character descriptions Python file.")
    parser.add_argument("--model", type=str, default="gpt-4.1-2025-04-14", help="OpenAI model to use (e.g., gpt-4.1-2025-04-14, gpt-4o, gpt-4, gpt-3.5-turbo)")
    args = parser.parse_args()

    # Use a temp file for new output
    temp_output = "_character_descriptions_new.py"
    prompt = build_prompt(args.script, args.output)
    llm_output = get_character_descriptions_from_llm(prompt, model=args.model)
    with open(temp_output, "w", encoding="utf-8") as f:
        f.write(llm_output)
    merge_and_save_descriptions(temp_output, args.output)
    os.remove(temp_output)

if __name__ == "__main__":
    main() 