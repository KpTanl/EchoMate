import os
from PIL import Image
import rembg
import io

input_dir = r"d:\Desk\Daily\Work\EchoMate\assets\parrot\Peach-faced-lovebird\flying_frames"
output_dir = r"d:\Desk\Daily\Work\EchoMate\assets\parrot\Peach-faced-lovebird\flying_frames\processed_new"

if not os.path.exists(output_dir):
    os.makedirs(output_dir)

# Define mapping based on wing position
# 1: fully up, 2: mid up, 3: horizontal, 4: mid down, 5: fully down
mapping = {
    "Peach-faced-lovebird_flying_01.png": "Peach-faced-lovebird_flying_01.png",
    "Peach-faced-lovebird_flying_02.png": "Peach-faced-lovebird_flying_02.png",
    "Gemini_Generated_Image_6494pe6494pe6494.png": "Peach-faced-lovebird_flying_03.png",
    "Gemini_Generated_Image_ckhflpckhflpckhf (1).png": "Peach-faced-lovebird_flying_04.png",
    "Gemini_Generated_Image_hc5gwqhc5gwqhc5g.png": "Peach-faced-lovebird_flying_05.png"
}

for original_name, new_name in mapping.items():
    input_path = os.path.join(input_dir, original_name)
    output_path = os.path.join(output_dir, new_name)
    
    if not os.path.exists(input_path):
        print(f"Skipping {original_name} - not found.")
        continue
        
    print(f"Processing {original_name} -> {new_name}...")
    
    # Read image
    with open(input_path, "rb") as i:
        input_data = i.read()
        
    # Remove background
    output_data = rembg.remove(input_data)
    
    # Open with PIL to crop
    img = Image.open(io.BytesIO(output_data))
    
    # Get bounding box of non-transparent pixels
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
        
    # Standardize size?
    # the existing images might have different sizes, maybe we just save them tightly cropped first.
    img.save(output_path)
    print(f"Saved {new_name}")

print("All processing done!")
