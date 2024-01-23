import csv
import os
import subprocess
import re
import turtle
from svg_turtle import SvgTurtle
import os
import time
import sys

Vert = [0]
Hori = [0]
Dep = [0]
cut_vec_list = [Vert, Hori, Dep]
directory_path = "./cuts_results"
class Item:
    def __init__(self, name, x, y, z, weight):
        self.name = name
        self.x = x
        self.y = y
        self.z = z
        self.weight = weight

    def volume(self):
        return self.x * self.y * self.z

    def __repr__(self):
        return f'Item({self.name}, {self.x}, {self.y}, {self.z}, {self.weight})'


class Bin:
    def __init__(self, name, length, width, height, max_weight):
        self.name = name
        self.length = length
        self.width = width
        self.height = height
        self.max_weight = max_weight
        self.items = []

    def volume(self):
        return self.length * self.width * self.height

    def get_current_weight(self):
        return sum(item.weight for item in self.items)

    def add_item(self, item):
        self.items.append(item)

    def can_fit(self, item, allow_rotation=False):
        if allow_rotation:
            # Check if the item can fit in any of the three possible orientations
            orientations = [(item.x, item.y, item.z), (item.x, item.z, item.y), (item.y, item.x, item.z),
                            (item.y, item.z, item.x), (item.z, item.x, item.y), (item.z, item.y, item.x)]
            for orientation in orientations:
                if (self.length >= orientation[0] and self.width >= orientation[1] and self.height >= orientation[2]
                        and self.get_current_weight() + item.weight <= self.max_weight):
                    return True
        else:
            return (self.length >= item.x and self.width >= item.y and self.height >= item.z
                    and self.get_current_weight() + item.weight <= self.max_weight)

        return False

