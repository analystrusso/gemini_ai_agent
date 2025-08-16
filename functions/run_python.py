import os
import subprocess
from google.genai import types

schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a Python file and returns the output of running the script.",    
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory. Must include the filename and have a .py extension."
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                description="Optional list of command-line arguments to pass to the Python file.",
                items=types.Schema(type=types.Type.STRING)
            ),
        },
        required=["file_path"]    
        ),
)

def run_python_file(working_directory, file_path, args=[]):
    full_path = os.path.abspath(os.path.join(working_directory, file_path))
    working_directory = os.path.abspath(working_directory)

    if not full_path.startswith(working_directory):
        return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
    
    else:
        try: 
            if not os.path.exists(full_path):
                return f'Error: File "{file_path}" not found.'
                
            if not file_path.endswith(".py"):
                return f'Error: "{file_path}" is not a Python file.'
                
            completed_process = subprocess.run(["python", full_path, *args], cwd=working_directory, timeout=30, capture_output=True, text=True)

            if not completed_process.stdout and not completed_process.stderr:
                return "No output produced."
            
            return_string = f"STDOUT:{completed_process.stdout}, STDERR: {completed_process.stderr}"

            if completed_process.returncode != 0:
                return_string += f"Process exited with code {completed_process.returncode}"

            return return_string
        
        except Exception as e:
            return f"Error: executing Python file: {e}"   
            
            