from pypdf import PdfReader

# Extract text from a PDF file.
def extract_text_from_pdf(file_path: str) -> str:
    reader = PdfReader(file_path)

    extracted_text = ""

    # Read each page of the PDF and collect its text.
    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            extracted_text += page_text + "\n"

    return extracted_text

# Test PDF text extraction when this file is run directly.
if __name__ == "__main__":
    pdf_text = extract_text_from_pdf("Test Doc.pdf")

    print("\n========== PDF TEXT TEST ==========")
    print(pdf_text[:3000])