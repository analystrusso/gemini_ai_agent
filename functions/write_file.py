import os
from google.genai import types

schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Creates or overwrites a text file within the working directory with the provided content. Creates intermediate directories if they do not exist. Returns a success message with the number of characters written.",    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the file to create or overwrite, relative to the working directory. Must include the filename."
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="The text content to write to the file."
            ),
        },
    ),
)



def write_file(working_directory, file_path, content):
    full_path = os.path.abspath(os.path.join(working_directory, file_path))
    working_directory = os.path.abspath(working_directory)

    if not full_path.startswith(working_directory):
        return f'Error: Cannot write "{file_path}" as it is outside the permitted working directory'
    
    else: 
        try:
            directory = os.path.dirname(full_path)

            if directory:
                os.makedirs(directory, exist_ok=True)

            with open(full_path, "w") as f:
                f.write(content)

            return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'

        except Exception as e:
            return f"Error: {str(e)}"        