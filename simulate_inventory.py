#!/usr/bin/env python3
"""
simulate_inventory.py  --  HemoSync starter kit
==================================================================
Synthetic Monte-Carlo experiments for a blood-bank network.
  * Standard library only (no installs needed).
  * ALL DATA ARE SYNTHETIC. Nothing here is clinical advice.
  * Purpose: give design intuition and a reproducible evaluation protocol.
    Replace the invented parameters with pilot data before drawing conclusions.

Run:   python simulate_inventory.py
Out:   results.json  (+ a short printed summary)

What is inside
  1. run_single()   : one hospital, availability-vs-wastage trade-off, three
                      issuing habits (RANDOM = "whatever is at the front of the
                      fridge", FIFO, FEFO).
  2. run_network()  : five hospitals, isolated vs. connected (lateral transfers
                      of units that are about to expire).
  3. forecast_backtest(): weekly collections with a school-calendar effect,
                      baseline-first evaluation (naive, seasonal naive,
                      calendar-aware) with 80% prediction intervals.
"""
import json
import math
import random

PRODUCTS = {
    # shelf = total shelf life (days); arrival = remaining life range when a
    # unit reaches the hospital (testing + processing + transport use some days)
    "RBC": dict(shelf=35, arrival=(25, 32), near_expiry=7),
    "PLT": dict(shelf=5, arrival=(3, 4), near_expiry=2),
}


def poisson(lam, rng):
    """Knuth's algorithm. Good enough for the small means used here."""
    limit, k, p = math.exp(-lam), 0, 1.0
    while p > limit:
        k += 1
        p *= rng.random()
    return k - 1


class Hospital:
    def __init__(self, lam, lead, z, policy, product, rng):
        # lead = full days in transit (0 = delivered next morning).  The order-up-to
        # level S protects demand over lead + 1 days (daily review).
        self.lam, self.lead, self.policy, self.rng = lam, lead, policy, rng
        self.arrival = PRODUCTS[product]["arrival"]
        mu = lam * (lead + 1)                       # demand over the protection interval
        self.S = max(1, math.ceil(mu + z * math.sqrt(mu)))   # order-up-to level
        self.stock = []                             # each unit = [remaining_life, arrival_day]
        self.pipeline = []                          # (arrival_day, n_units)
        self.received = self.expired = self.demand = self.issued = 0
        self.inv_sum = 0.0

    # --- daily steps -------------------------------------------------------
    def receive(self, day):
        n = sum(q for d, q in self.pipeline if d == day)
        self.pipeline = [(d, q) for d, q in self.pipeline if d != day]
        for _ in range(n):
            self.stock.append([self.rng.randint(*self.arrival), day])
        self.received += n

    def pick(self):
        idx = range(len(self.stock))
        if self.policy == "FEFO":
            return min(idx, key=lambda i: self.stock[i][0])
        if self.policy == "FIFO":
            return min(idx, key=lambda i: self.stock[i][1])
        return self.rng.randrange(len(self.stock))      # RANDOM

    def serve(self, d):
        self.demand += d
        served = 0
        while served < d and self.stock:
            self.stock.pop(self.pick())
            served += 1
        self.issued += served
        return d - served                                # shortage

    def end_of_day(self, day):
        for u in self.stock:
            u[0] -= 1
        alive = [u for u in self.stock if u[0] > 0]
        self.expired += len(self.stock) - len(alive)
        self.stock = alive
        self.inv_sum += len(self.stock)
        position = len(self.stock) + sum(q for _, q in self.pipeline)
        if position < self.S:
            self.pipeline.append((day + 1 + self.lead, self.S - position))


def _snapshot(hs):
    return [(h.received, h.expired, h.demand, h.issued, h.inv_sum) for h in hs]


def _delta(hs, snap):
    rec = sum(h.received - s[0] for h, s in zip(hs, snap))
    exp = sum(h.expired - s[1] for h, s in zip(hs, snap))
    dem = sum(h.demand - s[2] for h, s in zip(hs, snap))
    iss = sum(h.issued - s[3] for h, s in zip(hs, snap))
    inv = sum(h.inv_sum - s[4] for h, s in zip(hs, snap))
    return rec, exp, dem, iss, inv


