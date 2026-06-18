# Demo assets

Real captures of the pair-cost terminal running locally against the shipped
paper-trade simulation (`start.py`). No mock-ups — every number on screen comes
from the live `/api/stats` and `/api/positions` endpoints.

| File | What it shows |
| --- | --- |
| `dashboard.png` | Full desktop terminal with three demo books — two past the profit line (green) and one still accumulating (red). |
| `dashboard.gif` | The same terminal live: the clock ticks, the feed dot pulses, and `btc_up_15min_002` accumulates fills, nudging its pair cost as the simulator runs. |

## Regenerating

```bash
python3 -m venv .venv && source .venv/bin/activate
pip install fastapi uvicorn
PORT=5108 python start.py        # serves the dashboard on :5108
```

Then point any headless browser at `http://127.0.0.1:5108/` and capture the
`.wrap` element. The images here were taken at a 2× device scale for the still
and downsampled to 980px wide for the animation.
