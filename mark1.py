# -*- coding: utf8 -*-

############################
#   imports
import time
import datetime
import urllib2
import re
import os
import pickle
import numpy as np
import matplotlib.pyplot as plt
############################
#   defining the parameters
currentPriceRegex = re.compile(r'(?<=\<td\ align\=\"center\"\ bgcolor\=\"\#FFFfff\"\ nowrap\>\<b\>)\d*\.\d*(?=\<\/b\>\<\/td\>)')
#companyNameRegex = re.compile( ur'(?<=\<TITLE\>).+(?=-公司資料-奇摩股市\<\/TITLE\>)',re.UNICODE)   #doesn't work somehow
companyNameRegex = re.compile( ur'\<TITLE.+TITLE\>', re.UNICODE)
stockSymbolsList = []
outputFolder = "c:/chen chen/stocks/"
stockSymbolsFile='stockSymbols.pydump'
pricesFolder = outputFolder+ "prices/"
stocksFolder = outputFolder +"stocks/"
############################
#
############################
#   defining the classes

class stock:
    def __init__(self, symbol):
        """e.g.
        https://tw.stock.yahoo.com/d/s/company_1473.html
        """
        symbol= ('000'+str(symbol))[-4:]
        self.symbol = symbol
        self.yahooFrontPageUrl     = 'https://tw.stock.yahoo.com/d/s/company_' + symbol + '.html'
        self.yahooCurrentPageUrl   = 'https://tw.stock.yahoo.com/q/q?s=' + symbol

        #   get some basic information from the front page
        yahooFrontPage = urllib2.urlopen(self.yahooFrontPageUrl)
        raw_text       =  yahooFrontPage.read()
        self.name      =  companyNameRegex.findall(raw_text)[0]
        self.name      =  self.name[7:-26]
        self.pricesList          = []
     

    def __call__(self):
        outputString = ""
        #outputString += self.symbol  + '\n'  #unnecessary
        outputString += self.name + '\n'
        outputString += self.yahooCurrentPageUrl + '\n'
        outputString += '\n'.join([time.asctime(time.localtime((v['pingTime'])))+ ":  $" + str(v['price']) for v in self.pricesList])
        print outputString
        

    def openYahooCurrentPage(self):
        self.yahooCurrentPage = urllib2.urlopen(self.yahooCurrentPageUrl)
        
    def getCurrentPrice(self, verbose=True, showResponseTime=True):
        self.openYahooCurrentPage()
        t0 = time.time()
        raw_text = self.yahooCurrentPage.read()
        t1 = time.time()
        self.yahooCurrentPage.close()
        currentPrice = currentPriceRegex.findall(raw_text)[0]
        self.currentPricePingTime = t0
        self.currentPricePingReturnTime = t1
        self.currentPrice = currentPrice
        if verbose:
            print "Time: ", time.asctime(time.localtime(t0)),
            if showResponseTime:
                print "(response time: ", t1-t0, ")",
            #print self.symbol, #unnecessary
            print self.name, "Price:", currentPrice
        self.pricesList.append({'price'          : currentPrice,
                               'pingTime'       : t0,
                               'responseTime'   : t1-t0,
                               })


        return currentPrice, t0, t1-t0

    def getPriceList(self, throttle=1, repetitions=-999, verbose=True):
        count = 0
        while count!= repetitions:
            count +=1
            p, t0, dt = self.getCurrentPrice(verbose=verbose)
            self.pricesList.append({'price'          : p,
                                   'pingTime'       : t0,
                                   'responseTime'   : dt,
                                   })
            if throttle>0:
                time.sleep(throttle)

    def loadPrices(self, pricesPath="", eraseOld=True):
        if eraseOld:
            self.pricesList = []
        if pricesPath == "":
            pricesPath = pricesFolder + self.name + ".dat"
        raw_text = open(pricesPath, 'r').read()
        x        = raw_text.split('\n')[1:]
        xx       = [v.split(',') for v in x]
        for u in xx:
            print u
            if len(u) ==2:
                self.pricesList.append({'price'    : u[0],
                                       'pingTime' : u[1] ,
                                        'responseTime': 0
                                        })
            elif len(u) ==3:
                self.pricesList.append({'price'    : u[0],
                                       'pingTime' : u[1] ,
                                        'responseTime': u[2]
                                        })                     
    def load(self, *args, **kwargs):
        self.loadPrices(*args, **kwargs)

    def plot(self, display=True):
        y = [v['price'] for v in self.pricesList]
        x = [v['pingTime'] for v in self.pricesList]
        plt.plot(y,x)
        plt.title(self.symbol)
        if display:
            plt.show()
