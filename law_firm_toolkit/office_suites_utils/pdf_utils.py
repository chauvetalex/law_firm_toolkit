from ast import Index
import subprocess
import pathlib
import os

from io import StringIO
from re import I, T

from importlib.metadata import PathDistribution
import platform
from tempfile import TemporaryDirectory
from pathlib import Path
from turtle import pd

from pathlib import Path
from typing import Union, Literal, List
from pypdf import PdfWriter, PdfReader, Transformation


import pytesseract
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont

from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfdocument import PDFDocument
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from pdfminer.pdfparser import PDFParser

# from PyPDF2 import PdfReader, PdfWriter


if platform.system() == "Windows":
    # We may need to do some additional downloading and setup...
    # Windows needs a PyTesseract Download
    # https://github.com/UB-Mannheim/tesseract/wiki/Downloading-Tesseract-OCR-Engine

    pytesseract.pytesseract.tesseract_cmd = (
        r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    )

    # Windows also needs poppler_exe
    path_to_poppler_exe = Path(r"C:\.....")

    # Put our output files in a sane place...
    out_directory = Path(r"~\Desktop").expanduser()
else:
    out_directory = Path("~").expanduser()

# Path of the Input pdf
#PDF_file = Path(r"d.pdf")

# Store all the pages of the PDF in a variable
image_file_list = []

text_file = out_directory / Path("out_text.txt")

def extract_text_from_pdf_by_ocr(PDF_file, pages=None):

    ''' Main execution point of the program'''

    # Créer un contexte de  dossier temporaire où stocker les images pdf.
    image_file_list = []
    with TemporaryDirectory() as tempdir:

        # CONVERTIR LE PDF EN IMAGES.-------------------------------------------

        if platform.system() == "Windows":
            pdf_pages = convert_from_path(
                PDF_file, 500, poppler_path=path_to_poppler_exe
            )
        else:
            pdf_pages = convert_from_path(PDF_file, 500)
        # Read in the PDF file at 500 DPI

        # # Selectionner les pages à analyser.
        # if pages is not None:
        #     pdf_pages = [_ for i, _ in enumerate(pdf_pages, start=1) if i in pages]

        # Iterate through all the pages stored above
        for page_enumeration, page in enumerate(pdf_pages, start=1):
            # Selectionner les pages à analyser. Passer si la pages n'est pas requise.
            if page_enumeration not in pages:
                continue

            # Create a file name to store the image
            filename = f"{tempdir}\page_{page_enumeration:03}.jpg"

            # Declaring filename for each page of PDF as JPG
            # For each page, filename will be:
            # PDF page 1 -> page_001.jpg
            # PDF page 2 -> page_002.jpg
            # PDF page 3 -> page_003.jpg
            # ....
            # PDF page n -> page_00n.jpg

            # Save the image of the page in system
            page.save(filename, "JPEG")
            image_file_list.append(filename)

        # EFFECTUER L'OCR SUR LES PAGES REQUISES.-------------------------------

        # with open(text_file, "a") as output_file:
        # Open the file in append mode so that
        # All contents of all images are added to the same file

        # Iterate from 1 to total number of pages
        text = ""
        for image_file in image_file_list:

            # Set filename to recognize text from
            # Again, these files will be:
            # page_1.jpg
            # page_2.jpg
            # ....
            # page_n.jpg

            # Recognize the text as string in image using pytesserct
            text += str(((pytesseract.image_to_string(Image.open(image_file)))))

            # The recognized text is stored in variable text
            # Any string processing may be applied on text
            # Here, basic formatting has been done:
            # In many PDFs, at line ending, if a word can't
            # be written fully, a 'hyphen' is added.
            # The rest of the word is written in the next line
            # Eg: This is a sample text this word here GeeksF-
            # orGeeks is half on first line, remaining on next.
            # To remove this, we replace every '-\n' to ''.
            text = text.replace("-\n", "")

    return text

