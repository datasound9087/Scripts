from genericpath import isfile
import os
import os.path as path
import pathlib
import subprocess
import argparse
import sys

GLSL_COMPILER = "glslangValidator"
VALID_SHADER_EXTENSIONS = [
    ".vert", ".tesc", ".tese", ".geom", ".frag", ".comp",
    ".rgen", ".rint", ".rahit", ".rchit", ".rmiss", ".rcall"
]

verbose_output = False

def is_valid_shader_file(folder_path, filename):
    valid = path.isfile(path.join(folder_path, filename))
    if not valid:
        return False
    
    return pathlib.Path(path.join(folder_path, filename)).suffix in VALID_SHADER_EXTENSIONS

def find_shaders(folder_path):
    files = [f for f in os.listdir(folder_path) if is_valid_shader_file(folder_path, f)]
    if not files:
        print(f"No shaders found in directory: {folder_path}")
    return files

def compile_shaders(compiler, folder_path, shader_files):
    result = 0
    for shader in shader_files:
        result = compile_shader(compiler, folder_path, shader)
        if result != 0:
            print(f"!!! ERROR compiling {shader} !!!")
            break
    return result

def compile_shader(compiler, folder_path, shader):
    shaderPath = pathlib.Path(path.join(folder_path, shader))
    if verbose_output:
        print(f"Compiling {shaderPath.relative_to(folder_path)}")

    shaderPath = shaderPath.resolve()
    output_file = path.join(folder_path, shaderPath.name + ".spv")
    if path.exists(output_file):
        os.remove(output_file)

    commandline = [
        compiler,
        "--Quiet", # Suppress output unless there's an error
        "-V", # Create SPIR-V binary
        str(shaderPath.absolute()),
        "-o", # output file
        output_file
    ]

    if verbose_output:
        print(commandline)

    result = call_compiler(commandline)

    return result

def call_compiler(commandline):
    result = subprocess.run(commandline, shell = True, stdout = sys.stdout, stderr = subprocess.STDOUT)
    return result.returncode

def main(folder_path):
    vulkan_sdk = os.environ["VULKAN_SDK"]
    if vulkan_sdk is None:
        print("Cannot find vulkan SDK.")
        return
    
    file_extension = ".exe" if os.name == "nt" else ""
    compiler = path.join(vulkan_sdk, "Bin", GLSL_COMPILER + file_extension)
    if not path.exists(compiler) or not path.isfile(compiler):
        print(f"Compiler {GLSL_COMPILER} not found at {compiler}.")
        return
    
    if verbose_output:
        print(f"Compiler found: {compiler}")

    shader_files = find_shaders(folder_path)
    result = compile_shaders(compiler, folder_path, shader_files)
    if result != 0:
        print("Compiling Finished with errors.")
        exit(2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Compile folder of shaders.")
    parser.add_argument("-f", "--folder", type = str, required = True, help = "Folder containing shaders to comoile.")
    parser.add_argument("--verbose", action = argparse.BooleanOptionalAction, help = "Enable verbose output.")
    args = parser.parse_args()
    verbose_output = args.verbose

    folder_path = args.folder
    if not path.exists(args.folder):
        folder_path = path.join(os.getcwd(), folder_path)
        if not path.exists(folder_path):
            print(f"Cannot find path: {folder_path}")
            exit(1)
    
    if path.isfile(folder_path):
        print(f"{folder_path} is not a folder")
        exit(1)
    
    if verbose_output:
        print(f"Using folder: {folder_path}")
        
main(folder_path)