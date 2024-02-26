import csv

# Input and output file paths
input_file = 'D:/CURRENT/recreational_value_mapping_forest_pl/BDL_data/test_subarea_ul_lnp.csv'
output_file = 'D:/CURRENT/recreational_value_mapping_forest_pl/BDL_data/output_2.csv'

# Indices of the columns to keep (5 and 6 because it's zero-based indexing)

columns_to_keep = [0, 1, 2]

# Open input and output files
with open(input_file, 'r', encoding='utf-8') as csvfile, open(output_file, 'w', newline='', encoding='utf-8') as output_csvfile:
    reader = csv.reader(csvfile, delimiter=';')
    writer = csv.writer(output_csvfile, delimiter=';')

    for row in reader:
        # If the row has at least the maximum column index from columns_to_keep + 1 columns
        if max(columns_to_keep) + 1 <= len(row):
            # Only keep the columns at the specified indices
            row = [row[col] for col in columns_to_keep]

            # Write the row to the output CSV file
            writer.writerow(row)
