import os
from datetime import date

# Get today's date and initialize the version
base_filename = f"results/{date.today().strftime('%Y%m%d')}"
csv_filename = f"{base_filename}v1.csv"

# Check if the CSV file already exists, and if so, increment the version number
version = 1
while os.path.exists(csv_filename):
    version += 1
    csv_filename = f"{base_filename}v{version}.csv"

# Convert the text file to a CSV with the correct name
with open("results/trans_results_sorted_AETOS.txt") as f_in, open(csv_filename, "w") as f_out:
    for line in f_in:
        tokens = line.strip().split()  # splits on any whitespace
        f_out.write(",".join(tokens) + "\n")

print(f"CSV file saved as: {csv_filename}")
