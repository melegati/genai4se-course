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
    
def get_extension(filename):
    return filename.split(".")[-1]

def how_many_to_skip(original_file, logs_folder, multiplier=1):
    file_split = original_file.split("/")
    original_file = file_split[-1]
    extension = get_extension(original_file)
    files = os.listdir(logs_folder)
    search_file = original_file.replace(f".{extension}", "") + f"_*.{extension}"
    matching_files = [file for file in files if fnmatch.fnmatch(file, search_file) and len(file.replace(original_file.replace(f".{extension}", ""), "").split("_")) == multiplier + 1]
    pattern = re.compile(r'\d+')

    # Extract numbers from each filename and create an array
    numbers_array = [int(pattern.search(file).group()) for file in matching_files if pattern.search(file)]
    files_to_skip = max(numbers_array) if len(numbers_array) > 0 else 0
    return files_to_skip

def get_path(filename, idx, filetype="py", base_folder="."):
    extension = get_extension(filename)
    return "{}/{}.{}".format(base_folder, filename.replace(f".{extension}", "")+"_"+str(idx), filetype)