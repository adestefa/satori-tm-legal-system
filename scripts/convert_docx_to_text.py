import docx
import sys

def convert_docx_to_text(docx_path):
    """Converts a .docx file to plain text."""
    try:
        document = docx.Document(docx_path)
        full_text = []
        for para in document.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        return f"Error converting DOCX to text: {e}"

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(convert_docx_to_text(sys.argv[1]))
    else:
        print("Please provide the path to a .docx file.")

