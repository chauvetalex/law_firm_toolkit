# Gérer les interactions avec les bases de données.

import sqlite3
import functions

def insert_umo_html(umo_html_file):
    row_as_dict = functions.parse_umo_html(umo_html_file)
    values = ', '.join([f"'{_}'" for _ in row_as_dict.values()])
    sql_insert = f"INSERT INTO tbl_main ({', '.join(row_as_dict.keys())}) VALUES ({values}) ;"
    print(sql_insert)
    with sqlite3.connect('umo.db') as cnx:
        csr = cnx.cursor()
        csr.execute(sql_insert)
        cnx.commit()
