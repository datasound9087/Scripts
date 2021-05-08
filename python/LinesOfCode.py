import sys
import os
import argparse

verbose_logging = False

FILE_TYPES_LANG_C = ['.c', '.cpp', '.h']
FILE_TYPES_LANG_JAVA = ['.java']
FILE_TYPES_LANG_GLSL = ['.glsl']
FILE_TYPES_LANG_CSHARP = ['.cs']

FILE_GROUPS = [
    'c', 'java', 'glsl', 'c#'
]

def count_file(file, file_types):
    num = 0
    
    file = file.replace("\\", "/")
    ext = file[file.rfind('.'):]
    if(ext in file_types):
        if verbose_logging:
            print("    Counting:", file)

        with open(file, 'r') as f:
            lines = f.readlines()

            for line in lines:
                if(line.strip()):
                    continue             
                num += 1
    return num

def count_dir(path, file_types):
    loc = 0

    if verbose_logging:
        print("Checking path:", path)

    for file in os.listdir(path):
        file = os.path.join(path, file)

        if(os.path.isdir(file)):
            loc += count_dir(file, file_types)
        else:
            loc += count_file(file, file_types)

    return loc

def main():
    parser = argparse.ArgumentParser(description='Count Lines of code in a repo.')
    parser.add_argument('folder', help='Folder of repo')
    parser.add_argument('file_groups', nargs='+', help='Groups of file types to run against')
    parser.add_argument('--verbose', dest='verbose', default=False, action='store_true', help='Enable verbose logging')
    args = parser.parse_args()

    verbose_logging = args.verbose
    
    valid_args = True
    if not os.path.isdir(os.path.realpath(args.folder)):
        print('Invalid repo path')
        valid_args = False

    file_types = []
    for group in args.file_groups:
        if group not in FILE_GROUPS:
            print('Invalid file group:', group)
            valid_args = False
            break
        
        if group == 'c':
            file_types.extend(FILE_TYPES_LANG_C)
        elif group == 'java':
            file_types.extend(FILE_TYPES_LANG_JAVA)
        elif group == 'glsl':
            file_types.extend(FILE_TYPES_LANG_GLSL)
        elif group == 'c#':
            file_types.extend(FILE_TYPES_LANG_CSHARP)

    if valid_args:
        print("Total LOC: ", str(count_dir(args.folder, file_types)))

if __name__ == "__main__":
    main()