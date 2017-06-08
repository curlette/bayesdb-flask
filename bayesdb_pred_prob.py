import bayeslite
from iventure.bql_utils import cursor_to_df

import copy
import csv
import os

def compute_pred_prob(filename, bdb_name, col_names, table="satellites_t", population="satellites_p", columm="Apogee_km", start_row=1):
	# obtain a pointer to the bdb file
	bdb = bayeslite.bayesdb_open('./%s' %(bdb_name))
	with bdb.savepoint():
		# insert the data into the table of interest
		drop_table_query = "DROP TABLE IF EXISTS user_input;"
		create_table_query = "CREATE TABLE user_input FROM './tmp/%s'" % (filename)
		bdb.execute(drop_table_query)
		bdb.execute(create_table_query)

		# we need to know how many rows the table of interest had before we append
		# more rows
		num_rows_query = "SELECT COUNT(*) FROM %s" %(table)
		num_rows_cursor = bdb.execute(num_rows_query)
		num_rows_df = cursor_to_df(num_rows_cursor)
		num_rows = num_rows_df.iloc[0,0]

		col_names_query = "PRAGMA table_info(%s)" %(table)
		col_names_cursor = bdb.sql_execute(col_names_query)
		col_names_df = cursor_to_df(col_names_cursor)
		col_names = [str(c) for c in col_names_df.loc[:, "name"].tolist()]
		col_names_list = ', '.join(col_names)

		insert_data_query = "INSERT INTO %s (%s) SELECT %s FROM user_input" %(table, col_names_list, col_names_list)
		bdb.sql_execute(insert_data_query)

		# compute predictive probabilities
		pred_prob_query = "ESTIMATE PREDICTIVE PROBABILITY OF %s AS pred_prob FROM %s WHERE %s._rowid_ >= %s" %(column, population, table, str(int(num_rows) + start_row))
		pred_prob_cursor = bdb.execute(pred_prob_query)
		pred_prob_df = cursor_to_df(pred_prob_cursor)
		pred_prob_list = pred_prob_df.loc[:, "pred_prob"].tolist()

		# don't leave new rows in the table
		clear_new_rows_query = "DELETE FROM %s WHERE _rowid_ > %d" %(table, num_rows)
		bdb.sql_execute(clear_new_rows_query)

	# add pred. probs. into the csv
	data = csv.reader(open('./tmp/%s' %(filename)))
	lines = [l for l in data]
	pred_prob_column = ['predictive probability of %s' %(column)] + pred_prob_list
	new_lines = copy.deepcopy(lines)
	for i, nl in enumerate(new_lines):
		nl.append(pred_prob_column[i])

	writer = csv.writer(open('./tmp/%s_processed.csv' %(os.path.splitext(os.path.basename(filename))[0]), 'w'))
	writer.writerows(new_lines)
