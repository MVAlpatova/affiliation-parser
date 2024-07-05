import datetime
import pandas as pd
from dict import all_countries, possible_names, file_path, show_popup, publication_type_translations
from pathlib import Path


# Split the countries string into a list
all_countries_list = all_countries.split("; ")


def get_name_part(input_str):
    first_comma_index = input_str.find(",")
    if first_comma_index == -1:  # No comma in the string
        return input_str
    else:
        second_comma_index = input_str.find(",", first_comma_index + 1)
        if second_comma_index == -1:  # Only one comma in the string
            return input_str
        else:
            return input_str[:second_comma_index].strip()


def extract_and_split_by_countries(input_val, all_countries):
    input_parts = input_val.split(",")
    temp_string = ""
    output = []

    for part in input_parts:
        temp_string += part.strip() + ", "
        if part.strip() in all_countries:
            output.append(temp_string.rstrip(", "))
            temp_string = ""

    if temp_string:  # If there's anything left over, add it to the output
        output.append(temp_string.rstrip(", "))

    return output


def calculate_contribution(input_str, aliases, all_countries):
    affiliations = input_str.split("; ")
    total_authors_count = len(affiliations)
    polytech_contribution = 0

    for affiliation in affiliations:
        author_name = get_name_part(affiliation)
        orgs = affiliation[len(author_name) + 1:].strip()
        places_of_work = extract_and_split_by_countries(orgs, all_countries)

        is_polytech = any(alias.lower() in work.lower() for work in places_of_work for alias in aliases)

        if is_polytech:
            polytech_contribution += 1 / len(places_of_work)

    return polytech_contribution / total_authors_count if total_authors_count else 0


def get_author_details(affiliations, aliases):
    authors_with_affiliation = []
    for affiliation in affiliations:
        author_name = get_name_part(affiliation)
        orgs = affiliation[len(author_name) + 1:].strip()
        places_of_work = extract_and_split_by_countries(orgs, all_countries_list)
        is_polytech = any(alias.lower() in work.lower() for work in places_of_work for alias in aliases)
        if is_polytech:
            authors_with_affiliation.append(author_name)
    return authors_with_affiliation


def construct_bibliography_reference(row):
    authors = row['Authors with affiliations'].split("; ")
    authors_str = ", ".join([get_name_part(author) for author in authors])
    year = f" {int(row['Year'])} " if pd.notna(row['Year']) else ""

    tom = f", {row['Volume']}" if row['Volume'] != "" else ""

    if tom != "":
        issue = f" ({row['Issue']})" if row['Issue'] != "" else ""
    else:
        issue = f", Issue{row['Issue']}" if row['Issue'] != "" else ""

    article_number = f", Art. No. {row['Art. No.']}" if row['Art. No.'] != "" else ""

    start_page = row['Page start'] if row['Page start'] != "" else None
    end_page = row['Page end'] if row['Page end'] != "" else None
    pages = f", pp. {start_page}-{end_page}" if start_page != "" and end_page != "" else ""

    return f"{authors_str} {row['Title']}{year}{row['Source title']}{tom}{issue}{article_number}{pages}".strip()


def extract_organization_names(workplaces):
    organization_names = []
    for workplace in workplaces:
        # Split by the comma and take the first element, which is the organization name
        name = workplace.split(",")[0].strip()
        organization_names.append(name)
    return organization_names


# Check if a file was selected
if file_path:
    # Here you would add your logic to process the file and compute the output
    try:
        scopus_data = pd.read_csv(file_path)
    except:
        scopus_data = pd.read_csv(file_path, delimiter=';')

    # Create a copy of the filtered DataFrame to avoid the SettingWithCopyWarning
    filtered_scopus_data = scopus_data[scopus_data['Document Type'].isin(['Article', 'Review'])].copy()

    # Initialize the total contribution variable
    total_contribution = 0

    # Initialize an empty list for the new CSV data
    additional_data = []

    for index, row in filtered_scopus_data.iterrows():

        contribution = round(calculate_contribution(row['Authors with affiliations'], possible_names, all_countries_list), 2)

        authors = row['Authors with affiliations'].split("; ")
        authors_with_affiliation = get_author_details(authors, possible_names)

        # Extract last and second names
        last_names = [name.split(",")[0] for name in authors_with_affiliation]
        second_names = [name.split(",")[1] if len(name.split(",")) > 1 else "" for name in authors_with_affiliation]

        # Extract the places of work with the existing function
        places_of_work = [extract_and_split_by_countries(aff[len(get_name_part(aff)) + 1:].strip(), all_countries_list)
                          for aff in authors if any(alias.lower() in aff.lower() for alias in possible_names)]

        # Extract just the organization names from the places of work
        organization_names = [name for place in places_of_work for name in extract_organization_names(place)]

        # Count the unique workplaces while preserving the order they were found
        seen = set()
        unique_workplaces = [x for x in organization_names if not (x in seen or seen.add(x))]
        workplaces_count = len(unique_workplaces)

        bibliography_reference = construct_bibliography_reference(row)

        # Convert year to integer if it's not NaN
        year = int(row['Year']) if pd.notna(row['Year']) else None

        # Add the calculated contribution to the total contribution
        total_contribution += contribution

        # Translate publication type to Russian
        publication_type_russian = publication_type_translations.get(row['Document Type'], row['Document Type'])

        additional_data.append({
            'Идентификатор DOI *': row['DOI'],
            'Количество авторов *': len(authors),
            'Фамилия *': ", ".join(last_names),
            'Имя *': ", ".join(second_names),
            'Количество аффилиаций *': workplaces_count,
            'Аффиляция *': ", ".join(organization_names),
            'Контрибьюция *': contribution,
            'Дата публикации *': year,
            'Наименование публикации *': row['Title'],
            'Наименование издания *': row['Source title'],
            'Библиографическая ссылка *': bibliography_reference,
            'Вид издания  *': publication_type_russian
        })

        # Print the row index, title from 'Название' column, and the calculated contribution
        print(f"[{index}] {row['Title']} - {contribution}")

    # Create DataFrame from additional data and export to CSV
    additional_data_df = pd.DataFrame(additional_data)

    # Get the current date and time
    now = datetime.datetime.now()

    # Format the current date and time as a string
    now_str = now.strftime("[%Y-%m-%d] [%H-%M-%S]")

    # Create a new directory named 'SCOPUS' if it doesn't exist
    Path("SCOPUS").mkdir(exist_ok=True)

    # Specify the directory and filename with the current date and time
    filename = f"SCOPUS/{now_str} reformatted_scopus_data.csv"

    # Save the DataFrame to a CSV file in the specified directory with the specified filename
    additional_data_df.to_csv(filename, index=False)

    # Show the system popup with the output value
    show_popup(f"Коэффициент участия МосПолитеха: {round(total_contribution, 2)}")
else:
    show_popup("Файл не был выбран.")