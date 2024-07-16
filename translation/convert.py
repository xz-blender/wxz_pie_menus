import csv
import os


def swap_columns(input_file, output_file):
    with open(input_file, mode="r", encoding="utf-8") as infile, open(
        output_file, mode="w", encoding="utf-8", newline=""
    ) as outfile:

        reader = csv.reader(infile)
        writer = csv.writer(outfile, quoting=csv.QUOTE_ALL)

        for row in reader:
            # Swap the columns
            swapped_row = [row[1], row[0]]
            writer.writerow(swapped_row)


if __name__ == "__main__":
    input_filename = "list.csv"
    output_filename = "convert.csv"

    # Ensure the script works with relative paths
    script_dir = os.path.dirname(__file__)
    input_file = os.path.join(script_dir, input_filename)
    output_file = os.path.join(script_dir, output_filename)

    swap_columns(input_file, output_file)
    print(f"Swapped columns and saved to {output_filename}")
