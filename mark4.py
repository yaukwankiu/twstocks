# -*- coding: utf8 -*-
"""
USE:

from mark2 import *
main()

"""
############################
#   imports
#from matplotlib import ion
#ion()
import time
import datetime
import urllib2
import re
import sys
import os
#import random
import pickle
import numpy as np
import matplotlib.pyplot as plt

############################
#   defining the parameters
currentPriceRegex = re.compile(r'(?<=\<td\ align\=\"center\"\ bgcolor\=\"\#FFFfff\"\ nowrap\>\<b\>)\d*\.\d*(?=\<\/b\>\<\/td\>)')
#companyNameRegex = re.compile( ur'(?<=\<TITLE\>).+(?=-公司資料-奇摩股市\<\/TITLE\>)',re.UNICODE)   #doesn't work somehow
companyNameRegex = re.compile( ur'\<TITLE.+TITLE\>', re.UNICODE)
companyPageUrlRegex = re.compile(ur"(?<=\' target\=\'_NONE\'\>)http\:\/\/.+?\/"   )#hack
newsItemRegex       = re.compile(ur'(?<=\<td height\=\"37\" valign=\"bottom\">).+(?=\<\/td\>)', re.UNICODE) # we want to url too
stockSymbolsList = []
#outputFolder = "D:/twstocks/"
outputFolder = "c:/chen chen/stocks/"
stockSymbolsFile='stockSymbols.pydump'
pricesFolder = outputFolder+ "prices/"
stocksFolder = outputFolder +"stocks/"
newsFolder   = outputFolder +"news/"
foldersList = [stocksFolder, pricesFolder, newsFolder]
numberOfPricesToShow = 10
numberOfNewsItemsToShow= 4
stocksList=[]
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
        self.yahooNewsPageUrl      = 'https://tw.stock.yahoo.com/q/h?s=' + symbol
        #   get some basic information from the front page
        self.name      = str(symbol)    #default
        try:
            yahooFrontPage = urllib2.urlopen(self.yahooFrontPageUrl)
            raw_text       =  yahooFrontPage.read()
            self.name      =  companyNameRegex.findall(raw_text)[0]
            self.name      =  self.name[7:-26]
        except:
            print "Can't open yahooFrontPage for symbol ", symbol
        self.pricesList          = []
        self.newsItems           = []
        try:
            self.companyPageUrl = companyPageUrlRegex.findall(raw_text)[0]
        except:
            self.companyPageUrl = ""


        #return self

    def __call__(self, numberOfPricesToShow=numberOfPricesToShow, numberOfNewsItemsToShow=numberOfNewsItemsToShow):
        outputString = ""
        #outputString += self.symbol  + '\n'  #unnecessary
        outputString += self.name + '\n'
        outputString += self.yahooCurrentPageUrl + '\n'
        if self.newsItems ==[]:
            #self.loadNews()
            try:
                self.loadNews()
            except IOError:
                self.fetchNews()
                self.writeNews()

        outputString += self.showNews(N=3)
        outputString += '\n'.join([time.asctime(time.localtime((v['pingTime'])))+ ":  $" + str(v['price']) for v in self.pricesList][-numberOfPricesToShow:])
        print outputString
        return self        

    def openYahooCurrentPage(self):
        self.yahooCurrentPage = urllib2.urlopen(self.yahooCurrentPageUrl)
        
    def getCurrentPrice(self, verbose=True, showResponseTime=True):
        self.openYahooCurrentPage()
        t0 = time.time()
        raw_text = self.yahooCurrentPage.read()
        t1 = time.time()
        self.yahooCurrentPage.close()
        currentPrice = float(currentPriceRegex.findall(raw_text)[0])
        self.currentPricePingTime = t0
        self.currentPricePingReturnTime = t1
        self.currentPrice = currentPrice
        self.fetchNews(raw_text=raw_text)
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

    def writeCurrentPrice(self, verbose=True):
        P = self.pricesList[-1]  # the last one
        currentPrice = P['price']
        t0           = P['pingTime']
        dt           = P['responseTime']
        outputString= ''

        if not os.path.exists(pricesFolder+self.name+'.dat'):
           outputString = "#time,            price,    response time\n"
        else:
           outputString = ""
        outputString += str(t0) + ",  " + str(currentPrice)
        if dt>1:
           outputString += ",  " + str(int(dt))
        outputString +=  '\n'
        open(pricesFolder+self.name+'.dat','a').write(outputString)
        if verbose:
            print self.name, outputString

    def fetchNews(self, raw_text="", newsPageUrl="", verbose=True, veryVerbose=False):

        if not hasattr(self, 'yahooNewsPageUrl'):
            self.newsPageUrl = 'https://tw.stock.yahoo.com/q/h?s=' + symbol #hack
        if raw_text=="":
            if newsPageUrl =="":
                newsPageUrl = self.yahooNewsPageUrl
            newsPage = urllib2.urlopen(newsPageUrl)
            raw_text = newsPage.read()
            newsPage.close() 
        if veryVerbose:
            print raw_text
        newsItems = newsItemRegex.findall(raw_text)
        newsItems = [(int(time.time()), v) for v in newsItems]
        for newsItem in newsItems:
            if newsItem[1] not in [v[1] for v in self.newsItems]:
                self.newsItems.append(newsItem)
        if verbose:
            print '\n'.join([v[1] for v in newsItems])
        if veryVerbose:
            return raw_text

    def writeNews(self):
        newsItems2 = [str(v[0])+'\t'+v[1] for v in self.newsItems]
        outputString = "\n".join(newsItems2) + "\n"
        open(newsFolder+self.name+'.dat','a').write(outputString)

    def showNews(self, N=10, showTime=False, display=False):
        #cleanupRegex = re.compile(r'\< a href[.\/\"]+\"\>', re.S)#hack
        cleanupRegex = re.compile(r'\<a href\=\".+\"\>', re.S)#hack
        if showTime:
            #newsItems2 = [time.asctime(time.localtime(v[0]))+'\t'+ re.sub(r'\< a href.+\"\>', '', v[1]) for v in self.newsItems[-N:]]
            newsItems2 = [time.asctime(time.localtime(v[0]))+'  '+ cleanupRegex.sub('', v[1][:-4]) for v in self.newsItems[-N:]]
        else:
            newsItems2 = [cleanupRegex.sub('', v[1][:-4]) for v in self.newsItems[-N:]]
        outputString = "\n".join(newsItems2) + "\n"
        if display:
            print outputString
        return outputString

    def loadNews(self, eraseOld=False):
        if eraseOld:
            self.newsItems = []
        x = open(newsFolder+self.name+'.dat','r').read()
        y = x.split('\n')
        y = [v for v in y if "</a>" in v] # a simple check
        y = [v.split('\t') for v in y]
        y = [(int(v[0]), v[1]) for v in y]
        self.newsItems.extend(y)
        
    def getPriceList(self, throttle=0.3, repetitions=-999, verbose=True):
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
    
               
    def loadPrices(self, pricesPath="", eraseOld=True, verbose=False):
        if eraseOld:
            self.pricesList = []
        if pricesPath == "":
            pricesPath = pricesFolder + self.name + ".dat"
        if not os.path.exists(pricesPath):
            return []
        raw_text = open(pricesPath, 'r').read()
        x        = raw_text.split('\n')[1:]
        xx       = [v.split(',') for v in x]
        for u in xx:
            if verbose:
                print u
            if len(u) ==2:
                self.pricesList.append({'price'    : float(u[1]),
                                       'pingTime' : float(u[0]) ,
                                        'responseTime': 0
                                        })
            elif len(u) ==3:
                self.pricesList.append({'price'    : float(u[1]),
                                       'pingTime' : float(u[0]) ,
                                        'responseTime': float(u[2])
                                        })                     
        return self
    def load(self, *args, **kwargs):
        return self.loadPrices(*args, **kwargs)

    
    def plot(self, display=True, imagePath="", block=False):
        plt.close()
        y = [v['price'] for v in self.pricesList]
        x = [v['pingTime'] for v in self.pricesList]
        plt.plot(x,y)
        #plt.title(self.symbol+":" + time.asctime(time.localtime()) +'\n' +\
        #           self.companyPageUrl)
        plt.title(self.symbol+": " + self.companyPageUrl + '\n'+ time.asctime(time.localtime(self.pricesList[0]['pingTime'])) + "~"  +\
                 time.asctime(time.localtime()))
        if imagepath!="":
            plt.savefig(imagePath)
        if display:            
            plt.show(block=block)
        return self
