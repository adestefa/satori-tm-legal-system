import docx
import sys

def convert_text_to_docx(text_file_path, docx_file_path):
    """Converts a text file to a docx file."""
    try:
        document = docx.Document()
        with open(text_file_path, 'r') as f:
            for line in f:
                document.add_paragraph(line)
        document.save(docx_file_path)
        print(f"Successfully converted {text_file_path} to {docx_file_path}")
    except Exception as e:
        print(f"Error converting file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 convert_text_to_docx.py <input_text_file> <output_docx_file>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    convert_text_to_docx(input_file, output_file)
