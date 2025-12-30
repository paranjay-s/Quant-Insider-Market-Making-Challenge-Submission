
from trade_logger import TradeLogger
from inventory_manager import InventoryManager

class ExecutionSimulator:
    def __init__(self, logger: TradeLogger):
        self.logger = logger
    def try_execute(
        self,
        b_hat,
        a_hat,
        bt,
        at,
        inventory: InventoryManager,
        strategy_name=""
    ):
        trade = None

        # BUY
        if b_hat is not None and b_hat >= at:
            if inventory.on_buy(at):
                trade = ("BUY", at)

        # SELL
        elif a_hat is not None and a_hat <= bt:
            if inventory.on_sell(bt):
                trade = ("SELL", bt)

        if trade is not None:
            side, price = trade
            
            self.logger.log_trade(
                strategy=strategy_name,
                side=side,
                price=price,
                bt=bt,
                at=at,
                b_hat=b_hat,
                a_hat=a_hat,
                inventory=inventory,
            )
            
            print(
                f"[{strategy_name}] {side} @ {price} | "
                f"Q={inventory.Q} Cash={inventory.cash:.2f} "
                f"PnL={inventory.pnl():.2f}"
            )

        return trade
