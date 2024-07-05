import pandas as pd
import re
import Levenshtein

from dict import possible_names

# Constants
AFFILIATION_END_SYMBOL = ";"
AUTHORS_SEPARATOR = ";"
START_BRACKET = "["
END_BRACKET = "]"


# Function to normalize names to 'Last Name, First Initial' format
def shorten_name(name):
    parts = name.split(', ')
    last_name = parts[0]
    first_name = parts[1] if len(parts) > 1 else ''
    first_initial = first_name[0] if first_name else ''
    return f"{last_name}, {first_initial}"


def normalize_name(name):
    return re.sub(r'\s+|\.|,', '', name).lower()


def similar(a, b):
    return Levenshtein.distance(a, b)


# root like 'scopus-author/', folder with files
def merge_faculty_with_ids(faculty):
    root = 'faculty-data/'
    # Load the CSV files
    df_names = pd.read_csv(root + 'departments/'+faculty + '.csv', delimiter=';', low_memory=False)
    df_id = pd.read_csv(root + 'Id.csv', delimiter=';')

    # Filter rows where 'Вид занятости' equals 'Основное место работы'
    df_names = df_names[df_names['Вид занятости'] == 'Основное место работы']

    # Rename the column in df_names
    df_names = df_names.rename(columns={'Сотрудник': 'Name'})

    # Merge the two dataframes using a left join
    return pd.merge(df_names, df_id, on='Name', how='left')


class Affiliation:
    def __init__(self, authors, work_place, is_from_polytech):
        self.authors = authors
        self.work_place = work_place
        self.is_from_polytech = is_from_polytech


def parse_affiliation(affiliation_text):
    startIndex = affiliation_text.find(START_BRACKET)
    endIndex = affiliation_text.find(END_BRACKET)
    authorsText = affiliation_text[startIndex + 1:endIndex]
    workPlace = affiliation_text[endIndex + 2:].strip()

    authors = [author.strip() for author in authorsText.split(AUTHORS_SEPARATOR)]
    is_from_polytech = any(workPlace.startswith(univ) for univ in possible_names)

    return Affiliation(authors, workPlace, is_from_polytech)


def wos_parse_affiliations(input_text):
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


def wos_parse_authors_ids(input_string):
    # Split the string by semicolon to get individual entries
    entries = input_string.split('; ')

    # Create an empty dictionary to store the results
    result_dict = {}

    # Iterate over each entry
    for entry in entries:
        # Split the entry by '/' to separate name and ID
        # Split the entry by '/' to separate name and ID
        if '/' in entry:
            name, id = entry.split('/')
            # Clean up whitespace
            name = name.strip()
            id = id.strip()
            # Convert the name into 'Last Name, First Initial' format
            parts = name.split(', ')
            last_name = parts[0]
            first_name = parts[1] if len(parts) > 1 else ''
            first_initial = first_name[0] if first_name else ''
            formatted_name = f"{last_name}, {first_initial}"
            # Add the ID and formatted name to the dictionary
            result_dict[id] = formatted_name

    return result_dict


def wos_find_affiliations_by_id(person_id, id_to_name_map, affiliations):
    person_name = id_to_name_map.get(person_id, None)
    if person_name is None:
        return []

    # Normalizing the person's name for comparison
    person_name_normalized = normalize_name(person_name)

    def is_similar(name):
        distance = Levenshtein.distance(name.lower(), person_name_normalized)
        return distance <= 2

    # Find all affiliations where the person's name is close to any author's name
    target_affiliations = [
        aff for aff in affiliations
        if any(is_similar(normalize_name(shorten_name(author))) for author in aff.authors)
    ]

    return target_affiliations


def wos_get_distinct_authors(affiliations):
    authors = set()
    for affiliation in affiliations:
        authors.update(affiliation.authors)
    return list(authors)