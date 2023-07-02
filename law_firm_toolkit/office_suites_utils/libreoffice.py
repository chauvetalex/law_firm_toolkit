import subprocess

def _convert_file_to_pdf(input_file:str, output_file:str, output_dir:str='same'):

    """
    Convertit un fichier texte (html, txt, docx, odt, etc.) en fichier pdf.
    Utilise libreoffice en backend.

    Args:
        input_file (str): _description_
        output_file (str): _description_
        output_dir (str, optional): _description_. Defaults to 'same'.
    """

    if output_dir == 'same':
        subprocess.run(
            f'lowriter --headless --convert-to pdf {output_file} {input_file}')
    else:
        subprocess.run(
            f'lowriter --headless --convert-to pdf --outdir {output_dir} {output_file} {input_file}')
