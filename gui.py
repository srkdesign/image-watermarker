import flet as ft
import os
from main import add_watermarks
import platform
import subprocess

APP_DIRECTORY = os.getcwd()

INPUT_FOLDER = "images"
OUTPUT_FOLDER = "watermarked"

def open_input_folder(path):
  if not os.path.isdir(path):
    print(f"Folder doesn't exist: {path}")
    return False
  
  system = platform.system()
  try:
    if system == "Windows":
      os.startfile(path)
    elif system == "Darwin":
      subprocess.Popen(["open", path])
    else:
      subprocess.Popen(["xdg-open", path])
    return True
  except Exception as e:
    print(f"Error opening folder: {e}")
    return False


def main(page: ft.Page):
  page.title = "Image Watermarker"
  page.padding=32
  page.spacing=32
  page.scroll="auto"

  def create_open_folder_dialog(folder_path):
    def on_open_folder(e):
      success = open_input_folder(folder_path)
      if not success:
        page.snack_bar = ft.SnackBar(ft.Text(f"Cannot open folder:\n{folder_path}"))
        page.snack_bar.open = True
        page.update()
    return on_open_folder

  upload_files_btn = ft.ElevatedButton("Open directory", icon="FOLDER",on_click=create_open_folder_dialog(os.path.join(APP_DIRECTORY, INPUT_FOLDER)))

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
        input_folder=INPUT_FOLDER,
        output_folder=OUTPUT_FOLDER,
        text=text_input.value,
        font_size = int(font_size_input.value),
        opacity = int(opacity_input.value),
        progress_callback=update_progress,
      )
      status_text.value = "Watermarking Complete"
    except Exception as err:
      status_text.value = f"An error occurred: {err}"
    page.update()

  advanced_options_expansion_tile = ft.ExpansionTile(
    title=ft.Row(controls=[ft.Icon(ft.Icons.SETTINGS), ft.Text("Advanced Settings")]),
    visual_density=ft.VisualDensity.STANDARD,
    controls=[
      ft.Column(
        expand=True,
        spacing=32,
        controls=[
          ft.Container(
            margin=ft.margin.only(top=32),
            content=ft.TextField(label="Margin X", value="25", keyboard_type="number")), 
          ft.Container(
            margin=ft.margin.only(bottom=32),
            content=ft.TextField(label="Margin Y", value="-75", keyboard_type="number")
          )
        ],
      )
    ],
    initially_expanded=False,
  )

  run_btn = ft.ElevatedButton(icon="IMAGE",text="Add watermark", on_click=run_watermark)

  show_output_btn = ft.ElevatedButton("Show results", icon="FOLDER",on_click=create_open_folder_dialog(os.path.join(APP_DIRECTORY, OUTPUT_FOLDER)))

  layout = ft.Row(
    expand=True,
    controls=[
      ft.Column(
        expand=True,
        width=page.width,
        spacing=32,
        controls=[
          ft.Row(
            controls=[
              ft.Text("Move images to folder"),
              upload_files_btn,
            ]
          ),
          text_input,
          font_size_input,
          opacity_input,
          ft.Container(
            expand=True,
            content=advanced_options_expansion_tile,
          ),
          ft.Row(
            spacing=16,
            controls=[
              run_btn,
              show_output_btn,
            ]
          ),
          ft.Container(expand=True),
          ft.Column(
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
              progress_bar,
              status_text
            ]
          )
        ]
      )
    ]
  )

  page.add(layout)

ft.app(target=main)