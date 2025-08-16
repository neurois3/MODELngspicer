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


class SyntaxHighlighter(QtGui.QSyntaxHighlighter):


    def __init__(self, parent):
        super().__init__(parent)
        self.__rules = []
        self.__multiline_rules = []
    

    def add_rule(self, expression, format_):
        self.__rules.append((expression, format_))


    def add_multiline_rule(self, start, stop, format_):
        self.__multiline_rules.append((start, stop, format_))


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

        # Whitespaces
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#262626'))
        for match in re.finditer(r'\s', text):
            start, end = match.span()
            self.setFormat(start, end - start, format_)




class SyntaxHighlighter_Python(SyntaxHighlighter):

    def __init__(self, parent):
        super().__init__(parent)

        # Strings
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#99ad6a'))
        self.add_multiline_rule("'''", "'''", format_)
        self.add_multiline_rule('"""', '"""', format_)
        self.add_multiline_rule("'", "'", format_)
        self.add_multiline_rule('"', '"', format_)

        # Comments
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#888888'))
        format_.setFontItalic(True)
        self.add_rule(r'#.*$', format_)

        # Spectial methods: e.g. __name__
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#fad07a'))
        self.add_rule(r'\b__\w+__\b', format_)

        # Decorators: e.g. @staticmethod
        self.add_rule(r'@\w+', format_)

        # Class definitions: class <class name>
        self.add_rule(r'(?<=class\s)\w+', format_)

        # Function definitions: def <function name>
        self.add_rule(r'(?<=def\s)\w+', format_)

        # Built-in constants
        self.add_rule(r'\bFalse\b', format_)
        self.add_rule(r'\bTrue\b', format_)
        self.add_rule(r'\bNone\b', format_)
        self.add_rule(r'\bNotImplemented\b', format_)
        self.add_rule(r'\bEllipsis\b', format_)

        # Built-in functions
        self.add_rule(r'\babs\b', format_)
        self.add_rule(r'\baiter\b', format_)
        self.add_rule(r'\ball\b', format_)
        self.add_rule(r'\banext\b', format_)
        self.add_rule(r'\bany\b', format_)
        self.add_rule(r'\bascii\b', format_)
        self.add_rule(r'\bbin\b', format_)
        self.add_rule(r'\bbool\b', format_)
        self.add_rule(r'\bbreakpoint\b', format_)
        self.add_rule(r'\bbytearray\b', format_)
        self.add_rule(r'\bbytes\b', format_)
        self.add_rule(r'\bcallable\b', format_)
        self.add_rule(r'\bchr\b', format_)
        self.add_rule(r'\bclassmethod\b', format_)
        self.add_rule(r'\bcompile\b', format_)
        self.add_rule(r'\bcomplex\b', format_)
        self.add_rule(r'\bdelattr\b', format_)
        self.add_rule(r'\bdict\b', format_)
        self.add_rule(r'\bdir\b', format_)
        self.add_rule(r'\bdivmod\b', format_)
        self.add_rule(r'\benumerate\b', format_)
        self.add_rule(r'\beval\b', format_)
        self.add_rule(r'\bexec\b', format_)
        self.add_rule(r'\bfilter\b', format_)
        self.add_rule(r'\bfloat\b', format_)
        self.add_rule(r'\bformat\b', format_)
        self.add_rule(r'\bfrozenset\b', format_)
        self.add_rule(r'\bgetattr\b', format_)
        self.add_rule(r'\bglobals\b', format_)
        self.add_rule(r'\bhasattr\b', format_)
        self.add_rule(r'\bhash\b', format_)
        self.add_rule(r'\bhelp\b', format_)
        self.add_rule(r'\bhex\b', format_)
        self.add_rule(r'\bid\b', format_)
        self.add_rule(r'\binput\b', format_)
        self.add_rule(r'\bint\b', format_)
        self.add_rule(r'\bisinstance\b', format_)
        self.add_rule(r'\bissubclass\b', format_)
        self.add_rule(r'\biter\b', format_)
        self.add_rule(r'\blen\b', format_)
        self.add_rule(r'\blist\b', format_)
        self.add_rule(r'\blocals\b', format_)
        self.add_rule(r'\bmap\b', format_)
        self.add_rule(r'\bmax\b', format_)
        self.add_rule(r'\bmemoryview\b', format_)
        self.add_rule(r'\bmin\b', format_)
        self.add_rule(r'\bnext\b', format_)
        self.add_rule(r'\bobject\b', format_)
        self.add_rule(r'\boct\b', format_)
        self.add_rule(r'\bopen\b', format_)
        self.add_rule(r'\bord\b', format_)
        self.add_rule(r'\bpow\b', format_)
        self.add_rule(r'\bprint\b', format_)
        self.add_rule(r'\bproperty\b', format_)
        self.add_rule(r'\brange\b', format_)
        self.add_rule(r'\brepr\b', format_)
        self.add_rule(r'\breversed\b', format_)
        self.add_rule(r'\bround\b', format_)
        self.add_rule(r'\bset\b', format_)
        self.add_rule(r'\bsetattr\b', format_)
        self.add_rule(r'\bslice\b', format_)
        self.add_rule(r'\bsorted\b', format_)
        self.add_rule(r'\bstaticmethod\b', format_)
        self.add_rule(r'\bstr\b', format_)
        self.add_rule(r'\bsum\b', format_)
        self.add_rule(r'\bsuper\b', format_)
        self.add_rule(r'\btuple\b', format_)
        self.add_rule(r'\btype\b', format_)
        self.add_rule(r'\bvars\b', format_)
        self.add_rule(r'\bzip\b', format_)

        # Numbers
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#cf6a4c'))
        self.add_rule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', format_)
        self.add_rule(r'\b0[xX][0-9a-fA-F]+\b', format_)
        self.add_rule(r'\b0[oO][0-7]+\b', format_)
        self.add_rule(r'\b0[bB][0-1]+\b', format_)

        # Keywords
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#8197bf'))
        self.add_rule(r'\band\b', format_)
        self.add_rule(r'\bas\b', format_)
        self.add_rule(r'\bassert\b', format_)
        self.add_rule(r'\basync\b', format_)
        self.add_rule(r'\bawait\b', format_)
        self.add_rule(r'\bbreak\b', format_)
        self.add_rule(r'\bclass\b', format_)
        self.add_rule(r'\bcontinue\b', format_)
        self.add_rule(r'\bdef\b', format_)
        self.add_rule(r'\bdel\b', format_)
        self.add_rule(r'\belif\b', format_)
        self.add_rule(r'\belse\b', format_)
        self.add_rule(r'\bexcept\b', format_)
        self.add_rule(r'\bfinally\b', format_)
        self.add_rule(r'\bfor\b', format_)
        self.add_rule(r'\bfrom\b', format_)
        self.add_rule(r'\bglobal\b', format_)
        self.add_rule(r'\bif\b', format_)
        self.add_rule(r'\bimport\b', format_)
        self.add_rule(r'\bin\b', format_)
        self.add_rule(r'\bis\b', format_)
        self.add_rule(r'\blambda\b', format_)
        self.add_rule(r'\bnonlocal\b', format_)
        self.add_rule(r'\bnot\b', format_)
        self.add_rule(r'\bor\b', format_)
        self.add_rule(r'\bpass\b', format_)
        self.add_rule(r'\braise\b', format_)
        self.add_rule(r'\breturn\b', format_)
        self.add_rule(r'\btry\b', format_)
        self.add_rule(r'\bwhile\b', format_)
        self.add_rule(r'\bwith\b', format_)
        self.add_rule(r'\byield\b', format_)




