import os
from google.genai import types
from config import MAX_CHARS

schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description="Returns the contents of a specified file as a string. Does not execute files.",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to read, relative to the working directory. Must include the filename. Returns an error if the file is outside the working directory or does not exist.",
            ),
        },
        required=["file_path"]
    ),
)


def get_file_content(working_directory, file_path):
    full_path = os.path.abspath(os.path.join(working_directory, file_path))
    working_directory = os.path.abspath(working_directory)

    if not full_path.startswith(working_directory):
        return f'Error: Cannot read "{file_path}" as it is outside the permitted working directory'
    
    elif not os.path.isfile(full_path):
        return f'Error: File not found or is not a regular file: "{file_path}"'

    else:
        try:
            file_size = os.path.getsize(full_path)

            with open(full_path, "r") as f:
                file_content = ""
                new_file_message = f'[...File "{file_path}" truncated at 10000 characters]'
                
                if file_size > MAX_CHARS:
                    file_content = f.read(MAX_CHARS)
                    file_content += new_file_message
                else:
                    file_content = f.read()
                
                return file_content
        
        except Exception as e:
            return f"Error: {str(e)}"


