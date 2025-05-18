import subprocess
import sys
import os

def execute_script(relative_path):
    """
    Executes another Python script using a relative path.

    Args:
        relative_path (str): The relative path to the Python script to execute.
    """
    try:
        # Construct the absolute path to the script
        script_path = os.path.abspath(relative_path)

        # Construct the command to run the script using the same Python interpreter
        command = [sys.executable, script_path]

        # Execute the command
        process = subprocess.Popen(command)

        # Wait for the script to finish
        process.wait()

        if process.returncode == 0:
            print(f"Script '{relative_path}' executed successfully.")
        else:
            print(f"Script '{relative_path}' failed with return code: {process.returncode}")

    except FileNotFoundError:
        print(f"Error: Script not found at '{script_path}'.")
    except Exception as e:
        print(f"An error occurred while executing '{relative_path}': {e}")

if __name__ == "__main__":
    scripts_to_execute = [
        "./tooling/empire_list.py",
        "./tooling/empire_origin_analyser.py",
        "./tooling/empire_system_analyser.py",
        "./tooling/species_analyser.py"
    ]

    for script in scripts_to_execute:
        execute_script(script)