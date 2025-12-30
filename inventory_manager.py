class InventoryManager:
    def __init__(self, Qmax):
        self.Q = 0
        self.cash = 0.0
        self.Qmax = Qmax
        self.mid_price = None

    def update_mid_price(self, mt):
        self.mid_price = mt

    def can_buy(self):
        return self.Q < self.Qmax

    def can_sell(self):
        return self.Q > -self.Qmax

    def on_buy(self, price):
        if not self.can_buy():
            return False
        self.Q += 1
        self.cash -= price
        return True

    def on_sell(self, price):
        if not self.can_sell():
            return False
        self.Q -= 1
        self.cash += price
        return True

    def pnl(self):
        if self.mid_price is None:
            return self.cash
        return self.cash + self.Q * self.mid_price
