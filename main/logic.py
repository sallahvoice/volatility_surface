import threading
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from ibapi.client import EClient  # needed for our requests
from ibapi.contract import Contract  # allows us to specify instruments
from ibapi.wrapper import \
    EWrapper  # needed to define where can the server send the requested data back
from matplotlib.widgets import Button, TextBox
from mpl_toolkits.mplot3d import Axes3D

from db.repositories.surface-repo import (DataPointRepository,
                                          SnapshotRepository)
from logger import get_logger

logger = get_logger(__file__)
plt.style.use("dark_background")

class LiveSurfaceApp(EClient, EWrapper): #implements both classes 

    def __init__(self):
        EClient.__init__(self, self) #the class can (send, receive)
        self.iv_dict = {} #based on reqId.
        self.id_map = {} #each id maps to vol
        self.expirations = []
        self.strikes = []
        self.spot_price = 0
        self.underlying_conId = 0
        self.resolved = threading.Event()
        self.chain_resolved = threading.Event() #ensures correct code flow

    def connectAck(self):
        print("TWS acknowledged connection")

    def error(self, reqId, errorCode, errorString): 
        if errorCode not in [2104, 2106, 2158]:
            logger.error(f"request id :{reqId},error code: {errorCode},error string: {errorString}")

    def contractDetails(self, reqId, contractDetails):
        self.underlying_conId = contractDetails.contract.conId
        self.resolved.set() #flagged True,got conId now other threads are awakened

    def tickPrice(self, reqId, tickType, price, attr):
        if reqId == 9999 and tickType in [4, 9] and price > 0: #we received a spot
            self.spot_price = price

    def securityDefinitionOptionParameter(self, reqId, exchange, underlyingConId, tradingClass, multiplier, expirations, strikes):
        if exchange == "SMART":
            self.expirations = sorted(list(expirations))
            self.strikes = sorted(list(strikes))
            self.chain_resolved.set()

    def tickOptionComputation(self, reqId, tickType, tickAttr, impliedVol, delta, optPrice, pvDividend, gamma, vega, theta, underlyingPrice):
        if tickType == 13 and impliedVol is not None:
            self.iv_dict[reqId] = impliedVol


def run_loop(app):
    app.run()

def start_app(symbol="SPY"):
    app = LiveSurfaceApp()
    app.connect("127.0.0.1", 7497, clientId=1)

    api_thread = threading.Thread(target=run_loop, args=(app,), daemon=True)
    api_thread.start()
    time.sleep(1)

    underlying = Contract()
    underlying.symbol = symbol
    underlying.secType = "STK"
    underlying.exchange = "SMART"
    underlying.currency = "USD"

    app.reqContractDetails(1, underlying)
    app.resolved.wait(timeout=5)

    app.reqMktData(9999, underlying, "", False, False, [])
    while app.spot_price == 0:
        time.sleep(0.1)
    spot = app.spot_price

    app.reqSecDefOptParams(2, symbol, "", "STK", app.underlying_conId)
    app.chain_resolved.wait(timeout=5)

    today = time.strftime("%Y%m%d")
    target_exps = [e for e in app.expirations if e >= today][:6]
    target_strikes = [s for s in app.strikes if spot * 0.98 <= s <= spot * 1.02]

    req_id = 1000
    for exp in target_exps:
        for strike in target_strikes:
            opt = Contract()
            opt.symbol = symbol
            opt.secType = "OPT"
            opt.exchange = "SMART"
            opt.currency = "USD"
            opt.lastTradeDateOrContractMonth = exp
            opt.strike = strike
            opt.right = "C" if strike >= spot else "P"
            app.id_map[req_id] = (exp, strike)

            app.reqMktData(req_id, opt, "106", False, False, [])
            req_id += 1
            time.sleep(0.1)

    return app


class PlotState:

    def __init__(self, symbol, app):
        self.is_locked = False
        self.symbol = symbol
        self.app = app
        self.note = ""
        self.snapshot_repo = SnapshotRepository()
        self.datapoint_repo = DataPointRepository()

    def toggle_lock(self, event):
        self.is_locked = not self.is_locked
        btn_lock_label.set_text("UNLOCK" if self.is_locked else "LOCK")
        plt.draw()

    def save_snapshot(self, event):
        try:
            snapshot_id = self.snapshot_repo.create_snapshot(
                symbol=self.symbol,
                underlying_con_id=self.app.underlying_conId,
                spot_price=self.app.spot_price,
                note=self.note if self.note else None
            )
            snapshot_id = "SIMULATED"

            data_points = []
            for req_id, iv in self.app.iv_dict.items():
                exp_str, strike = self.app.id_map.get(req_id, (None, None))
                if exp_str and strike:
                    option_type = "C" if strike >= self.app.spot_price else "P"
                    data_points.append({
                        "expiration": exp_str,
                        "strike": strike,
                        "implied_vol": iv,
                        "option_type": option_type
                        })

            rows = self.datapoint_repo.bulk_insertion(snapshot_id, data_points)
            logger.info(f"saved snapshot {snapshot_id} with {rows} points")
            if self.note:
                print(f"Note: {self.note}")

        except Exception as e:
            logger.error(f"save failed: {e}")

    def update_note(self, text):
        self.note = text


