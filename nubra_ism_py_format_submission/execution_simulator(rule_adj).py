

RELAX_TICKS = 1.8         # allow 1 tick relaxation
RELAX_EPS = RELAX_TICKS * TICK_SIZE

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

        # BUY (relaxed)
        if b_hat is not None and b_hat >= at - RELAX_EPS:
            if inventory.on_buy(at):
                trade = ("BUY", at)

        # SELL (relaxed)
        elif a_hat is not None and a_hat <= bt + RELAX_EPS:
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

            # Optional print
            print(
                f"[{strategy_name}] {side} @ {price} | "
                f"Q={inventory.Q} PnL={inventory.pnl():.2f}"
            )

        return trade
