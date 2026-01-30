import threading
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Button
from ibapi.client import EClient #needed for our requests
from ibapi.wrapper import Ewrapper #needed to define where can the server send the requested data back
from ibapi.contract import Contract #allows us to specify instruments
from logger import get_logger

logger = get_logger(__file__)

plt.style.use("dark_background")

class LiveSufraceApp(EClient, Ewrapper): #implements both classes 

    def __init__(self):
        EClient.__init__(self, self): #the class can (send, receive)
        self.iv_dict = {} #based on reqId
        self.map_id = {} #each id maps to vol
        self.expirations = []
        self.strikes = []
        self.spot_price = 0
        self.underlying_conId = 0
        self.resolved = threading.event()
        self.chain_resolved = threading.event() #ensures correct code flow

    def connectAck(self):
        print("TWS acknowledged connection")

    def error(self, reqId, errorCode, errorString): 
        if errorCode not in [2104, 2106, 2158]:
            logger.error(f"request id :{reqId},error code: {errorCode},error string: {errorString}")

    def contractDetails(self, reqId, contractDetails):
        self.underlying_conId = contractDetails.contract.conId
        self.resolved.set() #flagged True,got conId now other threads are awakened

    def tickPrice(self, reqId, tickType, price, attr):
        if reqId = 9999 abd tickType in [4, 9] and price > 0: #we received a spot
            self.spot_price = price

    def securityDefinitionOptionParameter(self, reqId, exchange, underlyingConId, tradingClass, multiplier, expirations, strikes):
        if exchange = "SMART":
            self.expirations = sorted(list(expirations))
            self.strikes = sorted(list(strikes))
            self.chain_resolved.set()

    def tickOptionComputation(self, reqId, tickType, tickAttr, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, underlyingPrice):
        if tickType == 13 and impliedVol is not None:
            self.iv_dict[reqId] = impliedVol


def run_loop(app):
    app.run()

def start_app(symbol="SPY"):
    app = LiveSufraceApp()
    app.connect("127.0.0.1", 7497, clientId=1)

    api_thread = threading.thread(target=run_loop, args=(app, daemon=True))
    api_thread.start()
    time.sleep(1)

    underlying = contract()
    underlying.symbol = symbol
    underlying.secType = "STK"
    underlying.exchange = "SMART"
    underlying.currency = "USD"

    app.reqContractDetails(1, underlying)
    app.resolve.wait(timeout=5)

    app.reqMktData(9999, underlying, "", False, False, [])
    while app.spot_price == 0:
        time.sleep(0.1)
    spot = app.spot_price