def read_input_files(items_file, bins_file):
    items = []
    bins = []

    with open(items_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            item = Item(row['name'], int(row['Length']), int(row['Width']), int(row['Height']), float(row['Weight']))
            items.append(item)

    with open(bins_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            bin = Bin(row['name'], int(row['Length']), int(row['Width']), int(row['Height']), float(row['Weight']))
            bins.append(bin)

    return items, bins

def print_results(bins):
    for i, bin in enumerate(bins):
        print(f"Bin {i+1}:")
        print(f"\tItems: {[item.name for item in bin.items]}")
        print(f"\tTotal weight: {bin.get_current_weight()}")
        print(f"\tTotal volume: {bin.volume()}")
        wasted_space = bin.volume() - sum(item.volume() for item in bin.items)
        print(f"\twasted space: {wasted_space}")
        wasted_space_percent = wasted_space / bin.volume() * 100
        print(f"\twasted space in %: {wasted_space_percent:.2f}%")

def total_wasted_space(bins):
    total_wasted_space = 0
    for bin in bins:
        wasted_space = bin.volume() - sum(item.volume() for item in bin.items)
        total_wasted_space += wasted_space
    return total_wasted_space
def total_bins_size(bins):
    total_size = 0
    for bin in bins:
        total_size += bin.volume()
    return total_size

def save_output(bins, method_name):
    if not os.path.exists('results'):
        os.makedirs('results')

    for i, bin in enumerate(bins):
        filename = f'results/bin_{i}_{method_name}.txt'
        with open(filename, 'w') as f:
            f.write(f"{len(bin.items)}\n")
            f.write(f"{bin.length} {bin.width} {bin.height}\n")
            for item in bin.items:
                f.write(f"{item.x} {item.y} {item.z}\n")
            f.write(f"{method_name}")

def next_fit(items, bins):
    current_bin_index = 0
    current_bin = bins[current_bin_index]
    items_not_fit = []

    for item in items:
        if not current_bin.can_fit(item):
            items_not_fit.append(item)
            current_bin_index += 1
            if current_bin_index == len(bins):
                break
            current_bin = bins[current_bin_index]
        current_bin.add_item(item)

    print_results(bins)

    if items_not_fit:
        print("Items that did not fit:")
        for item in items_not_fit:
            print(f"\t{item.name} ({item.x} x {item.y} x {item.z}) with weight {item.weight}")
    wasted_space = total_wasted_space(bins)
    tbsize=total_bins_size(bins)
    wasted_space = wasted_space/tbsize
    save_output(bins, 'next_fit')
    return bins, wasted_space

def first_fit(items, bins):
    items_not_fit = []

    for item in items:
        bin_found = False
        for bin in bins:
            if bin.can_fit(item):
                bin.add_item(item)
                bin_found = True
                break
        if not bin_found:
            items_not_fit.append(item)

    print_results(bins)

    if items_not_fit:
        print("Items that did not fit:")
        for item in items_not_fit:
            print(f"\t{item.name} ({item.x} x {item.y} x {item.z}) with weight {item.weight}")
    wasted_space = total_wasted_space(bins)
    tbsize=total_bins_size(bins)
    wasted_space = wasted_space/tbsize
    save_output(bins, 'first_fit')
    return bins, wasted_space

def best_fit(items, bins):
    items = sorted(items, key=lambda x: x.volume(), reverse=True)
    items_not_fit = []

    for item in items:
        # Try to find the bin with the smallest remaining volume that can fit the item
        best_bin = None
        min_remaining_volume = float('inf')
        for bin in bins:
            if bin.can_fit(item):
                remaining_volume = bin.volume() - sum(item.volume() for item in bin.items)
                if remaining_volume < min_remaining_volume:
                    min_remaining_volume = remaining_volume
                    best_bin = bin

        if best_bin is None:
            items_not_fit.append(item)
        else:
            best_bin.add_item(item)

    print_results(bins)

    if items_not_fit:
        print("Items that did not fit:")
        for item in items_not_fit:
            print(f"\t{item.name} ({item.x} x {item.y} x {item.z}) with weight {item.weight}")
    wasted_space = total_wasted_space(bins)
    tbsize=total_bins_size(bins)
    wasted_space = wasted_space/tbsize
    save_output(bins, 'best_fit')
    return bins, wasted_space

def worst_fit(items, bins):
    items = sorted(items, key=lambda x: x.volume(), reverse=True)
    items_not_fit = []

    for item in items:
        bin_found = False
        max_wasted_percentage = 0

        for bin in bins:
            if bin.can_fit(item):
                wasted_percentage = bin.volume() - sum(item.volume() for item in bin.items)
                if wasted_percentage > max_wasted_percentage:
                    max_wasted_percentage = wasted_percentage
                    current_bin = bin
                    bin_found = True

        if not bin_found:
            items_not_fit.append(item)
        else:
            current_bin.add_item(item)

    print_results(bins)

    if items_not_fit:
        print("Items that did not fit:")
        for item in items_not_fit:
            print(f"\t{item.name} ({item.x} x {item.y} x {item.z}) with weight {item.weight}")
    wasted_space = total_wasted_space(bins)
    tbsize=total_bins_size(bins)
    wasted_space = wasted_space/tbsize
    save_output(bins, 'worst_fit')
    return bins, wasted_space



def compare_packing_methods(items, bins):
    start_time = time.time()
    nf_bins, nf_waste = next_fit(items, bins)
    nf_time = time.time() - start_time

    start_time = time.time()
    ff_bins, ff_waste = first_fit(items, bins)
    ff_time = time.time() - start_time

    start_time = time.time()
    bf_bins, bf_waste = best_fit(items, bins)
    bf_time = time.time() - start_time

    wf_bins, wf_waste = worst_fit(items, bins)

    print("Comparison results:")
    print("---------------------------------------------------------")
    print("Method\t\tUsed Boxes\tWaste (%)\tExecution Time (s)")
    print("---------------------------------------------------------")
    print(f"Next Fit\t{len(nf_bins)}\t\t{nf_waste*100:.2f}%\t\t{nf_time:.5f}")
    print(f"First Fit\t{len(ff_bins)}\t\t{ff_waste*100:.2f}%\t\t{ff_time:.5f}")
    print(f"Best Fit\t{len(bf_bins)}\t\t{bf_waste*100:.2f}%\t\t{bf_time:.5f}")
    print(f"Worst Fit\t{len(wf_bins)}\t\t{wf_waste*100:.2f}%\t\t{bf_time:.5f}")

"""
@function extract_dimensions
Gets the dimensions and weight from the strings that represent it in the csv input files, using regex
"""


def extract_dimensions(stringP):
    match = re.search(
        r'(\d+\.\d+)x(\d+\.\d+)x(\d+\.\d+), weight: (\d+\.\d+)', stringP)
    length, width, height, weight = match.groups()
    return "{0} {1} {2}".format(round(float(length)), round(float(width)), round(float(height)))



"""
@function read_file_lines
Gets the path of a file and organize their lines in a vector
"""


def read_file_lines(file_path):
    with open(file_path) as file:
        lines = file.readlines()
    line_lists = []
    for i, line in enumerate(lines):
        line_lists.append(f"line_{i + 1}")
        line_lists[i] = line.strip().split(" ")
    return line_lists




"""
@function print_vector_elements
Prints the elements of a vector starting after 6 positions
"""


def print_vector_elements(vector, n):
    for i in range(n):
        print(vector[i + 6])


"""
@function create_folder
Create a folder with the name 'cuts_of_order' in the current working directory
"""


def create_folder():
    folder_name = 'cuts_of_order'
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    return folder_name


def draw_borders(x, y, t, scale_factor, width, height):
    last_x = int(x[-1]) * scale_factor
    last_y = int(y[-1]) * scale_factor

    t.penup()
    t.goto(0, 0)
    t.pendown()
    t.goto(0, last_y)

    t.penup()
    t.goto(0, last_y)
    t.pendown()
    t.goto(last_x, last_y)

    t.penup()
    t.goto(last_x, last_y)
    t.pendown()
    t.goto(last_x, 0)

    t.penup()
    t.goto(last_x, 0)
    t.pendown()
    t.goto(0, 0)


"""
@function
Gets a vector and a parameter for turtle and draws straigt lines on x-axis
"""


def cuts_in_x(vector, t, scale_factor, width, height):
    for i in vector:
        x = int(i) * scale_factor
        y0 = 0
        y1 = int(vector[-1]) * scale_factor

        t.penup()
        t.goto(x, y0)
        t.pendown()
        t.goto(x, y1)
        t.write(int(i))


"""
@function
Gets a vector and a parameter for turtle and draws straigt lines on x-asis
"""


def cuts_in_y(vector, t, scale_factor, width, height):
    for i in vector:
        x0 = 0
        x1 = int(vector[-1]) * scale_factor
        y = int(i) * scale_factor

        t.penup()
        t.goto(x0, y)
        t.pendown()
        t.goto(x1, y)
        t.write(int(i))


"""
@function cut_in_directions
Transfer the parameters that it gets to the cutting functions
"""


def cut_in_directions(x, y, t, width, height):

    scale_factor = 10  # min(width, height) / max(image_width, image_height)*2

    draw_borders(x, y, t, scale_factor, width, height)
    cuts_in_x(x, t, scale_factor, width, height)
    cuts_in_y(y, t, scale_factor, width, height)


"""
@function cut_draws
Gets the sets of cuts and draws straigt cuts in a SVG
"""


def cut_draws(result_number, cut_group):
    width = 1000
    height = 1000

    for i in range(len(cut_group)):
        for j in range(len(cut_group)):
            if i != j:
                turtle.clearscreen()
                print(cut_group[i], cut_group[j])

                def draw(t): return cut_in_directions(
                    cut_group[i][1], cut_group[j][1], t, width, height)
                write_file(draw, "image_{0}_{1}.svg".format(
                    result_number, i), width, height)


"""
@function write_file
Gets a funtion to draw, a name to a SVG and it's dimensions and creates a svg file to save a draw done with the function
"""


def write_file(draw_func, filename, width, height):
    folder_name = create_folder()
    file_path = os.path.join(folder_name, filename)
    t = SvgTurtle(width, height)
    draw_func(t)
    t.save_as(file_path)


"""
@function makes_images
Gets the results of the Paker, for each result organizes the input to the program that solves the cuts
"""

def makes_images():
    depth_cut_regex = re.compile(r"Depth cuts at (\d+(?: \d+)*)")
    horizontal_cut_regex = re.compile(r"Horizontal cuts at (\d+(?: \d+)*)")
    vertical_cut_regex = re.compile(r"Vertical cuts at (\d+(?: \d+)*)")

    for file_name in os.listdir(directory_path):
        if file_name.endswith(".txt"):
            file_path = os.path.join(directory_path, file_name)
            lines = read_file_lines(file_path)
            new_lines = []
            for line_list in lines:
                if line_list[0] == '':
                    continue
                new_lines.append(line_list)

            with open(file_path) as file:
                #liness = file.readlines()

                cut_values = [[], [], []]
                length = 0
                width = 0
                height = 0

                def get_dimensions(the_line):
                    length_match = re.search(r"length:\s*(\d+)", the_line)
                    width_match = re.search(r"width:\s*(\d+)", the_line)
                    height_match = re.search(r"height:\s*(\d+)", the_line)
                    if length_match:
                        length = int(length_match.group(1))
                    if width_match:
                        width = int(width_match.group(1))
                    if height_match:
                        height = int(height_match.group(1))
                    return (length, width, height)

                for index, line in enumerate(file):
                    print(line)
                    if index == 2:
                        length, width, height = get_dimensions(line)
                        continue
                    depth_match = depth_cut_regex.search(line)
                    horizontal_match = horizontal_cut_regex.search(line)
                    vertical_match = vertical_cut_regex.search(line)

                    # Check if a match was found for any of the cut types
                    if depth_match:
                        cut_values[0] = list(map(int, depth_match.group(1).split()))
                    elif horizontal_match:
                        cut_values[1] = list(map(int, horizontal_match.group(1).split()))
                    elif vertical_match:
                        cut_values[2] = list(map(int, vertical_match.group(1).split()))
                cut_values[0].append(width)
                cut_values[1].append(height)
                cut_values[2].append(length)
                #print("\n\nHere are the cut values: \n")
                #print(cut_values)

            #print(new_lines)

        Vert.append(cut_values[2])
        Hori.append(cut_values[1])
        Dep.append(cut_values[0])
        print("Dep:", Dep)
        print("Hori:", Hori)
        print("Vert:", Vert)
        cut_group = [Dep, Vert, Hori]
        print(cut_group)
        cut_draws(file_name, cut_group)


def generate_html_with_svg_files():
    # Define the folder containing the SVG files
    folder = ".\cuts_of_order"

    # Get a list of all the SVG files in the folder
    svg_files = [f for f in os.listdir(folder) if f.endswith(".svg")]

    # Create the HTML document
    html = "<html><head><title>Packing options</title></head><body>"

    # Loop through each SVG file and add it to the HTML document
    for svg_file in svg_files:
        # Get the name of the SVG file without the file extension
        name = os.path.splitext(svg_file)[0]

        # Add the name of the SVG file to the HTML document
        html += f"<h1>{name}</h1>"

        # Add the SVG file to the HTML document
        html += f'<object type="image/svg+xml" data="{folder}/{svg_file}"></object>'

    # Close the HTML document
    html += "</body></html>"

    # Write the HTML document to a file
    with open("packing_options.html", "w") as f:
        f.write(html)


