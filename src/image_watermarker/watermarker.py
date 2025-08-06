import os
from PIL import Image, ImageDraw, ImageFont, UnidentifiedImageError

class Watermarker:
  def __init__(self, font_path, text="© srkdesign", font_size=72, opacity=60, margin_x=25, margin_y=-75):
    self.text = text
    self.font_size = font_size
    self.opacity = opacity
    self.margin_x = margin_x
    self.margin_y = margin_y

    try:
      self.font = ImageFont.truetype(font_path, self.font_size)
    except IOError:
      raise FileNotFoundError(f"Font not found at: {font_path}")
    
    ascent, descent = self.font.getmetrics()
    self.text_height = ascent + descent

  def get_files(self, directory):
    return [
      f for f in os.listdir(directory)
      if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp", ".avif"))
    ]
  
  def apply_watermark(self, input_folder, output_folder, progress_callback=None):
    os.makedirs(output_folder, exist_ok=True)

    files = self.get_files(input_folder)
    total = len(files)

    for i, filename in enumerate(files, start=1):
      input_path = os.path.join(input_folder, filename)
      output_path = os.path.join(output_folder, filename)

      try:
        image = Image.open(input_path).convert("RGBA")
      except UnidentifiedImageError:
        print(f"Skipping invalid file: {filename}")
        continue

      watermarked_image = self.draw_watermark(image)
      watermarked_image.convert("RGB").save(output_path, "JPEG")

      if progress_callback:
        progress_callback(i, total, filename)

  def draw_watermark(self, image):
    draw = ImageDraw.Draw(image)
    text_width = draw.textlength(self.text, font=self.font)

    text_image = Image.new("RGBA", (int(text_width), int(self.text_height)), (0, 0, 0, 0))
    text_draw = ImageDraw.Draw(text_image)
    text_draw.text((0, 0), self.text, font=self.font, fill=(0, 0, 0, self.opacity))

    rotated = text_image.rotate(45, expand=1)
    step_x = rotated.width + 50
    step_y = rotated.height + 100

    watermark = Image.new("RGBA", image.size, (0, 0, 0, 0))
    for y in range(-image.height + self.margin_y, image.height * 2, step_y):
      for x in range(-image.width + self.margin_x, image.width * 2, step_x):
        watermark.paste(rotated, (x, y), rotated)

    return Image.alpha_composite(image, watermark)