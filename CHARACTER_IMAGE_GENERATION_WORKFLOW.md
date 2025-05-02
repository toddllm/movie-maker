# Character Image Generation, Validation, and Locking Workflow

## Overview
This workflow describes how to use the provided scripts to generate, validate, lock, and version-control canonical character images for the movie-maker project. It is designed for robust, expert-reviewed, and reproducible image generation.

---

## 1. Single Character Image Generation & Validation

- Run the following command to generate and validate a single character image (e.g., for Bob):

```bash
.venv/bin/python test_generate_and_validate_character_image.py "Bob"
```

- The script will:
  - Generate up to 5 images for the character.
  - For each image, run the vision model QA to check if it matches the canonical description.
  - If the image fails, allow 1 edit and re-check.
  - Stop as soon as a valid image is found, or report failure after all attempts.
  - The first valid image is saved as `character_refs/{character_name}.png` and the character is locked.
  - The locked image is also copied to `committed_refs/{character_name}.png` for version control.

---

## 2. Locking and Unlocking Characters

- **Locking** happens automatically when a valid image is found.
- To **unlock** a character for regeneration:

```bash
.venv/bin/python test_generate_and_validate_character_image.py "Bob" --unlock
```

---

## 3. Committing Locked-In Images

- All locked-in images are copied to `committed_refs/`.
- To add a new locked-in image to git:

```bash
git add committed_refs/{character_name}.png
git commit -m "Add locked-in canonical image for {character_name}"
git push
```

---

## 4. Expert Review

- After each run, review the image in `committed_refs/{character_name}.png` with your expert.
- If changes are needed, unlock the character, update the prompt/description, and repeat the process.

---

## 5. Batch Processing (Optional)

- For now, run the script for each character individually to allow for expert review and prompt refinement.
- Batch automation can be added later if needed.

---

## 6. Notes

- The script will not overwrite locked-in images unless the character is explicitly unlocked.
- Only images in `committed_refs/` are tracked by git; all other outputs are ignored.
- This process ensures reproducibility, expert approval, and clean version control for all canonical character images. 