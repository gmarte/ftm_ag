import os

# Define the font file path and output file path
font_file_path = "c:\\temp\\roboto-condensed-latin-900-normal.ttf"
output_file_path = "font_zpl_output.txt"

# Convert to absolute path
font_file_path = os.path.abspath(font_file_path)

# Check if the font file exists
if not os.path.exists(font_file_path):
    raise FileNotFoundError(f"Font file not found: {font_file_path}")

# Read the font file and get its size
with open(font_file_path, "rb") as font_file:
    font_data = font_file.read()
    font_size = len(font_data)
    hex_data = font_data.hex().upper()

# Format the ZPL output string
zpl_output = f"~DUR:RobotoCondensed.TTF,{font_size},{hex_data}"

# Write the ZPL output to the text file
with open(output_file_path, 'w') as output_file:
    output_file.write(zpl_output)

print(f"ZPL output has been written to {output_file_path}")