def live_desktop_plot(app, symbol):
    plt.ion()
    fig = plt.figure(figsize=(16,9))
    fig.canvas.manager.set_window_title("Live Volatility Surface")
    fig.patch.set_facecolor("#1B1212")

    ax_3d = plt.subplot2grid((3, 3), (0, 0), colspan=2, rowspan=3, projection="3d")
    ax_skew = plt.subplot2grid((3,3), (0, 2), rowspan=2)
    ax_controls = plt.subplot2grid((3,3), (2,2))
    ax_controls.axis("off")

    state = PlotState(symbol, app)
    ax_button_lock = plt.axes([.69, .03, .10, .04])
    global btn_lock_label
    btn_lock = Button(ax_button_lock, "LOCK", color="#1f2329")
    btn_lock_label = btn_lock.label
    btn_lock_label.set_color("white")
    btn_lock_label.set_fontsize(9)
    btn_lock.on_clicked(state.toggle_lock)

    ax_btn_save = plt.axes([0.79, 0.03, 0.10, 0.04])
    btn_save = Button(ax_btn_save, "SAVE", cpmpr="#0d4f1a")
    btn_save.label.set_color("white")
    btn_save.label.set_fontsize(9)
    btn_save.on_clicked(state.save_snapshot)

    ax_textbox = plt.axes([0.68, 0.08, 0.21, 0.04])
    textbox = textBox(ax_textbox, "Note: ", initial="", color="#1f2329", label_pad=0.01)
    textBox.label.set_color("white")
    textBox.label.set_fontsize(9)
    textbox.on_submit(state.update_note) 

    print("live implied volatility surface started")

    try:
        current_data = []
        while True:
            if not state.is_locked:
                current_data = []
                for req_id, iv in app.iv_dict.items():
                    exp, strike = app.id_map.get(req_id, (None, None))
                    if exp and strike:
                        current_data.append({"Expiry": exp, "Strike": strike, "IV": iv})

            if len(current_data) > 10:
                df = pd.DataFrame(current_data)
                pivot = df.pivot_table(index="Expiry", columns="Strike", values="IV").sort_index(axis=1).sort_index()
                pivot = pivot.interpolate(method="linear", axis=0).bfill().ffill() #handles NaN

                X, Y_idx = np.meshgrid(pivot.columns, np.arange(len(pivot.index)))
                Z = pivot.values

                curr_elev, curr_azim = ax_3d.elev, ax_3d.azim

                ax_3d.clear()
                ax_3d.set_facecolor("#0b0d0f")
                ax_3d.plot_surface(X, Y_idx, Z, cmap="magma", edgecolor="white", lw=.1, alpha=.9)
                ax_3d.set_yticks(np.arange(len(pivot.index)))
                ax_3d.set_yticklabels(pivot.index)
                title = f"Live Vol Surface | {time.strftime('%H:%M:%S')} | {len(current_data)} pts"
                if state.is_locked:
                    title += "[LOCKED]"
                ax_3d.set_title(title, color="white")
                ax_3d.view_init(elev=curr_elev, azim=curr_azim)

                ax_skew.clear()
                ax_skew.set_facecolor("#0b0d0f")
                nearest_exp = pivot.index[0]
                skew_data = pivot.iloc[0]
                ax_skew.set_title(f"Front-Month-Skew {nearest_exp}", color="white")
                ax_skew.axvline(x=app.spot_price, color="#C41E3A", linestyle="--")
                ax_skew.plot(skew_data.index, skew_data.values, marker="o", color="#0047AB")
                ax_skew.grid(true, alpha=0.2)

            plt.pause(.5)

    except KeyboardInterrupt:
        app.disconnect()
        plt.close()
        print("/nDisconnected")


if __name__ == "__main__":
    SYMBOL = "SPY" #pick what you like
    app_instance = start_app(symbol=SYMBOL) 
    print(f"app started for {SYMBOL}")
    time.sleep(5)
    live_desktop_plot(app_instancen SYMBOL)