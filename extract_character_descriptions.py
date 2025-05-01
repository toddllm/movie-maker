PROMPT_TEMPLATE = '''
You are an expert at analyzing stories and extracting detailed, visually descriptive character profiles for use in consistent image generation.

Below is the script for a story. Your task is to:

1. Identify all major and recurring characters in the script.
2. For each character, write a detailed, canonical visual description that includes:
   - Physical appearance (shape, color, distinguishing features, accessories, etc.)
   - Personality traits that might influence their visual style or expression
   - Any other details that would help an artist or AI generate consistent images of this character in different scenes
3. Format your output as a Python dictionary called CHARACTER_DESCRIPTIONS, where each key is the character's name and the value is a multi-line string with the description.

Purpose:  
These descriptions will be used as the canonical reference for generating images of each character using an AI image generation API. The same description will be reused for every image prompt involving that character, and reference images will be generated and stored for each character to ensure visual consistency throughout the project.

Script:
{script}
'''

def build_character_description_prompt(script_path="script.txt", output_path=None):
    with open(script_path, "r", encoding="utf-8") as f:
        script = f.read()
    prompt = PROMPT_TEMPLATE.format(script=script)
    if output_path:
        with open(output_path, "w", encoding="utf-8") as out:
            out.write(prompt)
    else:
        print(prompt)

if __name__ == "__main__":
    # By default, print the prompt. Optionally, save to a file if output_path is given.
    import sys
    output_path = sys.argv[1] if len(sys.argv) > 1 else None
    build_character_description_prompt(output_path=output_path) 