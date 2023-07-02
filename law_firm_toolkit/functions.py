import re
from lxml import etree

def is_umo_html_valid(umo_html_file):
    pass

def format_ressources_onetab(onetag_links):
    ressources_dict = {}
    for line in onetag_links.strip().split('\n'):
        splitted_line = line.split(' | ')
        key = splitted_line[0]
        val = ' | '.join(splitted_line[1:])
        ressources_dict[key] = val

    return ressources_dict

def format_ressources_html(ressources_dict):
    for key, val in ressources_dict.items():
        html_tag = f"<a href='{key}'>{val}</a></br>"
        print(html_tag)
        yield html_tag

def read_format_umo_html(umo_html_file):

    with open(umo_html_file) as file:
        html = file.read()

    raw_ressources = re.search("(.*<div id='ressources'>)(.*)(</div>.*)", html, re.DOTALL).expand('\\2')
    formatted_ressources = format_ressources_onetab(raw_ressources)
    formatted_ressources = format_ressources_html(formatted_ressources)
    html = re.sub("(.*<div id='ressources'>)(.*)(</div>.*)", '\\1' + '\n'.join(formatted_ressources) + '\\3', html, flags=re.DOTALL)

    with open(umo_html_file, 'w') as file:
        file.write(html)

    return html

def parse_umo_html(umo_html_file='template_umo.html'):

    with open(umo_html_file) as file:
        html = file.read()

    dom = etree.HTML(html)

    return {
        'original_question': dom.xpath('//*[@id="original_question"]')[0].text,
        'question': dom.xpath('//*[@id="question"]')[0].text,
        'answer': dom.xpath('//*[@id="answer"]')[0].text,
        'ressources': [_.text for _ in dom.xpath('//*[@id="ressources"]/a')],
        'ressources_link': [_ for _ in dom.xpath('//*[@id="ressources"]/a/@href')]
    }

def get_md_answer(umo_html_file):
    md_content = parse_umo_html(umo_html_file).get('answer')

    return md_content
