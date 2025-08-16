import os
from google.genai import types

schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in the specified directory along with their sizes, constrained to the working directory.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="The directory to list files from, relative to the working directory. If not provided, lists files in the working directory itself.",
            ),
        },
    ),
)


def get_files_info(working_directory, directory="."):
    full_path = os.path.abspath(os.path.join(working_directory, directory))
    base_path = os.path.abspath(working_directory)

    if not full_path.startswith(base_path):
        return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'
    
    elif not os.path.isdir(full_path):
        return f'Error: "{directory}" is not a directory'
    
    else:
        try:
            final_string_list = []
        
            for file in os.listdir(full_path):
                file_path = os.path.join(full_path, file)
                is_directory = os.path.isdir(file_path)
                file_size = os.path.getsize(file_path)
            
                template = f"- {file}: file_size={file_size} bytes, is_dir={is_directory}"
                final_string_list.append(template)

            result = "\n".join(final_string_list)

            return result
        
        except Exception as e:
            return f"Error: {str(e)}"

            
            