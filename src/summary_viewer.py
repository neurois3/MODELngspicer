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

from PySide6 import QtCore, QtGui, QtWidgets
from PySide6.QtCore import Signal, Slot, Qt
from typing import override
import sys, os

class SummaryViewer(QtWidgets.QTextBrowser):


    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(500, 500)


    def openHtml(self, html_file):
        if not html_file:
            return
        try:
            with open(html_file, 'r', encoding='utf-8') as f:
                html_body = f.read()
                html = f"""
                <html>
                <head>
                  <style>
                    body {{
                        font-family: "Times New Roman", "Times", serif;
                        font-size: 12px;
                        color: #000;
                        background-color: #fff;
                    }}
                    h1, h2 {{
                        margin: 12px 0;
                    }}
                    table {{
                        border-collapse: collapse;
                        width: 100%;
                    }}
                    th, td {{
                        border: 1px solid #ccc;
                        padding: 1px 10px;
                        text-align: left;
                    }}
                    th {{
                        background-color: #f0f0f0;
                    }}
                    img {{
                        max-width: 100%;
                        height: auto;
                    }}
                  </style>
                </head>
                <body>
                {html_body}
                </body>
                </html>
                """
                self.setHtml(html)
                self.setWindowTitle(os.path.basename(html_file))
                self.setSearchPaths([os.path.dirname(os.path.abspath(html_file))])

        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Open Error', f"Failed to open file:\n{e}")
