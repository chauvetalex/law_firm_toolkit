# FONCTIONS  DIVERSES DE MANIUPLATION DE DOCUMENTS

from docx import Document
from docx.shared import Pt
from docxcompose.composer import Composer

def _merge_docx_documents(master_doc:str, other_docs:list, dst:str):

    """
    Fusionne des documents word.

    Args:
        master_doc (str): Fichier maître.
        other_docs (list): Liste des fichiers à fusionner.
        dst (str): Fichier de destination.
    """

    master = Document(master_doc)
    composer = Composer(master)
    for doc in other_docs:
        doc_ = Document(doc)
        composer.append(doc_)

    composer.save(dst)
