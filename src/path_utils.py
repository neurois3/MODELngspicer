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

# Converts a relative file path into an absolute path
def get_absolute_path(current_file:str, relative_path:str) -> str:
    base_dir = os.path.dirname(os.path.abspath(current_file))
    absolute_path = os.path.join(base_dir, relative_path)
    return os.path.abspath(absolute_path)
