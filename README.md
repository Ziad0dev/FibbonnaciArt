# FibbonnaciArt
Deriving art pieces with the Fibonacci sequence as a constraint.
### Spelling fibonacci with 2 b's to differ from other projects.

`src/main.py` generates SVG art where every decision comes from the sequence. No dependencies.

| Piece | Constraint |
| --- | --- |
| `phyllotaxis` | 987 seeds placed at multiples of the golden angle (137.5°), radius ∝ √k. The spiral arms come in Fibonacci counts; seeds at Fibonacci indices are drawn larger, colors cycle in 34 bands |
| `spiral` | Fibonacci rectangle tiling (squares of side 1, 1, 2, 3, 5, …) with the golden spiral through it |
| `pisano` | cell (r, c) = F(r)·F(c) mod m; the image repeats with the Pisano period of m |
| `word` | the Fibonacci word fractal: walk the infinite Fibonacci word, turning on each `0`; curve length F(n), colored in Fibonacci-length segments |

Palettes have 5 or 8 colors.

```sh
python src/main.py gallery                 # all pieces + index.html in gallery/
python src/main.py phyllotaxis --palette ocean -o sunflower.svg
python src/main.py pisano --modulus 13
python src/main.py word --order 23 --seed 42
```

`api/api.py` is an earlier experiment against a text-to-image API that no longer exists.