############################
#   defining the functions

def loadStock(symbol, folder=stocksFolder, verbose=True):
    symbol = str(symbol)
    L = os.listdir(folder)
    L = [v for v in L if symbol in v]
    if verbose:
        print "Folder:", folder+L[0]
    if len(L) == 0:
        print symbol, "not found!!"
    else:
        st = pickle.load(open(folder + L[0], 'r'))
        print st.name, "loaded"
        return st
    
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

def writeCurrentStockPrices(verbose=True):
    stocksList = loadStocksList()
    for st in stocksList:
        try:
            st.getCurrentPrice()
            #if verbose:
            #    print st.name, st.pricesList[-1]
        except:
            print st.name, "<-- can't get current price!"
        try:
            st.writeCurrentPrice(verbose=verbose)
        except:
            print "    ", st.name, "<-- no price to write!"
        time.sleep(0.5)

def isTradingHour():
    """determine if it is trading Hour"""
    return ((time.localtime(time.time()).tm_hour >8 and time.localtime(time.time()).tm_hour <13) or\
              (time.localtime(time.time()).tm_hour==13 and time.localtime(time.time()).tm_min<=40) or\
              (time.localtime(time.time()).tm_hour==8 and time.localtime(time.time()).tm_min>=30))\
              and\
            ( time.localtime(time.time()).tm_wday <=4) 
            

