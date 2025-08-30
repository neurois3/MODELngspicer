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

        self.updateTheme()
        ui_manager = UIManager()
        ui_manager.themeChanged.connect(self.updateTheme)
    

    def addRule(self, expression, format_):
        self.__rules.append((expression, format_))


    def addMultiLineRule(self, start, stop, format_):
        self.__multiline_rules.append((start, stop, format_))


    def clear(self):
        self.__rules.clear()
        self.__multiline_rules.clear()


    def refreshRules(self):
        pass


    def highlightWords(self, text):
        for (expression, format_) in self.__rules:
            for match in re.finditer(expression, text):
                start, end = match.span()
                if self.format(start) != QtGui.QTextCharFormat():
                    continue
                self.setFormat(start, end - start, format_)


    def highlightMultiLines(self, text):
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
        self.highlightMultiLines(text)
        self.highlightWords(text)

        # Whitespace characters
        for match in re.finditer(r'\s', text):
            start, end = match.span()
            self.setFormat(start, end - start, self.whitespace_format)


    @Slot()
    def updateTheme(self):
        ui_manager = UIManager()

        # Update colors
        if ui_manager.theme() == 'Light':
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
        self.refreshRules()

        # Redraw
        self.rehighlight()



class SyntaxHighlighter_Python(SyntaxHighlighter):


    @override
    def refreshRules(self):
        self.clear()

        # Strings
        self.addMultiLineRule("'''", "'''", self.string_format)
        self.addMultiLineRule('"""', '"""', self.string_format)
        self.addMultiLineRule("'", "'", self.string_format)
        self.addMultiLineRule('"', '"', self.string_format)

        # Comments
        self.addRule(r'#.*$', self.comment_format)

        # Spectial methods: e.g. __name__
        self.addRule(r'\b__\w+__\b', self.function_format)

        # Decorators: e.g. @staticmethod
        self.addRule(r'@\w+', self.function_format)

        # Class definitions: class <class name>
        self.addRule(r'(?<=class\s)\w+', self.function_format)

        # Function definitions: def <function name>
        self.addRule(r'(?<=def\s)\w+', self.function_format)

        # Built-in constants
        self.addRule(r'\bFalse\b', self.function_format)
        self.addRule(r'\bTrue\b', self.function_format)
        self.addRule(r'\bNone\b', self.function_format)
        self.addRule(r'\bNotImplemented\b', self.function_format)
        self.addRule(r'\bEllipsis\b', self.function_format)

        # Built-in functions
        self.addRule(r'\babs\b', self.function_format)
        self.addRule(r'\baiter\b', self.function_format)
        self.addRule(r'\ball\b', self.function_format)
        self.addRule(r'\banext\b', self.function_format)
        self.addRule(r'\bany\b', self.function_format)
        self.addRule(r'\bascii\b', self.function_format)
        self.addRule(r'\bbin\b', self.function_format)
        self.addRule(r'\bbool\b', self.function_format)
        self.addRule(r'\bbreakpoint\b', self.function_format)
        self.addRule(r'\bbytearray\b', self.function_format)
        self.addRule(r'\bbytes\b', self.function_format)
        self.addRule(r'\bcallable\b', self.function_format)
        self.addRule(r'\bchr\b', self.function_format)
        self.addRule(r'\bclassmethod\b', self.function_format)
        self.addRule(r'\bcompile\b', self.function_format)
        self.addRule(r'\bcomplex\b', self.function_format)
        self.addRule(r'\bdelattr\b', self.function_format)
        self.addRule(r'\bdict\b', self.function_format)
        self.addRule(r'\bdir\b', self.function_format)
        self.addRule(r'\bdivmod\b', self.function_format)
        self.addRule(r'\benumerate\b', self.function_format)
        self.addRule(r'\beval\b', self.function_format)
        self.addRule(r'\bexec\b', self.function_format)
        self.addRule(r'\bfilter\b', self.function_format)
        self.addRule(r'\bfloat\b', self.function_format)
        self.addRule(r'\bformat\b', self.function_format)
        self.addRule(r'\bfrozenset\b', self.function_format)
        self.addRule(r'\bgetattr\b', self.function_format)
        self.addRule(r'\bglobals\b', self.function_format)
        self.addRule(r'\bhasattr\b', self.function_format)
        self.addRule(r'\bhash\b', self.function_format)
        self.addRule(r'\bhelp\b', self.function_format)
        self.addRule(r'\bhex\b', self.function_format)
        self.addRule(r'\bid\b', self.function_format)
        self.addRule(r'\binput\b', self.function_format)
        self.addRule(r'\bint\b', self.function_format)
        self.addRule(r'\bisinstance\b', self.function_format)
        self.addRule(r'\bissubclass\b', self.function_format)
        self.addRule(r'\biter\b', self.function_format)
        self.addRule(r'\blen\b', self.function_format)
        self.addRule(r'\blist\b', self.function_format)
        self.addRule(r'\blocals\b', self.function_format)
        self.addRule(r'\bmap\b', self.function_format)
        self.addRule(r'\bmax\b', self.function_format)
        self.addRule(r'\bmemoryview\b', self.function_format)
        self.addRule(r'\bmin\b', self.function_format)
        self.addRule(r'\bnext\b', self.function_format)
        self.addRule(r'\bobject\b', self.function_format)
        self.addRule(r'\boct\b', self.function_format)
        self.addRule(r'\bopen\b', self.function_format)
        self.addRule(r'\bord\b', self.function_format)
        self.addRule(r'\bpow\b', self.function_format)
        self.addRule(r'\bprint\b', self.function_format)
        self.addRule(r'\bproperty\b', self.function_format)
        self.addRule(r'\brange\b', self.function_format)
        self.addRule(r'\brepr\b', self.function_format)
        self.addRule(r'\breversed\b', self.function_format)
        self.addRule(r'\bround\b', self.function_format)
        self.addRule(r'\bset\b', self.function_format)
        self.addRule(r'\bsetattr\b', self.function_format)
        self.addRule(r'\bslice\b', self.function_format)
        self.addRule(r'\bsorted\b', self.function_format)
        self.addRule(r'\bstaticmethod\b', self.function_format)
        self.addRule(r'\bstr\b', self.function_format)
        self.addRule(r'\bsum\b', self.function_format)
        self.addRule(r'\bsuper\b', self.function_format)
        self.addRule(r'\btuple\b', self.function_format)
        self.addRule(r'\btype\b', self.function_format)
        self.addRule(r'\bvars\b', self.function_format)
        self.addRule(r'\bzip\b', self.function_format)

        # Numbers
        self.addRule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', self.number_format)
        self.addRule(r'\b0[xX][0-9a-fA-F]+\b', self.number_format)
        self.addRule(r'\b0[oO][0-7]+\b', self.number_format)
        self.addRule(r'\b0[bB][0-1]+\b', self.number_format)

        # Keywords
        self.addRule(r'\band\b', self.keyword_format)
        self.addRule(r'\bas\b', self.keyword_format)
        self.addRule(r'\bassert\b', self.keyword_format)
        self.addRule(r'\basync\b', self.keyword_format)
        self.addRule(r'\bawait\b', self.keyword_format)
        self.addRule(r'\bbreak\b', self.keyword_format)
        self.addRule(r'\bclass\b', self.keyword_format)
        self.addRule(r'\bcontinue\b', self.keyword_format)
        self.addRule(r'\bdef\b', self.keyword_format)
        self.addRule(r'\bdel\b', self.keyword_format)
        self.addRule(r'\belif\b', self.keyword_format)
        self.addRule(r'\belse\b', self.keyword_format)
        self.addRule(r'\bexcept\b', self.keyword_format)
        self.addRule(r'\bfinally\b', self.keyword_format)
        self.addRule(r'\bfor\b', self.keyword_format)
        self.addRule(r'\bfrom\b', self.keyword_format)
        self.addRule(r'\bglobal\b', self.keyword_format)
        self.addRule(r'\bif\b', self.keyword_format)
        self.addRule(r'\bimport\b', self.keyword_format)
        self.addRule(r'\bin\b', self.keyword_format)
        self.addRule(r'\bis\b', self.keyword_format)
        self.addRule(r'\blambda\b', self.keyword_format)
        self.addRule(r'\bnonlocal\b', self.keyword_format)
        self.addRule(r'\bnot\b', self.keyword_format)
        self.addRule(r'\bor\b', self.keyword_format)
        self.addRule(r'\bpass\b', self.keyword_format)
        self.addRule(r'\braise\b', self.keyword_format)
        self.addRule(r'\breturn\b', self.keyword_format)
        self.addRule(r'\btry\b', self.keyword_format)
        self.addRule(r'\bwhile\b', self.keyword_format)
        self.addRule(r'\bwith\b', self.keyword_format)
        self.addRule(r'\byield\b', self.keyword_format)