def extract_text_from_pdf(pdf_file, i_pages='default'):

    """
    Extrait le texte d'un fichier .pdf de forme texte.
    Ne fonctionne pas avec les .pdf sous forme image qui nécessitent une OCR.
    """

    if i_pages != 'default':
        for _ in i_pages:
            if isinstance(_, int) is False:
                raise TypeError

    # Transformer i_pages pour les que les index soit exploitables.
    # (index naturel commencant à 1 + index opposé commencant par -1)
    if i_pages != 'default':
        i_pages = [_-1 if _>0 else _ for _ in i_pages]

    output_string = StringIO()
    with open(pdf_file, 'rb') as in_file:
        parser = PDFParser(in_file)
        doc = PDFDocument(parser)
        rsrcmgr = PDFResourceManager()
        device = TextConverter(rsrcmgr, output_string, laparams=LAParams())
        interpreter = PDFPageInterpreter(rsrcmgr, device)

        # Lister les pages
        # !!! transformer le générateur en liste pour pouvoir tester les index !!!
        all_pages = list(PDFPage.create_pages(doc))
        if i_pages != 'default':
            try:
                # pdf_pages = [_ for i,_ in enumerate(PDFPage.create_pages(doc), start=1) if i in i_pages]
                # pdf_pages = [_ for _ in all_pages if all_pages.index(_) in i_pages]
                pdf_pages = [all_pages[i] for i in i_pages]
            except IndexError:
                pdf_pages = all_pages
        else:
            pdf_pages = all_pages

        for page in pdf_pages:
            interpreter.process_page(page)

    return output_string.getvalue()

def split_pdf(src_pdf_file:str, dst_pdf_filestem:str, split_pages:list=None) -> list:
    
    """
    Coupe un fichier pdf en utilisant les pages indiquées comme séparateur et génère plusieurs fichiers pdf.
    Le séparateur est inclus dans le fichier n+1.

    Raises:
        ValueError: _description_

    Returns:
        list: _description_
    """

    # Instancier le Reader.
    src_pdf_reader = PdfReader(src_pdf_file)

    if isinstance(split_pages, int):
        split_pages = [split_pages]

    for split_page in split_pages:
        if split_page > src_pdf_reader.getNumPages():
            raise ValueError('Splitting page over pdf file length.')

    # Corriger les pages exprimées en indexation naturelle.
    split_pages = [_-1 for _ in split_pages]
    split_pages.append(0)
    split_pages.sort()

    # Itérer sur les index des splitters.
    new_pdf_files = []
    n_output_files = len(split_pages)
    for i in range(n_output_files):

        pdf_writer = PdfFileWriter()

        # Itérer sur les pages précédent l'index du splitter.
        if i == range(n_output_files)[-1]:
            for page in range(split_pages[i], src_pdf_reader.getNumPages()):
                pdf_writer.addPage(src_pdf_reader.pages[page])
        else:
            for page in range(split_pages[i], split_pages[i+1]):
                pdf_writer.addPage(src_pdf_reader.pages[page])

        # Ecrire le nouveau fichier pdf.
        with open(f'{dst_pdf_filestem}_{i}.pdf', mode="wb") as output_file:
            pdf_writer.write(output_file)

        new_pdf_files.append(f'{dst_pdf_filestem}_{i}.pdf')

    return new_pdf_files

def split_pdf_tui(src_pdf_file, dst_pdf_filestem=None):

    """
    Coupe un fichier pdf en utilisant les pages indiquées comme séparateur et génère plusieurs fichiers pdf.
    La fonction propose une interface terminal et permet à l'utilisateur de procéder par essai échec en vérifiant que 
    le résultat correspond à ses attentes.
    """

    src_pdf_file = str(src_pdf_file)
    if dst_pdf_filestem is None:
        dst_pdf_filestem = str(src_pdf_file).replace('.pdf', '')

    # Ouvrir le fichier pdf.
    vc_pid = subprocess.Popen(['okular', src_pdf_file]).pid

    while True:
        subprocess.run('clear')
        msg = 'Which page(s) do you want to use as splitters (natural index) ? Use \',\' as splitter. Leave bla\n'
        pages = input(msg).strip().lower()

        # Si le fichier pdf est correct ou que l'utilisateur demande à quitter, retourner.
        if pages in ['', 'q', 'quit']:
            subprocess.run(['kill', str(vc_pid)])
            return

        # Traiter le pdf.-----------------------------------------------------------
        pages = pages.split(',')
        split_pages = [int(_.strip()) for _ in pages]

        temp_dst_pdf_filestem = '/'.join(dst_pdf_filestem.split('/')[0:-1]) + '/temp_' + dst_pdf_filestem.split('/')[-1]
        new_pdf_files = split_pdf(src_pdf_file, temp_dst_pdf_filestem, split_pages)
        print(new_pdf_files)

        # Demander à l'utilisateur de vérifier que le traitement du fichier pdf.
        # est correct.
        pids = []
        for file in new_pdf_files:
            pids.append(subprocess.Popen(['okular', file]).pid)
        signal = input('Is transformation OK ? (y/n default n)\n').strip().lower()
        if signal in ['y', 'yes', '']:
            subprocess.run(['kill', str(vc_pid)])
            for pid in pids:
                subprocess.run(['kill', str(pid)])
            os.remove(src_pdf_file)
            signal = input('Do you want to rename files ?')
            if signal in ['y', 'yes']:
                for file in new_pdf_files:
                    new_pdf_filename = input()
                    new_pdf_file_dir = '/'.join(file.split('/')[0:-2])
                    os.rename(file, f'{new_pdf_file_dir}/{new_pdf_filename}.pdf')
            else:
                for file in new_pdf_files:
                    os.rename(file, file.replace('temp_', ''))
            break
        else:
            for pid in pids:
                subprocess.run(['kill', str(pid)])
            for file in new_pdf_files:
                os.remove(file)
            if signal in ['quit']:
                subprocess.run(['kill', str(vc_pid)])
                break

