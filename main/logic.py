import threading
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.widgets import Button
from ibapi.client import EClient
from ibapi.wrapper import Ewrapper
from ibapi.contract import Contract


plt.style.use("dark_background")

class LiveSufraceApp(EClient, Ewrapper):
    def __init__(self):
        EClient.__init__(self, self):
        self.iv_dict = {}
        self.map_id = {}
        self.expirations = []
        self.strikes = []
        self.spot_price = 0
        self.underlying_conId = 0
        self.resolved = threading.event()
        self.chain_resolved = threading.event()

    def connectAck(self):
        print("TWS acknowledged connection")