class SyntaxHighlighter_Matlab_Octave(SyntaxHighlighter):


    @override
    def refreshRules(self):
        self.clear()

        # Strings
        self.addMultiLineRule(r"(?<=[^\)\]\}a-zA-Z_0-9])'", r"'", self.string_format)
        self.addMultiLineRule(r'"', r'"', self.string_format)

        # Comments
        self.addRule(r'%.*$', self.comment_format)
        self.addMultiLineRule('%{', '%}', self.comment_format)

        # Built-in functions
        self.addRule(r'\berror\b', self.function_format)
        self.addRule(r'\bwarning\b', self.function_format)
        self.addRule(r'\bsize\b', self.function_format)
        self.addRule(r'\bclear\b', self.function_format)
        self.addRule(r'\breshape\b', self.function_format)
        self.addRule(r'\beye\b', self.function_format)
        self.addRule(r'\bones\b', self.function_format)
        self.addRule(r'\bzeros\b', self.function_format)
        self.addRule(r'\blinspace\b', self.function_format)
        self.addRule(r'\blogspace\b', self.function_format)
        self.addRule(r'\brand\b', self.function_format)
        self.addRule(r'\bexp\b', self.function_format)
        self.addRule(r'\blog\b', self.function_format)
        self.addRule(r'\blog10\b', self.function_format)
        self.addRule(r'\bsqrt\b', self.function_format)
        self.addRule(r'\babs\b', self.function_format)
        self.addRule(r'\barg\b', self.function_format)
        self.addRule(r'\bconj\b', self.function_format)
        self.addRule(r'\bimag\b', self.function_format)
        self.addRule(r'\breal\b', self.function_format)
        self.addRule(r'\bsin\b', self.function_format)
        self.addRule(r'\bcos\b', self.function_format)
        self.addRule(r'\btan\b', self.function_format)
        self.addRule(r'\basin\b', self.function_format)
        self.addRule(r'\bacos\b', self.function_format)
        self.addRule(r'\batan\b', self.function_format)
        self.addRule(r'\batan2\b', self.function_format)
        self.addRule(r'\bsinh\b', self.function_format)
        self.addRule(r'\bcosh\b', self.function_format)
        self.addRule(r'\btanh\b', self.function_format)
        self.addRule(r'\basinh\b', self.function_format)
        self.addRule(r'\bacosh\b', self.function_format)
        self.addRule(r'\batanh\b', self.function_format)
        self.addRule(r'\bsum\b', self.function_format)
        self.addRule(r'\bprod\b', self.function_format)
        self.addRule(r'\bceil\b', self.function_format)
        self.addRule(r'\bfloor\b', self.function_format)
        self.addRule(r'\bround\b', self.function_format)
        self.addRule(r'\bmax\b', self.function_format)
        self.addRule(r'\bmin\b', self.function_format)
        self.addRule(r'\bsign\b', self.function_format)
        self.addRule(r'\bmean\b', self.function_format)
        self.addRule(r'\bstd\b', self.function_format)
        self.addRule(r'\bcov\b', self.function_format)

        # Numbers
        self.addRule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?\b', self.number_format)
        self.addRule(r'\b0[xX][0-9a-fA-F]+\b', self.number_format)
        self.addRule(r'\b0[oO][0-7]+\b', self.number_format)
        self.addRule(r'\b0[bB][0-1]+\b', self.number_format)

        # Keywords
        self.addRule(r'\b__FILE__\b', self.keyword_format)
        self.addRule(r'\b__LINE__\b', self.keyword_format)
        self.addRule(r'\bbreak\b', self.keyword_format)
        self.addRule(r'\bcase\b', self.keyword_format)
        self.addRule(r'\bcatch\b', self.keyword_format)
        self.addRule(r'\bclassdef\b', self.keyword_format)
        self.addRule(r'\bcontinue\b', self.keyword_format)
        self.addRule(r'\bdo\b', self.keyword_format)
        self.addRule(r'\belse\b', self.keyword_format)
        self.addRule(r'\belseif\b', self.keyword_format)
        self.addRule(r'\bend\b', self.keyword_format)
        self.addRule(r'\bend_try_catch\b', self.keyword_format)
        self.addRule(r'\bend_unwind_protect\b', self.keyword_format)
        self.addRule(r'\bendclassdef\b', self.keyword_format)
        self.addRule(r'\bendenumeration\b', self.keyword_format)
        self.addRule(r'\bendevents\b', self.keyword_format)
        self.addRule(r'\bendfor\b', self.keyword_format)
        self.addRule(r'\bendfunction\b', self.keyword_format)
        self.addRule(r'\bendif\b', self.keyword_format)
        self.addRule(r'\bendmethods\b', self.keyword_format)
        self.addRule(r'\bendparfor\b', self.keyword_format)
        self.addRule(r'\bendproperties\b', self.keyword_format)
        self.addRule(r'\bendswitch\b', self.keyword_format)
        self.addRule(r'\bendwhile\b', self.keyword_format)
        self.addRule(r'\benumeration\b', self.keyword_format)
        self.addRule(r'\bevents\b', self.keyword_format)
        self.addRule(r'\bfor\b', self.keyword_format)
        self.addRule(r'\bfunction\b', self.keyword_format)
        self.addRule(r'\bglobal\b', self.keyword_format)
        self.addRule(r'\bif\b', self.keyword_format)
        self.addRule(r'\bmethods\b', self.keyword_format)
        self.addRule(r'\botherwise\b', self.keyword_format)
        self.addRule(r'\bparfor\b', self.keyword_format)
        self.addRule(r'\bpersistent\b', self.keyword_format)
        self.addRule(r'\bproperties\b', self.keyword_format)
        self.addRule(r'\breturn\b', self.keyword_format)
        self.addRule(r'\bswitch\b', self.keyword_format)
        self.addRule(r'\btry\b', self.keyword_format)
        self.addRule(r'\buntil\b', self.keyword_format)
        self.addRule(r'\bunwind_protect\b', self.keyword_format)
        self.addRule(r'\bunwind_protect_cleanup\b', self.keyword_format)
        self.addRule(r'\bwhile\b', self.keyword_format)




class SyntaxHighlighter_SPICE(SyntaxHighlighter):


    @override
    def refreshRules(self):
        self.clear()

        # Strings
        self.addMultiLineRule(r"'", r"'", self.string_format)
        self.addMultiLineRule(r'"', r'"', self.string_format)

        # Comments
        self.addRule(r'^\*.*$', self.comment_format)
        self.addRule(r'\$.*$', self.comment_format)

        # Numbers
        self.addRule(r'\b(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?(?:[TGMKmunpf]|Meg|MEG)?\b',\
                self.number_format)

        # Keywords
        self.addRule(r'(?<!\w)\.[a-zA-Z_]+', self.keyword_format)
        self.addRule(r'^\+', self.keyword_format)
        self.addRule(r'[()]', self.keyword_format)
