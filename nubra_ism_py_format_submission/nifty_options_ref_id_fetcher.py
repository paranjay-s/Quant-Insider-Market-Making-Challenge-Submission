from nubra_python_sdk.refdata.instruments import InstrumentData
from nubra_python_sdk.marketdata.market_data import MarketData

def fetch_instrument_ref_ids(nubra_sdk, nubra_names):
    market_data = MarketData(nubra_sdk)
    instruments = InstrumentData(nubra_sdk)

    ref_ids = []

    for name in nubra_names:
        instrument = instruments.get_instrument_by_nubra_name(name)
        ref_ids.append(instrument.ref_id)

    return ref_ids

def generate_nifty_option_nubra_names():
    expiry = "20260106"
    start_strike = 2050000
    end_strike = 3145000
    step = 5000

    nubra_names = []

    strike = start_strike
    while strike <= end_strike:
        nubra_names.append(f"OPT_NIFTY_{expiry}_CE_{strike}")
        nubra_names.append(f"OPT_NIFTY_{expiry}_PE_{strike}")
        strike += step

    return nubra_names
