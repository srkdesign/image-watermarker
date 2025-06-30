# Image Watermarker — Simple. Fast. Secure

This repository contains the **Image Watermarker** Flet app and an automated GitHub Actions workflow that builds a Windows `.exe` and macOS `.app` bundles.

---

## Download & Run

- Download the ZIP archive from the **GitHub Releases** or **Artifacts** section.
- Extract the ZIP by double-clicking it in Finder.
- Make sure you are **in the same folder** as the extracted `Image Watermarker.app`.

### Opening on macOS

The app is **not signed or notarized**, so macOS may show security warnings. Because the app is downloaded from the internet, macOS may block it with a warning:

> “App can’t be opened because Apple cannot check it for malicious software.”

---

## Optional: Remove Quarantine Flag (Advanced)

To allow the app to launch without Gatekeeper warnings, run this in Terminal:

```bash
cd /path/to/folder-containing-app
xattr -d -r com.apple.quarantine ./Image\ Watermarker.app
chmod -R +x ./Image\ Watermarker.app/Contents/MacOS/*
```

---

## Building Locally

To build the macOS app yourself, ensure you have Python and flet-cli installed:

```bash
pip install flet-cli==0.27.5
flet build macos --build-number=1 --build-version=1.0.0
```
