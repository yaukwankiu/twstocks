# -*- coding: utf8 -*-

############################
#   imports
import time
import datetime
import urllib2
import re

############################
#   defining the parameters

currentPriceRegex = re.compile(r'(?<=\<td\ align\=\"center\"\ bgcolor\=\"\#FFFfff\"\ nowrap\>\<b\>)\d*\.\d*(?=\<\/b\>\<\/td\>)')
#companyNameRegex = re.compile( ur'(?<=\<TITLE\>).+(?=-公司資料-奇摩股市\<\/TITLE\>)',re.UNICODE)   #doesn't work somehow
companyNameRegex = re.compile( ur'\<TITLE.+TITLE\>', re.UNICODE)

############################
#
############################
#
############################
#   defining the classes

class stock:
    def __init__(self, symbol):
        """e.g.
        https://tw.stock.yahoo.com/d/s/company_1473.html
        """
        symbol= str(symbol)
        self.symbol = symbol
        self.yahooFrontPageUrl     = 'https://tw.stock.yahoo.com/d/s/company_' + symbol + '.html'
        self.yahooCurrentPageUrl   = 'https://tw.stock.yahoo.com/q/q?s=' + symbol

        #   get some basic information from the front page
        yahooFrontPage = urllib2.urlopen(self.yahooFrontPageUrl)
        raw_text       =  yahooFrontPage.read()
        self.name      =  companyNameRegex.findall(raw_text)[0]
        self.name      =  self.name[7:-26]
        self.priceList          = []

    def __call__(self):
        outputString = ""
        #outputString += self.symbol    #unnecessary
        outputString +='\n' + self.name + '\n'
        outputString += self.yahooCurrentPageUrl + '\n'
        outputString += '\n'.join([time.asctime(time.localtime((v['pingTime'])))+ ":  $" + str(v['price']) for v in self.priceList])
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
        self.priceList.append({'price'          : currentPrice,
                               'pingTime'       : t0,
                               'responseTime'   : t1-t0,
                               })


        return currentPrice, t0, t1-t0

    def getPriceList(self, throttle=1, repetitions=-999, verbose=True):
        count = 0
        while count!= repetitions:
            count +=1
            p, t0, dt = self.getCurrentPrice(verbose=verbose)
            self.priceList.append({'price'          : p,
                                   'pingTime'       : t0,
                                   'responseTime'   : dt,
                                   })
            if throttle>0:
                time.sleep(throttle)

############################
#   constructing examples

tainam  = stock(symbol='1473')    
chenpinsen = stock(symbol=2926)
ganung     = stock(symbol=2374)
tungyang   = stock(symbol=1319)
htc        = stock(2498)
prince     = stock(2511)
stocksList = [tainam, chenpinsen, ganung, tungyang, htc, prince]

############################
#   test run
def main0():    
    for st in stocksList:
        st()
        st.getPriceList(repetitions=5, throttle=0.3)

def main():
    for st in stocksList:
        st()
    print "=================="
    while True:
        for st in stocksList:
            st.getCurrentPrice()
            time.sleep(.5)
if __name__=="__main__":
    main()






