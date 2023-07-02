import subprocess
import sys

import pyperclip
import keyboard


class QuoteMaker:

    def __init__(self):
        """
        Crée un menu permettant de rapidement générer des cituations de texte
        par copier/coller.
        La combinaison ctrl+c stocke la dernière sélection de texte.
        La touche 'esc' permet de quitter la boucle.
        """

        self.is_done=False
        self.quote_parts = []

    def stock_clipboard_content(self):
        self.quote_parts.append(pyperclip.waitForNewPaste(timeout=None))

    def run(self):

        # Definir la hotkey déclenchant une action.
        self.hotkey = keyboard.add_hotkey('ctrl+c', self.stock_clipboard_content)

        # Definir la hotkey déclenchant la sortie de 'boucle'.
        keyboard.wait('esc')

        text = '\n' + '\n[...]\n'.join(self.quote_parts)
        print(text)
        return text

if __name__ == '__main__':
    QuoteMaker().run()
