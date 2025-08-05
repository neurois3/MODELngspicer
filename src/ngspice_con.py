import sys, os
import subprocess

def run(scriptname):
    """ Executes the Ngspice simulation script using the 'ngspice_con' command.

    This function locates the simulation script's directory, runs Ngspice in batch mode, 
    and captures both standard output and error streams for debugging purposes.

    Args:
        scriptname (str): Path to the Ngspice simulation script.
    """
    try:
        # Determine the working directory of the script
        workingdir = os.path.dirname(os.path.abspath(scriptname))

        # Run the 'ngspice_con' command in batch mode
        subprocess.run(['ngspice_con', '-b', os.path.basename(scriptname)],\
                cwd=workingdir,\
                stdout=subprocess.PIPE,\
                stderr=subprocess.PIPE,\
                text=True,\
                check=True) # Raises CalledProcessError if returncode != 0

    except FileNotFoundError:
        print('Error: \'ngspice_con\' command not found. Please check your system PATH.')

    except subprocess.CalledProcessError as e:
        print('Error: ngspice_con failed to execute properly.')
        print('stderr:', e.stderr)
