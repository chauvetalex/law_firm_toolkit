# import python.office_suites_utils.pdf_utils as pdf_utils
import law_firm_toolkit.office_suites_utils.pdf_utils as pdf_utils
from pdf2image import convert_from_path
from PIL import Image, ImageDraw, ImageFont
import pathlib
import os
import logging
import re
from pathlib import Path
from typing import Union, Literal, List

from pypdf import PdfWriter, PdfReader, Transformation

# TODO créer 2 classes de stampers (avancé et basique)
# La fonction de génération des tampons indexé doit être sortie des classes pour être commune

class BasicStamper:

    def __init__(self, stamp_pdf:Path):
        """
        Implémente un tamponneur basique fusionnant deux pdf.

        Args:
            stamp_pdf (Path): _description_
        """
        self.stamp_pdf = stamp_pdf

    def stamp(
        self,
        input_pdf: Path,
        output_pdf: Path,
        stamped_page_indices: Union[Literal["ALL"], List[int]] = "ALL"
    ):
        stamp = PdfReader(self.stamp_pdf).pages[0]
        writer = PdfWriter()
        reader = PdfReader(input_pdf)

        if stamped_page_indices == "ALL":
            stamped_page_indices = list(range(0, len(reader.pages)))

        for index in range(0, len(reader.pages)):
            content_page = reader.pages[index]
            if index in stamped_page_indices:
                content_page.merge_transformed_page(
                    stamp,
                    Transformation().scale(sx=0.5, sy=0.5).translate(tx=0, ty=0),
                    over=True
                )
            writer.add_page(content_page)

        with open(output_pdf, "wb") as fp:
            writer.write(fp)

def generate_indexed_stamp(
    base_stamp,
    w_h_pos='default',
    index=1,
    color_opacity=(0, 0, 0, 255),
    output='raw_data/test_utils/temp_idx_stamp.png'
    ):
    """
    Génère un tampon numéroté à l'index précisé. La transparence du tampon peut être contrôlée.
    Le tampon généré est au format image (.png).

    Args:
        base_stamp (_type_): _description_
        w_h_pos (str, optional): _description_. Defaults to 'default'.
        index (int, optional): _description_. Defaults to 1.
        color_opacity (tuple, optional): _description_. Defaults to (0, 0, 0, 255).
        output (str, optional): _description_. Defaults to 'data/test_utils/temp_idx_stamp.png'.

    Returns:
        _type_: _description_
    """
    base_stamp = pathlib.Path(base_stamp)

    # Modifier le tampon de base.
    with Image.open(base_stamp).convert("RGBA") as base:

        # make a blank image for the text, initialized to transparent text color
        txt = Image.new("RGBA", base.size, (255, 255, 255, 0))

        # get a font
        fnt = ImageFont.truetype("Pillow/Tests/fonts/FreeMono.ttf", round(txt.height/3))

        # get a drawing context
        d = ImageDraw.Draw(txt)

        # draw text, full opacity
        d.text((txt.width/2, txt.height/2+100), str(index), font=fnt, fill=color_opacity)

        # Recomposer une image avec le tampon de base et le texte.
        out = Image.alpha_composite(base, txt)

        # Load image and extract alpha channel
        current_alpha = out.getchannel('A')

        # Make all opaque pixels into semi-opaque
        new_alpha = current_alpha.point(lambda i: 128 if i>0 else 0)
        out.putalpha(new_alpha)

        out.save(output)

    return output

def advanced_stamp(
    background,
    stamp,
    resize=1,
    w_h_pos='default',
    output="data/test_utils/new.png"
    ):

    """
    Tamponne une image avec un autre image.
    La position peut être paramétrée être paramétrée.
    """

    # Ouvrir/redimensionner l'image supérieure.
    frontImage = Image.open(stamp)
    # frontImage = frontImage.reduce(factor=8)
    if resize != 1:
        frontImage = frontImage.resize((
            round(frontImage.width*resize),
            round(frontImage.height*resize)
            ))

    # Ouvrir l'image de fond.
    background = Image.open(background)

    # Calculer les coordonnées de l'image supérieure.
    if w_h_pos == 'default':
        w_h_pos = (
            background.width - frontImage.width,
            0
        )
    else:
        w_h_pos = (
           (background.width - frontImage.width) // 2,
            (background.height - frontImage.height) // 2
        )

    # Convertir les images en RGBA (3 canaux + alpha).
    frontImage = frontImage.convert("RGBA")
    background = background.convert("RGBA")

    # Coller l'image supérieur aux coordonnées indiquées (width, height)
    background.paste(frontImage, w_h_pos, frontImage,)

    # Sauvegarder l'image composée.
    background.save(output, format="png",)