def clearStockPrices(stocksList=stocksList):
    for st in stocksList:
        st.pricesList = []

def initialise(toGetSymbols=False, toMakeStockObjects=True ):
    """to initialise the project, setting up the folders etc"""
    # creating the folders
    for path in foldersList:
        if not os.path.exists(path):
            os.makedirs(path)
    # getting the stock index lists
    # constructing the stocks objects
    if toGetSymbols:
        symbols = getStockSymbolsList2()
    else:
        symbols = loadStockSymbolsList()
    if toMakeStockObjects:
        makeStocksList()


def summary(stocks=""):
    if stocks =="":
        try:
            stocks=stocksList
        except:
            stocks = examples()
    for st in stocks:
        st.load()
        st()
        st.plot()
    return stocks

def find(key1=""):
    L =  [v for v in stocksList if key1 in v.name]
    if len(L)==1:
        L=L[0]
    return L

def check(symbol):
    return stock(symbol)().load()().plot()
###



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

def main2(#toWatch="fixed",
          toWatch="random",
          #toWatch="both",
          timeSleep=5,
          verbose=False):
    print "=================="
    print time.asctime(time.localtime(time.time()))

    #symbols = loadStockSymbolsList()
    if not isTradingHour() and (verbose=="yes" or verbose=="true" or verbose):
        print "not trading hour!"
        for st in stocksList:
            st.load()
        for st in stocksList:
            st()
            time.sleep(1)
        writeCurrentStockPrices()   #if after hour, do it once
 
    stocks = loadStocksList()
    randomPosition = int(np.random.random()*len(stocks))
    stocks = stocks[randomPosition:] + stocks[:randomPosition]
    while True:
        time0= time.time()
        time1= time0
        #print "loading stocks"
        print time.asctime(time.localtime(time.time()))
        
        #stocks = loadStocksList()   #clean up every day
        while not isTradingHour():
            if toWatch =='random':
                watchRandom(stocks=stocks)
            elif toWatch =='fixed':
                watch()
            else:
                watchRandom(stocks=stocks, timeSleep=timeSleep)
                watchRandom(stocks=stocks, timeSleep=timeSleep)
                watchRandom(stocks=stocks, timeSleep=timeSleep)
                watch(timeSleep=timeSleep)
                watchRandom(stocks=stocks, timeSleep=timeSleep)

        while isTradingHour():
             
            for st in stocks:
                if time.time()-time0 > 600: #every 10 minutes
                    for st in stocksList:   
                        st()                # watch selected stocks
                    time0 = time.time()
                if (time.time() - time0) % timeSleep < 0.7:
                    plt.close()
                    stockRandom = stocks[int(np.random.random()*len(stocks))]
                    try:
                        stockRandom.load()
                        stockRandom.getCurrentPrice()
                        #stockRandom.writeCurrentPrice()
                        stockRandom.plot()
                    except:
                        print "Can't get data for: ",stockRandom.name
                try:
                    currentPrice, t0, dt = st.getCurrentPrice()
                    if not os.path.exists(pricesFolder+st.name+'.dat'):
                        outputString = "#time,            price,    response time\n"
                    else:
                        outputString = ""
                    outputString += str(t0) + ",  " + str(currentPrice)
                    if dt>1:
                        outputString += ",  " + str(int(dt))
                    outputString +=  '\n'
                    open(pricesFolder+st.name+'.dat','a').write(outputString)
                    time.sleep(.3)
                except:
                    print "ERROR!!  <------ ", st.name
            T = time.localtime()
            print time.asctime(T)
            #if T.tm_hour < 9 or T.tm_hour>=13 and T.tm_min>=30:
            #    time.sleep(86400 - (13-9)*3600 - 30*60)
        #print "End of the trading session of the day!"
    
