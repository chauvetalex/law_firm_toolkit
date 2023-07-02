import tkinter.messagebox, tkinter.simpledialog

tkinter.messagebox.showinfo(message='ca marche')
text = tkinter.simpledialog.askstring('zulu', 'tape un truc')
tkinter.messagebox.showinfo(message=text)
