#!/usr/bin/env python
from __future__ import print_function

import sys
from bs4 import BeautifulSoup as bs
from make_colors import make_colors
from pydebugger.debug import debug
import clipboard
from datetime import datetime
from unidecode import unidecode
import argparse
import get_version

class SQLGen(object):

	def __init__(self):
		super(SQLGen, self)

	@classmethod
	def set_column_name(self, fieldname, pkey = False, null = True):
		data_type = ""
		is_int = ['id', 'number']
		is_date = ['date', 'access', 'time']
		if pkey:
			pkey = ' PRIMARY KEY '
		else:
			pkey = ''
		if null:
			null = ''
		else:
			null = ' NOT NULL'

		if list(filter(lambda k: k in fieldname.lower(), is_int)):
			data_type = "INT"
		elif list(filter(lambda k: k in fieldname.lower(), is_date)):
			data_type = "DATE"
		else:
			data_type = "VARCHAR(255)"

		return "{} {}{}{}".format(fieldname, data_type, pkey, null)

	@classmethod
	def gen_insert(self, table_name, fields, values):
		SQL = "INSERT INTO {} ({}) VALUES(".format(table_name, ", ".join(fields))
		debug(SQL = SQL)

		ADD = ""
		debug(values = values)
		for i in values:
			debug(ii = i)
			ADD += "'{}', ".format(unidecode(i).replace("'", ""))
		SQL += ADD.strip()[:-1] + ");"
		debug(SQL = SQL)
		return SQL

	@classmethod
	def gen(self, data, table_name):
		SQL = "DROP TABLE IF EXISTS {};CREATE TABLE {} (".format(table_name, table_name)

		data = bs(data, 'html.parser')
		if not data.find('table'):
			print(make_colors("Data not contain table tag !", 'lw', 'r'))
			sys.exit()

		tbody = data.find('tbody')
		debug(tbody = tbody)

		if tbody:
			all_tr = tbody.find_all('tr')
			debug(all_tr = all_tr)
		else:
			all_tr = data.find_all('tr')
			debug(all_tr = all_tr)

		thead = data.find('thead')
		debug(thead = thead)
		if thead:
			thead = thead.find_all('th')
			debug(thead = thead)
		if not thead:
			thead = all_tr[0].find_all('th')
			debug(thead = thead)
		if not thead:
			thead = all_tr[0].find_all('tr')
			debug(thead = thead)

		all_tr = all_tr[1:]

		head = [i.text for i in thead]
		debug(head = head)
		for i in head:
			 SQL += self.set_column_name(i) + ", "
		debug(SQL = SQL)
		SQL = SQL[:-2] + ");"
		debug(SQL = SQL)

		SQL_INSERT = ""
		for i in all_tr:
			data_td = []
			all_td = i.find_all('td')
			for td in all_td:
				data_td.append(td.text)

			SQL_INSERT += self.gen_insert(table_name, head, data_td)
			debug(SQL_INSERT = SQL_INSERT)
		debug(SQL_INSERT = SQL_INSERT)
		SQL += SQL_INSERT
		debug(SQL = SQL)
		clipboard.copy(SQL)
		print(make_colors("SQL:", 'lc') + " " + make_colors(SQL, 'ly'))
		return SQL

	@classmethod
	def usage(self):
		parser = argparse.ArgumentParser(prog="sqlgen", version="version: " + (get_version.get() or "0.1"))
		parser.add_argument('TABLE_NAME', help='Table Name', action='store')
		parser.add_argument('-s', '--source', help='Source: FILE_PATH | STRING, default from clipboard', action = 'store')
		if len(sys.argv) == 1:
			parser.print_help()
		else:
			args = parser.parse_args()
			if args.source:
				if os.path.isfile(args.source):
					data = open(args.source, 'r').read()
				else:
					data = args.source
			else:
				data = clipboard.paste()
			SQLGen.gen(data, args.TABLE_NAME)

def usage():
	return SQLGen.usage()

if __name__ == '__main__':
	# data = clipboard.paste()
	# SQLGen.gen(data, sys.argv[1])
	usage()
