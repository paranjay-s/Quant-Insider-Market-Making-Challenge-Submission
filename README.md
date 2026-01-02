# Quant-Insider-Market-Making-Challenge-Submission
# -by Indian Institute of Technology, Indian School of Mines (IIT ISM), Dhanbad

---

## Index
0. Quick Overview of the Whole Project
1. Competition Context    
2. Important Notes, Outputs, and Data Files       ***(Read this before, for correct interpretation of the output CSV files)***
3. Visual Plots and Analysis  
4. High-Level Execution Flow
5. Strategy Idea and Task  
   - A) Strategies (Baseline & Adaptive)  
   - B) Parameters  
   - C) Assumptions
6. Code Structure and File-wise Working  
7. Next Steps  
8. Competition Experience

---

## 0. Quick Overview of the Whole Project

- Built a real-time market making system for NIFTY options using live order book data via Nubra Python SDK  
- Compared a baseline static-spread strategy with an adaptive Avellaneda–Stoikov–based strategy  
- Used real-time 5-level depth data via WebSocket (prices, volumes, imbalance)  
- Simulated executions, tracked inventory, cash, and mark-to-market PnL  
- Logged trades and market states for both strategies on live data  
- Performed post-trade analysis and visualization to compare performance

## 1. Competition Context

This project was developed as part of a **Market Making Simulation Challenge** conducted in collaboration with **Quant Insider and IIT ISM (IIT Dhanbad)**.

- Environment: **UAT (User Acceptance Testing)**
- Market data: **Real-time live market data**
- Asset class: **NIFTY options**
- Nature of results: **Real trade logs generated on live market data**

The system uses the **Nubra Python SDK**, leveraging APIs for:
- Authentication and environment selection
- Instrument reference data
- Real-time WebSocket order book feeds
- Market quotes and depth data

Although order execution was simulated, **all market data used was live**, meaning the trade logs and PnL behavior reflect real market conditions.

---

## 2. Important Notes, Outputs, and Data Files

**IMPORTANT:**  
**All prices used throughout the project are in paise, not rupees.**

### Note on Execution Rule Adjustment

- The original execution rule was very strict and resulted in no trades on live market data  
- Due to time and hardware constraints, a tiny price tolerance (a few ticks) was added when checking buy/sell conditions   
- The change affects **only execution simulation**, not strategy logic or market data  
- For testing, `execution_simulator(rule_adj).py` was used instead of `execution_simulator.py`  
- Both versions are included in the `nubra_ism_py_format_submission` folder for correct interpretation of the output CSV files  


### Code Availability
- Full solution provided in:
  - Jupyter Notebook format     in  "nubra_ism_jupyter_notebook_"
  - Clean, modular `.py` files  in  "nubra_ism_py_format_submission"
Users may use either format.

### Output Files

- `baseline_trades.csv`  
  Trade log for baseline strategy

- `adaptive_trades.csv`  
  Trade log for adaptive strategy

- `pnl_status.json`  
  Final session snapshot (PnL, inventory, quotes, market state)

- `latest_orderbooks.json`  
  Continuously updated snapshot of the latest WebSocket order book data

---

## 3. Visual Plots and Analysis

All plots are generated in `visualizer.ipynb`.

Plots include:
- PnL curves (Baseline vs Adaptive)
- Inventory over time
- Drawdown comparison
- Strategy performance metrics
  
<img width="1011" height="1372" alt="nbs" src="https://github.com/user-attachments/assets/390839fd-0c95-4a7a-b96a-615ff1feb287" />


## 4. High-Level Execution Flow

1. Authenticate using the Nubra API  
2. Fetch NIFTY option instruments (CE and PE across ITM, ATM, and OTM strikes)  
3. Start the WebSocket to receive real-time order book data  
4. Maintain the latest order book snapshot in shared memory  
5. Run baseline and adaptive strategies in parallel  
6. Simulate executions based on quote crossing logic  
7. Log trades and mark-to-market PnL  
8. Convert trade logs from JSONL to CSV format  
9. Visualize results using the analysis notebook  

---
## 5. Strategy Idea and Task

The objective is to **compare a simple baseline market-making strategy against an adaptive market-making strategy**, inspired by professional trading models.

The quoting equations are based on the **Avellaneda–Stoikov market-making model**, which is widely used by professional trading firms.

### Notation Used

- `bt` = Best bid  
- `at` = Best ask  
- `V_bt` = Volume at best bid  
- `V_at` = Volume at best ask  
- `s0` = Static spread = `2 × tick size`  
- `st` = Adaptive spread = `s0 (1 + α |I_t|)`  
- `I_t` = Imbalance signal  
- `b̂` = Quoted (hypothetical) bid  
- `â` = Quoted (hypothetical) ask  
- `Q_t` = Inventory (units / lots)  
- `Qmax` = Maximum allowed inventory  

---

### A) Strategies

#### System Flow (Common to Both Strategies)

1. Authenticate and log in using the Nubra API  
2. Subscribe to **5-level real-time order book data** for NIFTY options  
   - All ITM, ATM, and OTM strikes  
   - Both CE and PE  
   - Expiry: **6 January 2026**
3. From the order book, extract:
   - `bt`, `at`, `V_bt`, `V_at`
4. Compute mid price:
   - m_t = (bt + at) / 2

---

