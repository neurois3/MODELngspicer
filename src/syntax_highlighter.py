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
import re

from ui_manager import UIManager

class SyntaxHighlighter(QtGui.QSyntaxHighlighter):


    def __init__(self, parent):
        super().__init__(parent)
        self.__rules = []
        self.__multiline_rules = []

        self.update_theme()
        ui_manager = UIManager()
        ui_manager.themeChanged.connect(self.update_theme)
    

    def add_rule(self, expression, format_):
        self.__rules.append((expression, format_))


    def add_multiline_rule(self, start, stop, format_):
        self.__multiline_rules.append((start, stop, format_))


    def clear(self):
        self.__rules.clear()
        self.__multiline_rules.clear()


    def highlight_keywords(self, text):
        for (expression, format_) in self.__rules:
            for match in re.finditer(expression, text):
                start, end = match.span()
                if self.format(start) != QtGui.QTextCharFormat():
                    continue
                self.setFormat(start, end - start, format_)


    def highlight_multiline(self, text):
        block_state = self.previousBlockState()
        start_index = 0
        index = 0
        while index < len(text):
            if block_state == -1:
                match_result = False
                for i, (start, stop, format_) in enumerate(self.__multiline_rules):
                    # Regular expression
                    for match in re.finditer(start, text):
                        if index == match.start():
                            start_index = index
                            index += match.end() - match.start()
                            match_result = True
                            break
                    if match_result:
                        block_state = i
                        break
                if not match_result:
                    index += 1
            else:
                start, stop, format_ = self.__multiline_rules[block_state]
                match = re.match(stop, text[index:])
                if match:
                    index += match.end()
                    length = index - start_index
                    self.setFormat(start_index, length, format_)
                    block_state = -1
                else:
                    index += 1

        if block_state != -1:
            start, stop, format_ = self.__multiline_rules[block_state]
            length = len(text) - start_index
            self.setFormat(start_index, length, format_)

        self.setCurrentBlockState(block_state)


    @override
    def highlightBlock(self, text):
        self.highlight_multiline(text)
        self.highlight_keywords(text)

        # Whitespace characters
        for match in re.finditer(r'\s', text):
            start, end = match.span()
            self.setFormat(start, end - start, self.whitespace_format)


    def refresh_rules(self):
        pass


    @Slot()
    def update_theme(self):
        ui_manager = UIManager()

        # Update colors
        if ui_manager.theme == 'Light':
            # Strings
            self.string_format = QtGui.QTextCharFormat()
            self.string_format.setForeground(QtGui.QColor('#665295'))
            # Comments
            self.comment_format = QtGui.QTextCharFormat()
            self.comment_format.setForeground(QtGui.QColor('#777777'))
            self.comment_format.setFontItalic(True)
            # Functions
            self.function_format = QtGui.QTextCharFormat()
            self.function_format.setForeground(QtGui.QColor('#052f85'))
            # Numbers
            self.number_format = QtGui.QTextCharFormat()
            self.number_format.setForeground(QtGui.QColor('#3095b3'))
            # Keywords
            self.keyword_format = QtGui.QTextCharFormat()
            self.keyword_format.setForeground(QtGui.QColor('#7e6840'))
            # Whitespace characters
            self.whitespace_format = QtGui.QTextCharFormat()
            self.whitespace_format.setForeground(QtGui.QColor('#d9d9d9'))
        else:
            # Strings
            self.string_format = QtGui.QTextCharFormat()
            self.string_format.setForeground(QtGui.QColor('#99ad6a'))
            # Comments
            self.comment_format = QtGui.QTextCharFormat()
            self.comment_format.setForeground(QtGui.QColor('#888888'))
            self.comment_format.setFontItalic(True)
            # Functions
            self.function_format = QtGui.QTextCharFormat()
            self.function_format.setForeground(QtGui.QColor('#fad07a'))
            # Numbers
            self.number_format = QtGui.QTextCharFormat()
            self.number_format.setForeground(QtGui.QColor('#cf6a4c'))
            # Keywords
            self.keyword_format = QtGui.QTextCharFormat()
            self.keyword_format.setForeground(QtGui.QColor('#8a97bf'))
            # Whitespace characters
            self.whitespace_format = QtGui.QTextCharFormat()
            self.whitespace_format.setForeground(QtGui.QColor('#262626'))

        # Refresh syntax rules
        self.refresh_rules()

        # Redraw
        self.rehighlight()



