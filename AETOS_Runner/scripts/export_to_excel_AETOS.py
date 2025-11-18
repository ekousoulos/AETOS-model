import os
import sys
from datetime import date

if len(sys.argv) < 2:
    print("Usage: python export_csv.py <input_txt_file>")
    exit(1)

input_file = sys.argv[1]
out_dir = os.path.dirname(input_file)  # same folder as input

# Extract suffix from input filename (e.g. _BS, _PN)
base_input = os.path.basename(input_file)
parts = base_input.replace(".txt", "").split("_")
suffix = parts[-1] if len(parts) > 1 else ""

# Build output name
base_filename = os.path.join(out_dir, f"{date.today().strftime('%Y%m%d')}_{suffix}")
csv_filename = f"{base_filename}v1.csv"

version = 1
while os.path.exists(csv_filename):
    version += 1
    csv_filename = f"{base_filename}v{version}.csv"

# Convert the text file to a CSV
with open(input_file) as f_in, open(csv_filename, "w") as f_out:
    for line in f_in:
        tokens = line.strip().split()
        f_out.write(",".join(tokens) + "\n")

print(f"CSV file saved as: {csv_filename}")
