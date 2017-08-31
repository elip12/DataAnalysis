import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import datetime as dt
import os

# makes IDs 1-9 into 01-09
def make_valid_ID(num):
	if num < 10:
		num = '0' + str(num)
	return str(num)

# takes filenames and returns initial timestamp and computer ID
def splitFile(filename):
    if filename is None:
        return None
    components = filename.split('_')
    timestamp = components[-2]
    compNumber = components[-3].split('-')[1]
    return (timestamp, compNumber)

# creates a dataframe with one column, the aggregate (by a function) of all
# columns in the df passed as an argument
def create_aggr_col(df, fcn):
	df_aggr = pd.DataFrame()
	if len(df) == 0:
		return df_aggr
	if fcn  == 'mean':
		df_aggr[fcn] = df.mean(axis=1)
	elif fcn  == 'median':
		df_aggr[fcn] = df.median(axis=1)
	elif fcn  == 'max':
		df_aggr[fcn] = df.max(axis=1)
	elif fcn  == 'min':
		df_aggr[fcn] = df.min(axis=1)
	elif fcn  == 'std':
		df_aggr[fcn] = df.std(axis=1)
	elif fcn == 'sum':
		df_aggr[fcn] = df.sum(axis=1)
	return df_aggr

#used to find closest file_ts before or up to 10 minutes after ts
#returns difference in time
def time_range(ts, file_ts):
	if int(file_ts) <= ts + 600000:
		return abs(int(file_ts) - ts)
	else:
		return -1

# normalizes a dataframe from a csv file:
# 1) pads all missing index data by filling forward
# 2) resamples the timestamp index to 5 samples per second
# 3) makes the index a range from -x to y, with 0 being the
# 	 timestamp given as an arg
def normalize(afdxleda, fname, timestamp):

	if afdxleda == 'Afdx':
		index_col = 'delta_secs'
	elif afdxleda == 'Leda':
		index_col = 'data.time.data'

	# make timestamp a 13 digit (millisecond) number (used in case a 9-digit
	# timestamp accurate to seconds is given)
	while timestamp / 1000000000000 < 1:
		timestamp *= 10

	#prepare df
	df = pd.read_csv(fname)
	file_ts, compNumber = splitFile(fname)
	df[index_col].fillna(method='pad', inplace=True)

	#convert deltatimes to timestamps
	for index in df.index:
		new_ts = int(float(df[index_col][index]) * 1000 + int(file_ts))
		df.set_value(index, index_col, new_ts)

	# convert index to datetime, resample data to 5x per second,
	# reconvert back to timestamps
	df[index_col] = pd.to_datetime(df[index_col], unit = 'ms')
	df.set_index(index_col, inplace=True)
	df = df.resample('200L').mean()

	#c onvert index back to timestamps
	df.index = df.index.astype(np.int64) / 10**6

	# normalize df's timestamps to have -n < timestamp < m; convert timestamps
	# back to normalized deltatimes
	df.set_index(np.round((df.index - timestamp) / 1000, 1), inplace=True)
	return df

# finds a csv file with matching type (afdx or leda), matching leeps ID, and
# matching timestamp (before or up to 10 min after)
# returns either NaN if no file was found or the full path to the file:
# /data/KLAB/ptt_express_analysis/Afdx (or Leda)/filename
def find_csv(afdxleda, directory, ID, ts):
	filename = 'NaN'

	#error handling
	if afdxleda == 'Afdx':
		name_start = 'Affd'
	elif afdxleda == 'Leda':
		name_start = 'Leda'
	else:
		print('afdxleda must be either "Afdx" or "Leda"')
		return

	#get file matching ID from given directory
	closest = -1
	directory += afdxleda + '/'
	for _, dirnames, filenames in os.walk(directory):
		for filen in filenames:
			name, ext = os.path.splitext(filen)
			if ext == '.csv' and name[0:4] == name_start:
				timestamp, compNumber = splitFile(filen)
				if compNumber == ID and time_range(int(ts), timestamp) != -1
						and (time_range(int(ts), timestamp) < closest
						or closest == -1):
					filename = filen
					closest = time_range(int(ts), timestamp)

	if(filename != 'NaN'):
		filename = directory + filename

	return filename

# takes in a toggle for afdx or leda, a csv file with timestamps and IDs,
# a variable (column header), a function, a time ramge, and an optional message
# finds matching csv files, normalizes them, and plots them within the time
# range (from the now normalized 0 timestamp)
# saves the plot to a file called plot.pf
def plot(afdxleda, df_in, var, fcn, delta_t, message=''):

	df = pd.DataFrame()
	if not isinstance(df_in, pd.DataFrame):
		df_in = pd.read_csv(df_in)
	directory = '/Users/Eli/Desktop/LEEPS/'
	for row in df_in.index:
		#find closest csv file
		fname = find_csv(afdxleda, directory, make_valid_ID(df_in.iloc[row, 0]),
						 df_in.iloc[row, 1])
		if fname != 'NaN':
			#normalize it to a 0-timestamp and 5 samples per second
			df_temp = normalize(afdxleda, fname, df_in.iloc[row, 1])
			#check that the variable name is an existing column
			if var in df_temp.columns.values:
				col_name = splitFile(fname)[1]
				#create series with variable info and x range
				column = pd.Series(df_temp[var][-delta_t:delta_t + .1],
							name=col_name)
				if (len(column) == 0):
					print('ERROR: no ' + var + ' data in range -'
						  + str(delta_t) + ' to ' + str(delta_t)
						  + ' in file ' + fname)
				else:
					#align all indices to be even decimals (1.0, 1.2, 1.4
					# vs 1.1, 1.3, 1.5)
					if column.index[0] * 10 % 2 == 1:
				 		column.index = (10 * column.index - 1) / 10
					df[col_name] = column
			else:
				print('ERROR: "' + var + '" is not a column in dataframe')
				return

	#create aggregate col
	df_aggr = create_aggr_col(df, fcn)
	if len(df) == 0:
		print('ERROR: no data in dataframe')
		return
	#plot data
	ax1 = df.plot(zorder=1, alpha=.55)
	plt.axvline(x=0, color='#999999', linewidth=3, zorder=0)
	df_aggr.plot(ax=ax1, color='#1c5b7d', linewidth=3, zorder=2)
	plt.legend(loc='best')
	plt.xlabel('delta seconds\n' + message)
	plt.ylabel(var)
	plt.title(fcn + ' of ' + var)
	plt.savefig('plot.pdf', bbox_inches='tight')

def main():
	plot('Leda', '/Users/Eli/Desktop/LEEPS/plot_in.csv', 'analysis.phasicData',
		 'mean', 100, '"this is a sample message"')

main()