class SyntaxHighlighter_Matlab_Octave(SyntaxHighlighter):

    def __init__(self, parent):
        super().__init__(parent)

        # Strings
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#99ad6a'))
        self.add_multiline_rule(r"(?<=[^\)\]\}a-zA-Z_0-9])'", r"'", format_)
        self.add_multiline_rule(r'"', r'"', format_)

        # Comments
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#888888'))
        format_.setFontItalic(True)
        self.add_rule(r'%.*$', format_)
        self.add_multiline_rule('%{', '%}', format_)

        # Built-in functions
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#fad07a'))
        self.add_rule(r'\berror\b', format_)
        self.add_rule(r'\bwarning\b', format_)
        self.add_rule(r'\bsize\b', format_)
        self.add_rule(r'\bclear\b', format_)
        self.add_rule(r'\breshape\b', format_)
        self.add_rule(r'\beye\b', format_)
        self.add_rule(r'\bones\b', format_)
        self.add_rule(r'\bzeros\b', format_)
        self.add_rule(r'\blinspace\b', format_)
        self.add_rule(r'\blogspace\b', format_)
        self.add_rule(r'\brand\b', format_)
        self.add_rule(r'\bexp\b', format_)
        self.add_rule(r'\blog\b', format_)
        self.add_rule(r'\blog10\b', format_)
        self.add_rule(r'\bsqrt\b', format_)
        self.add_rule(r'\babs\b', format_)
        self.add_rule(r'\barg\b', format_)
        self.add_rule(r'\bconj\b', format_)
        self.add_rule(r'\bimag\b', format_)
        self.add_rule(r'\breal\b', format_)
        self.add_rule(r'\bsin\b', format_)
        self.add_rule(r'\bcos\b', format_)
        self.add_rule(r'\btan\b', format_)
        self.add_rule(r'\basin\b', format_)
        self.add_rule(r'\bacos\b', format_)
        self.add_rule(r'\batan\b', format_)
        self.add_rule(r'\batan2\b', format_)
        self.add_rule(r'\bsinh\b', format_)
        self.add_rule(r'\bcosh\b', format_)
        self.add_rule(r'\btanh\b', format_)
        self.add_rule(r'\basinh\b', format_)
        self.add_rule(r'\bacosh\b', format_)
        self.add_rule(r'\batanh\b', format_)
        self.add_rule(r'\bsum\b', format_)
        self.add_rule(r'\bprod\b', format_)
        self.add_rule(r'\bceil\b', format_)
        self.add_rule(r'\bfloor\b', format_)
        self.add_rule(r'\bround\b', format_)
        self.add_rule(r'\bmax\b', format_)
        self.add_rule(r'\bmin\b', format_)
        self.add_rule(r'\bsign\b', format_)
        self.add_rule(r'\bmean\b', format_)
        self.add_rule(r'\bstd\b', format_)
        self.add_rule(r'\bcov\b', format_)

        # Numbers
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#cf6a4c'))
        self.add_rule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', format_)
        self.add_rule(r'\b0[xX][0-9a-fA-F]+\b', format_)
        self.add_rule(r'\b0[oO][0-7]+\b', format_)
        self.add_rule(r'\b0[bB][0-1]+\b', format_)

        # Keywords
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#8197bf'))
        self.add_rule(r'\b__FILE__\b', format_)
        self.add_rule(r'\b__LINE__\b', format_)
        self.add_rule(r'\bbreak\b', format_)
        self.add_rule(r'\bcase\b', format_)
        self.add_rule(r'\bcatch\b', format_)
        self.add_rule(r'\bclassdef\b', format_)
        self.add_rule(r'\bcontinue\b', format_)
        self.add_rule(r'\bdo\b', format_)
        self.add_rule(r'\belse\b', format_)
        self.add_rule(r'\belseif\b', format_)
        self.add_rule(r'\bend\b', format_)
        self.add_rule(r'\bend_try_catch\b', format_)
        self.add_rule(r'\bend_unwind_protect\b', format_)
        self.add_rule(r'\bendclassdef\b', format_)
        self.add_rule(r'\bendenumeration\b', format_)
        self.add_rule(r'\bendevents\b', format_)
        self.add_rule(r'\bendfor\b', format_)
        self.add_rule(r'\bendfunction\b', format_)
        self.add_rule(r'\bendif\b', format_)
        self.add_rule(r'\bendmethods\b', format_)
        self.add_rule(r'\bendparfor\b', format_)
        self.add_rule(r'\bendproperties\b', format_)
        self.add_rule(r'\bendswitch\b', format_)
        self.add_rule(r'\bendwhile\b', format_)
        self.add_rule(r'\benumeration\b', format_)
        self.add_rule(r'\bevents\b', format_)
        self.add_rule(r'\bfor\b', format_)
        self.add_rule(r'\bfunction\b', format_)
        self.add_rule(r'\bglobal\b', format_)
        self.add_rule(r'\bif\b', format_)
        self.add_rule(r'\bmethods\b', format_)
        self.add_rule(r'\botherwise\b', format_)
        self.add_rule(r'\bparfor\b', format_)
        self.add_rule(r'\bpersistent\b', format_)
        self.add_rule(r'\bproperties\b', format_)
        self.add_rule(r'\breturn\b', format_)
        self.add_rule(r'\bswitch\b', format_)
        self.add_rule(r'\btry\b', format_)
        self.add_rule(r'\buntil\b', format_)
        self.add_rule(r'\bunwind_protect\b', format_)
        self.add_rule(r'\bunwind_protect_cleanup\b', format_)
        self.add_rule(r'\bwhile\b', format_)




class SyntaxHighlighter_SPICE(SyntaxHighlighter):

    def __init__(self, parent):
        super().__init__(parent)

        # Strings
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#99ad6a'))
        self.add_multiline_rule(r"'", r"'", format_)
        self.add_multiline_rule(r'"', r'"', format_)

        # Comments
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#888888'))
        format_.setFontItalic(True)
        self.add_rule(r'^\*.*$', format_)
        self.add_rule(r'\$.*$', format_)

        # Numbers
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#cf6a4c'))
        self.add_rule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?(?:[TGMKmunpf]|Meg|MEG)?\b', format_)

        # Keywords
        format_ = QtGui.QTextCharFormat()
        format_.setForeground(QtGui.QColor('#8197bf'))
        self.add_rule(r'(?<!\w)\.[a-zA-Z_]+', format_)
