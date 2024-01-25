# Gérer les interactions avec les bases de données.

import sqlite3
import law_firm_toolkit.answer_mails as answer_mails

database = 'data/emails.db'

def insert_answer_mail_html(answer_mail_html_file):
    row_as_dict = answer_mails.parse_answer_mail_html(answer_mail_html_file)
    values = ', '.join([f"'{_}'" for _ in row_as_dict.values()])
    sql_insert = f"INSERT INTO tbl_main ({', '.join(row_as_dict.keys())}) VALUES ({values}) ;"
    with sqlite3.connect(database) as cnx:
        csr = cnx.cursor()
        csr.execute(sql_insert)
        cnx.commit()
