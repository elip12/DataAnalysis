# querymerge
# author: Eli Pandolfo
#
# A script that pulls data from csv files in pandas dataframes, performs
# analysis (applies a statistical function, e.g. mean, sum, min) on a slice
# of the data, and appends the results of the analysis to another CSV file

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import os
from math import isnan
from sys import argv
import datetime as dt


# face_sample =  "Affdex_2016-11-08_16-12_Leeps-02_1478650349944_.csv"
# leda_sample = "Leda_GSR_2016-11-08_S2_Leeps-02_1478649825471_.csv"

# takes filenames and returns initial time and computer ID
def splitFile(filename):
    if filename is None:
        return None
    components = filename.split('_')
    timestamp = components[-2]
    compNumber = components[-3].split('-')[1]
    return (timestamp, compNumber)

#returns a 13-digit timestamp given a utc datetime in format:
# YYYY-mm-ddTHH:MM:SS.fffZ or format: YYYY-mm-dd HH:MM:SS.ffffff+00:00
def parse_ts(utc_dt):
    if utc_dt.strip()[-1] == 'Z':
        return int(dt.datetime.strptime(utc_dt,
					'%Y-%m-%dT%H:%M:%S.%fZ').replace(
					tzinfo=dt.timezone.utc).timestamp()*1000)
    else:
        return int(dt.datetime.strptime(utc_dt,
					'%Y-%m-%d %H:%M:%S.%f+00:00').replace(
					tzinfo=dt.timezone.utc).timestamp()*1000)

#returns true if two different timestamps are within 30 minutes of each other
def isWithinTimeRange(base, compare, diff=30):
    minutes_range = diff  # this is the key parameter to test difference in time
    ms_range = minutes_range*60*1000
    ibase = int(base)
    icompare = int(compare)
    return abs(ibase - icompare) <= ms_range

def tsname(ts):
    start_ = ts.find('time_') + 5
    return ts[start_:]

# converts a string input into a numpy fcn that can be applied to a DataFrame or
# Series. This is better than getattr because np functions are not attributes of
# pandas objects and the pandas min, max, mean, etc don't work in the way we
# want them to
def fcnConvert(fcn):
    if fcn == 'mean' or fcn == 'np.mean':
        fcn = np.mean
    if fcn == 'std' or fcn == 'np.std' or fcn == 'sd':
        fcn = np.std
    if fcn == 'min' or fcn == 'np.min':
        fcn = np.min
    if fcn == 'max' or fcn == 'max':
        fcn = np.max
    return fcn

#evaulates fcns on given columns in a DataFrame for a given time window
def evaluate(df, ts_screen, timestamp, var_names, fcns, delta_ts):
    #get range of data from ts arguments
    start_ts = (ts_screen - int(timestamp))/1000
    end_ts = start_ts + delta_ts

    #error handling: if a var_name is not a column in the csv file, ignore it,
    # but record its position
    missingPos = []
    names = df.columns.values
    var_names2 = [var_name for var_name in var_names]
    for var_name in var_names2:
        if var_name not in names:
            missingPos.append(var_names2.index(var_name))

    # delete the elements in var_names the indices in missingPos; ugly but it
	# works and I think it's the shortest solution
    for i in range(len(missingPos)-1, -1,-1):
        del var_names2[missingPos[i]]

    # get columns corresponding to var_names
    varcols = df[var_names2]

    #get dataframe of values from the range within that column (inclusive)
    values = varcols[start_ts:end_ts]

    #perform fcn on values, store into list
    results = []
    for valuecol in values:
        varlist = []
        for fcn in fcns:
            fcn = fcnConvert(fcn) # converts from string to np function
            varlist.append(fcn(values[valuecol]))
        results.append(varlist)

    return results, missingPos

#--------------------------------------------Afdx------------------------------

# returns [[var1_fcn1, var1_fcn2... ,var1_fcnN]...,
# 		   [varM_fcn1, varM_fcn2... ,varM_fcnM]]
def queryAfdx(directory, ts_screen, ID, var_names, fcns, delta_ts=20):
    filename = 'NaN'
    ID = str(ID)

    #get file matching ID from given directory
    for dirname, dirpath, filenames in os.walk(directory):
        for filen in filenames:
            name, ext = os.path.splitext(filen)
            if(ext == '.csv' and name[0:4] == ('Affd')):
                timestamp, compNumber = splitFile(filen)
                if(compNumber == ID and isWithinTimeRange(timestamp, ts_screen, 30)):
                    filename = filen

    #error handling
    if(filename == 'NaN'):
        return ('ERROR: No Afdx file found with ID=' + ID + ' and timestamp \
				within 30 minutes of' + str(ts_screen), [])

    #read csv file, and open as a pandas dataframe
    filepath = directory + 'Afdx/' + filename
    df = pd.read_csv(filepath)

    #pad missing index values to prevent indexing errors
    try:
        df['delta_secs'].fillna(method='pad', inplace=True)
    except Exception as e:
        return 'ERROR: Adfx file has no column header ' + str(e), []

    df.set_index('delta_secs', inplace=True)

    #perform functions on given cols and ts ranges
    return evaluate(df, ts_screen, timestamp, var_names, fcns, delta_ts)

#-------------------------------------------Leda---------------------------------

