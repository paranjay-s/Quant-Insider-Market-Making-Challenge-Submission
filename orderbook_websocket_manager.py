import time
import json
import threading
from nubra_python_sdk.ticker import websocketdata

# WEBSOCKET STARTER
def start_orderbook_websocket(nubra, ref_ids):
    global ws_thread, market_socket

    ws_stop_event.clear()

    def on_orderbook_data(msg):
        try:
            ref_id = msg.ref_id
            timestamp = msg.timestamp

            # -------- Filter valid levels --------
            valid_bids = [
                o for o in msg.bids
                if o.price is not None and o.quantity is not None
            ]
            valid_asks = [
                o for o in msg.asks
                if o.price is not None and o.quantity is not None
            ]

            if not valid_bids or not valid_asks:
                return

            # -------- Compute L1 safely --------
            best_bid = max(valid_bids, key=lambda x: x.price)
            best_ask = min(valid_asks, key=lambda x: x.price)

            if best_bid.price >= best_ask.price:
                return

            snapshot = {
                "timestamp": timestamp,
                "best_bid": best_bid.price,
                "best_bid_qty": best_bid.quantity,
                "best_ask": best_ask.price,
                "best_ask_qty": best_ask.quantity,
            }

            with orderbook_lock:
                latest_orderbooks[ref_id] = snapshot

        except Exception as e:
            print("Orderbook parse error:", repr(e))

    def on_connect(msg):
        print("[WS CONNECTED]", msg)

    def on_close(reason):
        print("[WS CLOSED]", reason)

    def on_error(err):
        print("[WS ERROR]", err)

    market_socket = websocketdata.NubraDataSocket(
        client=nubra,
        on_orderbook_data=on_orderbook_data,
        on_connect=on_connect,
        on_close=on_close,
        on_error=on_error,
    )

    def run():
        market_socket.connect()

        for ref_id in ref_ids:
            market_socket.subscribe([str(ref_id)], data_type="orderbook")

        while not ws_stop_event.is_set():
            time.sleep(0.2)

        try:
            market_socket.close()
        except Exception:
            pass

        print("[WS THREAD EXITED]")

    ws_thread = threading.Thread(target=run, daemon=True)
    ws_thread.start()

    return market_socket


# WEBSOCKET STOPPER

def stop_orderbook_websocket():
    global ws_thread, market_socket

    print("Stopping WebSocket...")
    ws_stop_event.set()

    if ws_thread is not None:
        ws_thread.join(timeout=2)

    ws_thread = None
    market_socket = None

    print("WebSocket stopped cleanly.")


# JSON LOGGER
def start_orderbook_json_logger(
    file_path="latest_orderbooks.json",
    interval_sec=1.0
):
    global json_logger_thread

    json_logger_stop_event.clear()

    def run():
        while not json_logger_stop_event.is_set():
            try:
                with orderbook_lock:
                    snapshot = {
                        str(ref_id): data
                        for ref_id, data in latest_orderbooks.items()
                    }

                with open(file_path, "w") as f:
                    json.dump(snapshot, f, indent=2)

            except Exception as e:
                print("JSON logger error:", repr(e))

            time.sleep(interval_sec)

        print("[JSON LOGGER EXITED]")

    json_logger_thread = threading.Thread(
        target=run,
        daemon=True
    )
    json_logger_thread.start()

    print(f"[JSON LOGGER STARTED] → {file_path}")


def stop_orderbook_json_logger():
    global json_logger_thread

    print("Stopping JSON logger...")
    json_logger_stop_event.set()

    if json_logger_thread is not None:
        json_logger_thread.join(timeout=2)

    json_logger_thread = None

    print("JSON logger stopped cleanly.")
