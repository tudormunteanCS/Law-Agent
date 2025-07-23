import json
import os
from pathlib import Path
import zipfile
import re
from docx import Document
import xml.etree.ElementTree as ET

def line_is_valid(line) -> bool:
    """
    a line is not valid if it is an empty line or starts with "SECŢIUNEA"/ "CAPITOLUL" / "SUBSECŢIUNEA"/ "TITLUL"
    :param line: String
    :return: True if line is valid, False otherwise
    """

    if not line.strip():
        return False

    keywords = ["SECŢIUNEA", "CAPITOLUL", "SUBSECŢIUNEA", "TITLUL", "CARTEA"]
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
    alineate = re.split(r'(?=^\s*\(\d+(?:\.\d+)*\))', current_article_text.strip(),
                        flags=re.MULTILINE)  # good deoarece multi line schimba comportamentul ^ si face sa ia inceputul fiecarei linii
    # Remove empty strings if any
    alineate = [part.strip() for part in alineate if part.strip()]

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
    alineate_list = []
    for text in alineate:
        alineat_match = re.match(r'^\s*\((\d+(?:\.\d+)*)\)', text)
        alin = alineat_match.group(1) if alineat_match else "?"
        alineate_list.append({
            "id": generate_id(file_name, current_article, aliniat_number=alin),
            "sursa": file_name.split(".")[0],
            "articol": current_article,
            "alin": alin,
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
            current_article_text += '\n'  # add \n for the regex to work MULTILINE

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


def get_rid_of_superscript(path_to_document_xml):
    """
    parses an xml file and searches for superscript occurences and swaps them to '.'
    :param path_to_document_xml:
    :return:
    """
    tree = ET.parse(path_to_document_xml)
    root = tree.getroot()

    #change superscript occurences
    #for each w:p
    #   for each w:r
        # for each w:rPr
            #check if there is a <w:vertAlign w:val="superscript"/> inside the w:rPr and delete the w:vertAlign node
            #get out of the current w:rPr and get in the next w:r and add a <w:t> containing a '.' like this; <w:t>.</w:t>

    NS = {
        'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main',
        'w14': 'http://schemas.microsoft.com/office/word/2010/wordml',
        'w15': 'http://schemas.microsoft.com/office/word/2012/wordml',
        'w16': 'http://schemas.microsoft.com/office/word/2018/wordml',
        # Add other namespaces if needed for broader compatibility, but 'w' is primary for this task.
    }

    tree = ET.parse(path_to_document_xml)
    root = tree.getroot()

    for p in root.findall('.//w:p', NS):
        runs = list(p.findall('w:r', NS))
        i = 0
        while i < len(runs):
            run = runs[i]
            rPr = run.find('w:rPr', NS)
            superscript = rPr is not None and rPr.find('w:vertAlign', NS) is not None

            if superscript:
                # Remove superscript element
                rPr.remove(rPr.find('w:vertAlign', NS))

                # Get the text element
                t = run.find('w:t', NS)
                if t is not None and t.text:
                    # Prepend a dot
                    t.text = '.' + t.text

                    # Try to merge with previous <w:r> if it has <w:t>
                    if i > 0:
                        prev_run = runs[i - 1]
                        prev_t = prev_run.find('w:t', NS)
                        if prev_t is not None and prev_t.text is not None:
                            prev_t.text += t.text
                            # Remove the current run (superscript one)
                            p.remove(run)
                            runs.pop(i)
                            continue  # Don't increment i

            i += 1


    #write the new document.xml file
    tree.write(path_to_document_xml, xml_declaration=True, encoding='utf-8', method='xml')



def process_superscript_data(file_path)-> Document:
    """
    processes a docx doc containing superscript data e.g Art. 162^1 converting each superscript to 162.1
    :param file_path: docx
    :return: document without superscript data
    """
    #change file name from .docx to .zip
    file_name = file_path.split('.')[0]
    zip_file_name = file_name + '.zip'
    os.rename(file_path,zip_file_name)

    #extract .zip
    with zipfile.ZipFile(zip_file_name,'r') as zip_ref:
        zip_ref.extractall(file_name)

    #go trough filename (until .) filename/word/document.xml
    path = Path(file_name)
    path_to_document_xml = path / "word" / "document.xml"

    #pass document to function so it changes superscript occurences
    get_rid_of_superscript(path_to_document_xml)
    #compress to zip zip_file_name
    zip_directory_contents(file_name,f"processed_{file_name}.zip")
    #change filename to docx after compressing to zip
    os.rename(f"processed_{file_name}.zip",f"processed_{file_name}.docx")



def zip_directory_contents(source_dir, output_zip):
    with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for foldername, subfolders, filenames in os.walk(source_dir):
            for filename in filenames:
                file_path = os.path.join(foldername, filename)
                arcname = os.path.relpath(file_path, source_dir)  # relative path inside ZIP
                zipf.write(file_path, arcname)



if __name__ == "__main__":
    dir_path = Path("unprocessed_data")
    for file in dir_path.iterdir():
        file_name = file.name
        doc = Document("unprocessed_data/" + file_name)
        current_json_data = extract_json_data(doc, file_name)
        save_json_data(file_name, current_json_data)
        print("Parsed and saved " + file_name)
        print("-" * 30)