# returns [[var1_fcn1, var1_fcn2... ,var1_fcnN]... ,
#		   [varM_fcn1, varM_fcn2... ,varM_fcnM]]
def queryLeda(directory, ts_screen, ID, var_names, fcns, delta_ts=20):
    filename = 'NaN'
    ID = str(ID)

    #get file matching ID from given directory
    for dirname, dirpath, filenames in os.walk(directory):
        for filen in filenames:
            name, ext = os.path.splitext(filen)
            if(ext == '.csv' and name[0:4] == ('Leda')):
                timestamp, compNumber = splitFile(filen)
                if(compNumber == ID and isWithinTimeRange(timestamp, ts_screen, 30)):
                    filename = filen
                    dr = dirname

    #error handling
    if(filename == 'NaN'):
        return 'ERROR: No Leda file found with ID=' + ID + ' and timestamp \
				within 30 minutes of ' + str(ts_screen), []

    #read csv file, and open as a pandas dataframe
    filepath = dr + '/' + filename
    df = pd.read_csv(filepath)

    #pad missing index values to prevent indexing errors
    try:
        df['data.time.data'].fillna(method='pad', inplace=True)
    except Exception as e:
        return 'ERROR: Adfx file has no column header ' + str(e), []

    df.set_index('data.time.data', inplace=True)

    #perform functions on given cols and ts ranges
    return evaluate(df, ts_screen, timestamp, var_names, fcns, delta_ts)

#----------------------------merge----------------------------------------------

# merges pulled afdx and leda aggregates into columns of a new df, that gets
# appended to a csv file
def merge(directory, merge_df_file, ID_col, ts_screens, variables, fcns, delta_ts):

    #open dataframe
    merge_df = pd.read_csv(merge_df_file, index_col=0)

    numrows = len(merge_df.index)
    augmentedCols = []

    for ts in ts_screens:
        ts_name = tsname(ts)
        for var in variables:
            for fcn in fcns:
                colname = str(ts_name) + '_' + str(var) + '_' + str(fcn)
                if ts in merge_df:
                    augmentedCols.append((colname,ts_name))
                newcol = np.zeros(numrows)
                joincol = pd.DataFrame(newcol,
									   index=merge_df.index,
									   columns=[colname])
                merge_df = merge_df.join(joincol)

#player_time_EmoQuestPage1_2

    for row in range(numrows):
        for ts in ts_screens:
            if ts in merge_df:
                #get ts for the current screen
                screen_dt = str(merge_df[ts][row])
                screenNum = parse_ts(screen_dt)

                #get ID at current row
                ID = int(merge_df[ID_col][row].split('_')[1])
                if(ID<10):
                    ID = '0' + str(ID)
                #query for afdx and leda results
                afdxResults, afdxMissingPos = queryAfdx(directory, screenNum,
					ID, variables, fcns, delta_ts)
                ledaResults, ledaMissingPos = queryLeda(directory, screenNum,
					ID, variables, fcns, delta_ts)

                #splice affdex and leda results together
                if isinstance(afdxResults, list)
						and not isnan(afdxResults[0][0])
						and isinstance(ledaResults, list)
						and not isnan(ledaResults[0][0]):
                    splicedList = afdxResults
                    for i in range(len(ledaResults)):
                        splicedList.insert(afdxMissingPos[i], ledaResults[i])
                elif isinstance(afdxResults, list)
						and not isnan(afdxResults[0][0])
						and (not isinstance(ledaResults, list)
						or isnan(ledaResults[0][0])):
                    splicedList = afdxResults
                    for i in afdxMissingPos:
                        splicedList.insert(i, np.repeat('NaN',
											len(fcns)).tolist())
                elif (not isinstance(afdxResults, list)
						or isnan(afdxResults[0][0]))
						and isinstance(ledaResults, list)
						and not isnan(ledaResults[0][0]):
                    splicedList = ledaResults
                    for i in ledaMissingPos:
                        splicedList.insert(i, np.repeat('NaN',
											len(fcns)).tolist())
                else:
                    splicedList = []
                    innerList = np.repeat('NaN', len(fcns)).tolist()
                    for i in variables:
                        splicedList.append(innerList)

                listIndex = 0
                flatSplicedList = [num for sublist in splicedList
									for num in sublist]

                for col, ts_name in augmentedCols:
                    if(tsname(ts)) == ts_name:
                        merge_df.loc[row,col] = flatSplicedList[listIndex]
                        listIndex += 1


    merge_df.to_csv('/data/KLAB/EEE_data/Processed/oTree/ \
					EEE_otree_postquery.csv')
    return
#-----------------------------------------------------------------------------------------------------------------------------------------

#parse command line arguments for merge fcn: directory, otreefile, idCol,
#varlist, screenlist, fcnlist, delta_ts
#IMPORTANT: separate separate command line args with spaces, but separate
# in lists with commas and no spaces
# example command line:
# python3 /data/KLAB/ptt_express_analysis/MergeFunctions/querymerge.py
#	/data/KLAB/EEE_data/Processed/
#	/data/KLAB/EEE_data/Processed/oTree/EEE_otree_new.csv
#	participant_label
#	player_time_EmoQuestPage1_2,player_time_screen3
#	disgust,analysis.phasicData
#	mean,std
#	20
directory = str(argv[1])
otreeFile = str(argv[2])
idCol = str(argv[3])
screenList = argv[4].split(',')
varList = argv[5].split(',')
fcnList = argv[6].split(',')
delta_ts = argv[7]


merge(directory, otreeFile, idCol, varList, screenList, fcnList, delta_ts)
