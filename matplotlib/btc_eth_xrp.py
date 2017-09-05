# bitcoin + ripple matplotlib example
# author: Eli Pandolfo
#
# A graph of bitcoin price compared to xrp price for the year 2017,
# with shared x axes, and data retrieved from Quandl (bitcoin),
# xrpcharts.ripple.com (xrp), and etherchain.org (ether)

import quandl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import style
style.use('./elip12.mplstyle')
import datetime as dt
import requests

def get_data():

	# so that I don't show my Quandl API key
	with open('/Users/Eli/Desktop/coding/quandl_api.txt', 'r') as api:
		key = api.read()
	quandl.ApiConfig.api_key = key

	# pull bitcoin price data from bitstamp through quandl
	#https://www.quandl.com/data/BCHARTS/BITSTAMPUSD-Bitcoin-Markets-bitstampUSD
	btc = quandl.get('BCHARTS/BITSTAMPUSD', )
	btc = btc['Weighted Price']['2017-01-01':]
	btc = np.round(btc, 2)
	btc = btc.rename('BTC')
	btc.index = pd.to_datetime(btc.index)
	btc.index.rename('Date', inplace=True)

	# got XRP data from xrpcharts.ripple.com, saved data as CSV, and stored it
	# locally
	xrp = pd.read_csv('../XRP-USD.csv', index_col='start')
	xrp.index = pd.to_datetime(xrp.index)
	xrp = xrp['close']['2017-01-01':]
	xrp = xrp.rename('XRP')
	xrp.index.rename('Date,', inplace=True)

	#read ethereum data from https://etherchain.org/api/statistics/price
	r = requests.get('https://etherchain.org/api/statistics/price')
	eth = eval(r.text)
	eth = pd.DataFrame(eth['data'])
	eth.index = pd.to_datetime(eth.index, unit='h',
								origin='2015-09-01 08:00:00')
	eth = eth['usd'].resample('D').last()
	eth = eth.loc['2017-01-01':]
	eth = eth.rename('ETH')
	eth.index.rename('Date', inplace=True)

	return (btc, xrp, eth)

# shows correlation between two datasets
def correlate(df1, df2):
	return df1.corr(df2)

# sets limits for y axis to make grid line up with ticks
def ylim(ax, df):
	if df.name is 'BTC':
		ax.set_ylim(bottom=750, top=5000)
	elif df.name is 'ETH':
		ax.set_ylim(bottom=-25, top=400)
	elif df.name is 'XRP':
		ax.set_ylim(bottom=-.025, top=.40)

# plots each subplot on the input axes, with the input data, in the
# corresponding input color
def subplot(ax1, ax2, df1, df2, color1, color2):

	# customize graphs
	df1.plot(ax=ax1, color=color1, linewidth=1)
	ax1.set_title(df1.name + ' ' + df2.name + '     Correlation: '
				  + str(round(correlate(df1, df2), 2)))

	ax1.tick_params(axis='x', which='both')
	ax1.xaxis.label.set_visible(False)

	ax1.tick_params(colors=color1, axis='y')
	ax1.yaxis.label.set_color(color1)
	ax1.set_ylabel(df1.name + ' Price (USD)')
	ylim(ax1, df1)

	df2.plot(color=color2, linewidth=1, label=df2.name, ax=ax2)

	ax2.spines['bottom'].set_color('#848484')
	ax2.spines['left'].set_color(color1)
	ax2.spines['top'].set_color('#848484')
	ax2.spines['right'].set_color(color2)

	ax2.set_ylabel(df2.name + ' Price (USD)')
	ax2.yaxis.label.set_color(color2)
	ax2.tick_params(colors=color2, axis='y')
	ylim(ax2, df2)

	ax2.plot(0, 0, label=df1.name, linewidth=1, color=color1)
	leg = plt.legend(loc=2)

# creates 3 subplots, and plots each combination of dfs on them, with
# their appropriate colors
def plot(df1, df2, df3, color1, color2, color3):

	fig = plt.figure()
	fig.canvas.set_window_title(df1.name + '-' + df2.name + '-'
								+ df3.name + ' 2017')

	#subplot 1
	s11 = plt.subplot2grid((2,2), (1,0), rowspan=1, colspan=1)
	s12 = s11.twinx()
	subplot(s11, s12, df1, df2, color1, color2)

	#subplot 2
	s21 = plt.subplot2grid((2,2), (0,0), rowspan=1, colspan=1, sharex=s11)
	s22 = s21.twinx()
	subplot(s21, s22, df1, df3, color1, color3)

	#subplot 3
	s31 = plt.subplot2grid((2,2), (0,1), rowspan=2, colspan=1, sharex=s11)
	s32 = s31.twinx()
	subplot(s31, s32, df3, df2, color3, color2)

	# adjust parameters for optimal full screen view
	plt.subplots_adjust(left=.07, bottom=.09, right=.94, top=.92,
						wspace=.28, hspace=.31)
	plt.draw()
	plt.show()

btc, xrp, eth = get_data()
d = {'green': '#60d515', 'red': '#d22b10', 'blue': '#1fa8e4',
	 'yellow': '#e0cc05','orange': '#eb860d', 'magenta': '#b113ef'}
plot(btc, xrp, eth, d['orange'], d['yellow'], d['red'])
