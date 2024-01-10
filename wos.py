import csv
import datetime

import pandas as pd

from dict import possible_names, file_path, show_popup, publication_type_translations

# Constants
AFFILIATION_END_SYMBOL = ";"
AUTHORS_SEPARATOR = ";"
START_BRACKET = "["
END_BRACKET = "]"


class Affiliation:
    def __init__(self, authors, work_place, is_from_polytech):
        self.authors = authors
        self.work_place = work_place
        self.is_from_polytech = is_from_polytech


def fix_string(input_string):
    output_string = ""
    is_inside_brackets = False
    current_part = ""

    for char in input_string:
        if char == '[':
            is_inside_brackets = True
            current_part += char
        elif char == ']':
            is_inside_brackets = False
            current_part += char
        elif char == ';' and not is_inside_brackets:
            # Append the current part and a semicolon to the output string, then reset current_part
            output_string += current_part + ';'
            current_part = ""
        else:
            # Keep appending characters to current_part
            current_part += char

    # Append any remaining part to the output string
    output_string += current_part

    return output_string


def parse_affiliation(affiliation_text):
    startIndex = affiliation_text.find(START_BRACKET)
    endIndex = affiliation_text.find(END_BRACKET)
    authorsText = affiliation_text[startIndex + 1:endIndex]
    workPlace = affiliation_text[endIndex + 2:].strip()

    authors = [author.strip() for author in authorsText.split(AUTHORS_SEPARATOR)]
    is_from_polytech = any(workPlace.startswith(univ) for univ in possible_names)

    return Affiliation(authors, workPlace, is_from_polytech)


def parse_affiliations(input_text):
    affiliations = []
    current_affiliation = ""
    is_in_bracket = False

    for symbol in input_text:
        if symbol == START_BRACKET:
            is_in_bracket = True
        elif symbol == END_BRACKET:
            is_in_bracket = False

        if symbol == AFFILIATION_END_SYMBOL and not is_in_bracket:
            affiliations.append(parse_affiliation(current_affiliation))
            current_affiliation = ""
        else:
            current_affiliation += symbol

    if current_affiliation:
        affiliations.append(parse_affiliation(current_affiliation))

    return affiliations


def get_distinct_authors(affiliations):
    authors = set()
    for affiliation in affiliations:
        authors.update(affiliation.authors)
    return list(authors)


def calculate_contribution(input_text):
    fixed_input_text = fix_string(input_text)
    affiliations = parse_affiliations(fixed_input_text)
    authors = get_distinct_authors(affiliations)

    author_map = {author: {'TotalAffiliations': 0, 'PolyAffiliations': 0} for author in authors}

    for affiliation in affiliations:
        for author in affiliation.authors:
            author_map[author]['TotalAffiliations'] += 1
            if affiliation.is_from_polytech:
                author_map[author]['PolyAffiliations'] += 1

    only_poly = [a for a in author_map.values() if a['PolyAffiliations'] > 0]
    contribution_sum = sum(a['PolyAffiliations'] / a['TotalAffiliations'] for a in only_poly)

    result = contribution_sum / len(authors) if authors else 0

    return result


def extract_polytech_authors(affiliations):
    polytech_authors = []
    for affiliation in affiliations:
        if affiliation.is_from_polytech:
            for author in affiliation.authors:
                names = author.split(', ')
                if len(names) == 2:
                    polytech_authors.append({'last': names[0], 'first': names[1]})
    return polytech_authors


def extract_work_places(affiliations):
    # Initialize a list to hold all work places
    work_places = []

    # First, add the primary Polytech work place (is_from_polytech == True)
    for aff in affiliations:
        if aff.is_from_polytech:
            primary_polytech_work_place = aff.work_place.split(',')[0].strip()
            work_places.append(primary_polytech_work_place)
            break

    # Next, add other unique work places related to Polytech authors
    polytech_authors = {author for aff in affiliations if aff.is_from_polytech for author in aff.authors}

    for aff in affiliations:
        if any(author in polytech_authors for author in aff.authors):
            work_place = aff.work_place.split(',')[0].strip()
            if work_place not in work_places:
                work_places.append(work_place)

    return work_places


