import flet as ft
import os
from main import add_watermarks

def main(page: ft.Page):
  page.title = "Image Watermarker"
  page.scroll = "auto"

  text_input = ft.TextField(label="Watermark", value="© srkdesign")
  font_size_input = ft.TextField(label="Font size", value="72", keyboard_type="number")
  opacity_input = ft.TextField(label="Opacity (0-255)", value="120", keyboard_type="number")

  progress_bar = ft.ProgressBar(value=0, expand=True)
  status_text = ft.Text("Ready")

  def update_progress(current, total, filename):
    progress_bar.value = current / total
    status_text.value = f"Processing {current} of {total}: {filename}"
    page.update()

  def run_watermark(e):
    status_text.value = "Processing..."
    progress_bar.value = 0
    page.update()

    try:
      add_watermarks(
        input_folder="images",
        output_folder="watermarked",
        text=text_input.value,
        font_size = int(font_size_input.value),
        opacity = int(opacity_input.value),
        progress_callback=update_progress,
      )
      status_text.value = "Watermarking Complete"
    except Exception as err:
      status_text.value = "An error occurred"
    page.update()

  run_btn = ft.ElevatedButton(text="Add watermark", on_click=run_watermark)

  page.add(
    text_input,
    font_size_input,
    opacity_input,
    run_btn,
    progress_bar,
    status_text,
  )

ft.app(target=main)