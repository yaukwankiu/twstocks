#   codes for analysing historical stock prices
"""
1. to get data for e.g. symbol AXP, go to 
        http://finance.yahoo.com/q/hp?s=AXP
    and save to a .csv file
2. to read the csv file:
        from numpy import genfromtext
        data = genfromtxt('axp.csv')
3. to plot:
        import matplotlib.pyplot as plt
        plt.plot(data[:,-1])
        plt.show(block=False)

"""
import time, datetime, re, os, shutil, pickle
import urllib, urllib2
import numpy as np
from numpy import genfromtxt
import matplotlib.pyplot as plt

def help():
    print "1. to get data for e.g. symbol AXP, go to \n        http://finance.yahoo.com/q/hp?s=AXP\n    and save to a .csv file"
    print "2. to read the csv file:\n        from numpy import genfromtext\n        data = genfromtxt('axp_historical.csv')"
    print "3. to plot:        import matplotlib.pyplot as plt\n        plt.plot(data[:,-1])\n        plt.show(block=False)"


def getGMTday():
    t = time.gmtime()
    return t.tm_year, t.tm_mon, t.tm_mday

class stock(object):

    def __init__(self, symbol, dataFolder="./"):
    
        symbol = symbol.lower()
        self.symbol = symbol
        self.URLhistorical  = "http://finance.yahoo.com/q/hp?s=%s" % symbol.upper()
        self.dataFolder=dataFolder
    
    def download(self, y1="", m1="", d1="", y0=1972, m0=5, d0=1, *args, **kwargs):
        if d1 =="":
            y1, m1, d1 = getGMTday()
        URLprices = "http://real-chart.finance.yahoo.com/table.csv?s=%s&amp;d=%d&amp;e=%d&amp;f=%d&amp;g=d&amp;a=%d&amp;b=%d&amp;c=%d&amp;ignore=.csv" \
                                                                %(self.symbol.upper(), m1, d1, y1, m0, d0, y0)
        downloadPath = self.dataFolder + self.symbol + '%d-%d-%d.csv' % getGMTday()
        x = urllib2.urlopen(URLprices).read()
        open(downloadPath , 'w').write(x)
        print "downloaded to", downloadPath
        stock.pricesFilePath = downloadPath
    
    def load(self, pricesFilePath=""):
        """
        load prices from file to memory
        """
        if pricesFilePath =="":
            try:
                pricesFileName = [v for v in os.listdir(self.dataFolder) if self.symbol in v][-1]  # get the latest one
                prices = genfromtxt(self.dataFolder+ pricesFileName , delimiter = ',')
                self.prices = prices
                self.pricesFilePath = self.dataFolder+pricesFileName
                return self
            except:
                return 0
        else:
            try:
                prices = genfromtxt(pricesFilePath , delimiter = ',')
                self.prices = prices
                self.pricesFilePath = pricesFilePath
                return self
            except:
                return False
    def plot(self, block=False):
        try:
            prices = self.prices[:,-1]
        except AttributeError:
            self.load()
            prices = self.prices[:,-1]
        prices = prices.tolist()
        prices.reverse()        
        plt.plot(prices)
        plt.title(str(self.symbol)+ '\n' + self.pricesFilePath)
        plt.show(block=block)
        
