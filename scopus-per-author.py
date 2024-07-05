import pandas as pd
from dict import all_countries, possible_names
import numpy as np

from global_methods import merge_faculty_with_ids


def get_name_part(input_str):
    first_comma_index = input_str.find(",")
    if first_comma_index == -1:  # No comma in the string
        return input_str
    else:
        return input_str[:first_comma_index].strip()


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


def extract_organization_names(workplaces):
    organization_names = []
    for workplace in workplaces:
        # Split by the comma and take the first element, which is the organization name
        name = workplace.split(",")[0].strip()
        organization_names.append(name)
    return organization_names


def calculate_author_contribution(author, affiliations_str, aliases):
    affiliations = affiliations_str.split("; ")
    total_authors_count = len(affiliations)
    author_contribution = 0
    places_of_work = []

    for affiliation in affiliations:
        author_name = get_name_part(affiliation)

        if author.lower() not in author_name.lower():
            continue

        orgs = affiliation[len(author_name) + 1:].strip()
        places = extract_and_split_by_countries(orgs, all_countries)

        is_polytech = any(alias.lower() in work.lower() for work in places for alias in aliases)

        if is_polytech:
            author_contribution += 1 / len(places)
            places_of_work.extend(places)

        break  # break the loop once we find a match for the author's name

    return author_contribution / total_authors_count if total_authors_count else 0, places_of_work


# Load the CSV files
faculty = "ИИДИЖ"
df_merged = merge_faculty_with_ids(faculty)

# Fill NaN values in 'Scopus' column with an empty string
df_merged['Scopus'] = df_merged['Scopus'].fillna('')

# Create a new dataframe with only 'Name' and 'Scopus'
df_final = df_merged[['Name', 'Scopus']]

# Remove rows with NaN in 'Name' column
df_final = df_final.dropna(subset=['Name'])

# Load the Scopus.csv file
df_scopus = pd.read_csv('input/Scopus.csv')

# Create an empty DataFrame to store the results
df_results = pd.DataFrame(columns=['Author', 'Scopus ID', 'Scopus Article'])

# Iterate over each row in df_final
for index, row in df_final.iterrows():
    author = row['Name']
    scopus_id = row['Scopus']

    # Skip authors with an empty Scopus ID
    if not scopus_id or scopus_id == '0':
        continue

    # Find all rows in df_scopus where 'Author(s) ID' contains the scopus_id
    matching_rows = df_scopus[df_scopus['Author(s) ID'].str.contains(scopus_id, na=False)]

    # For each match, add a new row to df_results
    for _, matching_row in matching_rows.iterrows():
        df_results.loc[len(df_results)] = [author, scopus_id, matching_row['Title']]

# Print the final dataframe
print(df_results)
df_results.to_csv('pre-final_results.csv', index=False)

# Iterate over each row in df_results
for index, row in df_results.iterrows():
    author_id = row['Scopus ID']

    # Skip authors with an empty Scopus ID
    if not author_id:
        continue

    # Find the row in df_scopus where 'Title' matches the 'Scopus Article'
    matching_row = df_scopus[df_scopus['Title'] == row['Scopus Article']].iloc[0]

    if row['Scopus Article'] == 'Preface':
        print(matching_row)

    # Extract the 'Authors' and 'Author(s) ID' strings and split them by semicolon
    authors = matching_row['Authors'].split('; ')
    ids = matching_row['Author(s) ID'].split('; ')

    # Find the index of the author's ID in the IDs list
    try:
        author_index = ids.index(author_id)
    except ValueError:
        continue

    # Use this index to get the corresponding author's name from the authors list
    author_name = authors[author_index]

    # Extract the 'Authors with affiliations' string
    authors_with_affiliations = matching_row['Authors with affiliations']

    # Add the total count of authors to the row
    df_results.loc[index, 'Total Authors Count'] = len(authors)

    # Calculate the author's contribution and places of work
    author_contribution, places_of_work = calculate_author_contribution(author_name, authors_with_affiliations,
                                                                        possible_names)
    df_results.loc[index, 'Author Contribution'] = np.round(author_contribution, 2)

    # Add the workplaces count to the row
    df_results.loc[index, 'Workplaces Count'] = len(places_of_work)

# Print the final dataframe
df_results = df_results.dropna()
print(df_results)

# Convert 'Total Authors Count' and 'Workplaces Count' to integers
df_results['Total Authors Count'] = df_results['Total Authors Count'].astype(int)
df_results['Workplaces Count'] = df_results['Workplaces Count'].astype(int)

# Save the DataFrame to a CSV file
df_results.to_csv(faculty + '_final_results.csv', index=False)