############################
#   defining the functions


def getStockSymbolsList1():
    for N in range(9999):
        try:
            s   = stock(N)
            stockSymbolsList.append(N)
            print N, s.name, "<-------------added"
        except:
            print N, "doesn't exist!"
    return stocksSymbolsList

def getStockSymbolsList2(url="http://sheet1688.blogspot.tw/2008/11/blog-post_18.html"):
    raw_text = urllib2.urlopen(url).read()
    symbols  = re.findall(ur'(?<=num\>)\d\d\d\d(?=\<\/td\>)', raw_text, re.UNICODE)
    symbols.sort()
    pickle.dump(symbols, open(outputFolder+stockSymbolsFile,'w'))
    stockSymbolsList = symbols
    return symbols

def loadStockSymbolsList(path=outputFolder+stockSymbolsFile):
    stockSymbolsList = pickle.load(open(path,'r'))
    return stockSymbolsList

def makeStocksList(inPath=outputFolder+stockSymbolsFile,
                   outputFolder=stocksFolder):
    symbols = loadStockSymbolsList()
    for N in symbols:
        try:
            st = stock(N)
            pickle.dump(st, open(outputFolder+st.name+'.pydump','w'))
            print st.name, "-->", outputFolder+st.name+'.pydump'

        except:
            print "stock symbol", N, "not found!!!!"

def loadStocksList(inputFolder=stocksFolder):
    stocksList = []
    L = os.listdir(inputFolder)
    L.sort(key=lambda v: v[-13:-7])
    for fileName in L:
        stocksList.append(pickle.load(open(inputFolder+fileName,'r')))
    return stocksList



############################
#   test run
def main0():    
    for st in stocksList:
        st()
        st.getPriceList(repetitions=5, throttle=0.3)

def main1():
    for st in stocksList:
        st()
    print "=================="
    while True:
        for st in stocksList:
            st.getCurrentPrice()
            time.sleep(.5)

def main2():
    print "=================="
    print time.asctime(time.localtime(time.time()))
    #symbols = loadStockSymbolsList()
    while True:
        stocks = loadStocksList()   #clean up every day
        while time.localtime(time.time()).tm_wday > 4:  #weekends
            pass
        while time.localtime(time.time()).tm_hour<9:
            pass
        while (time.localtime(time.time()).tm_hour >=9 and \
              time.localtime(time.time()).tm_hour < 13) or \
              (time.localtime(time.time()).tm_hour==13 and time.localtime(time.time()).tm_min<=30):
            for st in stocks:
                try:
                    currentPrice, t0, dt = st.getCurrentPrice()
                    if not os.path.exists(pricesFolder+st.name+'.dat'):
                        outputString = "time,            price,    response time\n"
                    else:
                        outputString = ""
                    outputString += str(t0) + ",  " + str(currentPrice)
                    if dt>1:
                        outputString += ",  " + str(int(dt))
                    outputString +=  '\n'
                    open(pricesFolder+st.name+'.dat','a').write(outputString)
                    time.sleep(.5)
                except:
                    print "ERROR!!  <------ ", st.name
            T = time.localtime()
            print time.asctime(T)
            #if T.tm_hour < 9 or T.tm_hour>=13 and T.tm_min>=30:
            #    time.sleep(86400 - (13-9)*3600 - 30*60)
        print "End of the trading session of the day!"
    
def main():
    main1()

if __name__=="__main__":
    ############################
    #   constructing examples
    tainam  = stock(symbol='1473')    
    chenpinsen = stock(symbol=2926)
    ganung     = stock(symbol=2374)
    tungyang   = stock(symbol=1319)
    htc        = stock(2498)
    prince     = stock(2511)
    stocksList = [tainam, chenpinsen, ganung, tungyang, htc, prince]
    ##############################
    #   test run
    main()






