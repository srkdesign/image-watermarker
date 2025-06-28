import os
import json
import locale
import traceback
import flet as ft
from folder import open_input_folder
from main import add_watermarks
from translator import Translator
from consts import BASE_DIRECTORY, INPUT_FOLDER, OUTPUT_FOLDER

with open(os.path.join(BASE_DIRECTORY, "translations.json"), "r", encoding="utf-8") as f:
  data = json.load(f)

translations = data["translations"]

def main(page: ft.Page):

  try:
    page.title = "Image Watermarker by srkdesign"
    page.padding=32
    page.spacing=32
    page.scroll="auto"

    system_locale = locale.getlocale()[0]

    if system_locale is None:
      system_locale = "en_US"

    current_lang = system_locale.split("_")[0]

    if current_lang not in translations:
      current_lang="en"
    
    translator = Translator(current_lang, translations)

    def create_open_folder_dialog(folder_path):
      def on_open_folder(e):
        success = open_input_folder(folder_path)
        if not success:
          page.snack_bar = ft.SnackBar(ft.Text(translator.t_fmt("no_folder", folder_path=folder_path)))
          page.snack_bar.open = True
          page.update()
      return on_open_folder

    upload_files_text = ft.Text()

    upload_files_btn = ft.ElevatedButton( icon="FOLDER",on_click=create_open_folder_dialog(os.path.join(BASE_DIRECTORY, INPUT_FOLDER)))

    def open_website(e):
      page.launch_url("https://srkdesign.pro")

    about_dlg = ft.AlertDialog(
      title=ft.Text("Image Watermarker App"),
      content=ft.Text("Copyright (C) 2025, srkdesign"),
      on_dismiss=lambda e: print("Dialog dismissed"),
    )

    def check_item_clicked(e):
      e.control.checked = not e.control.checked
      page.update()

    pb = ft.PopupMenuButton(
      items=[
        ft.PopupMenuItem(icon="INFO", text="About this app", on_click=lambda e: page.open(about_dlg)),
        ft.PopupMenuItem(icon="WEB",text="Author's website", on_click=open_website),
      ]
    )

    lang_selector = ft.Dropdown(
      value=current_lang,
      options=[
        ft.dropdown.Option("en", "English"),
        ft.dropdown.Option("ru", "Русский")
      ]
    )

    def on_lang_change(e):
      translator.set_lang(e.control.value)
      page.update()

    lang_selector.on_change = on_lang_change

    text_input = ft.TextField(value="© srkdesign")
    font_size_input = ft.TextField(value="72", keyboard_type="number")
    opacity_input = ft.TextField(value="120", keyboard_type="number")

    progress_bar = ft.ProgressBar(value=0, expand=True)
    status_text = ft.Text(translator.t("status_text"))

    def update_progress(current, total, filename):
      progress_bar.value = current / total
      status_text.value = translator.t_fmt("status_text_files", current=current, total=total, filename=filename)
      page.update()

    def run_watermark(e):
      status_text.value = translator.t("status_text_processing")
      progress_bar.value = 0
      page.update()

      try:
        add_watermarks(
          input_folder=os.path.join(BASE_DIRECTORY, INPUT_FOLDER),
          output_folder=os.path.join(BASE_DIRECTORY, OUTPUT_FOLDER),
          text=text_input.value,
          font_size = int(font_size_input.value),
          opacity = int(opacity_input.value),
          progress_callback=update_progress,
        )
        status_text.value = translator.t("status_text_complete")
      except Exception as err:
        status_text.value = translator.t_fmt("status_text_error", err=err)
      page.update()

    adv_options_text = ft.Text()

    margin_x_input = ft.TextField(value="25", keyboard_type="number")
    margin_y_input = ft.TextField(value="-75", keyboard_type="number")

    adv_options = ft.ExpansionTile(
      title=ft.Row(controls=[ft.Icon(ft.Icons.SETTINGS), adv_options_text]),
      visual_density=ft.VisualDensity.STANDARD,
      controls=[
        ft.Column(
          expand=True,
          spacing=32,
          controls=[
            ft.Container(
              margin=ft.margin.only(top=32),
              content=margin_x_input), 
            ft.Container(
              margin=ft.margin.only(bottom=32),
              content=margin_y_input
            )
          ],
        )
      ],
      initially_expanded=False,
    )

    run_btn = ft.ElevatedButton(icon="IMAGE", on_click=run_watermark)

    show_output_btn = ft.ElevatedButton(icon="FOLDER",on_click=create_open_folder_dialog(os.path.join(BASE_DIRECTORY, OUTPUT_FOLDER)))

    translator.bind(upload_files_text, "value", "upload_files")
    translator.bind(upload_files_btn, "text", "upload_files_btn")
    translator.bind(text_input, "label", "text_input")
    translator.bind(font_size_input, "label", "font_size_input")
    translator.bind(opacity_input, "label", "opacity_input")
    translator.bind(adv_options_text, "value", "advanced_options_expansion_tile")
    translator.bind(margin_x_input, "label", "margin_x")
    translator.bind(margin_y_input, "label", "margin_y")
    translator.bind(run_btn, "text", "run_btn")
    translator.bind(show_output_btn, "text", "show_output_btn")
    translator.bind(status_text, "value", "status_text")

    layout = ft.Row(
      expand=True,
      controls=[
        ft.Column(
          expand=True,
          width=page.width,
          spacing=32,
          controls=[
            ft.Row(
              alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
              controls=[
                ft.Row(
                  controls=[
                    upload_files_text,
                    upload_files_btn,
                  ]
                ),
                ft.Row(
                  controls=[
                    lang_selector,
                    pb,
                  ]
                ),
                
              ]
            ),
            text_input,
            font_size_input,
            opacity_input,
            ft.Container(
              expand=True,
              content=adv_options,
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
  except Exception as e:
    tb = traceback.format_exc()
    print(tb)
    page.add(ft.Text(f"Error:\n{e}"))
    page.update()

if __name__ == "__main__":
  ft.app(target=main)