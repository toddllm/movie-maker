# Iterative Character Image Generation and Validation Plan

## Overview

To maximize the chance of generating a valid, expert-approved character image (e.g., Billy with no mouth), we will use an iterative approach that combines image generation, vision model QA, and image editing. This is necessary because even with strong prompts and edits, the image model may not always follow the requirements perfectly.

## Approach

1. **Generate up to 5 images** for the character using the canonical description.
2. **For each image, run the vision model QA** to check if the image matches the requirements (e.g., no mouth).
3. **If the image fails QA, allow up to 1 edit** using the vision model's suggested edit prompt.
4. **After each edit, re-run the vision model QA.**
5. **Stop immediately if a valid image is found** (vision model says it matches the requirements).
6. **If no valid image is found after all attempts, report failure.**

## Rationale

- The image model is not always consistent, especially for strict requirements (like "no mouth").
- The vision model can reliably judge if the image meets the requirements.
- Limiting to 5 generations and 1 edit per image (max 10 attempts) balances cost and likelihood of success.
- This approach is robust, automatable, and can be extended to batch processing for many characters.

## Pseudocode

```python
max_generations = 5
max_edits = 1
for i in range(max_generations):
    out_file = f"character_refs/{character_name.replace(' ', '_').lower()}_try{i+1}.png"
    generate_reference_image(character_name, out_file)
    edit_prompt = vision_check_and_edit_prompt(out_file, character_name)
    if not edit_prompt:
        print(f"Valid image found: {out_file}")
        break
    for j in range(max_edits):
        edited_out_file = out_file.replace(".png", f"_edited{j+1}.png")
        edit_image(out_file, edit_prompt, edited_out_file)
        edit_prompt = vision_check_and_edit_prompt(edited_out_file, character_name)
        if not edit_prompt:
            print(f"Valid image found: {edited_out_file}")
            break
    if not edit_prompt:
        break
else:
    print("No valid image found after all attempts.")
```

## Next Steps

- Implement this loop in the character image generation script.
- Test with characters that have strict visual requirements.
- Review results and adjust max attempts if needed. 