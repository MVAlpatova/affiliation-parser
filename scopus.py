import pandas as pd

from dict import all_countries, possible_names, file_path, show_popup

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


# Check if a file was selected
if file_path:
    # Here you would add your logic to process the file and compute the output
    scopus_data = pd.read_csv(file_path)

    # Filter the DataFrame
    filtered_scopus_data = scopus_data[scopus_data['Тип документа'].isin(['Article', 'Review'])]

    # Initialize the total contribution variable
    total_contribution = 0

    # Iterate over each row in the DataFrame
    for index, row in filtered_scopus_data.iterrows():
        # Call the calculate_contribution function for the 'Авторы организаций' column of the current row
        contribution = calculate_contribution(row['Авторы организаций'], possible_names, all_countries_list)

        # Get the value from the 'Название' column
        title = row['Название']

        # Print the row index, title from 'Название' column, and the calculated contribution
        print(f"[{index}] {title} - {contribution}")

        # Add the calculated contribution to the total contribution
        total_contribution += contribution

    # After the loop, if you want to print the total contribution, you can do so:
    print(f"Общий вклад: {total_contribution}")

    # Show the system popup with the output value
    show_popup(f"Коэффициент участия МосПолитеха: {round(total_contribution, 2)}")
else:
    show_popup("Файл не был выбран.")
