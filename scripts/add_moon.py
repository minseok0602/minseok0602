"""3D 잔디 야경 SVG의 왼쪽 위 빈 하늘에만 달이 떠오르는 레이어를 끼워 넣는다.

사용법: python3 scripts/add_moon.py <입력 night-view.svg> <출력 svg>

- 달은 배경 사각형 바로 뒤(3D 막대보다 앞 순서)에 넣어 빌딩 뒤에서 떠오르게 한다.
- clipPath로 범위를 제한해 달과 달빛이 지정한 영역 밖으로 나가지 않는다.
- 다른 요소의 색, 스타일, 필터는 건드리지 않는다.
"""

import re
import sys

# 달이 보이는 범위 (원본 SVG 좌표, 1280x850 기준)
CLIP = {"x": 40, "y": 30, "width": 560, "height": 240}
START = (470, 330)  # 범위 아래쪽 바깥에서 시작 (가려진 상태)
MID = (385, 190)
END = (300, 115)
DURATION = "6s"

MOON = f"""<defs><clipPath id="moonrise-clip"><rect x="{CLIP['x']}" y="{CLIP['y']}" width="{CLIP['width']}" height="{CLIP['height']}" rx="8"/></clipPath></defs>
<g id="moonrise" clip-path="url(#moonrise-clip)">
<g transform="translate({END[0]} {END[1]})">
<animateTransform attributeName="transform" type="translate" values="{START[0]} {START[1]};{MID[0]} {MID[1]};{END[0]} {END[1]}" keyTimes="0;0.5;1" calcMode="spline" keySplines="0.3 0.1 0.6 1;0.2 0.5 0.4 1" dur="{DURATION}" begin="0s" repeatCount="1" fill="freeze"/>
<circle r="84" fill="#f3e9c6" opacity="0.05"/>
<circle r="58" fill="#f3e9c6" opacity="0.10"/>
<circle r="38" fill="#f6ecca"/>
<circle cx="-11" cy="-8" r="7" fill="#e3d6a8"/>
<circle cx="12" cy="6" r="5" fill="#e3d6a8"/>
<circle cx="-3" cy="15" r="4" fill="#e3d6a8"/>
</g>
</g>
"""

BG_RECT = re.compile(r'<rect\b[^>]*class="fill-bg"[^>]*?(?:/>|>\s*</rect>)')


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: add_moon.py <input.svg> <output.svg>")
    src, dst = sys.argv[1], sys.argv[2]

    with open(src, encoding="utf-8") as f:
        svg = f.read()

    if 'id="moonrise"' in svg:
        sys.exit("already contains moonrise layer")

    m = BG_RECT.search(svg)
    if not m:
        sys.exit("background rect (class=fill-bg) not found")

    out = svg[: m.end()] + "\n" + MOON + svg[m.end():]

    with open(dst, "w", encoding="utf-8") as f:
        f.write(out)
    print(f"wrote {dst}")


if __name__ == "__main__":
    main()
