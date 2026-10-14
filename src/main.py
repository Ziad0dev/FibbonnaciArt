#!/usr/bin/env python3
"""Generative art with the Fibonacci sequence as the constraint.

Every piece is derived from Fibonacci numbers: counts, sizes, angles, color
choices and palette lengths all come from the sequence. Output is plain SVG,
no dependencies.

    python src/main.py phyllotaxis -o sunflower.svg
    python src/main.py spiral --palette ember
    python src/main.py pisano --modulus 8
    python src/main.py word --order 21
    python src/main.py gallery            # every piece + index.html in gallery/
"""
import argparse
import math
import random
from pathlib import Path

PHI = (1 + 5 ** 0.5) / 2
GOLDEN_ANGLE = math.tau * (1 - 1 / PHI)  # ~137.508 degrees

# Palettes have a Fibonacci number of colors (5 or 8)
PALETTES = {
    "mondrian": ["#f2f0e6", "#d62828", "#1d3557", "#f4c430", "#111111"],
    "ember": ["#03071e", "#370617", "#6a040f", "#9d0208", "#d00000", "#dc2f02", "#e85d04", "#faa307"],
    "ocean": ["#03045e", "#023e8a", "#0077b6", "#0096c7", "#00b4d8", "#48cae4", "#90e0ef", "#caf0f8"],
    "moss": ["#081c15", "#1b4332", "#2d6a4f", "#40916c", "#52b788", "#74c69d", "#95d5b2", "#d8f3dc"],
}


def fibonacci(n):
    """First n Fibonacci numbers, starting 1, 1, 2, 3, 5, ..."""
    seq = [1, 1]
    while len(seq) < n:
        seq.append(seq[-1] + seq[-2])
    return seq[:n]


def svg(width, height, body, background):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width:.2f} {height:.2f}" '
        f'width="{width:.0f}" height="{height:.0f}">\n'
        f'<rect width="100%" height="100%" fill="{background}"/>\n{body}\n</svg>\n'
    )


