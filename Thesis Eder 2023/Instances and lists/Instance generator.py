import csv
import os
import random


def generate_new_csv(input_file, output_file_prefix, n, max_rows):
    # create the "Instances" folder if it doesn't exist
    os.makedirs("Instances", exist_ok=True)

    with open(input_file) as input_csv:
        reader = csv.reader(input_csv)
        headers = next(reader)

        data = list(reader)
        for i in range(n):
            num_rows = random.randint(1, max_rows)
            selected_data = random.sample(data, num_rows)
            output_file = f'Instances/{output_file_prefix}{i + 1}.csv'  # prepend the folder name to the output file path
            with open(output_file, 'w', newline='') as output_csv:
                writer = csv.writer(output_csv)
                writer.writerow(headers)
                for row in selected_data:
                    writer.writerow(row)


input_file = 'Instances and lists\All Items List.csv'
output_file_prefix = 'item'
max_rows = 10

n = int(input("Enter the number of new CSV files to generate: "))

generate_new_csv(input_file, output_file_prefix, n, max_rows)
