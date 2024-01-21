# Script de nettoyage des mails bruts.

# https://pypi.org/project/extract-msg/

import pathlib
import json
import re
import pandas as pd
import unicodedata
import sqlite3

import extract_msg

raw_mails_folder = 'data/raw_mails/'
csv_file = 'data/emails.csv'
database = 'data/emails.db'

def run_pipeline() -> pd.DataFrame:

    # Extraire/lire les mails du dossier local.
    # Générer une liste de dictionnaire pour le montage d'un dataframe.
    emails = []
    for folder in pathlib.Path(raw_mails_folder).glob('*'):
        for file in folder.glob('*.msg'):
            temp_json = json.loads(extract_msg.openMsg(file).getJson())
            temp_json['category'] = str(folder).split('/')[-1]
            emails.append(temp_json)


    # Créer un dataframe et ajouter les colonnes utiles.
    df = pd.DataFrame(emails)
    df['raw_question'] = ''
    df['norm_question'] = ''
    df['auto_tags'] = ''
    df['question_from'] = ''

    # Nettoyer la colonne category.
    df['category'] = df['category'].str.replace('(\d+\.)(.*)', '\\2', regex=True).str.lower()

    # Nettoyer/formatter les dates.
    months_mapper = {
        ' Jan ':'-01-',
        ' Feb ':'-02-',
        ' Mar ':'-03-',
        ' Apr ':'-04-',
        ' May ':'-05-',
        ' Jun ':'-06-',
        ' Jul ':'-07-',
        ' Aug ':'-08-',
        ' Sep ':'-09-',
        ' Oct ':'-10-',
        ' Nov ':'-11-',
        ' Dec ':'-12-',
    }
    df['date'] = df['date'].str.replace('(.*,)(.*)(\d{2}:\d{2}:\d{2}.*)', '\\2', regex=True)

    for month, repl in months_mapper.items():
        filt = df['date'].str.contains(month)
        df.loc[filt, 'date'] = df['date'].str.replace(month, repl)

    def reverse_date_format(dd_mm_yyyy_date):
        split_date = dd_mm_yyyy_date.split('-')[::-1]
        return '-'.join(split_date)

    df['date'] = df['date'].apply(reverse_date_format)

    # Nettoyer l'objet des messages.
    df['subject'] = df['subject'].str.lower()
    mail_marks = ['re:', 're :', 'tr:', 'fwd:']
    for mark in mail_marks:
        filt = df['subject'].str.contains(mark)
        df.loc[filt, 'subject'] = df['subject'].str.replace(mark, '').str.strip(' -')

    # Nettoyer le corps des messages.
    def split_email(email_text):
        mail_splitter = 'De : [^\r\n]+[\r\n]+Envoyé : [^\r\n]+[\r\n]+À : [^\r\n]+[\r\n]+'
        return re.sub(mail_splitter, '\nMAIL_SPLITTER\n', email_text).split('\nMAIL_SPLITTER\n')

    def compute_email_length(email_text):
        return len(split_email(email_text))

    def get_answer(email_text):
        return split_email(email_text)[0]
    df['raw_question'].str.contains(f' city ', case=False,  regex=False)

    def get_raw_question(email_text):
        return split_email(email_text)[-1]

    df['conv_length'] = df['body'].apply(compute_email_length)

    # Extraire question originale et réponse finale du corps du message.
    df['temp_answer'] = df['body'].apply(get_answer)
    df['raw_question'] = df['body'].apply(get_raw_question)

    # Nettoyer les colonnes avec des emails.
    def extract_email_adress(raw_text):
        email_pattern = "[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9-]+(?:\.[a-zA-Z0-9-]+)*"
        return ' ; '. join(re.findall(email_pattern, raw_text))

    df['cc'] = df['cc'].apply(extract_email_adress)
    df['to'] = df['to'].apply(extract_email_adress)

    # Exporter le dataframe en csv.
    df.to_csv(csv_file, sep='\t')

    # Exporter le dataframe en base de données sqlite.
    df.to_sql('tbl_main',con=sqlite3.connect(database))

    return df