#### a) Baseline Strategy

- Uses a **fixed symmetric spread**
- Quote prices:

b̂ = m_t − (s0 / 2), 

â = m_t + (s0 / 2)

**Execution rules**
1. If `b̂ ≥ at`, place a **buy** at `at`
2. If `â ≤ bt`, place a **sell** at `bt`

This strategy ignores:
- Order book imbalance
- Inventory risk

It serves as a **control benchmark**.

---

#### b) Adaptive Strategy

This strategy adjusts quotes using **order book imbalance and inventory**.

**Imbalance signal**
I_t = (V_bt − V_at) / (V_bt + V_at)
- `I_t ∈ [-1, 1]`
- `|I_t| ∈ [0, 1]`

**Adaptive spread**
s_t = s0 (1 + α |I_t|)

**Quote prices using adaptive strategy**

b̂ = m_t − (s_t / 2) − k*Q_t

â = m_t + (s_t / 2) − k*Q_t

where `|Q_t| ≤ Qmax`

**Execution rules**
1. If `b̂ ≥ at`, place a **buy** at `at`
2. If `â ≤ bt`, place a **sell** at `bt`

---

#### Position and Cash Update (Both Strategies)

- Buy  → `Q += 1`, `Cash -= ask`
- Sell → `Q -= 1`, `Cash += bid`

---

#### PnL Definition (Mark-to-Market)
PnL_t = C_t + Q_t · m_t


Finally, we **plot Adaptive vs Baseline PnL versus time**.

---

### B) Parameters

#### Alpha (α) – Adaptive Spread Parameter

- Controls how much the spread widens when market imbalance increases  
- Higher α makes the strategy more cautious during strong buying or selling pressure  
- Lower α keeps quotes closer to mid price, increasing trade frequency  
- Helps protect against informed or one-sided market moves  
- **Purpose:** widen spread when imbalance is strong  

**Negative α is not allowed.**

---

#### k – Inventory Control Parameter

- Controls how strongly quotes are adjusted based on current inventory  
- Higher k pushes inventory back toward zero more aggressively  
- Lower k allows larger inventory buildup, increasing risk  
- Prevents the market maker from getting stuck with a large position  

**Meaning:** inventory aversion and penalty on large `|Q|`

---

Parameter Selection  
- Attempted grid search on short recorded real-time order book data  
- Results were unstable  
- Final values were selected empirically  
- This section will be improved in future iterations

---

### C) Assumptions

**Supply–Demand Intuition**
- Higher bid volume ⇒ stronger demand  
- Higher ask volume ⇒ stronger supply  
- Spread `(at − bt)` reflects liquidity and uncertainty  

**Imbalance Intuition**
- `|I_t|` small ⇒ tighten spread (high liquidity)  
- `|I_t|` large ⇒ widen spread (adverse-selection risk)  

**Inventory Skew Rule**
b̂_t = m_t − s_t/2 − k Q_t
â_t = m_t + s_t/2 − k Q_t


If long → want to sell faster  
If short → want to buy faster  

---

## 6. Working of the `.py` Files

### `main.py`
- Entry point of the system  
- Defines configuration parameters and shared global state  
- Handles authentication, WebSocket startup, trading lifecycle, and graceful shutdown  

### `nifty_options_ref_id_fetcher.py`
- Generates the NIFTY options instrument universe  
- Fetches instrument `ref_id`s using Nubra reference data APIs  

### `orderbook_websocket_manager.py`
- Manages WebSocket connections for real-time order book data  
- Parses and validates bid/ask levels  
- Maintains the latest L1 snapshot per instrument  
- Periodically writes snapshots to `latest_orderbooks.json`  

### `quote_models.py`
- Implements quote construction logic  
- Contains both baseline and adaptive (Avellaneda–Stoikov inspired) models  

### `inventory_manager.py`
- Tracks inventory, cash, and position limits  
- Computes mark-to-market PnL  
- Enforces maximum inventory constraints  

### `execution_simulator.py`
- Simulates trade execution when quotes cross the order book  
- Updates inventory and cash  
- Acts as a placeholder for real trading APIs  

### `trade_logger.py`
- Logs executed trades in JSONL format  
- Converts JSONL logs into CSV for analysis  

### `trading_engine.py`
- Core trading loop  
- Runs baseline and adaptive strategies concurrently  
- Coordinates quote generation, execution, logging, and PnL snapshots  

---

## 7. Next Steps

- Replace simulated execution logic in `execution_simulator.py`  
- Integrate real trading APIs for live order placement  
- Deploy the adaptive market-making strategy in a real trading environment  

---

## 8. Competition Experience

This was my **second algorithmic trading competition**, but my **first market-making competition**, and that too on **real live market data**.

The competition day was initially scheduled for **31st December**, but on **29th December**, we were notified that it was **preponed to 30th December**.

At that point:

- No ready codebase existed  
- Everything was coded **within live market hours**  
- The system was designed, implemented, and tested on the same day  

Due to laptop constraints:

- Trade logs were recorded twice:
  - **12:00 – 1:00**
  - **2:00 – 3:00**

Additionally:

- The UAT trading API authentication was unstable  
- Execution had to be simulated instead of using the Nubra trading API  

Despite these constraints, building and testing a **market-making strategy on real live data** was a **fabulous and highly educational experience**.
