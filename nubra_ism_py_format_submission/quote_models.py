def compute_baseline_quotes(mt):
    b_hat = mt - S0 / 2
    a_hat = mt + S0 / 2
    return b_hat, a_hat

def compute_adaptive_quotes(mt, V_bt, V_at, Q):
    if V_bt + V_at == 0:
        return None, None, 0.0

    I_t = (V_bt - V_at) / (V_bt + V_at)
    st = S0 * (1 + ALPHA * abs(I_t))

    b_hat = mt - st / 2 - K * Q
    a_hat = mt + st / 2 - K * Q

    return b_hat, a_hat, I_t