class SyntaxHighlighter_Python(SyntaxHighlighter):


    @override
    def refresh_rules(self):
        self.clear()

        # Strings
        self.add_multiline_rule("'''", "'''", self.string_format)
        self.add_multiline_rule('"""', '"""', self.string_format)
        self.add_multiline_rule("'", "'", self.string_format)
        self.add_multiline_rule('"', '"', self.string_format)

        # Comments
        self.add_rule(r'#.*$', self.comment_format)

        # Spectial methods: e.g. __name__
        self.add_rule(r'\b__\w+__\b', self.function_format)

        # Decorators: e.g. @staticmethod
        self.add_rule(r'@\w+', self.function_format)

        # Class definitions: class <class name>
        self.add_rule(r'(?<=class\s)\w+', self.function_format)

        # Function definitions: def <function name>
        self.add_rule(r'(?<=def\s)\w+', self.function_format)

        # Built-in constants
        self.add_rule(r'\bFalse\b', self.function_format)
        self.add_rule(r'\bTrue\b', self.function_format)
        self.add_rule(r'\bNone\b', self.function_format)
        self.add_rule(r'\bNotImplemented\b', self.function_format)
        self.add_rule(r'\bEllipsis\b', self.function_format)

        # Built-in functions
        self.add_rule(r'\babs\b', self.function_format)
        self.add_rule(r'\baiter\b', self.function_format)
        self.add_rule(r'\ball\b', self.function_format)
        self.add_rule(r'\banext\b', self.function_format)
        self.add_rule(r'\bany\b', self.function_format)
        self.add_rule(r'\bascii\b', self.function_format)
        self.add_rule(r'\bbin\b', self.function_format)
        self.add_rule(r'\bbool\b', self.function_format)
        self.add_rule(r'\bbreakpoint\b', self.function_format)
        self.add_rule(r'\bbytearray\b', self.function_format)
        self.add_rule(r'\bbytes\b', self.function_format)
        self.add_rule(r'\bcallable\b', self.function_format)
        self.add_rule(r'\bchr\b', self.function_format)
        self.add_rule(r'\bclassmethod\b', self.function_format)
        self.add_rule(r'\bcompile\b', self.function_format)
        self.add_rule(r'\bcomplex\b', self.function_format)
        self.add_rule(r'\bdelattr\b', self.function_format)
        self.add_rule(r'\bdict\b', self.function_format)
        self.add_rule(r'\bdir\b', self.function_format)
        self.add_rule(r'\bdivmod\b', self.function_format)
        self.add_rule(r'\benumerate\b', self.function_format)
        self.add_rule(r'\beval\b', self.function_format)
        self.add_rule(r'\bexec\b', self.function_format)
        self.add_rule(r'\bfilter\b', self.function_format)
        self.add_rule(r'\bfloat\b', self.function_format)
        self.add_rule(r'\bformat\b', self.function_format)
        self.add_rule(r'\bfrozenset\b', self.function_format)
        self.add_rule(r'\bgetattr\b', self.function_format)
        self.add_rule(r'\bglobals\b', self.function_format)
        self.add_rule(r'\bhasattr\b', self.function_format)
        self.add_rule(r'\bhash\b', self.function_format)
        self.add_rule(r'\bhelp\b', self.function_format)
        self.add_rule(r'\bhex\b', self.function_format)
        self.add_rule(r'\bid\b', self.function_format)
        self.add_rule(r'\binput\b', self.function_format)
        self.add_rule(r'\bint\b', self.function_format)
        self.add_rule(r'\bisinstance\b', self.function_format)
        self.add_rule(r'\bissubclass\b', self.function_format)
        self.add_rule(r'\biter\b', self.function_format)
        self.add_rule(r'\blen\b', self.function_format)
        self.add_rule(r'\blist\b', self.function_format)
        self.add_rule(r'\blocals\b', self.function_format)
        self.add_rule(r'\bmap\b', self.function_format)
        self.add_rule(r'\bmax\b', self.function_format)
        self.add_rule(r'\bmemoryview\b', self.function_format)
        self.add_rule(r'\bmin\b', self.function_format)
        self.add_rule(r'\bnext\b', self.function_format)
        self.add_rule(r'\bobject\b', self.function_format)
        self.add_rule(r'\boct\b', self.function_format)
        self.add_rule(r'\bopen\b', self.function_format)
        self.add_rule(r'\bord\b', self.function_format)
        self.add_rule(r'\bpow\b', self.function_format)
        self.add_rule(r'\bprint\b', self.function_format)
        self.add_rule(r'\bproperty\b', self.function_format)
        self.add_rule(r'\brange\b', self.function_format)
        self.add_rule(r'\brepr\b', self.function_format)
        self.add_rule(r'\breversed\b', self.function_format)
        self.add_rule(r'\bround\b', self.function_format)
        self.add_rule(r'\bset\b', self.function_format)
        self.add_rule(r'\bsetattr\b', self.function_format)
        self.add_rule(r'\bslice\b', self.function_format)
        self.add_rule(r'\bsorted\b', self.function_format)
        self.add_rule(r'\bstaticmethod\b', self.function_format)
        self.add_rule(r'\bstr\b', self.function_format)
        self.add_rule(r'\bsum\b', self.function_format)
        self.add_rule(r'\bsuper\b', self.function_format)
        self.add_rule(r'\btuple\b', self.function_format)
        self.add_rule(r'\btype\b', self.function_format)
        self.add_rule(r'\bvars\b', self.function_format)
        self.add_rule(r'\bzip\b', self.function_format)

        # Numbers
        self.add_rule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', self.number_format)
        self.add_rule(r'\b0[xX][0-9a-fA-F]+\b', self.number_format)
        self.add_rule(r'\b0[oO][0-7]+\b', self.number_format)
        self.add_rule(r'\b0[bB][0-1]+\b', self.number_format)

        # Keywords
        self.add_rule(r'\band\b', self.keyword_format)
        self.add_rule(r'\bas\b', self.keyword_format)
        self.add_rule(r'\bassert\b', self.keyword_format)
        self.add_rule(r'\basync\b', self.keyword_format)
        self.add_rule(r'\bawait\b', self.keyword_format)
        self.add_rule(r'\bbreak\b', self.keyword_format)
        self.add_rule(r'\bclass\b', self.keyword_format)
        self.add_rule(r'\bcontinue\b', self.keyword_format)
        self.add_rule(r'\bdef\b', self.keyword_format)
        self.add_rule(r'\bdel\b', self.keyword_format)
        self.add_rule(r'\belif\b', self.keyword_format)
        self.add_rule(r'\belse\b', self.keyword_format)
        self.add_rule(r'\bexcept\b', self.keyword_format)
        self.add_rule(r'\bfinally\b', self.keyword_format)
        self.add_rule(r'\bfor\b', self.keyword_format)
        self.add_rule(r'\bfrom\b', self.keyword_format)
        self.add_rule(r'\bglobal\b', self.keyword_format)
        self.add_rule(r'\bif\b', self.keyword_format)
        self.add_rule(r'\bimport\b', self.keyword_format)
        self.add_rule(r'\bin\b', self.keyword_format)
        self.add_rule(r'\bis\b', self.keyword_format)
        self.add_rule(r'\blambda\b', self.keyword_format)
        self.add_rule(r'\bnonlocal\b', self.keyword_format)
        self.add_rule(r'\bnot\b', self.keyword_format)
        self.add_rule(r'\bor\b', self.keyword_format)
        self.add_rule(r'\bpass\b', self.keyword_format)
        self.add_rule(r'\braise\b', self.keyword_format)
        self.add_rule(r'\breturn\b', self.keyword_format)
        self.add_rule(r'\btry\b', self.keyword_format)
        self.add_rule(r'\bwhile\b', self.keyword_format)
        self.add_rule(r'\bwith\b', self.keyword_format)
        self.add_rule(r'\byield\b', self.keyword_format)




