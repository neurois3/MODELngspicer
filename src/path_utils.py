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

def resolvePath(path:str, extra_aliases=None) -> str:
    """Resolve known aliases and return absolute path."""
    base_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    aliases = {\
            '<APPLICATIONDIR>': base_dir,\
            }
    if extra_aliases:
        aliases.update(extra_aliases)
    for alias, real_path in aliases.items():
        path = path.replace(alias, real_path)
    return os.path.normpath(path).replace('\\', '/')
