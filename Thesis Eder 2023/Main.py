import os
from svg_turtle import SvgTurtle
import os
import time
from relevant_functions import *
import sys
start_time = time.time()

items_file = 'Instances and lists/Items/item10.csv'
bins_file = 'Instances and lists/Boxes/box10.csv'
items, bins = read_input_files(items_file, bins_file)

def save_function_output_to_file(file_name):
    
    original_stdout = sys.stdout
    with open(file_name, 'w') as file:
        sys.stdout = file
        

        compare_packing_methods(items, bins)
        

        sys.stdout = original_stdout
save_function_output_to_file('complete results.txt')
        


if not os.path.exists('cuts_results'):
    os.makedirs('cuts_results')

for filename in os.listdir('results'):

    if filename.endswith('.txt'):

        os.system(f'DP3SUK.exe  results/{filename} > cuts_results/{filename}')
# vectors to store the cuts

Vert = [0]
Hori = [0]
Dep = [0]
cut_vec_list = [Vert, Hori, Dep]
makes_images()

generate_html_with_svg_files()
print("--- %s seconds ---" % (time.time() - start_time))
