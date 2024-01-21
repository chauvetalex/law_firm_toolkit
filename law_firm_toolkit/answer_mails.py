# Le module définit des fonctions utiles pour la manipulation de courts mails standards de réponse.
# Les fonctions reposentsur un template html.

import re
from lxml import etree

def is_answer_mail_html_valid(answer_mail_html_file):
    pass

# Les sources utilisées pour la réponse doivent être conserver comme des lignes d'un fichier texte.
# L'utilitaire onetab permet de les extraire facilement.
def format_ressources_onetab(onetag_links:str) -> dict:
    ressources_dict = {}
    for line in onetag_links.strip().split('\n'):
        splitted_line = line.split(' | ')
        key = splitted_line[0]
        val = ' | '.join(splitted_line[1:])
        ressources_dict[key] = val

    return ressources_dict

def format_ressources_html(ressources:dict) -> list:
    for key, val in ressources.items():
        html_tag = f"<a href='{key}'>{val}</a></br>"
        print(html_tag)
        yield html_tag

def read_format_answer_mail_html(answer_mail_html_file:str) -> str:

    with open(answer_mail_html_file) as file:
        html = file.read()

    raw_ressources = re.search("(.*<div id='ressources'>)(.*)(</div>.*)", html, re.DOTALL).expand('\\2')
    formatted_ressources = format_ressources_onetab(raw_ressources)
    formatted_ressources = format_ressources_html(formatted_ressources)
    html = re.sub("(.*<div id='ressources'>)(.*)(</div>.*)", '\\1' + '\n'.join(formatted_ressources) + '\\3', html, flags=re.DOTALL)

    with open(answer_mail_html_file, 'w') as file:
        file.write(html)

    return html

def parse_answer_mail_html(answer_mail_html_file:str='template_answer_mail.html'):

    with open(answer_mail_html_file) as file:
        html = file.read()

    dom = etree.HTML(html)

    return {
        'original_question': dom.xpath('//*[@id="original_question"]')[0].text,
        'question': dom.xpath('//*[@id="question"]')[0].text,
        'answer': dom.xpath('//*[@id="answer"]')[0].text,
        'ressources': [_.text for _ in dom.xpath('//*[@id="ressources"]/a')],
        'ressources_link': [_ for _ in dom.xpath('//*[@id="ressources"]/a/@href')]
    }

def get_md_answer(answer_mail_html_file:str) -> str:
    md_content = parse_answer_mail_html(answer_mail_html_file).get('answer')

    return md_content
