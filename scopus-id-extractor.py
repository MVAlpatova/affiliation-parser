import pandas as pd

# Load the Scopus.csv file
df_scopus = pd.read_csv('input/Scopus.csv')

# Create an empty dictionary to store the authors and their IDs
authors_dict = {}

# Iterate over each row in df_scopus
for _, row in df_scopus.iterrows():
    # Get the value from the 'Author full names' column and split it by semicolon
    authors = row['Author full names'].split(';')

    # For each author, split the string by '(' to separate the name and the ID
    for author in authors:
        name, id = author.rsplit('(', 1)
        id = id.rstrip(')')  # Remove the trailing ')'

        # If the ID already exists in the dictionary, skip it
        if id in authors_dict:
            continue

        # Store the author name and ID in the dictionary
        authors_dict[id] = name.strip()

# Convert the dictionary to a DataFrame
df_authors = pd.DataFrame(list(authors_dict.items()), columns=['ID', 'Name'])

# Save the DataFrame to a CSV file
df_authors.to_csv('authors.csv', index=False)