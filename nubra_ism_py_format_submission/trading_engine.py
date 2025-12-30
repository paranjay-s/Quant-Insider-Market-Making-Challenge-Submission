
import time
import json
import threading

from inventory_manager import InventoryManager
from trade_logger import TradeLogger
from execution_simulator import ExecutionSimulator
from quote_models import (
    compute_baseline_quotes,
    compute_adaptive_quotes,
)

def trading_loop():
    baseline_inv = InventoryManager(QMAX)
    adaptive_inv = InventoryManager(QMAX)
    logger = TradeLogger()

    simulator = ExecutionSimulator(logger)

    step = 0

    print("[TRADING] Loop started")

    while not trading_stop_event.is_set():
        with orderbook_lock:
            snapshots = list(latest_orderbooks.values())

        for snap in snapshots:
            bt = snap["best_bid"]
            at = snap["best_ask"]
            V_bt = snap["best_bid_qty"]
            V_at = snap["best_ask_qty"]

            mt = (bt + at) / 2

            baseline_inv.update_mid_price(mt)
            adaptive_inv.update_mid_price(mt)

            # Baseline
            b_hat_b, a_hat_b = compute_baseline_quotes(mt)
            # #  TEMP DEBUG 
            # print(
            #     f"[DEBUG] bt={bt}, at={at}, "
            #     f"b_hat={b_hat_b:.1f}, a_hat={a_hat_b:.1f}"
            # )
            simulator.try_execute(
                b_hat_b, a_hat_b, bt, at,
                baseline_inv, "BASELINE"
            )

            # Adaptive
            b_hat_a, a_hat_a, _ = compute_adaptive_quotes(
                mt, V_bt, V_at, adaptive_inv.Q
            )
            # #  TEMP DEBUG 
            # print(
            #     f"[DEBUG] bt={bt}, at={at}, "
            #     f"b_hat={b_hat_a:.1f}, a_hat={a_hat_a:.1f}"
            # )
            simulator.try_execute(
                b_hat_a, a_hat_a, bt, at,
                adaptive_inv, "ADAPTIVE"
            )

        step += 1
        if step % 50 == 0:
            write_pnl_snapshot(baseline_inv, adaptive_inv, bt, at, b_hat_b, a_hat_b, b_hat_a, a_hat_a, mt)

        time.sleep(0.05)

        time.sleep(0.05)

    logger.jsonl_to_csv("BASELINE")
    logger.jsonl_to_csv("ADAPTIVE")

    print("[TRADING] Loop stopped")

def start_trading():
    global trading_thread
    trading_stop_event.clear()
    trading_thread = threading.Thread(
        target=trading_loop,
        daemon=True
    )
    trading_thread.start()


def stop_trading():
    trading_stop_event.set()
    if trading_thread is not None:
        trading_thread.join(timeout=2)
    print("Trading stopped cleanly")

