import subprocess

input('Select title then press enter.')
title = subprocess.check_output(
    "xsel", universal_newlines=True).strip().replace('\n', ' ')

# Demander à l'utilisateur la partie de texte qu'il veut conserver.
# (boucler si plusieurs paragraphe discontinus)
text_parts = []
while True:
    # tkinter.messagebox.showinfo(message='Select text parts. Type n if not parts')
    ipt = input('Select text part then press enter.')
    if ipt.strip().lower() in ['q', 'quit']:
        break
    text_parts.append(
        subprocess.check_output(
        "xsel", universal_newlines=True).strip().replace('\n', ' ')
    )

# Recomposer le texte.
text = title + '\n' + '\n[...]\n'.join(text_parts)

# Exporter le texte vers le presse-papier.
echo = subprocess.Popen(('echo', text), stdout=subprocess.PIPE)
subprocess.Popen(('xclip', '-selection', 'clipboard'), stdin=echo.stdout)