def create_new_csv_entry(row, affiliations):
    polytech_authors = extract_polytech_authors(affiliations)
    work_places = extract_work_places(affiliations)

    public_date = f"{row['Publication Date']}".strip()
    public_year = f"{row['Publication Year']}".strip()

    contribution = round(calculate_contribution(row['Addresses']), 2)

    return {
        'Идентификатор DOI *': row['DOI'],
        'Количество авторов *': len(get_distinct_authors(affiliations)),
        'Фамилия *': ", ".join([author['last'] for author in polytech_authors]),
        'Имя *': ", ".join([author['first'] for author in polytech_authors]),
        'Количество аффилиаций *': len(work_places),
        'Аффиляция *': ", ".join(work_places),
        'Контрибьюция *': round(contribution, 2),
        'Дата публикации *': f"{public_date} {public_year}".strip(),
        'Наименование публикации *': row['Article Title'],
        'Наименование издания *': row['Source Title'],
        'Библиографическая ссылка *': create_bibliography_reference(row),
        'Вид издания  *': filter_publication_type(row['Document Type'])
    }


def create_bibliography_reference(row):
    year = f" {int(row['Publication Year'])} " if pd.notna(row['Publication Year']) else ""

    tom = f", {row['Volume']}" if row['Volume'] != "" else ""

    if tom != "":
        issue = f" ({row['Issue']})" if row['Issue'] != "" else ""
    else:
        issue = f", Выпуск {row['Issue']}" if row['Issue'] != "" else ""

    article_number = f", Статья № {row['Article Number']}" if row['Article Number'] != "" else ""

    start_page = row['Start Page'] if pd.notna(row['Start Page']) else None
    end_page = row['End Page'] if pd.notna(row['End Page']) else None

    if end_page == "+":
        pages = f", pp. {start_page}+"
    else:
        pages = f", pp. {start_page}-{end_page}" if start_page != "" and end_page != "" else ""

    return f"{row['Author Full Names']} {row['Article Title']}{year}{row['Source Title']}{tom}{issue}{article_number}{pages}".strip()


def filter_publication_type(doc_type):
    types = doc_type.split(';')
    for t in types:
        if t.strip() in publication_type_translations:
            return publication_type_translations[t.strip()]
    return None


def affiliation_parser(csv_file_path):
    total_sum = 0
    new_csv_data = []

    with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
        reader = csv.DictReader(file, delimiter=';')
        for row in reader:
            if row['Document Type'] in ['Article', 'Proceedings Paper']:
                affiliations = parse_affiliations(row['Addresses'])
                total_sum += calculate_contribution(row['Addresses'])
                new_csv_data.append(create_new_csv_entry(row, affiliations))

    return total_sum, new_csv_data


def write_new_csv(data):
    # Get the current date and time
    now = datetime.datetime.now()

    # Format the current date and time as a string
    now_str = now.strftime("[%Y-%m-%d] [%H-%M-%S]")

    # Specify the directory and filename with the current date and time
    filename = f"WOS/{now_str} reformatted_wos_data.csv"

    with open(filename, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.DictWriter(file, fieldnames=data[0].keys(), delimiter=';')
        writer.writeheader()
        for row in data:
            writer.writerow(row)


# Check if a file was selected
if file_path:
    total_affiliation_value, new_csv_data = affiliation_parser(file_path)
    print(f"Total Affiliation Value: {total_affiliation_value}")

    # Write the new CSV file
    write_new_csv(new_csv_data)

    # Show the system popup with the output value
    show_popup(f"Коэффициент участия МосПолитеха: {round(total_affiliation_value, 2)}")
else:
    show_popup("Файл не был выбран.")