def is_blank_page(text, char_threshold=100):

    # Tester la longueur de la chaine.
    if len(text) > char_threshold:
        return False

    # Tester les caractères reconnus.
    for char in text:
        if re.search('[A-Za-z]', char) is not None:
            return False
    return True

def delete_pages(
    src_pdf_file, dst_pdf_file,
    pages=None,
    start=None, end=None, step=1):

    # Inputs check.
    if pages is None and (start is None or end is None or step is None):
        raise ValueError

    if pages is None:
        if isinstance(start, int) is False \
        or isinstance(end, int) is False \
        or isinstance(step, int) is False:
            raise TypeError

    if isinstance(pages, int):
        pages=[pages]

    # Instancier le Writer et le Reader.
    src_pdf_reader = PdfReader(src_pdf_file)
    pdf_writer = PdfWriter()

    # Corriger les pages exprimées en indexation naturelle.
    pages = [_-1 for _ in pages]

    # Boucler sur les pages du fichier .pdf original et filtrer.
    for page in range(0, len(src_pdf_reader.pages)):
        if page not in pages:
            pdf_writer.add_page(src_pdf_reader.pages[page])

    # Ecrire le fichier nettoyer.
    with open(dst_pdf_file, mode="wb") as output_file:
        pdf_writer.write(output_file)

def delete_pages_cli(
    src_pdf_file, dst_pdf_file=None,
    pages=None,
    start=None, end=None, step=1):

    if dst_pdf_file is None:
        dst_pdf_file = src_pdf_file

    src_pdf_file = str(src_pdf_file)
    dst_pdf_file = str(dst_pdf_file)

    # Ouvrir le fichier pdf.
    vc_pid = subprocess.Popen(['okular', src_pdf_file]).pid

    while True:

        subprocess.run('clear')
        msg = 'Which page(s) do you want to delete (natural index) ? Use \',\' as splitter. Leave bla\n'
        pages = input(msg).strip().lower()

        # Si le fichier pdf est correct ou que l'utilisateur demande à quitter, retourner.
        if pages in ['', 'q', 'quit']:
            subprocess.run(['kill', str(vc_pid)])
            return

        # Traiter le pdf.-----------------------------------------------------------
        pages = pages.split(',')
        pages = [int(_.strip()) for _ in pages]

        # Instancier le Writer et le Reader.
        src_pdf_reader = PdfReader(src_pdf_file)
        pdf_writer = PdfFileWriter()

        # Corriger les pages exprimées en indexation naturelle.
        pages = [_-1 for _ in pages]

        # Boucler sur les pages du fichier .pdf original et filtrer.
        for page in range(0, src_pdf_reader.getNumPages()):
            if page not in pages:
                pdf_writer.addPage(src_pdf_reader.pages[page])

        # Ecrire le fichier nettoyé.
        temp_pdf_file = dst_pdf_file.replace('.pdf','_temp_.pdf')
        with open(temp_pdf_file, mode="wb") as output_file:
            pdf_writer.write(output_file)

        # Demander à l'utilisateur de vérifier le que le traitement du fichier pdf
        # est correct.
        vc_pid_temp = subprocess.Popen(['okular', temp_pdf_file]).pid
        signal = input('Is transformation OK ? (y/n default n)\n').strip().lower()
        if signal in ['y', 'yes', '']:
            subprocess.run(['kill', str(vc_pid)])
            subprocess.run(['kill', str(vc_pid_temp)])
            os.remove(src_pdf_file)
            os.rename(temp_pdf_file, dst_pdf_file)
            # with open(dst_pdf_file.replace('.pdf','_pdf_ok.txt'), 'w')as f:
            #     f.write('')
            subprocess.run(['kill', str(vc_pid)])
            break
        elif signal in ['quit']:
            subprocess.run(['kill', str(vc_pid)])
            break
        else:
            subprocess.run(['kill', str(vc_pid_temp)])
            os.remove(temp_pdf_file)

