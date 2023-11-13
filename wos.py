import csv

from dict import possible_names, file_path, show_popup

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
    bracket_content = ""
    output_string = ""
    split_string = input_string.split("; ")

    for part in split_string:
        if "[" in part and "]" in part:
            bracket_content = part[part.find("["):part.find("]") + 1]
        else:
            if bracket_content:
                part = bracket_content + " " + part
        output_string += "; " + part if output_string else part

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
    input_text = fix_string(input_text)
    affiliations = parse_affiliations(input_text)
    authors = get_distinct_authors(affiliations)

    author_map = {author: {'TotalAffiliations': 0, 'PolyAffiliations': 0} for author in authors}

    for affiliation in affiliations:
        for author in affiliation.authors:
            author_map[author]['TotalAffiliations'] += 1
            if affiliation.is_from_polytech:
                author_map[author]['PolyAffiliations'] += 1

    only_poly = [a for a in author_map.values() if a['PolyAffiliations'] > 0]
    contribution_sum = sum(a['PolyAffiliations'] / a['TotalAffiliations'] for a in only_poly)

    return contribution_sum / len(authors) if authors else 0


def affiliation_parser(csv_file_path):
    total_sum = 0
    try:
        with open(csv_file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.DictReader(file, delimiter=';')
            total_sum = sum(calculate_contribution(row['Addresses']) for row in reader)
    except UnicodeDecodeError:
        with open(csv_file_path, mode='r', newline='', encoding='windows-1251') as file:
            reader = csv.DictReader(file, delimiter=';')
            total_sum = sum(calculate_contribution(row['Addresses']) for row in reader)

    return total_sum


# Check if a file was selected
if file_path:
    # Here you would add your logic to process the file and compute the output
    total_affiliation_value = affiliation_parser('wos.csv')
    print(f"Total Affiliation Value: {total_affiliation_value}")

    # Show the system popup with the output value
    show_popup(f"Коэффициент участия МосПолитеха: {round(total_affiliation_value, 2)}")
else:
    show_popup("Файл не был выбран.")
