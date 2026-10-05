"""Oráculo: implementação de referência (NÃO SOLID, propositalmente procedural) das regras
de references/regras.md. Gera references/expected_week41.json, usado como teste golden.
Uso: python .claude/skills/dominio-alocacao/scripts/oracle.py <seed.json> <saida.json>
"""
import json, math, sys
from collections import defaultdict

S = json.load(open(sys.argv[1]))
P = S["policies"]; W = P["forecast_weights"]; H = P["horizon_weeks"]
cur = S["current_week"]["iso_week"]
stores = {s["id"]: s for s in S["stores"]}
skus = {k["id"]: k for k in S["skus"]}
grids = S["size_grids"]
sales = defaultdict(dict)
for r in S["sales_history"]:
    sales[(r["store"], r["sku"], r["size"])][r["week"]] = r["qty"]
stock = {(r["store"], r["sku"], r["size"]): r["qty"] for r in S["stock"]}
dc = {(r["sku"], r["size"]): r["qty"] for r in S["dc_stock"]}


def event_uplift(store, sku):
    u = 0.0
    for e in S["events"]:
        if store in e["stores"] and e["start_week"] <= cur + H - 1 and e["end_week"] >= cur:
            u += e["uplift_by_category"].get(skus[sku]["category"], 0.0)
    return u


def signal_uplift(store, sku, size):
    t = 0.0
    for sg in S["signals"]:
        if sg["store"] != store:
            continue
        for a in sg["interpreted"]["adjustments"]:
            if a["pct"] > P["signal_max_auto_adjust_pct"]:
                continue
            if a["scope"] in ("all", sku, f"{sku}:{size}"):
                t += a["pct"] / 100
    return t


def weekly_forecast(store, sku, size):
    k = skus[sku]
    if k.get("launch_week"):
        refs = [r["qty_first_2_weeks"] for r in S["reference_sales"]
                if r["store"] == store and r["size"] == size and r["reference_sku"] in k["similar_skus"]]
        return (sum(refs) / len(refs)) / 2 if refs else 0.0
    h = sales[(store, sku, size)]
    return sum(w * h.get(cur - 1 - i, 0) for i, w in enumerate(W))


lines = {}
for (st, sk, z), q in sorted(stock.items()):
    wk = weekly_forecast(st, sk, z)
    f2 = wk * H * (1 + event_uplift(st, sk) + signal_uplift(st, sk, z))
    mind = P["min_display_basic"] if skus[sk]["is_basic"] else P["min_display_other"]
    L = dict(store=st, sku=sk, size=z, stock=q, weekly_forecast=round(wk, 4), forecast_horizon=round(f2, 4),
             target=0, need=0, excess=0, dc_allocated=0, transfer_in=0, transfer_out=0, status="ok")
    if q < 0:
        L["status"] = "blocked"
    else:
        L["target"] = max(mind, math.ceil(f2 * P["cover_factor"]))
        n = L["target"] - q
        if n > 0:
            L["need"] = n
        elif q > f2 * P["excess_trigger_factor"]:
            L["excess"] = math.floor(q - f2 * P["excess_keep_factor"])
    L["_f2"] = f2; L["_wk"] = wk
    lines[(st, sk, z)] = L

transfers = []
by = defaultdict(list)
for L in lines.values():
    by[(L["sku"], L["size"])].append(L)
for key in sorted(by):
    ls = by[key]
    pos = [L for L in ls if L["need"] > 0]
    tot = sum(L["need"] for L in pos)
    avail = dc[key]
    if tot <= avail:
        for L in pos:
            L["dc_allocated"] = L["need"]
        continue
    for L in pos:
        L["dc_allocated"] = math.floor(L["need"] * avail / tot)
    rest = avail - sum(L["dc_allocated"] for L in pos)
    for L in sorted(pos, key=lambda L: (-(L["need"] - L["dc_allocated"]), L["store"]))[:rest]:
        L["dc_allocated"] += 1
    for L in sorted(pos, key=lambda L: (-(L["_f2"] - L["stock"] - L["dc_allocated"]), L["store"])):
        short = L["need"] - L["dc_allocated"]
        cover = (L["stock"] + L["dc_allocated"]) / L["_wk"] if L["_wk"] else float("inf")
        if short <= 0 or cover >= H:
            continue
        srcs = [s for s in ls if s["excess"] - s["transfer_out"] > 0 and s["_wk"]
                and s["stock"] / s["_wk"] > P["transfer_min_source_cover_weeks"]]
        for s in sorted(srcs, key=lambda s: (-(s["excess"] - s["transfer_out"]), s["store"])):
            qty = min(s["excess"] - s["transfer_out"], short)
            if qty <= 0:
                continue
            s["transfer_out"] += qty; L["transfer_in"] += qty; short -= qty
            transfers.append(dict(sku=key[0], size=key[1], source=s["store"], destination=L["store"], qty=qty))
            if short <= 0:
                break

