# Live Volatility Surface

Real-time implied volatility surface visualization and snapshot storage using Interactive Brokers TWS and MySQL.

![Python](https://img.shields.io/badge/Python-3.10%2B-blue)
![IB API](https://img.shields.io/badge/IB%20API-9.76%2B-orange)
![MySQL](https://img.shields.io/badge/MySQL-8.0%2B-green)

---

## What It Does

Connects to your IB TWS session, streams live IV data across strikes and expirations,
and plots a 3D volatility surface with a front-month skew panel. You can lock the display and save snapshots to a MySQL database for later analysis.

---

## Prerequisites

- **Interactive Brokers TWS** running with API enabled
  - Paper trading port: `7497`
  - Live trading port: `7496`
- **Python 3.10+**
- **MySQL 8.0+**

---

## Installation

```bash
git clone <https://github.com/sallahvoice/volatility_surface>
cd live-vol-surface

python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate

pip install -r requirements.txt
```

### requirements.txt
```
ib_insync
mysql-connector-python
pandas
numpy
matplotlib
python-dotenv
```

---

## Configuration

Create a `.env` file in the project root:

```env
DB_HOST=localhost
DB_PORT=3306
DB_USER=your_user
DB_PASSWORD=your_password
DB_NAME=vol_surface
DB_POOL_SIZE=5
DB_POOL_NAME=vol_pool
```

---

## Database Setup

```bash
# 1. Create the database in MySQL
mysql -u your_user -p
> CREATE DATABASE vol_surface;
> EXIT;

# 2. Run migration
python -m db.migrate
```

This creates the `surface_snapshots` and `surface_data_points` tables.

---

## Running

```bash
python live_surface_simple.py
```

By default it runs on **SPY**. To change the ticker, edit the `SYMBOL` variable at the bottom of the file:

```python
if __name__ == "__main__":
    SYMBOL = "AAPL"  # ← change here
```

---

## Controls

| Button | Action |
|--------|--------|
| **LOCK** | Freezes the surface display (useful when rotating the 3D view) |
| **SAVE** | Stores the current surface snapshot to the database |
| **Note field** | Add context before saving (e.g. "pre-FOMC") |

---

## How It Works

```
TWS ──► LiveSurfaceApp ──► iv_dict (live IV data)
                │
                │  SAVE clicked
                ▼
        SnapshotRepo.create_snapshot()      ← metadata
        DataPointRepo.bulk_insert()         ← all IV points
                │
                ▼
            MySQL DB
```

The app inherits both `EClient` (sends requests to TWS) and `EWrapper` (receives callbacks).
IV updates stream into `iv_dict` continuously. When you hit SAVE, it reads the current state and writes everything to the database in two queries.

---

## Querying Snapshots

```python
from db.surface_repo import SnapshotRepo, DataPointRepo

# Recent snapshots
snapshots = SnapshotRepo().get_recent("SPY", limit=5)

# Full surface for a snapshot
points = DataPointRepo().get_for_snapshot(snapshot_id=3)
```

Or directly in MySQL using the included view:

```sql
SELECT * FROM v_surface_full
WHERE symbol = 'SPY'
  AND DATE(captured_at) = CURDATE();
```
