import os
from PIL import Image

def remove_white_bg(image_path, output_path, tolerance=30):
    img = Image.open(image_path).convert("RGBA")
    
    # We do a BFS from the corners to find all connected "white" pixels
    width, height = img.size
    pixels = img.load()
    
    # White background definition
    # Anything above 255-tolerance
    def is_white(r, g, b):
        return r > 255 - tolerance and g > 255 - tolerance and b > 255 - tolerance
        
    visited = set()
    queue = []
    
    # Start from corners
    corners = [(0,0), (width-1, 0), (0, height-1), (width-1, height-1)]
    for cx, cy in corners:
        if cx < width and cy < height:
            r, g, b, a = pixels[cx, cy]
            if is_white(r, g, b):
                queue.append((cx, cy))
                visited.add((cx, cy))
                
    # BFS
    while queue:
        x, y = queue.pop(0)
        
        # Set pixel to transparent
        pixels[x, y] = (255, 255, 255, 0)
        
        # Check neighbors
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and (nx, ny) not in visited:
                r, g, b, a = pixels[nx, ny]
                if is_white(r, g, b):
                    queue.append((nx, ny))
                    visited.add((nx, ny))
                    
    img.save(output_path, "PNG")

def process_directory(directory="assets/parrot"):
    if not os.path.exists(directory):
        print(f"Directory {directory} not found.")
        return

    files = [f for f in os.listdir(directory) if f.lower().endswith(('.png', '.jpg', '.jpeg'))]
    print(f"Found {len(files)} images to process in {directory}.")
    
    for filename in files:
        filepath = os.path.join(directory, filename)
        print(f"Processing {filename}...")
        try:
            out_filename = filename
            if not out_filename.lower().endswith('.png'):
                out_filename = os.path.splitext(filename)[0] + '.png'
            out_filepath = os.path.join(directory, out_filename)
            
            remove_white_bg(filepath, out_filepath)
            
            if out_filepath != filepath:
                os.remove(filepath)
            print(f"Successfully processed {filename}.")
        except Exception as e:
            print(f"Failed to process {filename}: {e}")

if __name__ == "__main__":
    process_directory()
