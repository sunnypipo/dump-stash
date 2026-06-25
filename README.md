# dump-stash

A CLI tool that converts files (PDF, DOCX, images) into Markdown and writes them to an output folder. Runs on proot-Ubuntu via Termux on Android.

---

## Supported formats

`PDF` `DOCX` `PNG` `JPG` `JPEG` `WEBP` `TIFF` `BMP` `GIF`

---

## Prerequisites

- Android phone with Termux installed (from F-Droid, not Play Store)
- At least 2GB of free storage

---

## Step 1 — Set up Termux storage

Run this in Termux and allow storage permission when Android prompts:

```bash
termux-setup-storage
```

Verify it worked:

```bash
ls ~/storage/shared
```

You should see your Android shared storage folders.

---

## Step 2 — Install proot-distro

```bash
pkg update
pkg install proot-distro
```

Install Ubuntu:

```bash
proot-distro install ubuntu
```

---

## Step 3 — Set up login alias with storage mount

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

## Step 4 — Set up your folders

Inside proot, create the folders on Android shared storage:

```bash
mkdir -p /root/storage/shared/Documents/dump
mkdir -p /root/storage/shared/Documents/output
```

---

## Step 5 — Clone and install

```bash
apt install git
git clone https://github.com/sunnypipo/dump-stash
cd dump-stash
chmod +x install.sh
./install.sh
```

The installer will:
- Install system dependencies (tesseract, pandoc, ghostscript)
- Create a Python virtual environment
- Install Python dependencies
- Create the dump and output folders

---

## Step 6 — Configure paths

```bash
cp .env.example .env
nano .env
```

Set your paths:

```bash
INPUT_FOLDER=/root/storage/shared/Documents/dump
OUTPUT_FOLDER=/root/storage/shared/Documents/output
```

Save with `Ctrl+X` → `Y` → `Enter`.

---

## Step 7 — Run

```bash
source .venv/bin/activate
python stash.py
```

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

---

## What happens to processed files

| Result | Action |
|---|---|
| Converted successfully | `.md` written to `OUTPUT_FOLDER`; original untouched |
| Failed or duplicate | skipped; reason printed at end of run |

---

## Warnings you can ignore

When running the script you may see messages like:

```
GPU device discovery failed: Permission denied
pthread_setaffinity_np failed
```

These are harmless — proot cannot access Android GPU or low-level CPU scheduling. Your files will still be processed correctly.