def main(*args, **kwargs):
    main2(*args, **kwargs)

def getWatchList():
    ############################
    #   constructing examples
    symbols = [1473,
               #2926,  #no data
               2374, 1319, 2498, 2511]
    tainam = ""
    chenpinsen = ""
    ganung = ""
    tungyang = ""
    htc = ""
    prince = ""
    stocksList = []
    try:
        tainam  = stock(symbol='1473')    
        #chenpinsen = stock(symbol=2926)    #no data
        ganung     = stock(symbol=2374)
        tungyang   = stock(symbol=1319)
        htc        = stock(2498)
        prince     = stock(2511)
        stocksList = [tainam,
                      #chenpinsen,
                      ganung, tungyang, htc, prince]
    except:
        print "Error constructing the %dth example!" % (len(stocksList)+1)
        for i in range(len(symbols)):
            try:
                stocksList.append(stock(symbol=i))
            except:
                print "Error constructing stock with symbol " + str(i)
            
    ##############################
    return stocksList

def watch(L="", load=True, display=True, timeSleep=5):
    if L =="":
        L = getWatchList()
    for st in L:
        if load:
            st.load()
        st(30)
        if display:
            st.plot()
            time.sleep(timeSleep)

def watchRandom(stocks="", timeSleep=10):
    if stocks=="":
        stocks = loadStocksList()
    print '...............'
    print time.asctime(time.localtime(time.time()))
    N = int(len(stocks)* np.random.random())
    st = stocks[N]
    st.load(verbose=False)
    st(5)
    st.plot()
    seconds = time.localtime().tm_sec
    #time.sleep(60-seconds-0.05)
    time.sleep(timeSleep)

#   make stock list if not found in the first import
if not os.path.exists(stocksFolder):
    print "-----------------------------"
    print "first import:  stocksFolder not found!"
    print "makeStocksList function called"
    time.sleep(1)
    os.makedirs(stocksFolder)
    makeStocksList()

if __name__=="__main__":
    print "sleeping 5 seconds"
    time.sleep(5)
    tainam  = stock(symbol='1473')    
    chenpinsen = stock(symbol=2926)
    ganung     = stock(symbol=2374)
    tungyang   = stock(symbol=1319)
    htc        = stock(2498)
    prince     = stock(2511)
    stocksList = [tainam, chenpinsen, ganung, tungyang, htc, prince]
    #   test run
    main(*sys.argv[1:])


#######################################
# examples
#if __name__ != "__main__":
#    stocksList = loadStocksList()
#   examples   = examples()
