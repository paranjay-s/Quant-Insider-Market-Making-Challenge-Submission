import time
import json
import csv
import os

class TradeLogger:
    def __init__(self):
        self.files = {
            "BASELINE": "baseline_trades.jsonl",
            "ADAPTIVE": "adaptive_trades.jsonl",
        }

    def log_trade(
        self,
        strategy,
        side,
        price,
        bt,
        at,
        b_hat,
        a_hat,
        inventory
    ):
        record = {
            "timestamp": time.time(),
            "strategy": strategy,
            "side": side,
            "trade_price": price,
            "best_bid": bt,
            "best_ask": at,
            "b_hat": b_hat,
            "a_hat": a_hat,
            "Q": inventory.Q,
            "cash": inventory.cash,
            "pnl": inventory.pnl(),
        }

        with open(self.files[strategy], "a") as f:
            f.write(json.dumps(record) + "\n")

    def jsonl_to_csv(self, strategy):
        jsonl_file = self.files[strategy]
        csv_file = jsonl_file.replace(".jsonl", ".csv")

        if not os.path.exists(jsonl_file):
            return

        with open(jsonl_file, "r") as f:
            rows = [json.loads(line) for line in f]

        if not rows:
            return

        with open(csv_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)

        print(f"[LOGGER] Converted {csv_file}")
