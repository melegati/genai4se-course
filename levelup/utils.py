import argparse
import fnmatch
import re
import os

def str2bool(v):
    if isinstance(v, bool):
        return v
    if v.lower() in ('yes', 'true', 't', 'y', '1'):
        return True
    elif v.lower() in ('no', 'false', 'f', 'n', '0'):
        return False
    else:
        raise argparse.ArgumentTypeError('Boolean value expected.')
    
def how_many_to_skip(original_file, logs_folder, multiplier=1):
    file_split = original_file.split("/")
    path = "/".join(file_split[0:len(file_split) - 1])
    path = "." if path == "" else path
    original_file = file_split[-1]
    files = os.listdir(logs_folder)
    search_file = original_file.replace(".py", "") + "_*.py"
    matching_files = [file for file in files if fnmatch.fnmatch(file, search_file)and len(file.replace(original_file.replace(".py", ""), "").split("_")) == multiplier +1]
    pattern = re.compile(r'\d+')

    # Extract numbers from each filename and create an array
    numbers_array = [int(pattern.search(file).group()) for file in matching_files if pattern.search(file)]
    files_to_skip = max(numbers_array) if len(numbers_array) > 0 else 0
    return files_to_skip