from pathlib import Path

from docx import Document


def line_is_valid(line) -> bool:
    """
    a line is not valid if it is an empty line or starts with "SECŢIUNEA"/ "CAPITOLUL" / "SUBSECŢIUNEA"/ "TITLUL"
    :param line: String
    :return: True if line is valid, False otherwise
    """

    if not line.strip():
        return False

    keywords = ["SECŢIUNEA", "CAPITOLUL", "SUBSECŢIUNEA", "TITLUL"]
    line = line.strip()
    return not any(line.startswith(keyword) for keyword in keywords)


def extract_chunks(lines) -> list[dict]:
    """
    parse each line and creates a list of dictionaries with information about articles
    :param lines: valid lines from document
    :return: chunks of information per article from current source
    """
    chunks = []
    for line in lines:
        pass




def extract_json_data(doc) -> list[dict]:
    """
    parses the text from the docx and extracts information about each article
    :param doc: Document
    :return: a JSON containing a list of information about each article from each source
    """
    lines = []
    for paragraph in doc.paragraphs:
        line = paragraph.text
        if line_is_valid(line):
            lines.append(line)

    return extract_chunks(lines)


if __name__ == "__main__":
    json_data = []
    dir_path = Path("data")
    for file in dir_path.iterdir():
        doc = Document("data/" + file.name)
        current_json_data = extract_json_data(doc)
        json_data.extend(current_json_data)
