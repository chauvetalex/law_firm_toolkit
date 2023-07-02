import sys
sys.path.append('/usr/lib/python3/dist-packages')

import uno
import unohelper

def hello():
    context = XSCRIPTCONTEXT.getDocument()
    context.getText().setString("$cgct")

    repl_descriptor = context.createReplaceDescriptor()
    repl_descriptor.SearchString = '$cgct'
    repl_descriptor.ReplaceString = 'Code général des collectivités territoriales'
    context.getText().setString("zulu")

    # found_text = context.searchForward('$cgct')
    # fount_text.

    # # replace = cellRange.createReplaceDescriptor()

    # replace.SearchRegularExpression = True
    # replace.SearchString = r".+$"
    # replace.ReplaceString = r"\&"
