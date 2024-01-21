import subprocess
import tkinter.messagebox, tkinter.simpledialog


# Récupérer le focus placé sur l'url.        # Vider le presse papier de xsel.
subprocess.run('xsel -cb', shell=True)

# input('Select url')
# tkinter.messagebox.showinfo(message='Select url')
tkinter.messagebox.askquestion(title=None, message='Select url')
url = subprocess.check_output(
    "xsel", universal_newlines=True).strip().replace('\n', ' ')

# input('Select title')
tkinter.messagebox.askquestion(title=None, message='Select title')
title = subprocess.check_output(
    "xsel", universal_newlines=True).strip().replace('\n', ' ')

# TODO récupérer le code html de la page.

# demander à l'utilisateur la partie de texte qu'il veut conserver (boucle si plusieurs paragraphe discontinus)
text_parts = []
while True:
    # ipt = input('Select text parts. Type n if not parts').strip().lower()
    # tkinter.messagebox.showinfo(message='Select text parts. Type n if not parts')
    ipt = tkinter.messagebox.askokcancel(title=None, message='Select text parts. Type n if not parts')
    if ipt is False:
        break
    text_parts.append(
        subprocess.check_output(
        "xsel", universal_newlines=True).strip().replace('\n', ' ')
    )

# générer un dict avec les informations utiles.
print({
    'url':url,
    'title':title,
    'text': '\n...\n'.join(text_parts)
})

tkinter.messagebox.showinfo(message=url + ' '+ title)
