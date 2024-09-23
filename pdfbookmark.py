import PyPDF2
import argparse
import os
import re

def get_page_number_from_index(pdf_path, index):
    reader = PdfReader(pdf_path)
    page = reader.pages[index]
    # Extract the page label
    page_label = reader.get_page_label(index)
    return page_label

def extract_actual_page_number(page):
    # Extract text from the page
    text = page.extract_text()
    if text:
        # Split the text into lines and get the last line
        lines = text.splitlines()
        if lines:
            last_line = lines[-1]
            #print (last_line)
            # Use a regular expression to find a number in the last line
            match = re.search(r'\b(\d+)\b$', last_line.strip())
            if match:
                return int(match.group(1))
    return None

def extract_bookmarks(pdf_path):
    with open(pdf_path, 'rb') as file:
        reader = PyPDF2.PdfReader(file)
        bookmarks = []

        def _extract_bookmarks(outlines, parent_title=''):
            for outline in outlines:
                if isinstance(outline, list):
                    _extract_bookmarks(outline, parent_title)
                else:
                    # Get the destination page index
                    page_index = reader.get_destination_page_number(outline)
                    # Extract the actual page number
                    actual_page_number = extract_actual_page_number(reader.pages[page_index])
                    if actual_page_number is None:
                        actual_page_number = page_index + 1  # Fallback if not found
                    title = outline.title
                    if parent_title:
                        title = f"{parent_title} > {title}"
                    bookmarks.append(f"{title} ( {actual_page_number})")

        try:
            _extract_bookmarks(reader.outlines)
        except Exception as e:
            print(f"An error occurred: {e}")

        return bookmarks

def main():
    parser = argparse.ArgumentParser(description='Extract bookmarks from a PDF file.')
    parser.add_argument('pdf_path', type=str, help='Path to the PDF file')

    args = parser.parse_args()
    pdf_path = args.pdf_path

    base_name = os.path.splitext(os.path.basename(pdf_path))[0]
    output_file = f"{base_name}_bookmarks.txt"

    bookmarks = extract_bookmarks(pdf_path)

    with open(output_file, 'w', encoding='utf-8') as f:
        for bookmark in bookmarks:
            f.write(f"{bookmark}\n")

    print(f"Bookmarks have been saved to {output_file}")

if __name__ == '__main__':
    main()
