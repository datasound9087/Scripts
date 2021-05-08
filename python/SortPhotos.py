import argparse
import os
import pathlib
import shutil
import datetime

OP_NUM_DAY = 'num_day'
OP_NUM_DAY_NEST = 'num_day_nest'
OP_NUM_MONTH = 'num_month'
OP_NUM_MONTH_NEST = 'num_month_nest'
OP_NUM_YEAR = 'num_year'

OP_NAMED_MONTH_DAY = 'named_month_day'
OP_NAMED_MONTH_FORMATTED_DAY = 'named_month_formatted_day'

OPERATIONS = [
    OP_NUM_DAY,
    OP_NUM_DAY_NEST,
    OP_NUM_MONTH,
    OP_NUM_MONTH_NEST,
    OP_NUM_YEAR,
    OP_NAMED_MONTH_DAY,
    OP_NAMED_MONTH_FORMATTED_DAY
]

verbose_logging = False

# Data about each file including metadata
class FileData:
    def __init__(self, path, name):
        self.path = path
        self.name = name

        stat = pathlib.Path(path).stat()
        self.size = stat.st_size
        self.mtime = stat.st_mtime
        self.ctime = stat.st_ctime
        self.atime = stat.st_atime

        self.cdate = datetime.datetime.fromtimestamp(self.ctime)

def print_operations():
    print('Valid operations:')
    for o in OPERATIONS:
        print('   ', o, '\n')

def is_media_file(file):
    dot = file.rfind('.')
    if dot == -1:
        return
    
    ext = file[dot:]
    # todo: decide using file extensions
    return True

def get_media(src_folder):
    files = [f for f in os.listdir(src_folder) if is_media_file(f)]
    file_data = [FileData(os.path.join(src_folder, f), f) for f in files]
    return file_data

def output_media(file, out_path, sub_folder_path):
    full_out_path = os.path.join(out_path, sub_folder_path, file.name)
    if verbose_logging:
        print('Copy', file.path, 'to', full_out_path)
    shutil.move(file.path, full_out_path)

def create_dirs_if_not_exist(start_path, sub_path):
    if not os.path.isdir(os.path.join(start_path, sub_path)):
        if verbose_logging:
            print('Creating sub path: ', sub_path)
        os.makedirs(os.path.join(start_path, sub_path))

def sort_folder_named_month_formatted_day(photo, out_folder):
    month_name = photo.cdate.strftime("%B")
    day_postfix = 'th'

    if photo.cdate.day in [1, 21, 31]:
        day_postfix = 'st'
    elif photo.cdate.day in [2, 22]:
        day_postfix = 'nd'
    elif photo.cdate.day in [3, 23]:
        day_postfix = 'rd'
    
    sub_path = os.path.join(str(photo.cdate.year), month_name, f"{photo.cdate.day}{day_postfix}")
    create_dirs_if_not_exist(out_folder, sub_path)
    output_media(photo, out_folder, sub_path)

def sort_folder_named_month_day(photo, out_folder):
    month_name = photo.cdate.strftime("%B")
    month_day = photo.cdate.strftime("%A")
    sub_path = os.path.join(str(photo.cdate.year), month_name, month_day)

    create_dirs_if_not_exist(out_folder, sub_path)
    output_media(photo, out_folder, sub_path)

def sort_folder_num_year(photo, out_folder):
    sub_path = str(photo.cdate.year)
    create_dirs_if_not_exist(out_folder, sub_path)
    output_media(photo, out_folder, sub_path)

def sort_folder_num_day(photo, out_folder, nest=False):
    sub_path = photo.cdate.strftime("%Y-%m-%d")
    if nest:
        sub_path = os.path.join(str(photo.cdate.year), str(photo.cdate.month), str(photo.cdate.day))

    create_dirs_if_not_exist(out_folder, sub_path)
    output_media(photo, out_folder, sub_path)

def sort_folder_num_month(photo, out_folder, nest=False):
    sub_path = photo.cdate.strftime("%Y-%m")
    if nest:
        sub_path = os.path.join(str(photo.cdate.year), str(photo.cdate.month))

    create_dirs_if_not_exist(out_folder, sub_path)
    output_media(photo, out_folder, sub_path)

def sort_photos(src_folder, operation, out_folder):
    photos = get_media(src_folder)
    
    # select function for operation
    operation_func = None
    if operation == OP_NUM_DAY:
        operation_func = sort_folder_num_day
    elif operation == OP_NUM_DAY_NEST:
        operation_func = lambda photo, out_folder: sort_folder_num_day(photo, out_folder, nest=True)

    elif operation == OP_NUM_YEAR:
        operation_func = sort_folder_num_year

    elif operation == OP_NAMED_MONTH_DAY:
        operation_func = sort_folder_named_month_day

    elif operation == OP_NAMED_MONTH_FORMATTED_DAY:
        operation_func = sort_folder_named_month_formatted_day

    elif operation == OP_NUM_MONTH:
        operation_func = sort_folder_num_month
    elif operation == OP_NUM_MONTH_NEST: 
        operation_func = lambda photo, out_folder: sort_folder_num_month(photo, out_folder, nest=True)

    for photo in photos:
        if verbose_logging:
            print('Processing file:', photo.name)
        operation_func(photo, out_folder)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Sort photos')
    parser.add_argument('operation', metavar='folders', type=str.lower, help='Sorting peration to do.')
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

