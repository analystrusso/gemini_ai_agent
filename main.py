import os
import sys
from dotenv import load_dotenv
from config import WORKING_DIRECTORY
from google import genai
from google.genai import types
from functions.available_functions import available_functions
from functions.get_files_info import get_files_info
from functions.get_file_content import get_file_content
from functions.write_file import write_file
from functions.run_python import run_python_file
from prompts import system_prompt


def main():
    load_dotenv()
    verbose = "--verbose" in sys.argv
    args = []
    for arg in sys.argv[1:]:
        if not arg.startswith("--"):
            args.append(arg)

    if not args:
        print("AI Code Assistant")
        print('\nUsage: python main.py "your prompt here" [--verbose]')
        print('Example: python main.py "How do I fix the calculator?"')
        sys.exit(1)

    api_key = os.environ.get("GEMINI_API_KEY")
    client = genai.Client(api_key=api_key)

    user_prompt = " ".join(args)

    if verbose:
        print(f"User prompt: {user_prompt}\n")

    messages = [
        types.Content(role="user", parts=[types.Part(text=user_prompt)]),
    ]

    counter = 0
    while counter < 20:
        try:
            final_response = generate_content(client, messages, verbose)
            counter += 1
            if final_response != None:
                print("Final response:")
                print(final_response)
                break           
        except Exception as e:
            print(f"Error: problem in generate_content(): {e}") 
            sys.exit(1)



def generate_content(client, messages, verbose):
    response = client.models.generate_content(
        model="gemini-2.0-flash-001",
        contents=messages,
        config=types.GenerateContentConfig(
            tools=[available_functions], system_instruction=system_prompt
        ),
    )

    for candidate in response.candidates:
        messages.append(candidate.content)

    if verbose:
        print("Prompt tokens:", response.usage_metadata.prompt_token_count)
        print("Response tokens:", response.usage_metadata.candidates_token_count)
        
    if not response.function_calls:
        return response.text

    for function_call_part in response.function_calls:
        function_call_result = call_function(function_call_part, verbose)

        if not function_call_result.parts or not function_call_result.parts[0].function_response:
            raise Exception("Invalid function call result structure")
        
        if verbose:
            response_data = function_call_result.parts[0].function_response.response
            if isinstance(response_data, types.FunctionResponse):
                response_data = response_data.response

            if isinstance(response_data, dict):
                result = response_data.get("result", "")
            else:
                result = response_data
          
            if isinstance(result, str) and "STDOUT:" in result and ", STDERR:" in result:
                stdout = result.split("STDOUT:")[1].split(", STDERR:")[0]
                stderr = result.split(", STDERR:")[1]
                if stdout.strip():
                    print(stdout.strip())
                if stderr.strip():
                    print(stderr.strip())
            else:
                print(result)

        messages.append(
        types.Content(
            role="user",
            parts=function_call_result.parts
        )
    )
    




def call_function(function_call_part, verbose=False):
    function_dict = {        
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file, 
        "write_file": write_file
    }

    function_args = dict(function_call_part.args)    
    function_args["working_directory"] = WORKING_DIRECTORY
    target_function = function_dict.get(function_call_part.name)    



    if target_function is not None:
        if verbose:
            print(f"Calling function: {function_call_part.name}({function_args})")
        else:
            print(f" - Calling function: {function_call_part.name}")

        function_result = target_function(**function_args)

        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"result": function_result},
                )
            ],
        )    
    
    else:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_call_part.name,
                    response={"error": f"Unknown function: {function_call_part.name}"},
                )
            ],
        )


if __name__ == "__main__":
    main()
