import os
import io
from PIL import Image
try:
    from rembg import remove
except ImportError:
    print("rembg is not installed. Run 'pip install rembg onnxruntime'")
    exit(1)

def process_directory(directory="assets/parrot"):
    # Create the directory if it doesn't exist (it should)
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(files)} images to process in {directory}.")
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Processing {filename}...")
        try:
            with open(filepath, 'rb') as f:
                input_data = f.read()

            subject = remove(input_data)
            
            # Save it back, converting to PNG to keep transparency if it was JPG
            img = Image.open(io.BytesIO(subject))
            
            # Use same path (overwrite) or rename
            # Since these are loaded elsewhere, it's easiest to overwrite them and make sure they're png
            out_filename = filename
            if not out_filename.lower().endswith('.png'):
                out_filename = os.path.splitext(filename)[0] + '.png'
                
            out_filepath = os.path.join(directory, out_filename)
            img.save(out_filepath, 'PNG')
            
            # Remove old jpg if we created a new png
            if out_filepath != filepath:
                os.remove(filepath)
                
            print(f"Successfully processed {filename}.")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    process_directory()
