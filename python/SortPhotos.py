import argparse
import os
import pathlib
import shutil
import datetime

OPERATIONS = ['fol_day', 'fol_day_nest']

verbose_logging = False
nest_folders = False

class FileData:
    def __init__(self, path, name):
        self.path = path
        self.name = name

        stat = pathlib.Path(path).stat()
        self.size = stat.st_size
        self.mtime = stat.st_mtime
        self.ctime = stat.st_ctime
        self.atime = stat.st_atime

def is_windows():
    return os.name == 'nt'

def is_linux():
    return not is_windows()

def print_operations():
    print('Valid operations:')
    for o in OPERATIONS:
        print('   ', o)

def is_media_file(file):
    dot = file.rfind('.')
    if dot == -1:
        return
    
    ext = file[dot:]

    return True

def get_media(src_folder):
    files = [f for f in os.listdir(src_folder) if is_media_file(f)]
    file_data = [FileData(os.path.join(src_folder, f), f) for f in files]
    return file_data

def output_media(file, out_path, sub_folder_path):
    full_out_path = os.path.join(out_path, sub_folder_path, file.name)
    if verbose_logging:
        print('Copy', file.path, 'to', full_out_path)
    #shutil.move(file.path, full_out_path)

def sort_folder(photo, out_folder):

    # get date as YYYY-MM-DD
    date = datetime.datetime.fromtimestamp(photo.ctime)
    sub_path = date.strftime("%Y-%m-%d")

    if not os.path.isdir(os.path.join(out_folder, sub_path)):
        if verbose_logging:
            print('Creating sub_path: ', sub_path)
        os.mkdir(os.path.join(out_folder, sub_path))

    output_media(photo, out_folder, sub_path)

def sort_photos(src_folder, operation, out_folder):
    photos = get_media(src_folder)

    operation_func = None
    if operation == OPERATIONS[0]: # fold_day
        print('Sorting into folders by date created...')
        operation_func = sort_folder
    elif operation == OPERATIONS[1] # fol_day_nest
    
    for photo in photos:
        if verbose_logging:
            print('Processing file:', photo.name)
        operation_func(photo, out_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sort photos')
    parser.add_argument('operation', metavar='folders', type=str.lower, help='Sort photos into folders. Operations: fol_day, fol_day_nest')
    parser.add_argument('src_folder', metavar='input', help='Folder of photos to sort')
    parser.add_argument('--out_folder', default=None, help='Output folder (Default: input)')
    parser.add_argument('--verbose', dest='verbose', default=False, action='store_true', help='Enable verbose logging')

    args = parser.parse_args()

    valid_args = True
    if not os.path.isdir(os.path.realpath(args.src_folder)):
        print('Not a valid input folder.')
        valid_args = False
    args.src_folder = os.path.realpath(args.src_folder)

    if not args.out_folder:
        args.out_folder = args.src_folder
    elif not os.path.isdir(os.path.realpath(args.out_folder)):
        args.out_folder = os.path.realpath(args.out_folder)
        print('Creating output directory...')
        os.makedirs(args.out_folder)

    if args.operation not in OPERATIONS:
        print('Not a valid operation.')
        print_operations()
        valid_args = False

    verbose_logging = args.verbose

    if valid_args:
        print('Input dir:', args.src_folder)
        print('Out dir:', args.out_folder)
        print('Running operation:', args.operation)

        sort_photos(args.src_folder, args.operation, args.out_folder)