def lawyer_stamper(
    pdf_file,
    stamp_file,
    output='same_as_source',
    resize=1,
    w_h_pos='default',
    start_index=1,
    stamped_pages='all'
    ):

    if isinstance(pdf_file, pathlib.Path) is False:
        pdf_file = pathlib.Path(pdf_file)

    # Convertir  le pdf en images.
    images = convert_from_path(pdf_file)

    pdf_reader = PdfReader(pdf_file)

    # Itérer sur les images.
    pil_image_objects = []
    for i, image in enumerate(images):

        # Enregistrer la page comme une image jpeg.
        temp_image_path = f'{pdf_file.parents[0]}/page{str(i)}.jpg'
        image.save(temp_image_path, 'JPEG')

        # Générer le tampon indexé.
        temp_stamp = generate_indexed_stamp(base_stamp=stamp_file, index=start_index)

        # Tamponner uniqument les pages requises.
        if stamped_pages == 'all' or i + 1 in stamped_pages:
            advanced_stamp(background=temp_image_path, stamp=temp_stamp, resize=resize, output=temp_image_path)

        # Ajouter la nouvelle image tamponnée en tant qu'objet PIL à la liste des images qui serviront à recontruire le pdf.
        pil_image_objects.append(Image.open(temp_image_path).convert('RGB'))

        # Supprimer l'image temporaire.
        os.remove(temp_image_path)
    os.remove(temp_stamp)

    # # Reconstruire le pdf à partir des images.
    # if output == 'same_as_source':
    #     output = pdf_file
    # pil_image_objects[0].save(output, save_all=True, append_images=pil_image_objects[1:])

    new_pdf_writer = PdfWriter()
    for i, page in enumerate(pdf_reader.pages):
        # TODO refaire une ROC sur la page tamponnée.
        if page == 'all' or i+1 in stamped_pages:
            logging.debug(f'Adding stamped page {i+1}')
            temp_pdf_stamped_page = 'tmp_pdf_stamped_page.pdf'
            pil_image_objects[i].save(temp_pdf_stamped_page)
            new_pdf_writer.add_page(PdfReader(temp_pdf_stamped_page).pages[0])
            os.remove(temp_pdf_stamped_page)
        else:
            new_pdf_writer.add_page(page)
    if output == 'same_as_source':
        output = pdf_file
    new_pdf_writer.write(output)

    return output

def get_document_index(document):

    RGX_DOC_INDEX = re.compile('(^\d+)(_.*)', re.DOTALL)

    # Récupérer les documents à tamponner.
    document = pathlib.Path(document)

    # Déterminer le numéro de pièce correspondant au document.
    doc_index = RGX_DOC_INDEX\
        .search(pathlib.Path(document).name)\
        .expand(r'\1')

    return int(doc_index)

def documents_lawyer_stamper(
    docs_folder:list,
    stamp:str,
    output='same_as_source',
    resize=1,
    stamped_pages='all'):

    RGX_DOC_INDEX = re.compile('(^\d+)(_.*)', re.DOTALL)

    # Récupérer les documents à tamponner.
    documents = pathlib.Path(docs_folder).glob('*.pdf')
    documents = [_ for _ in documents if RGX_DOC_INDEX.search(_.name)]

    # Itérer sur les documents.
    for document in documents:
        lawyer_stamper(
            pdf_file=document,
            output=output,
            stamp_file=stamp,
            resize=resize,
            start_index=get_document_index(document),
            stamped_pages=stamped_pages
        )

if __name__ == '__main__':

    docs_folder = 'raw_data/test_utils/stamper'
    stamp = 'path/to/stamp.png'
    stamped_pages='all'

    documents_lawyer_stamper(
        docs_folder=docs_folder,
        stamp=stamp,
        resize=0.65,
        stamped_pages=[1,3],
    )
