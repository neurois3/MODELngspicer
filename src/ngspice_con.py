import os
import subprocess
import shutil

def run(script_filename):
    """ Executes the ngspice simulation script using 'ngspice_con' command. """
    if shutil.which('ngspice_con') is None:
        print("Error: 'ngspice_con' command not found. Please check your system PATH.")
        return False

    working_dir = os.path.dirname(os.path.abspath(script_filename))
    try:
        # Run 'ngspice_con' command in batch mode
        subprocess.run(['ngspice_con', '-b', os.path.basename(script_filename)],\
                cwd=working_dir,\
                stdout=subprocess.DEVNULL,\
                stderr=subprocess.DEVNULL,\
                check=True) # Raises CalledProcessError if returncode != 0
        return True

    except subprocess.CalledProcessError as e:
        print("Error: ngspice_con failed to execute properly.")
        print("Return code:", e.returncode)
        return False
