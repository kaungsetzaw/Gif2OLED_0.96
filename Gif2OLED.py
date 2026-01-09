import os
import glob
from PIL import Image

WIDTH = 128
HEIGHT = 64
TOTAL_BYTES = int((WIDTH * HEIGHT) / 8) 

def drawPixel(buffer, x, y, colour):
    byteNum = int((y * (WIDTH / 8)) + int(x / 8))
    bitNum = x % 8
    if colour == 1:
        buffer[byteNum] |= (1 << (7 - bitNum))
    else:
        buffer[byteNum] &= ~(1 << (7 - bitNum))

def process_gif(file_path):
    base_filename = os.path.splitext(os.path.basename(file_path))[0]
    parts = base_filename.rpartition('_')
    clean_name = parts[0] if parts[1] == '_' else base_filename

    imageObject = Image.open(file_path)
    
    valid_frames = []
    for i in range(imageObject.n_frames):
        frame_number = i + 1 
        if frame_number % 3 != 0:
            valid_frames.append(i)
            
    num_saved_frames = len(valid_frames)
    
    # --- FIXED: Initialize c_content before using += ---
    c_content = f'#include "{clean_name}.h"\n\n'
    c_content += f"const unsigned char {clean_name}_data[{num_saved_frames}][{TOTAL_BYTES}]= {{\n"

    for frameIdx in valid_frames:
        c_content += "    {"
        buffer = [0] * TOTAL_BYTES
        imageObject.seek(frameIdx)
        frame = imageObject.convert('RGBA').resize((WIDTH, HEIGHT))
        px = frame.load()

        for y in range(HEIGHT):
            for x in range(WIDTH):
                r, g, b, a = px[x, y]
                # Monochrome thresholding
                if r < 128 and g < 128 and b < 128 and a > 0:
                    drawPixel(buffer, x, y, 1)

        c_content += ", ".join(map(str, buffer))
        c_content += "},\n"

    c_content = c_content.rstrip(',\n') + "\n};\n"

    with open(f"{clean_name}.c", "w") as f:
        f.write(c_content)

    # --- Start H File String ---
    h_content = f"#ifndef {clean_name.upper()}_H\n#define {clean_name.upper()}_H\n\n"
    # h_content += "#include <Arduino.h>\n\n" # Added for PROGMEM/byte types
    h_content += f"#define {clean_name.upper()}_FRAME_COUNT {num_saved_frames}\n"
    h_content += f"extern const unsigned char {clean_name}_data[{num_saved_frames}][{TOTAL_BYTES}];\n\n"
    h_content += "#endif"
    
    with open(f"{clean_name}.h", "w") as f:
        f.write(h_content)

    print(f"Processed: {os.path.basename(file_path)}")
    print(f"  -> Reduced from {imageObject.n_frames} to {num_saved_frames} frames.")

# Main execution
gif_files = glob.glob("*.gif")
if not gif_files:
    print("No .gif files found in the directory.")
    
for gif in gif_files:
    try:
        process_gif(gif)
    except Exception as e:
        print(f"Error processing {gif}: {e}")