def run_network(lams, product, lead, z, policy, pooled, days=900, warmup=60,
                seed=1, reserve_frac=0.5, max_moves=1):
    """Returns dict(fill, expiry, avg_stock, transfers_per_day)."""
    rng = random.Random(seed)
    hs = [Hospital(l, lead, z, policy, product, rng) for l in lams]
    life0 = PRODUCTS[product]["arrival"]
    for h in hs:                                         # warm start
        h.stock = [[rng.randint(*life0), 0] for _ in range(h.S)]
    near = PRODUCTS[product]["near_expiry"]
    transfers, snap, t0 = 0, None, 0
    for day in range(days):
        if day == warmup:
            snap, t0 = _snapshot(hs), transfers
        for h in hs:
            h.receive(day)
        shortages = [h.serve(poisson(h.lam, rng)) for h in hs]
        if pooled:
            # (a) lateral transshipment to cover a stock-out, FEFO from donors
            for i, short in enumerate(shortages):
                if short <= 0:
                    continue
                donors = sorted((j for j in range(len(hs)) if j != i),
                                key=lambda j: -(len(hs[j].stock) - hs[j].lam))
                for j in donors:
                    reserve = math.ceil(reserve_frac * hs[j].lam)
                    while short > 0 and len(hs[j].stock) > reserve:
                        k = min(range(len(hs[j].stock)), key=lambda x: hs[j].stock[x][0])
                        hs[j].stock.pop(k)
                        hs[i].issued += 1
                        short -= 1
                        transfers += 1
            # (b) move units that are about to expire to the "hungriest" hospital
            for j, hj in enumerate(hs):
                moved = 0
                for u in sorted((u for u in hj.stock if u[0] <= near), key=lambda u: u[0]):
                    if moved >= max_moves:
                        break
                    dos_j = len(hj.stock) / hj.lam
                    cands = [r for r in range(len(hs)) if r != j and len(hs[r].stock) < hs[r].S]
                    if not cands:
                        break
                    r = min(cands, key=lambda r: len(hs[r].stock) / hs[r].lam)
                    if len(hs[r].stock) / hs[r].lam >= dos_j:
                        continue
                    hj.stock.remove(u)
                    hs[r].stock.append([u[0], day])
                    moved += 1
                    transfers += 1
        for h in hs:
            h.end_of_day(day)
    rec, exp, dem, iss, inv = _delta(hs, snap)
    n_days = days - warmup
    return dict(fill=iss / dem, expiry=exp / max(rec, 1),
                avg_stock=inv / n_days, transfers_per_day=(transfers - t0) / n_days)


def run_single(lam, product, lead, z, policy, reps=40, days=900):
    fills, exps = [], []
    for r in range(reps):
        res = run_network([lam], product, lead, z, policy, False, days=days, seed=1000 + r)
        fills.append(res["fill"])
        exps.append(res["expiry"])
    return sum(fills) / reps, sum(exps) / reps


# ---------------------------------------------------------------------------
# Forecast back-test on a synthetic weekly "collections" series
# ---------------------------------------------------------------------------
def school_holiday(week_of_year):
    """Reported pattern: students (about 80% of donors) are away in April, August
    and December. Approximated as weeks 14-17, 32-35 and 48-52 + 1-2."""
    w = week_of_year
    return (14 <= w <= 17) or (32 <= w <= 35) or (w >= 48) or (w <= 2)


def make_series(weeks=260, base=1000.0, holiday_effect=-0.35, trend=0.05, noise=0.07, seed=7):
    rng = random.Random(seed)
    y, hol = [], []
    for t in range(weeks):
        woy = (t % 52) + 1
        h = school_holiday(woy)
        level = base * (1 + trend * t / 52)
        v = level * (1 + holiday_effect * h)
        v *= 1 + rng.gauss(0, noise)
        if rng.random() < 0.05:                          # occasional big drive
            v *= 1.2
        y.append(v)
        hol.append(h)
    return y, hol


def forecast_backtest(h=4, start=104, weeks=260):
    y, hol = make_series(weeks)
    out = dict(week=[], actual=[], naive=[], snaive=[], calendar=[], lo=[], hi=[], holiday=[])
    errs_ratio = []                                  # (target_week, actual/forecast)
    for t in range(start, weeks - h + 1):
        target = t + h - 1                               # forecast made after seeing y[:t]
        hist_y, hist_h = y[:t], hol[:t]
        # calendar-aware: learn holiday factor from trailing 104 weeks, EWMA level
        win = slice(max(0, t - 104), t)
        hv = [v for v, f in zip(hist_y[win], hist_h[win]) if f]
        tv = [v for v, f in zip(hist_y[win], hist_h[win]) if not f]
        factor = (sum(hv) / len(hv)) / (sum(tv) / len(tv))
        level, alpha = None, 0.2
        for v, f in zip(hist_y[-26:], hist_h[-26:]):
            d = v / (factor if f else 1.0)
            level = d if level is None else alpha * d + (1 - alpha) * level
        cal = level * (factor if hol[target] else 1.0)
        naive = hist_y[-1]
        snaive = y[target - 52]
        known = [r for tw, r in errs_ratio if tw < t]       # no peeking into the future
        if len(known) >= 20:
            r = sorted(known[-52:])
            lo, hi = cal * r[int(0.1 * (len(r) - 1))], cal * r[int(0.9 * (len(r) - 1))]
        else:
            lo, hi = cal * 0.85, cal * 1.15
        errs_ratio.append((target, y[target] / cal))
        for k, v in zip(out, [target, y[target], naive, snaive, cal, lo, hi, int(hol[target])]):
            out[k].append(v)

    def wape(key):
        return sum(abs(a - f) for a, f in zip(out["actual"], out[key])) / sum(out["actual"])
    cover = sum(l <= a <= u for a, l, u in zip(out["actual"], out["lo"], out["hi"])) / len(out["actual"])
    # skip the first 20 forecasts (interval warm-up) when quoting coverage
    c2 = sum(l <= a <= u for a, l, u in zip(out["actual"][20:], out["lo"][20:], out["hi"][20:])) / len(out["actual"][20:])
    return dict(series=out, wape=dict(naive=wape("naive"), snaive=wape("snaive"), calendar=wape("calendar")),
                coverage80=c2, n=len(out["actual"]), horizon_weeks=h)


