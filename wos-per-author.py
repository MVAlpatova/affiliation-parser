import pandas as pd
from dict import all_countries, possible_names
import numpy as np

from global_methods import merge_faculty_with_ids, wos_parse_affiliations, wos_parse_authors_ids, \
    wos_find_affiliations_by_id, wos_get_distinct_authors

# Load the CSV files
faculty = "ИИДИЖ"
df_merged = merge_faculty_with_ids(faculty)

# Fill NaN values in 'WoS' column with an empty string
df_merged['WoS'] = df_merged['WoS'].fillna('')

# Create a new dataframe with only 'Name' and 'Scopus'
df_final = df_merged[['Name', 'WoS']]

# Remove rows with NaN in 'Name' column
df_final = df_final.dropna(subset=['Name'])

# Load the Scopus.csv file
df_wos = pd.read_csv('input/WoS.csv', delimiter=';', low_memory=False)

# Create an empty DataFrame to store the results
df_results = pd.DataFrame(columns=['Author', 'WoS ID', 'WoS Article'])


# Iterate over each row in df_final
for index, row in df_final.iterrows():
    author = row['Name']
    wos_id = row['WoS']

    # Skip authors with an empty Scopus ID
    if not wos_id or wos_id == '0':
        continue

    # Find all rows in df_wos where 'Author(s) ID' contains the wos_id
    matching_rows = df_wos[df_wos['Researcher Ids'].str.contains(wos_id, na=False)]

    # For each match, add a new row to df_results
    for _, matching_row in matching_rows.iterrows():
        df_results.loc[len(df_results)] = [author, wos_id, matching_row['Article Title']]

# Print the pre-final dataframe
print(df_results)
df_results.to_csv('pre-final_results_wos.csv', index=False)

# Iterate over each row in df_results
for index, row in df_results.iterrows():
    author_id = row['WoS ID']

    # Skip authors with an empty WoS ID
    if not author_id:
        continue

    # Find the row in df_scopus where 'Title' matches the 'Scopus Article'
    matching_row = df_wos[df_wos['Article Title'] == row['WoS Article']].iloc[0]

    # Extract affiliations
    affiliations = wos_parse_affiliations(matching_row['Addresses'])
    total_authors = wos_get_distinct_authors(affiliations)

    # Extract IDs
    ids = wos_parse_authors_ids(matching_row['Researcher Ids'])
    resulting_affiliations = wos_find_affiliations_by_id(author_id, ids, affiliations)

    places_of_work = len(resulting_affiliations)
    if places_of_work == 0:
        print(f"Author {row['Author']} has no affiliation with Moscow Polytech University")
        continue

    total_author_count = len(total_authors)
    author_contribution = (1 / places_of_work) / total_author_count

    df_results.loc[index, 'Total Authors Count'] = total_author_count
    df_results.loc[index, 'Author Contribution'] = np.round(author_contribution, 2)
    df_results.loc[index, 'Workplaces Count'] = places_of_work


# Print the final dataframe
df_results = df_results.dropna()

# Check if df_results contains any rows
if df_results.empty:
    print("No results found")
    exit()

# Check if 'Total Authors Count' or 'Author Contribution' or 'Workplaces Count' columns exists in df_results
if 'Total Authors Count' not in df_results.columns or 'Author Contribution' not in df_results.columns or 'Workplaces Count' not in df_results.columns:
    print("Columns 'Total Authors Count', 'Author Contribution' or 'Workplaces Count' do not exist in the DataFrame")
    exit()

# Delete all rows from df_results where 'Total Authors Count' or 'Author Contribution' or 'Workplaces Count' is NaN
df_results = df_results.dropna(subset=['Total Authors Count', 'Author Contribution', 'Workplaces Count'])

print(df_results)

# Convert 'Total Authors Count' and 'Workplaces Count' to integers
df_results['Total Authors Count'] = df_results['Total Authors Count'].astype(int)
df_results['Workplaces Count'] = df_results['Workplaces Count'].astype(int)

# Save the DataFrame to a CSV file
df_results.to_csv('output/wos/'+faculty + '_wos_final_results.csv', index=False)
