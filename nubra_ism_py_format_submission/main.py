
# IMPORTS

import time
import json
import threading
import json
import time
import csv
import os

from nubra_python_sdk.start_sdk import InitNubraSdk, NubraEnv
from nubra_python_sdk.ticker import websocketdata
from nubra_python_sdk.marketdata.market_data import MarketData
from nubra_python_sdk.refdata.instruments import InstrumentData

from auth import authenticate_nubra
from nifty_options_ref_id_fetcher import fetch_instrument_ref_ids, generate_nifty_option_nubra_names
from orderbook_websocket_manager import start_orderbook_websocket, stop_orderbook_websocket, start_orderbook_json_logger, stop_orderbook_json_logger
from quote_models import compute_baseline_quotes, compute_adaptive_quotes
from inventory_manager import InventoryManager
from trade_logger import TradeLogger
from execution_simulator import ExecutionSimulator
from trading_engine import trading_loop, start_trading, stop_trading

import pandas as pd
import matplotlib.pyplot as plt

# PARAMETERS (FIXED FOR NOW)

TICK_SIZE = 5
S0 = 2 * TICK_SIZE          # static spread
ALPHA = 0.3
K = 0.1
QMAX = 10

# GLOBAL SHARED STATE

latest_orderbooks = {}
orderbook_lock = threading.Lock()

ws_stop_event = threading.Event()
ws_thread = None
market_socket = None

json_logger_stop_event = threading.Event()
json_logger_thread = None

trading_stop_event = threading.Event()
trading_thread = None

# MAIN

def main():
    nubra = authenticate_nubra(NubraEnv.PROD)
    # nubra = authenticate_nubra(NubraEnv.UAT)

    nubra_names = generate_nifty_option_nubra_names()
    ref_ids = fetch_instrument_ref_ids(nubra, nubra_names)

    #  Start WebSocket
    print("Starting WebSocket...")
    # nubra = authenticate_nubra(NubraEnv.UAT)
    start_orderbook_websocket(nubra, ref_ids)

    # Start JSON logger
    start_orderbook_json_logger(
        file_path="latest_orderbooks.json",
        interval_sec=1
    )

    #  Wait for data
    print("Waiting for first snapshots...")
    while True:
        with orderbook_lock:
            if len(latest_orderbooks) > 0:
                break
        time.sleep(0.1)

    print(
        "WebSocket live. Snapshots received:",
        len(latest_orderbooks)
    )

    #  Start trading (THREAD)
    start_trading()

    # Keep main alive
    try:
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\nStopping system...")

        stop_trading()
        stop_orderbook_json_logger()
        stop_orderbook_websocket()

        print("System stopped cleanly")


###
if __name__ == "__main__":
    main()
