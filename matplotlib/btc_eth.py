# bitcoin + ethereum matplotlib example 2
# author: Eli Pandolfo
#
# A graph of bitcoin price compared to ether price for the year 2017,
# with shared x axes,
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
	#https://www.quandl.com/data/BCHARTS/BITSTAMPUSD-Bitcoin-Markets-bitstampUSD
	btc = quandl.get('BCHARTS/BITSTAMPUSD', )
	btc = btc['Weighted Price']['2017-01-01':]
	btc = np.round(btc, 2)

	#read ethereum data from https://etherchain.org/api/statistics/price
	r = requests.get('https://etherchain.org/api/statistics/price')
	eth = eval(r.text)
	eth = pd.DataFrame(eth['data'])
	eth.index = pd.to_datetime(eth.index, unit='h',
							   origin='2015-09-01 07:56:28')
	eth = eth['usd'].resample('D').last()
	eth = eth.loc['2017-01-01':]

	return (btc, eth)

# plot the graphs
def plot(btc, eth):

	fig = plt.figure()
	fig.patch.set_facecolor('#1c1c1c')
	fig.canvas.set_window_title('BTC-ETH 2017 Overlapped')

	# customize graphs
	ax1 = btc.plot(color='#ff8f00', linewidth=.5)
	ax1.grid(True, color='#848484', linewidth=.5, linestyle='--')
	ax1.set_title('BTC/USD + ETH/USD 2017', color='#848484')
	ax1.set_facecolor('#252525')

	ax1.tick_params(colors='#848484', axis='x', which='both')
	ax1.xaxis.label.set_color('#848484')

	ax1.tick_params(colors='#ff8f00', axis='y')
	ax1.yaxis.label.set_color('#ff8f00')
	ax1.set_ylabel('BTC Price (USD)')
	ax1.set_ylim(bottom=750, top=5000)

	ax2 = ax1.twinx()
	eth.plot(color='#00e8d3', linewidth=.5, label='ETH', ax=ax2)

	ax2.spines['bottom'].set_color('#848484')
	ax2.spines['left'].set_color('#ff8f00')
	ax2.spines['top'].set_color('#848484')
	ax2.spines['right'].set_color('#00e8d3')

	ax2.set_ylabel('ETH Price (USD)')
	ax2.yaxis.label.set_color('#00e8d3')
	ax2.tick_params(colors='#00e8d3', axis='y')
	ax2.set_ylim(bottom=-25, top=400)

	ax2.plot(0,0, label='BTC', linewidth=.5, color='#ff8f00')
	leg = plt.legend(loc=2, facecolor='#1c1c1c', edgecolor='#848484')
	for text in leg.get_texts():
		text.set_color('#848484')

	plt.tight_layout()
	plt.show()

btc, eth = get_data()
plot(btc, eth)
