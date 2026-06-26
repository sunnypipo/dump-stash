from pathlib import Path
from PIL import Image
import ocrmypdf
import pypandoc
import pymupdf
import pymupdf4llm
import pytesseract
import tempfile
import os
import shutil
from dotenv import load_dotenv
load_dotenv()

INPUT_FOLDER  = Path(os.getenv("INPUT_FOLDER",  "./dump"))
OUTPUT_FOLDER = Path(os.getenv("OUTPUT_FOLDER", "./output"))
DOUBLE_DUMPED_FOLDER = INPUT_FOLDER / "double_dumped"

OCR_LANGUAGE  = "eng+fil"
MIN_TEXT_CHARS = 50
OCR_OPTIONS = {
    "deskew":              True,
    "clean":               True,
    "oversample":          300,
    "language":            OCR_LANGUAGE,
    "optimize":            1,
    "skip_text":           True,
    "progress_bar":        False,
    "tesseract_pagesegmode": 3,
}
IMAGE_FORMATS = {
    ".bmp", ".gif", ".jpeg", ".jpg",
    ".pbm", ".pgm", ".png", ".pnm",
    ".ppm", ".tif", ".tiff", ".webp",
}

# ── converters ────────────────────────────────────────────────────────────────
def has_text_layer(pdf_path: str, min_chars: int = MIN_TEXT_CHARS) -> bool:
    with pymupdf.open(pdf_path) as doc:
        total = sum(len(page.get_text()) for page in doc)
    return total >= min_chars

def convert_doc(input_path: str) -> str:
    return pypandoc.convert_file(input_path, "md", format="docx")

def convert_pdf(input_path: str) -> str:
    if has_text_layer(input_path):
        return pymupdf4llm.to_markdown(
            input_path,
            header=False,
            footer=False,
            write_images=False,
        )
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_ocr_pdf = Path(temp_dir) / "ocr.pdf"
        ocrmypdf.ocr(input_path, temp_ocr_pdf, **OCR_OPTIONS)
        return pymupdf4llm.to_markdown(
            temp_ocr_pdf,
            header=False,
            footer=False,
            write_images=False,
        )
    
def convert_image(input_path: str) -> str:
    text = pytesseract.image_to_string(
        Image.open(input_path),
        lang=OCR_LANGUAGE,
    ).strip()
    if not text:
        raise ValueError("No text detected")
    return text
CONVERTERS = {
    ".docx": convert_doc,
    ".pdf":  convert_pdf,
    **{ext: convert_image for ext in IMAGE_FORMATS},
}
# ── processing ────────────────────────────────────────────────────────────────
def process_file(file_path: Path) -> Path:
    ext = file_path.suffix.lower()
    out_path = OUTPUT_FOLDER / f"{file_path.stem}.md"
    if out_path.exists():
        raise FileExistsError(out_path)
    markdown = CONVERTERS[ext](str(file_path))
    if not markdown.strip():
        raise ValueError("Empty output")
    out_path.write_text(markdown, encoding="utf-8")
    return out_path

def move_to_double_dumped(file_path: Path) -> Path:
    DOUBLE_DUMPED_FOLDER.mkdir(parents=True, exist_ok=True)
    dest = DOUBLE_DUMPED_FOLDER / file_path.name
    if dest.exists():
        stem, ext = file_path.stem, file_path.suffix
        counter = 1
        while dest.exists():
            dest = DOUBLE_DUMPED_FOLDER / f"{stem}_{counter}{ext}"
            counter += 1
    return Path(shutil.move(str(file_path), str(dest)))

def convert_all() -> None:
    INPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    OUTPUT_FOLDER.mkdir(parents=True, exist_ok=True)
    DOUBLE_DUMPED_FOLDER.mkdir(parents=True, exist_ok=True)
    if not INPUT_FOLDER.exists():
        print(f"Input folder '{INPUT_FOLDER}' does not exist.")
        return
    skipped: list[tuple[str, str]] = []
    for file_path in sorted(INPUT_FOLDER.iterdir()):
        if not file_path.is_file():
            continue
        ext = file_path.suffix.lower()
        if ext not in CONVERTERS:
            skipped.append((file_path.name, f"unsupported format ({ext})"))
            continue
        try:
            out_path = process_file(file_path)
            moved_path = move_to_double_dumped(file_path)
            print(f"✓  {file_path.name}  ->  {out_path.name}  (moved to {moved_path})")
        except FileExistsError:
            skipped.append((file_path.name, "output already exists, skipped"))
        except Exception as e:
            skipped.append((file_path.name, str(e)))
    print(f"\nOutput stored in: {OUTPUT_FOLDER.resolve()}")
    if skipped:
        print("\n── skipped ──────────────────────────────")
        for name, reason in skipped:
            print(f"✗  {name}: {reason}")

if __name__ == "__main__":
    convert_all()