def delete_split_pdf_tui(src_pdf_file, dst_pdf_filestem=None):

    # Traiter le nom du/des fichiers de sortie.
    src_pdf_file = str(src_pdf_file)
    if dst_pdf_filestem is None:
        dst_pdf_filestem = str(src_pdf_file).replace('.pdf', '')

    # Ouvrir le fichier pdf orignal.
    vc_pid = subprocess.Popen(['okular', src_pdf_file]).pid

    while True:
        subprocess.run('clear')

        new_pdf_files = []
        while True:
            msg = """
                Which page(s) do you want to delete or use as splitters ?\n
                Use delete/split:n0,n1,...,n2. Use (natural index) ?\n
                Use ';' as commands splitter.\n"""
            temp_commands = input(msg).strip().lower().split(';')
            # [!] Pour un fonctionnement optimal, le splitter doit intervenir après le deleter [!]
            if len(temp_commands) == 2 and ('delete' in temp_commands[0] or 'del' in temp_commands[0]):
                del_commands, split_commands = temp_commands
                del_pages = [_.strip() for _ in del_commands.split(':')[1].strip().split(',')]
                split_pages = [_.strip() for _ in split_commands.split(':')[1].strip().split(',')]
                break
            elif len(temp_commands) == 2 and ('delete' in temp_commands[1] or 'del' in temp_commands[1]):
                input('Delete commands must come before split commands.\n')
                continue
            elif len(temp_commands) == 1 and ('delete' in temp_commands[0] or 'del' in temp_commands[0]):
                del_pages = [_.strip() for _ in temp_commands.split(':')[1].strip().split(',')]
                break
            elif len(temp_commands) == 1 and temp_commands[0] in ['split']:
                split_pages = [_.strip() for _ in temp_commands.split(':')[1].strip().split(',')]
                break
            # Si l'utilisateur demande à quitter, retourner.
            if temp_commands in ['', 'q', 'quit']:
                subprocess.run(['kill', str(vc_pid)])
                return

        # Supprimer les pages.--------------------------------------------------
        if del_pages:

            # Instancier le Writer et le Reader.
            del_pdf_reader = PdfReader(src_pdf_file)
            pdf_writer = PdfFileWriter()

            # Transformer les pages exprimées en indexation naturelle en indexation-0.
            del_pages = [_-1 for _ in del_pages]

            # Boucler sur les pages du fichier .pdf original et filtrer.
            for page in range(0, del_pdf_reader.getNumPages()):
                if page not in del_pages:
                    pdf_writer.addPage(del_pdf_reader.pages[page])

            # Ecrire le fichier nettoyé.
            temp_pdf_file = '/'.join(dst_pdf_filestem.split('/')[0:-1]) + '/temp_' + dst_pdf_filestem.split('/')[-1] +'.pdf'
            with open(temp_pdf_file, mode="wb") as output_file:
                pdf_writer.write(output_file)
        else:
            temp_pdf_file = src_pdf_file

        # Séparer les documents.------------------------------------------------
        if split_pages:
            split_pdf_reader = PdfReader(temp_pdf_file)

            if isinstance(split_pages, int):
                split_pages = [split_pages]

            for split_page in split_pages:
                if split_page > split_pdf_reader.getNumPages():
                    raise ValueError('Splitting page over pdf file length.')

            # Transformer les pages exprimées en indexation naturelle en indexation-0.
            split_pages = [_-1 for _ in split_pages]
            split_pages.append(0)
            split_pages.sort()

            # Itérer sur les index des splitters.
            n_output_files = len(split_pages)
            if '/temp_' in temp_pdf_file:
                temp_new_pdf_filestem = temp_pdf_file[0:-1]
            else:
                temp_new_pdf_filestem = '/'.join(temp_pdf_file.split('/')[0:-1]) + '/temp_' + temp_pdf_file.split('/')[-1]
            for i in range(n_output_files):

                pdf_writer = PdfFileWriter()

                # Itérer sur les pages précédent l'index du splitter.
                if i == range(n_output_files)[-1]:
                    for page in range(split_pages[i], split_pdf_reader.getNumPages()):
                        pdf_writer.addPage(split_pdf_reader.pages[page])
                else:
                    for page in range(split_pages[i], split_pages[i+1]):
                        pdf_writer.addPage(split_pdf_reader.pages[page])

                # Ecrire le nouveau fichier pdf.
                temp_new_pdf_file = f'{temp_new_pdf_filestem}_{i}.pdf'
                with open(temp_new_pdf_file, mode="wb") as output_file:
                    pdf_writer.write(output_file)

                # Ajouter le fichier pdf généré à la liste des fichiers retournés par la fonction.
                new_pdf_files.append(temp_new_pdf_file)
            input(new_pdf_files)
        # Si aucune séparation n'est requise, ajouter dictement le fichier à la
        # liste des fichiers transormés
        else:
            new_pdf_files.append(temp_pdf_file)

        # Demander à l'utilisateur de vérifier le que le traitement du fichier pdf
        # est correct.
        pids = []
        for file in new_pdf_files:
            pids.append(subprocess.Popen(['okular', file]).pid)
        signal = input('Is transformation OK ? (y/n default n)\n').strip().lower()
        if signal in ['y', 'yes', '']:
            subprocess.run(['kill', str(vc_pid)])
            for pid in pids:
                subprocess.run(['kill', str(pid)])
            os.remove(src_pdf_file)
            for file in new_pdf_files:
                os.rename(file, file.replace('temp_', ''))
            break
        else:
            for pid in pids:
                subprocess.run(['kill', str(pid)])
            for file in new_pdf_files:
                os.remove(file)
            if signal in ['quit']:
                subprocess.run(['kill', str(vc_pid)])
                break

