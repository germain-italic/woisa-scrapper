from PIL import Image, ImageDraw, ImageFont
import imageio
import numpy as np

# Paths to the images
source_path = "gif_screen_source.png"
scrapped_path = "gif_screen_result.png"
gif_output_path = "hero.gif"
# gif_output_path = "hero.fr.gif"

# Load images
source_image = Image.open(source_path)
scrapped_image = Image.open(scrapped_path)

# Resize images for uniformity
target_size = (800, 450)
source_image = source_image.resize(target_size, Image.LANCZOS)
scrapped_image = scrapped_image.resize(target_size, Image.LANCZOS)

# Create a blank image for text
def create_text_image(text, size):
    font = ImageFont.truetype("DejaVuSans-Bold.ttf", 48)
    text_image = Image.new("RGB", size, (15, 16, 24))  # Dark mode background
    draw = ImageDraw.Draw(text_image)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width, text_height = text_bbox[2] - text_bbox[0], text_bbox[3] - text_bbox[1]
    text_position = ((size[0] - text_width) // 2, (size[1] - text_height) // 2)
    draw.text(text_position, text, fill="white", font=font)  # White text
    return text_image

# Create text frames
text_image_1 = create_text_image("From this...", target_size)
text_image_2 = create_text_image("...to this", target_size)
text_image_3 = create_text_image("in less than 2 minutes", target_size)

# text_image_1 = create_text_image("De ça...", target_size)
# text_image_2 = create_text_image("...à ça", target_size)
# text_image_3 = create_text_image("en moins de 2 minutes", target_size)

# Prepare all frames
frames = [
    text_image_1,
    source_image,
    text_image_2,
    scrapped_image,
    text_image_3
]

# Create an output GIF with specified durations
frames[0].save(
    gif_output_path,
    save_all=True,
    append_images=frames[1:],
    duration=[750, 1750, 750, 1750, 2000],  # Durations in milliseconds
    loop=0  # Loop the GIF indefinitely
)

print(f"GIF saved to {gif_output_path}")
