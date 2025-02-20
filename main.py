import os
from typing import List
import pdfplumber


def extract_pdf_text_with_layout(pdf_path: str)->List:
    structured_text = []
    
    with pdfplumber.open(pdf_path) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            # Extract words with metadata (bounding box, font size might be available in some PDFs)
            words = page.extract_words()
            page_content = []

            for word in words:
                # Each word dict may include text, x0, x1, top, bottom, and sometimes font size info.
                # (PDF may not provide this info)
                text = word.get("text", "")
                # inspect other keys if available:
                font_info = word.get("fontname", "default")
                # add text and metadata
                
                page_content.append({
                    "text": text,
                    "font": font_info,
                    "x0": word.get("x0"),
                    "top": word.get("top")
                })
            structured_text.append({
                "page": page_num,
                "content": page_content
            })

    return structured_text


def save_text(data: List, filename: str):
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"
    # Open the file in write mode and specify UTF-8 encoding
    with open(filename, "w", encoding="utf-8") as f:
        f.write(data)


def save_structured_text_with_metadata(structured_text:List, filename:str):
    """
    Saves structured text to a file, including a metadata section at the end of each page.

    For each page, the text is written first (joined from each word), followed by a metadata section
    that lists each word's metadata (font, x0, and top).
    """
    if not filename.endswith(".txt"):
        filename = f"{filename}.txt"

    with open(filename, "w", encoding="utf-8") as f:
        for page in structured_text:
            page_num = page.get("page", "unknown")
            f.write(f"=== Page {page_num} ===\n")

            # Combine the words to form the page's text
            page_text = " ".join(word.get("text", "")
                                 for word in page.get("content", []))
            f.write(page_text + "\n\n")

            # Write metadata details for each word
            f.write("=== Metadata ===\n")
            for word in page.get("content", []):
                metadata_line = (
                    f"Word: {word.get('text', '')} | "
                    f"Font: {word.get('font', 'default')} | "
                    f"x0: {word.get('x0')} | "
                    f"top: {word.get('top')}"
                )
                f.write(metadata_line + "\n")
            f.write("\n\n")  # Extra newline to separate pages


def main():
    pdf_file = os.path.join(os.path.expanduser(
        "~"), "Documents", "record.pdf") # set file path
    data = extract_pdf_text_with_layout(pdf_file)
    print(data[:100]) # debug
    save_structured_text_with_metadata(data, "record")


if __name__ == "__main__":
    main()