class SyntaxHighlighter_Matlab_Octave(SyntaxHighlighter):


    @override
    def refresh_rules(self):
        self.clear()

        # Strings
        self.add_multiline_rule(r"(?<=[^\)\]\}a-zA-Z_0-9])'", r"'", self.string_format)
        self.add_multiline_rule(r'"', r'"', self.string_format)

        # Comments
        self.add_rule(r'%.*$', self.comment_format)
        self.add_multiline_rule('%{', '%}', self.comment_format)

        # Built-in functions
        self.add_rule(r'\berror\b', self.function_format)
        self.add_rule(r'\bwarning\b', self.function_format)
        self.add_rule(r'\bsize\b', self.function_format)
        self.add_rule(r'\bclear\b', self.function_format)
        self.add_rule(r'\breshape\b', self.function_format)
        self.add_rule(r'\beye\b', self.function_format)
        self.add_rule(r'\bones\b', self.function_format)
        self.add_rule(r'\bzeros\b', self.function_format)
        self.add_rule(r'\blinspace\b', self.function_format)
        self.add_rule(r'\blogspace\b', self.function_format)
        self.add_rule(r'\brand\b', self.function_format)
        self.add_rule(r'\bexp\b', self.function_format)
        self.add_rule(r'\blog\b', self.function_format)
        self.add_rule(r'\blog10\b', self.function_format)
        self.add_rule(r'\bsqrt\b', self.function_format)
        self.add_rule(r'\babs\b', self.function_format)
        self.add_rule(r'\barg\b', self.function_format)
        self.add_rule(r'\bconj\b', self.function_format)
        self.add_rule(r'\bimag\b', self.function_format)
        self.add_rule(r'\breal\b', self.function_format)
        self.add_rule(r'\bsin\b', self.function_format)
        self.add_rule(r'\bcos\b', self.function_format)
        self.add_rule(r'\btan\b', self.function_format)
        self.add_rule(r'\basin\b', self.function_format)
        self.add_rule(r'\bacos\b', self.function_format)
        self.add_rule(r'\batan\b', self.function_format)
        self.add_rule(r'\batan2\b', self.function_format)
        self.add_rule(r'\bsinh\b', self.function_format)
        self.add_rule(r'\bcosh\b', self.function_format)
        self.add_rule(r'\btanh\b', self.function_format)
        self.add_rule(r'\basinh\b', self.function_format)
        self.add_rule(r'\bacosh\b', self.function_format)
        self.add_rule(r'\batanh\b', self.function_format)
        self.add_rule(r'\bsum\b', self.function_format)
        self.add_rule(r'\bprod\b', self.function_format)
        self.add_rule(r'\bceil\b', self.function_format)
        self.add_rule(r'\bfloor\b', self.function_format)
        self.add_rule(r'\bround\b', self.function_format)
        self.add_rule(r'\bmax\b', self.function_format)
        self.add_rule(r'\bmin\b', self.function_format)
        self.add_rule(r'\bsign\b', self.function_format)
        self.add_rule(r'\bmean\b', self.function_format)
        self.add_rule(r'\bstd\b', self.function_format)
        self.add_rule(r'\bcov\b', self.function_format)

        # Numbers
        self.add_rule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', self.number_format)
        self.add_rule(r'\b0[xX][0-9a-fA-F]+\b', self.number_format)
        self.add_rule(r'\b0[oO][0-7]+\b', self.number_format)
        self.add_rule(r'\b0[bB][0-1]+\b', self.number_format)

        # Keywords
        self.add_rule(r'\b__FILE__\b', self.keyword_format)
        self.add_rule(r'\b__LINE__\b', self.keyword_format)
        self.add_rule(r'\bbreak\b', self.keyword_format)
        self.add_rule(r'\bcase\b', self.keyword_format)
        self.add_rule(r'\bcatch\b', self.keyword_format)
        self.add_rule(r'\bclassdef\b', self.keyword_format)
        self.add_rule(r'\bcontinue\b', self.keyword_format)
        self.add_rule(r'\bdo\b', self.keyword_format)
        self.add_rule(r'\belse\b', self.keyword_format)
        self.add_rule(r'\belseif\b', self.keyword_format)
        self.add_rule(r'\bend\b', self.keyword_format)
        self.add_rule(r'\bend_try_catch\b', self.keyword_format)
        self.add_rule(r'\bend_unwind_protect\b', self.keyword_format)
        self.add_rule(r'\bendclassdef\b', self.keyword_format)
        self.add_rule(r'\bendenumeration\b', self.keyword_format)
        self.add_rule(r'\bendevents\b', self.keyword_format)
        self.add_rule(r'\bendfor\b', self.keyword_format)
        self.add_rule(r'\bendfunction\b', self.keyword_format)
        self.add_rule(r'\bendif\b', self.keyword_format)
        self.add_rule(r'\bendmethods\b', self.keyword_format)
        self.add_rule(r'\bendparfor\b', self.keyword_format)
        self.add_rule(r'\bendproperties\b', self.keyword_format)
        self.add_rule(r'\bendswitch\b', self.keyword_format)
        self.add_rule(r'\bendwhile\b', self.keyword_format)
        self.add_rule(r'\benumeration\b', self.keyword_format)
        self.add_rule(r'\bevents\b', self.keyword_format)
        self.add_rule(r'\bfor\b', self.keyword_format)
        self.add_rule(r'\bfunction\b', self.keyword_format)
        self.add_rule(r'\bglobal\b', self.keyword_format)
        self.add_rule(r'\bif\b', self.keyword_format)
        self.add_rule(r'\bmethods\b', self.keyword_format)
        self.add_rule(r'\botherwise\b', self.keyword_format)
        self.add_rule(r'\bparfor\b', self.keyword_format)
        self.add_rule(r'\bpersistent\b', self.keyword_format)
        self.add_rule(r'\bproperties\b', self.keyword_format)
        self.add_rule(r'\breturn\b', self.keyword_format)
        self.add_rule(r'\bswitch\b', self.keyword_format)
        self.add_rule(r'\btry\b', self.keyword_format)
        self.add_rule(r'\buntil\b', self.keyword_format)
        self.add_rule(r'\bunwind_protect\b', self.keyword_format)
        self.add_rule(r'\bunwind_protect_cleanup\b', self.keyword_format)
        self.add_rule(r'\bwhile\b', self.keyword_format)




class SyntaxHighlighter_SPICE(SyntaxHighlighter):


    @override
    def refresh_rules(self):
        self.clear()

        # Strings
        self.add_multiline_rule(r"'", r"'", self.string_format)
        self.add_multiline_rule(r'"', r'"', self.string_format)

        # Comments
        self.add_rule(r'^\*.*$', self.comment_format)
        self.add_rule(r'\$.*$', self.comment_format)

        # Numbers
        self.add_rule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?(?:[TGMKmunpf]|Meg|MEG)?\b',\
                self.number_format)

        # Keywords
        self.add_rule(r'(?<!\w)\.[a-zA-Z_]+', self.keyword_format)
