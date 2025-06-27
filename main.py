import os
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

def add_watermarks(input_folder="images", output_folder="watermarked", text="© srkdesign", font_size=72, opacity=120, progress_callback=None):
    os.makedirs(output_folder, exist_ok=True)

    font_path = "fonts/PPNeueMontreal-Medium.otf"
    font = ImageFont.truetype(font_path, font_size)

    ascent, descent = font.getmetrics()
    text_height = ascent + descent

    files = [f for f in os.listdir(input_folder) if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".avif"))]
    total = len(files)

    for i, filename in enumerate(files, start=1):

        image_path = os.path.join(input_folder, filename)
        output_path = os.path.join(output_folder, filename)

        try:
            image = Image.open(image_path).convert("RGBA")
        except UnidentifiedImageError:
            print(f"Not a valid image: {filename}")
            continue

        watermark = Image.new("RGBA", image.size, (0,0,0,0))
        
        draw = ImageDraw.Draw(image)
        text_width = draw.textlength(text, font=font)

        text_image = Image.new("RGBA", (int(text_width), int(text_height)), (0, 0, 0, 0))
        text_draw = ImageDraw.Draw(text_image)
        text_draw.text((0,0), text, font=font, fill=(255, 255, 255, opacity))

        rotated = text_image.rotate(45, expand=1)

        step_x = rotated.width + 50
        step_y = rotated.height + 100

        margin_x = 25
        margin_y = -75

        for y in range(-image.height + margin_y, image.height * 2, step_y):
            for x in range(-image.width + margin_x, image.width * 2, step_x):
                watermark.paste(rotated, (x, y), rotated)

        combined = Image.alpha_composite(image, watermark)
        combined.convert("RGB").save(output_path, "JPEG")

        if progress_callback:
            progress_callback(i, total, filename)

        print(f"Saved watermarked image: {filename}")


if __name__ == "__main__":
    add_watermarks()