def phyllotaxis(palette, rng, points=987, size=800):
    """Sunflower seed head: seed k sits at angle k * golden angle, radius ~ sqrt(k).

    987 is a Fibonacci number; the visible spiral arms come in consecutive
    Fibonacci counts (21, 34, 55...). Seeds on a Fibonacci index are drawn larger.
    """
    fibs = set(fibonacci(20))
    c = size / 2
    scale = (size * 0.46) / math.sqrt(points)
    rot = rng.random() * math.tau
    shapes = []
    for k in range(1, points + 1):
        r = scale * math.sqrt(k)
        a = k * GOLDEN_ANGLE + rot
        x, y = c + r * math.cos(a), c + r * math.sin(a)
        dot = scale * (0.95 if k in fibs else 0.42 + 0.18 * k / points)
        color = palette[(k % 34) * len(palette) // 34]  # 34 bands -> the 34-arm parastichy pops out
        shapes.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{dot:.2f}" fill="{color}"/>')
    return svg(size, size, "\n".join(shapes), palette[0] if palette[0] != palette[-1] else "#000")


def spiral(palette, rng, squares=12):
    """Fibonacci rectangle tiling with the golden spiral drawn through it."""
    fibs = fibonacci(squares)
    unit = 900 / (fibs[-1] + fibs[-2])
    # Grow the tiling: each new square is attached on the next side (right, top, left, bottom)
    x0, y0, x1, y1 = 0.0, 0.0, 1.0, 1.0  # bounding box in Fibonacci units
    tiles = [(0.0, 0.0, 1.0, 0)]
    for i in range(1, squares):
        s = fibs[i]
        side = i % 4
        if side == 1:
            x, y = x1, y0
        elif side == 2:
            x, y = x1 - s, y0 - s
        elif side == 3:
            x, y = x0 - s, y1 - s
        else:
            x, y = x0, y1
        tiles.append((x, y, s, side))
        x0, y0, x1, y1 = min(x0, x), min(y0, y), max(x1, x + s), max(y1, y + s)

    def tx(v):
        return (v - x0) * unit

    def ty(v):
        return (v - y0) * unit

    body, arc = [], []
    colors = palette[1:]
    for i, (x, y, s, side) in enumerate(tiles):
        color = colors[(fibs[i] + rng.randrange(len(colors))) % len(colors)] if rng.random() < 0.6 else palette[0]
        body.append(
            f'<rect x="{tx(x):.2f}" y="{ty(y):.2f}" width="{s * unit:.2f}" height="{s * unit:.2f}" '
            f'fill="{color}" stroke="#111" stroke-width="{max(1.5, 6 - i * 0.4):.2f}"/>'
        )
        # Quarter circle through each square, from the corner shared with the previous square
        r = s * unit
        start, end = {
            0: ((x, y + s), (x + s, y)),
            1: ((x, y), (x + s, y + s)),
            2: ((x + s, y), (x, y + s)),
            3: ((x + s, y + s), (x, y)),
        }[side]
        cmd = "M" if not arc else "L"
        arc.append(f'{cmd}{tx(start[0]):.2f},{ty(start[1]):.2f} A{r:.2f},{r:.2f} 0 0 1 {tx(end[0]):.2f},{ty(end[1]):.2f}')
    body.append(f'<path d="{" ".join(arc)}" fill="none" stroke="#111" stroke-width="4" stroke-linecap="round"/>')
    return svg((x1 - x0) * unit, (y1 - y0) * unit, "\n".join(body), palette[0])


def pisano(palette, rng, modulus=8, n=34, cell=21):
    """Cell (r, c) is F(r) * F(c) mod m. Fibonacci numbers mod m repeat with
    the Pisano period, so the pattern tiles itself with that period."""
    period = pisano_period(modulus)
    fib_mod = [0, 1]
    while len(fib_mod) < n + 1:
        fib_mod.append((fib_mod[-1] + fib_mod[-2]) % modulus)
    offset = rng.randrange(period)
    shapes = []
    for r in range(n):
        for c in range(n):
            v = (fib_mod[(r + offset) % len(fib_mod)] * fib_mod[(c + offset) % len(fib_mod)]) % modulus
            color = palette[v * len(palette) // modulus]
            shapes.append(f'<rect x="{c * cell}" y="{r * cell}" width="{cell}" height="{cell}" fill="{color}"/>')
    shapes.append(
        f'<text x="{n * cell - 8}" y="{n * cell - 8}" text-anchor="end" font-family="monospace" '
        f'font-size="13" fill="#fff" opacity="0.8">F(r)·F(c) mod {modulus} · Pisano period {period}</text>'
    )
    return svg(n * cell, n * cell, "\n".join(shapes), palette[0])


def pisano_period(m):
    a, b = 0, 1
    for i in range(1, 6 * m + 1):
        a, b = b, (a + b) % m
        if (a, b) == (0, 1):
            return i
    raise ValueError(m)


def fibonacci_word(n):
    """The infinite Fibonacci word: S(n) = S(n-1) + S(n-2), S(0)="0", S(1)="01"."""
    a, b = "0", "01"
    while len(b) < n:
        a, b = b, b + a
    return b[:n]


def word(palette, rng, order=21):
    """The Fibonacci word fractal (Monnerot-Dumaine): walk the word, step
    forward at every symbol, and turn on each '0' (left at even positions,
    right at odd). The curve length is a Fibonacci number."""
    length = fibonacci(order)[-1]
    w = fibonacci_word(length)
    x = y = 0
    dx, dy = 1, 0
    pts = [(0, 0)]
    for k, ch in enumerate(w, start=1):
        x, y = x + dx, y + dy
        pts.append((x, y))
        if ch == "0":
            dx, dy = (-dy, dx) if k % 2 == 0 else (dy, -dx)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    pad = 20
    scale = 860 / max(max(xs) - min(xs), max(ys) - min(ys), 1)
    w_px = (max(xs) - min(xs)) * scale + 2 * pad
    h_px = (max(ys) - min(ys)) * scale + 2 * pad
    # Color the curve in Fibonacci-length segments
    fibs = fibonacci(order)
    paths, start, i = [], 0, 0
    while start < len(pts) - 1:
        seg = max(fibs[i % (order // 2)], 8)
        chunk = pts[start:start + seg + 1]
        d = " ".join(f"{(px - min(xs)) * scale + pad:.2f},{(py - min(ys)) * scale + pad:.2f}" for px, py in chunk)
        bright = palette[len(palette) // 2:]  # the darker half would vanish into the background
        paths.append(f'<polyline points="{d}" fill="none" stroke="{bright[i % len(bright)]}" '
                     f'stroke-width="{max(1.5, scale * 0.6):.2f}" stroke-linejoin="round" stroke-linecap="round"/>')
        start += seg
        i += 1
    return svg(w_px, h_px, "\n".join(paths), palette[0])


PIECES = {"phyllotaxis": phyllotaxis, "spiral": spiral, "pisano": pisano, "word": word}


def gallery(out_dir, seed):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    cards = []
    jobs = [
        ("phyllotaxis", "ember", {}), ("phyllotaxis", "ocean", {}),
        ("spiral", "mondrian", {}), ("spiral", "moss", {}),
        ("pisano", "ocean", {"modulus": 8}), ("pisano", "ember", {"modulus": 13}),
        ("word", "moss", {"order": 21}), ("word", "ember", {"order": 18}),
    ]
    for i, (piece, palette, kw) in enumerate(jobs):
        name = f"{i + 1:02d}-{piece}-{palette}.svg"
        (out / name).write_text(PIECES[piece](PALETTES[palette], random.Random(seed + i), **kw))
        cards.append(f'<figure><img src="{name}" alt="{piece}"><figcaption>{piece} · {palette}</figcaption></figure>')
    (out / "index.html").write_text(
        "<!DOCTYPE html><html lang=\"en\"><head><meta charset=\"utf-8\">"
        "<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\"><title>FibbonnaciArt</title>"
        "<style>body{margin:0;padding:16px;background:#111;color:#ddd;font-family:system-ui}"
        "main{display:grid;gap:16px;grid-template-columns:repeat(auto-fill,minmax(280px,1fr))}"
        "img{width:100%;aspect-ratio:1;object-fit:contain;background:#000}figure{margin:0}"
        "figcaption{padding:6px 0;font-size:14px;color:#999}</style></head>"
        f"<body><h1>FibbonnaciArt</h1><main>{''.join(cards)}</main></body></html>\n"
    )
    print(f"wrote {len(jobs)} pieces and index.html to {out}/")


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("piece", choices=[*PIECES, "gallery"])
    parser.add_argument("--palette", choices=PALETTES, default="ember")
    parser.add_argument("--seed", type=int, default=1123)  # 1, 1, 2, 3
    parser.add_argument("-o", "--out", help="output .svg (or directory for gallery)")
    parser.add_argument("--modulus", type=int, default=8, help="pisano: modulus m")
    parser.add_argument("--order", type=int, default=21, help="word: curve length is F(order)")
    args = parser.parse_args()

    if args.piece == "gallery":
        gallery(args.out or "gallery", args.seed)
        return
    kwargs = {"pisano": {"modulus": args.modulus}, "word": {"order": args.order}}.get(args.piece, {})
    out = args.out or f"{args.piece}.svg"
    Path(out).write_text(PIECES[args.piece](PALETTES[args.palette], random.Random(args.seed), **kwargs))
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
