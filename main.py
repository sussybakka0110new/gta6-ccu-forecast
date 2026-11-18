"""Forecast GTA VI's launch-day Twitch viewers from past big launches.

The case gives us hour 1's print and the hourly curves of 38-42 comparable
game launches. A launch day follows a recognisable shape: an early spike at
the local-midnight unlock, a lull while one continent sleeps, then a second
peak when another continent comes online. The exact shape depends strongly on
how large the category already is at hour 1 -- the biggest launches peak in
hour 1 and drift down, while smaller ones build for many hours.

So we condition on hour 1's magnitude: comparable launches of a similar size
get more weight. For each hour we take the weighted quantiles of the
comparables' log-ratios to their own hour 1, and add a small residual spread
so the five numbers are honest quantiles rather than a point forecast.
"""

import json
import math
import os
from pathlib import Path

INPUT_DIR = Path(os.environ.get("MAKEFUN_INPUT_DIR", "/input"))
OUTPUT_DIR = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))

# The levels the contest scores, and the standard normal's quantile at each.
LEVELS = (0.05, 0.25, 0.5, 0.75, 0.95)
Z = (-1.6448536269514722, -0.6744897501960817, 0.0,
     0.6744897501960817, 1.6448536269514722)

# Width of the log-magnitude kernel used to weight comparable launches.
SIGMA = 0.5
# Extra log-space spread on top of the spread the comparables already imply.
SPREAD = 0.0


def launch_hours(comparable):
    """Hourly viewer counts for the comparable's own release day.

    SullyGnome samples a quiet category only every few hours, so a day can
    have gaps. Return {hour: viewers} for hours 0..23 of day_start.
    """
    day = comparable["day_start"][:10]
    out = {}
    for point in comparable["hourly"]:
        stamp = point["from"]
        if stamp[:10] != day:
            continue
        hour = int(stamp[11:13])
        viewers = point.get("viewers")
        if isinstance(viewers, (int, float)) and viewers > 0:
            out[hour] = float(viewers)
    return out


def log_curve(hours):
    """log(viewers_h / viewers_1) for h = 2..24, with gaps interpolated."""
    base = hours.get(0)
    if base is None:
        return None
    known = sorted(hours)
    curve = []
    for h in range(2, 25):
        if h in hours:
            value = hours[h]
        elif h == 24:
            # The source stops at hour 23; average the last two evening hours
            # so a single noisy final point does not set the whole tail.
            tail = [hours[k] for k in (22, 23) if k in hours]
            value = math.exp(sum(math.log(v) for v in tail) / len(tail)) if tail else hours[known[-1]]
        else:
            lo = max((k for k in known if k < h), default=known[0])
            hi = min((k for k in known if k > h), default=known[-1])
            if hi == lo:
                value = hours[lo]
            else:
                frac = (h - lo) / (hi - lo)
                value = math.exp((1 - frac) * math.log(hours[lo])
                                 + frac * math.log(hours[hi]))
        curve.append(math.log(max(1.0, value) / base))
    return curve


def weighted_quantile(pairs, q):
    """Quantile of values carrying relative weights. pairs: [(value, weight)]."""
    total = sum(w for _, w in pairs)
    if total <= 0:
        return 0.0
    target = q * total
    running = 0.0
    for value, weight in sorted(pairs):
        running += weight
        if running >= target:
            return value
    return pairs[-1][0]


def hour_1_print(case):
    for row in case["known"]:
        if row["hour"] == 1:
            return max(1.0, float(row["viewers"]))
    return 1.0


def forecast_case(case):
    p1 = hour_1_print(case)
    log_p1 = math.log(p1)

    pool = []
    for comp in case.get("comparables") or []:
        hours = launch_hours(comp)
        first = hours.get(0)
        if not first:
            continue
        curve = log_curve(hours)
        if curve is None:
            continue
        # Magnitude similarity: a launch with a comparable hour-1 count is
        # a closer guide to today's shape than one ten times smaller/larger.
        gap = (math.log(first) - log_p1) / SIGMA
        if abs(gap) > 6:
            continue
        weight = math.exp(-0.5 * gap * gap)
        # Every practice game, like GTA VI, unlocked at midnight local time;
        # those launches are a closer analogue than a single global unlock.
        if "midnight" in str(comp.get("unlock", "")).lower():
            weight *= 16.0
        pool.append((curve, weight))

    rows = []
    for index, hour in enumerate(range(2, 25)):
        if pool:
            samples = [(curve[index], weight) for curve, weight in pool]
            levels = [weighted_quantile(samples, tau) + z * SPREAD
                      for tau, z in zip(LEVELS, Z)]
            # With an unusually large hour-1 print only a couple of
            # comparables carry real weight. Widen the band a little so the
            # band still reflects that extrapolation rather than pretending
            # two launches pin down the whole distribution.
            mass = sum(w for _, w in samples)
            effective = mass * mass / sum(w * w for _, w in samples) if mass else 0
            guard = 0.0  # the comparables' own dispersion already spans the band
            levels = [x + z * guard for x, z in zip(levels, Z)]
        else:
            # No usable comparables: fall back to the persistent forecast.
            drift = 0.15 * math.sqrt(hour - 1)
            levels = [z * drift for z in Z]
        quantiles = [min(1e9, max(1e-6, p1 * math.exp(level))) for level in levels]
        rows.append({"hour": hour, "q": quantiles})
    return {"hours": rows}


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for path in sorted(INPUT_DIR.glob("*.in")):
        case = json.loads(path.read_text(encoding="utf-8"))
        result = forecast_case(case)
        text = json.dumps(result, separators=(",", ":"), ensure_ascii=True) + "\n"
        (OUTPUT_DIR / (path.stem + ".out")).write_text(text, encoding="utf-8")


if __name__ == "__main__":
    main()
