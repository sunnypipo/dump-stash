from datetime import datetime
from pathlib import Path
from PIL import Image
import ocrmypdf
import pypandoc
import pymupdf
import pymupdf4llm
import pytesseract
import tempfile
import os
from dotenv import load_dotenv

load_dotenv()

INPUT_FOLDER = Path(os.getenv("INPUT_FOLDER", "./dump"))
OUTPUT_VAULT = Path(os.getenv("OUTPUT_VAULT", "./vault"))
DOUBLE_DUMP_FOLDER = INPUT_FOLDER / "double_dumped"
FAILED_DUMP_FOLDER = INPUT_FOLDER / "failed_dumps"

OCR_LANGUAGE = "eng+fil"
MIN_TEXT_CHARS = 50

OCR_OPTIONS = {
    "deskew": True,
    "clean": True,
    "oversample": 300,
    "language": OCR_LANGUAGE,
    "optimize": 1,
    "skip_text": True,
    "progress_bar": False,
    "tesseract_pagesegmode": 3,
}

IMAGE_FORMATS = {
    ".bmp", ".gif", ".jpeg", ".jpg",
    ".pbm", ".pgm", ".png", ".pnm",
    ".ppm", ".tif", ".tiff", ".webp",
}


def split_subject_and_name(file_name: str) -> tuple[str, str]:
    stem = Path(file_name).stem

    if " - " not in stem:
        return "Uncategorized", stem

    subject, note_name = stem.split(" - ", 1)

    return subject.strip(), note_name.strip()


def has_text_layer(pdf_path: str, min_chars: int = MIN_TEXT_CHARS) -> bool:
    with pymupdf.open(pdf_path) as doc:
        total = sum(len(page.get_text()) for page in doc)

    return total >= min_chars


def get_note_path(vault_dir: Path, stem: str) -> Path:
    path = vault_dir / f"{stem}.md"

    if path.exists():
        raise FileExistsError(str(path))

    return path


def make_frontmatter(source_name: str) -> str:
    return (
        "---\n"
        f"source: {source_name}\n"
        f"converted: {datetime.now().isoformat(timespec='seconds')}\n"
        "---\n\n"
    )


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
        temp_ocr_pdf = Path(temp_dir) / "processed_searchable.pdf"

        ocrmypdf.ocr(
            input_path,
            temp_ocr_pdf,
            **OCR_OPTIONS,
        )

        return pymupdf4llm.to_markdown(
            temp_ocr_pdf,
            header=False,
            footer=False,
            write_images=False,
        )


def convert_images(input_path: str) -> str:
    text = pytesseract.image_to_string(
        Image.open(input_path),
        lang=OCR_LANGUAGE,
    ).strip()

    if not text:
        raise ValueError("No text detected")

    return text


CONVERTERS = {
    ".docx": convert_doc,
    ".pdf": convert_pdf,
    **{ext: convert_images for ext in IMAGE_FORMATS},
}


def process_file(file_path: Path) -> Path:
    ext = file_path.suffix.lower()

    markdown = CONVERTERS[ext](str(file_path))

    if not markdown.strip():
        raise ValueError("Empty output")

    subject, note_name = split_subject_and_name(file_path.name)

    subject_folder = OUTPUT_VAULT / subject
    subject_folder.mkdir(parents=True, exist_ok=True)

    final_note_path = get_note_path(subject_folder, note_name)

    content = make_frontmatter(file_path.name) + markdown
    final_note_path.write_text(content, encoding="utf-8")

    return final_note_path


def move_to_failed(file_path: Path) -> None:
    failed_path = FAILED_DUMP_FOLDER / file_path.name
    file_path.rename(failed_path)
    print(f"  -> moved to {failed_path}")

def move_to_double_dumped(file_path: Path) -> None:
    dumped_path = DOUBLE_DUMP_FOLDER / file_path.name
    file_path.rename(dumped_path)

def sort_files() -> None:
    OUTPUT_VAULT.mkdir(parents=True, exist_ok=True)
    FAILED_DUMP_FOLDER.mkdir(parents=True, exist_ok=True)
    DOUBLE_DUMP_FOLDER.mkdir(parents=True, exist_ok=True)

    if not INPUT_FOLDER.exists():
        print(f"Source directory '{INPUT_FOLDER}' does not exist.")
        return

    for file_path in INPUT_FOLDER.iterdir():
        if not file_path.is_file():
            continue

        ext = file_path.suffix.lower()

        if ext not in CONVERTERS:
            print(
                f"[INVALID FORMAT] {file_path.name} "
                f"({ext})"
            )
            move_to_failed(file_path)
            continue

        try:
            final_note_path = process_file(file_path)

            move_to_double_dumped(file_path)

            print(
                f"✓ {file_path.name} "
                f"-> {final_note_path.relative_to(OUTPUT_VAULT)}"
            )

        except FileExistsError as e:
            print(
                f"[DUPLICATE] {file_path.name} "
                f"would overwrite {e}"
            )
            move_to_failed(file_path)

        except Exception as e:
            print(f"[ERROR] {file_path.name}: {e}")
            move_to_failed(file_path)


if __name__ == "__main__":
    sort_files()
