# dump-stash
A CLI tool that converts files (PDF, DOCX, images) into Markdown and writes them to an output folder. Runs on proot-Ubuntu via Termux on Android.

---

## Why use this

Most AI chat interfaces (ChatGPT, Claude, Gemini) accept PDF uploads, but they read the file themselves you don't control how much of it they use. dump-stash converts your files to markdown first, so you can paste the readable text directly into the chat.

meaning:
- no skipped pages
- images and scanned PDF's text becomes selectable text
- you can paste text directly on chatbox

---

## Limitations

The output is not always clean. Depending on the source file you may get:
- garbled or missing text from scanned PDFs with low-quality scans
- broken table formatting from complex multi-column layouts
- OCR not recognizing text in handwritten notes or stylized fonts
- stray characters, broken line breaks or random characters appearing in the output

---

If the markdown looks messy, just send it to an AI to clean up before using it.

> example:
> "Clean up this Markdown. Fix broken formatting, remove repeated headers and footers, and make it readable. Don't change the actual content."
>
> then, paste the raw `.md` output

---

## Supported formats

`PDF` `DOCX` `PNG` `JPG` `JPEG` `WEBP` `TIFF` `BMP` `GIF`

---

## Prerequisites
- Android phone with Termux installed (from F-Droid, not Play Store)
- At least 2GB of free storage

---

> **Termux** = run in the Termux terminal
> **proot-distro** = run inside Ubuntu (after typing `ubuntu`)

---

## Step 1 · Termux — Set up Termux storage

```bash
termux-setup-storage
```

Allow storage permission when Android prompts, then verify:

```bash
ls ~/storage/shared
```

> You should see your Android shared storage folders.

---

## Step 2 · Termux — Install proot-distro

```bash
pkg update && pkg upgrade -y
pkg install proot-distro
```

Install Ubuntu:

```bash
proot-distro install ubuntu
```

---

## Step 3 · Termux — Set up login alias with storage mount

This makes storage accessible inside proot every time you log in:

```bash
echo "alias ubuntu='proot-distro login ubuntu --bind /sdcard:/root/storage/shared'" >> ~/.bashrc
source ~/.bashrc
```

Log into proot:

```bash
ubuntu
```

Verify storage is mounted:

```bash
ls /root/storage/shared/Documents
```

---

## Step 4 · proot-distro — Set up your folders

```bash
mkdir -p /root/storage/shared/Documents/dump
mkdir -p /root/storage/shared/Documents/output
```

> **Note:** This step is optional. If you skip it and don't set `INPUT_FOLDER` / `OUTPUT_FOLDER` in Step 6, dump-stash will default to using `./dump` and `./output` inside the cloned project folder instead.

---

## Step 5 · proot-distro — Clone and install

```bash
cd ~
git clone https://github.com/sunnypipo/dump-stash
cd dump-stash
chmod +x install.sh
./install.sh
```

> **Note:** The repo is cloned into proot's own filesystem (`/root/dump-stash/`), not into your phone's `/sdcard`. Only your input/output folders need to be on shared storage. The project folder won't appear in your phone's file manager.

The installer will:
- Run `apt update` and `apt upgrade` to ensure packages are current
- Install system dependencies (git, tesseract, pandoc, ghostscript, python3)
- Bootstrap pip inside a virtual environment using `ensurepip`
- Install Python dependencies
- Create `dump/` and `output/` folders

---

## Step 6 · proot-distro — Configure paths

```bash
cp .env.example .env
nano .env
```

Set your paths:

```bash
INPUT_FOLDER=/root/storage/shared/Documents/dump
OUTPUT_FOLDER=/root/storage/shared/Documents/output
```

> Save with `Ctrl+X` → `Y` → `Enter`.

---

## Step 7 · proot-distro — Run

```bash
source .venv/bin/activate
python stash.py
```

> **Note:** The venv only stays active for your current terminal session. If you close Termux, exit proot, or open a new session, reactivate it before running again:
>
> ```bash
> ubuntu              # log back into proot (in Termux)
> cd ~/dump-stash
> source .venv/bin/activate
> python stash.py
> ```
>
> If you get `ModuleNotFoundError` or `command not found: python` it means the venv is not active, run the lines above.

---

## Usage

Drop files into your dump folder and run the script:

```
/sdcard/Documents/dump/Math - Derivatives.pdf
/sdcard/Documents/dump/photo.jpg
```

Converted files will appear in your output folder with the same filename stem:

```
/sdcard/Documents/output/Math - Derivatives.md
/sdcard/Documents/output/photo.md
```

The original source files are moved into `dump/double_dumped/` after a successful conversion:

```
/sdcard/Documents/dump/double_dumped/Math - Derivatives.pdf
/sdcard/Documents/dump/double_dumped/photo.jpg
```

---

## What happens to processed files

| Result | Action |
|---|---|
| Converted successfully | `.md` written to `OUTPUT_FOLDER`; original moved to `dump/double_dumped/` |
| Duplicate output already exists | skipped before conversion runs; reason printed at end of run |
| Failed | skipped; original left in `dump/`; reason printed at end of run |

---

## Warnings you can ignore

When running the script you may see messages like:

```
GPU device discovery failed: Permission denied
pthread_setaffinity_np failed
```

These are harmless proot cannot access Android GPU or low-level CPU scheduling. Your files will still be processed correctly.
