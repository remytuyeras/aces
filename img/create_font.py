from PIL import Image, ImageDraw, ImageFont
import math
import os

def create_logo(output_path, text="PyACES", font_size=100, width=500, height=200, font_path=None, add_shadow=True):
    """Creates a logo with a custom font and saves it as an image with optional gradient text and a shadow effect."""
    
    # Set the starting and ending colors for the gradient
    start_color = (26, 188, 156)  # Teal (start)
    delta = 15
    end_color = (26+delta, 188-delta, 156+delta)  # Slightly lighter for contrast
    
    shadow_color = (10, 50, 40, 100)  # Dark greenish transparent shadow
    shadow_offset = (6, 6)  # Offset (x, y) for shadow position

    # Create an image with transparent background
    img = Image.new("RGBA", (width, height), (0, 0, 0, 0))  # Transparent background
    draw = ImageDraw.Draw(img)

    # Load the font (if a font_path is given)
    try:
        font = ImageFont.truetype(font_path, font_size)
    except IOError:
        print(f"Error: Font file not found for {font_path}! Skipping font.")
        return

    # Get text bounding box to center it
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Adjust text size if it overflows the image width
    while text_width > width - 20:
        font_size -= 5
        font = ImageFont.truetype(font_path, font_size)
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]

    # Calculate position to center text
    text_x = (width - text_width) // 2
    text_y = (height - text_height) // 2

    # Draw shadow text if enabled
    if add_shadow:
        for i, char in enumerate(text):
            char_x = text_x + i * text_width // len(text)
            char_y = text_y
            draw.text((char_x + shadow_offset[0], char_y + shadow_offset[1]), char, font=font, fill=shadow_color)

    # Draw the gradient text
    for i, char in enumerate(text):
        # Interpolate the color for the gradient
        ratio = i / len(text)
        r = int(start_color[0] * (1 - ratio) + end_color[0] * ratio)
        g = int(start_color[1] * (1 - ratio) + end_color[1] * ratio)
        b = int(start_color[2] * (1 - ratio) + end_color[2] * ratio)
        text_color = (r, g, b)

        # Draw the character with the interpolated gradient color
        draw.text((text_x + i * text_width // len(text), text_y), char, font=font, fill=text_color)

    # Save the logo as PNG
    img.save(output_path)

def generate_logos(font_paths, output_dir="img"):
    """Generate logos using multiple fonts and save them in the output directory."""
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    for i, font_path in enumerate(font_paths):
        suffix = font_path.split("/")[-1].split(".")[0].lower().replace("-","_")
        output_path = os.path.join(output_dir, f"logo_{suffix}.png")
        create_logo(output_path, font_path=font_path, height=150)
        print(f"Logo created for font {font_path} and saved as {output_path}")

# List of fonts (can use Google Fonts or system fonts)
fonts = [
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Default system fonts (Linux example)
    "/usr/share/fonts/truetype/dejavu/DejaVuSans-Medium.ttf",  
    "/usr/share/fonts/truetype/msttcorefonts/Arial.ttf",  # Arial (common)
    "RobotoMono-Regular.ttf",  # Download this from Google Fonts
    "FiraCode-Regular.ttf",  # Download this from Google Fonts
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-C.ttf",  # Ubuntu font
    "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",  # Liberation Mono
    "/usr/share/fonts/truetype/msttcorefonts/Comic_Sans_MS.ttf",  # Comic Sans for fun
    "/usr/share/fonts/truetype/dejavu/DejaVuSansCondensed-Bold.ttf",  # DejaVu Sans Condensed
    "/usr/share/fonts/truetype/msttcorefonts/Georgia.ttf",  # Georgia
    "/usr/share/fonts/truetype/ubuntu/Ubuntu-Regular.ttf",  # Ubuntu Regular
    "/usr/share/fonts/truetype/dejavu/DejaVuSerif-Bold.ttf",  # DejaVu Serif
    "OpenSans-Regular.ttf",  # Download from Google Fonts
    "Lobster-Regular.ttf",  # Download from Google Fonts
    "Pacifico-Regular.ttf",  # Download from Google Fonts
    "PermanentMarker-Regular.ttf",  # Download from Google Fonts
    "PlayfairDisplay-Regular.ttf",  # Download from Google Fonts
    "Roboto-Regular.ttf",  # Roboto Regular
    "SourceSansPro-Regular.ttf",  # Source Sans Pro
    "UbuntuMono-Regular.ttf",  # Ubuntu Mono
    "IndieFlower-Regular.ttf",  # Indie Flower
    "Anton-Regular.ttf",  # Anton
    "DancingScript-Regular.ttf",  # Dancing Script
    "FredokaOne-Regular.ttf",  # Fredoka One
    "Quicksand-Regular.ttf",  # Quicksand
    "Poppins-Regular.ttf",  # Poppins
    "Bitter-Regular.ttf",  # Bitter
    "Exo-Regular.ttf",  # Exo
    "Roboto-Black.ttf"
]

# Generate logos for the listed fonts
generate_logos(fonts)