def basic_stamp(
    content_pdf: Path,
    stamp_pdf: Path,
    pdf_result: Path,
    page_indices: Union[Literal["ALL"], List[int]] = "ALL",
):
    stamp_page = PdfReader(stamp_pdf).pages[0]
    writer = PdfWriter()
    reader = PdfReader(content_pdf)

    if page_indices == "ALL":
        page_indices = list(range(0, len(reader.pages)))

    for index in page_indices:
        content_page = reader.pages[index]
        content_page.merge_transformed_page(
            stamp_page,
            Transformation().scale(sx=0.2, sy=0.2).translate(tx=700, ty=0),
            over=True
        )
        writer.add_page(content_page)

    with open(pdf_result, "wb") as fp:
        writer.write(fp)

def advanced_stamp(background, front, w_h_pos='default', output="data/test_utils/new.png"):

    # Définir les chemins.
    background = 'data/test_utils/Screenshot_20221110_104831.png'
    front = 'data/test_utils/Approved-stamp-on-transparent-PNG.png'

    # Ouvrir l'image supérieure.
    frontImage = Image.open(front)
    frontImage = frontImage.reduce(factor=8)

    # Ouvrir l'image de fond.
    background = Image.open(background)

    # Calculer les coordonnées de l'image collée.
    # width = (background.width - frontImage.width) // 2
    # height = (background.height - frontImage.height) // 2
    if w_h_pos == 'default':
        print('here')
        w_h_pos = (
            background.width - frontImage.width//2,
            background.height - frontImage.height//2
        )
        print(w_h_pos)

    # Convert image to RGBA
    frontImage = frontImage.convert("RGBA")
    background = background.convert("RGBA")

    # Coller l'image supérieur aux coordonnées indiquées (width, height)
    background.paste(frontImage, w_h_pos, frontImage)

    # Sauvegarder l'image composée.
    background.save(output, format="png")

if __name__ == '__main__':
    # src_pdf = '/home/alex/projects/lexbase_collect/lexbase_collect/dumps/20221108150956_.pdf'
    # delete_split_pdf_tui(src_pdf)

    print('hello')
