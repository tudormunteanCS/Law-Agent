import json
from pathlib import Path
import re
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


def cod_abreviat(file_name) -> str:
    """
    1 to 1 mapping from full source name to an abbreviation
    :param file_name: str
    :return: str
    """
    coduri = {
        "Codul Civil.docx": "cc",
        "Codul administrativ.docx": "ca",
        "Codul de procedură civilă.docx": "cpc",
        "Codul de procedură penală.docx": "cpp",
        "Codul penal.docx": "cp",
        "Legea contenciosului administrativ (554-2004).docx": "l554",
        "Legea societăților (31-1990).docx": "l31"
    }
    return coduri.get(file_name)


def generate_id(file_name, current_article, aliniat_number) -> str:
    """

    :param file_name: current file name
    :param current_article: current article number
    :param aliniat_number: None if there is only an aliniat in the article, else (n)
    :return: str
    """
    cod = cod_abreviat(file_name)
    if aliniat_number is None:
        return f"{cod}_{current_article}"
    else:
        return f"{cod}_{current_article}_{aliniat_number}"


def split_article_into_aliniate(current_article_text, file_name, current_article) -> list[dict]:
    """
    splits an article's text into aliniate chunks if they exist
    :param current_article_text: String representing text of an article. It may contain aliniate or may not
    :param file_name: current file_name - String
    :param current_article: current current_article name - String
    :return: list of chunks(dict) may contain a single list element
    """
    alineate = re.split(r'(?=\(\d+\))',
                        current_article_text.strip())  # (?= ) este lookahead - nu consuma textul matchuit si il pastreaza

    if len(alineate) == 1:
        return [
            {
                "id": generate_id(file_name, current_article, aliniat_number=None),
                "sursa": file_name.split(".")[0],
                "articol": current_article,
                "alin": None,
                "text": current_article_text
            }
        ]

    alineate = alineate[1:]  # lookahead problem solved
    alineate_list = []
    for i, text in enumerate(alineate):
        alineate_list.append({
            "id": generate_id(file_name, current_article, aliniat_number=i + 1),
            "sursa": file_name.split(".")[0],
            "articol": current_article,
            "alin": i + 1,
            "text": text
        })
    return alineate_list



def extract_chunks(lines, file_name) -> list[dict]:
    """
    parse each line and creates a list of dictionaries with information about articles
    :param lines: List - valid lines from document
    :param file_name: current file_name - String
    :return: chunks of information per article from current source
    """
    chunks = []
    current_article_text = ""
    current_article = None
    for line in lines:
        if line.startswith("Art."):
            if current_article_text and current_article:
                chunks.extend(split_article_into_aliniate(current_article_text, file_name, current_article))
            current_article = line.split(":")[0]  # Art. n
            current_article_text = ""
        else:
            current_article_text += line

    # save last article
    if current_article_text:
        chunks.extend(split_article_into_aliniate(current_article_text, file_name, current_article))

    return chunks


def extract_json_data(doc, file_name) -> list[dict]:
    """
    parses the text from the docx and extracts information about each article
    :param doc: current - Document
    :param file_name: current file_name - String
    :return: a JSON containing a list of information about each article from each source
    """
    lines = []
    for paragraph in doc.paragraphs:
        line = paragraph.text
        if line_is_valid(line):
            lines.append(line)

    return extract_chunks(lines, file_name)


def save_json_data(file_name, json_data):
    processed_file_path = file_name.split(".")[0] + ".json"
    save_path = f"processed_data/{processed_file_path}"
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(json_data, f, indent=2,
                  ensure_ascii=False)  # ensure_ascii=False → avoids escaping Unicode (important for Romanian diacritics)


if __name__ == "__main__":
    json_data = []
    dir_path = Path("data")
    for file in dir_path.iterdir():
        file_name = file.name
        doc = Document("data/" + file_name)
        current_json_data = extract_json_data(doc, file_name)
        json_data.extend(current_json_data)
        save_json_data(file_name, json_data)