exceptions = []
# 1 lançamento
for k in skus.values():
    if k.get("launch_week") and cur - k["launch_week"] < P["launch_approval_weeks"]:
        per = {st: sum(L["need"] for L in lines.values() if L["sku"] == k["id"] and L["store"] == st) for st in sorted(stores)}
        exceptions.append(dict(rule="launch_approval", severity="critical", sku=k["id"], stores=per))
# 2 transferências agrupadas por sku×tamanho×origem
grp = defaultdict(list)
for t in transfers:
    grp[(t["sku"], t["size"], t["source"])].append({"destination": t["destination"], "qty": t["qty"]})
for (sk, z, src), d in sorted(grp.items()):
    exceptions.append(dict(rule="stockout_transfer", severity="high", sku=sk, size=z, source=src, destinations=d))
# 3 sinal acima do limite
for sg in S["signals"]:
    for a in sg["interpreted"]["adjustments"]:
        if a["pct"] > P["signal_max_auto_adjust_pct"]:
            exceptions.append(dict(rule="signal_divergence", severity="high", signal_id=sg["id"], store=sg["store"], requested_pct=a["pct"], scope=a["scope"]))
# 4 queda sazonal
for k in sorted(skus.values(), key=lambda k: k["id"]):
    if k.get("launch_week"):
        continue
    hit = []
    for st in sorted(stores):
        sz = grids[k["size_grid"]]
        h = [sum(sales[(st, k["id"], z)].get(w, 0) for z in sz) for w in range(cur - 6, cur)]
        prev, last = sum(h[:3]), sum(h[3:])
        stq = sum(stock[(st, k["id"], z)] for z in sz)
        wk = sum(lines[(st, k["id"], z)]["_wk"] for z in sz)
        if prev and (prev - last) / prev * 100 >= P["seasonal_decline_pct"] and wk and stq / wk >= P["seasonal_min_cover_weeks"]:
            hit.append(st)
    if len(hit) >= P["seasonal_min_stores"]:
        exceptions.append(dict(rule="seasonal_decline", severity="medium", sku=k["id"], stores=hit))
# 5 curva de tamanho
for k in sorted(skus.values(), key=lambda k: k["id"]):
    if k.get("launch_week"):
        continue
    sz = grids[k["size_grid"]]; std = S["standard_size_curves"][k["size_grid"]]
    for st in sorted(stores):
        tot = [sum(sales[(st, k["id"], z)].get(w, 0) for w in range(cur - P["size_curve_weeks"], cur)) for z in sz]
        T = sum(tot)
        if T < P["size_curve_min_units"]:
            continue
        dev = [abs(t / T - c) * 100 for t, c in zip(tot, std)]
        if sum(d >= P["size_curve_deviation_pp"] for d in dev) >= P["size_curve_min_sizes"]:
            exceptions.append(dict(rule="size_curve_deviation", severity="medium", store=st, sku=k["id"]))
# 6 estoque negativo
for L in lines.values():
    if L["status"] == "blocked":
        exceptions.append(dict(rule="negative_stock", severity="medium", store=L["store"], sku=L["sku"], size=L["size"]))
# 7 rejeição repetida
rej = defaultdict(int)
for d in S["decision_history"]:
    if d["action"] == "reject":
        rej[(d["store"], d["sku"])] += 1
for (st, sk), n in sorted(rej.items()):
    if n >= P["repeated_rejection_count"]:
        exceptions.append(dict(rule="repeated_rejection", severity="low", store=st, sku=sk, rejections=n))
# 8 limite de valor (lojas próprias, linhas não cobertas por outra exceção)
covered = {(L["store"], L["sku"]) for L in lines.values() if any(e.get("sku") == L["sku"] and e["rule"] == "launch_approval" for e in exceptions)}
for st in sorted(stores):
    if stores[st]["ownership"] != "own":
        continue
    v = sum(L["dc_allocated"] * skus[L["sku"]]["price"] for L in lines.values() if L["store"] == st and (st, L["sku"]) not in covered)
    if v > P["auto_execution_max_value_brl"]:
        exceptions.append(dict(rule="auto_execution_limit", severity="medium", store=st, value_brl=round(v, 2)))

out = dict(total_lines=len(lines),
           lines=[{k: v for k, v in L.items() if not k.startswith("_")} for L in lines.values()],
           transfers=transfers, exceptions=exceptions)
json.dump(out, open(sys.argv[2], "w"), ensure_ascii=False, indent=1)
print(len(lines), "linhas;", len(exceptions), "exceções:", [e["rule"] for e in exceptions])
print("transfers", transfers)
