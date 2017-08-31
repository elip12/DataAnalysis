# bitcoin + ethereum matplotlib example
# author: Eli Pandolfo
#
# A graph of bitcoin price compared to ether price for the year 2017,
# with shared x axes to allow zooming in on both subplots at the same time,
# and data retrieved from Quandl (bitcoin) and etherchain.org (ethereum)

import quandl
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import requests

def get_data():

	# so that I don't show my Quandl API key
	with open('/Users/Eli/Desktop/coding/quandl_api.txt', 'r') as api:
		key = api.read()
	quandl.ApiConfig.api_key = key

	# pull bitcoin price data from bitstamp through quandl
	# https://www.quandl.com/data/BCHARTS/BITSTAMPUSD-Bitcoin-Markets-bitstampUSD
	btc = quandl.get('BCHARTS/BITSTAMPUSD', )
	btc = btc['Weighted Price']['2017-01-01':]
	btc = np.round(btc, 2)

	#read ethereum data from https://etherchain.org/api/statistics/price
	r = requests.get('https://etherchain.org/api/statistics/price')
	eth = eval(r.text)
	eth = pd.DataFrame(eth['data'])
	eth.index = pd.to_datetime(eth.index, unit='h', origin='2015-09-01 07:56:28')
	eth = eth['usd'].resample('D').last()
	eth = eth.loc['2017-01-01':]

	return (btc, eth)

# plot the graphs
def plot(btc, eth):
	fig = plt.figure()
	fig.patch.set_facecolor('#d4d4d4')
	fig.canvas.set_window_title('BTC + ETH 2017')

	b = plt.subplot2grid((2, 1), (0, 0), rowspan=1, colspan=1)
	e = plt.subplot2grid((2, 1), (1, 0), rowspan=1, colspan=1, sharex=b)

	font = {'size': 16}

	# customize graphs
	btc.plot(ax=b, color='darkred', linewidth=2)
	b.set_title('Bitcoin', color='darkred', **font)
	b.grid(True, color='#848484')
	b.set_facecolor('#e5e5e5')
	b.spines['bottom'].set_color('darkred')
	b.spines['left'].set_color('darkred')
	b.spines['top'].set_color('#111111')
	b.spines['right'].set_color('#111111')
	b.set_ylabel('Price (USD)')
	b.xaxis.label.set_color('#111111')
	b.yaxis.label.set_color('darkred')
	b.tick_params(colors='#111111')

	eth.plot(ax=e, color='tab:blue', linewidth=2)
	e.set_title('Ether', color='tab:blue', **font)
	e.grid(True, color='#848484')
	e.set_facecolor('#e5e5e5')
	e.spines['bottom'].set_color('tab:blue')
	e.spines['left'].set_color('tab:blue')
	e.spines['top'].set_color('#111111')
	e.spines['right'].set_color('#111111')
	e.set_ylabel('Price (USD)')
	e.xaxis.label.set_color('#111111')
	e.yaxis.label.set_color('tab:blue')
	e.tick_params(colors='#111111')

	plt.show()

btc, eth = get_data()
plot(btc, eth)
