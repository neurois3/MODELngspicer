# Copyright (C) 2025 ペE(neurois3)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <https://www.gnu.org/licenses/>.

import os
import subprocess
import shutil

def run(script_name):
    """Executes the ngspice simulation script using 'ngspice_con' command."""

    if shutil.which('ngspice_con') is None:
        print("Error: 'ngspice_con' command not found. Please check your system PATH.")
        return False

    working_dir = os.path.dirname(os.path.abspath(script_name))
    try:
        # Run 'ngspice_con' command in batch mode
        subprocess.run(['ngspice_con', '-b', os.path.basename(script_name)],\
                cwd=working_dir,\
                stdout=subprocess.DEVNULL,\
                stderr=subprocess.DEVNULL,\
                check=True) # Raises CalledProcessError if returncode != 0
        return True

    except subprocess.CalledProcessError as e:
        print("Error: ngspice_con failed to execute properly.")
        print("Return code:", e.returncode)
        return False