# ---------------------------------------------------------------------------
def order_up_to(lam, lead, z):
    """The same formula the Hospital class uses (shown here so you can print it)."""
    mu = lam * (lead + 1)
    return max(1, math.ceil(mu + z * math.sqrt(mu)))


def _avg(runs):
    return {k: sum(r[k] for r in runs) / len(runs) for k in runs[0]}


if __name__ == "__main__":
    results = {}
    zs = [0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0]

    # 1) Availability-vs-wastage frontier for ONE hospital.
    cases = {
        "RBC_rare_group": dict(lam=0.4, product="RBC", lead=2, policies=("RANDOM", "FIFO", "FEFO")),
        "PLT_small_hospital": dict(lam=1.5, product="PLT", lead=1, policies=("RANDOM", "FIFO", "FEFO")),
    }
    results["frontier"] = {}
    for name, c in cases.items():
        entry = dict(z=zs, S=[order_up_to(c["lam"], c["lead"], z) for z in zs], lam=c["lam"], lead=c["lead"])
        for pol in c["policies"]:
            pts = [run_single(c["lam"], c["product"], c["lead"], z, pol, reps=40) for z in zs]
            entry[pol] = [dict(fill=f, expiry=e) for f, e in pts]
        results["frontier"][name] = entry

    # 2) Network effect: five hospitals sharing one blood group / component.
    net_cases = {
        "RBC": dict(lams=[0.4, 0.8, 1.5, 3.0, 6.0], lead=2, z=1.0),
        "PLT": dict(lams=[0.5, 1.0, 2.0, 3.0, 5.0], lead=1, z=1.0),
    }
    results["network"] = {}
    for prod, c in net_cases.items():
        entry = dict(lams=c["lams"], lead=c["lead"], z=c["z"])
        for name, (pol, pooled) in {"isolated_random": ("RANDOM", False),
                                    "isolated_fefo": ("FEFO", False),
                                    "connected_fefo": ("FEFO", True)}.items():
            runs = [run_network(c["lams"], prod, c["lead"], c["z"], pol, pooled, seed=500 + r) for r in range(30)]
            entry[name] = _avg(runs)
        results["network"][prod] = entry

    # 3) Forecasting back-test on a synthetic weekly collections series.
    results["forecast_1w"] = forecast_backtest(h=1)
    results["forecast_4w"] = forecast_backtest(h=4)

    with open("results.json", "w") as f:
        json.dump(results, f)

    print("== Frontier (one hospital): fill% / expiry% at each safety factor z ==")
    for name, e in results["frontier"].items():
        print(name, "lam=", e["lam"], "lead=", e["lead"], "S=", e["S"])
        for pol in ("RANDOM", "FIFO", "FEFO"):
            row = "  ".join(f"{p['fill']*100:5.1f}/{p['expiry']*100:5.1f}" for p in e[pol])
            print(f"  {pol:6s} {row}")
    print("== Network (5 hospitals) ==")
    for prod, e in results["network"].items():
        print(prod, "lams=", e["lams"], "lead=", e["lead"], "z=", e["z"])
        for k in ("isolated_random", "isolated_fefo", "connected_fefo"):
            v = e[k]
            print(f"  {k:16s} fill={v['fill']*100:5.1f}%  expiry={v['expiry']*100:5.1f}%  "
                  f"avg_stock={v['avg_stock']:.1f}  lateral moves/day={v['transfers_per_day']:.2f}")
    for k in ("forecast_1w", "forecast_4w"):
        fw = results[k]
        print(k, "WAPE %:", {m: round(v * 100, 1) for m, v in fw["wape"].items()},
              " 80% interval coverage:", round(fw["coverage80"] * 100, 1), "% (n =", fw["n"], ")")
