"""3D 잔디 이미지를 프로필용으로 다듬는다.

사용법: python3 scripts/add_moon.py <입력 night-view.svg> <출력 svg>

1) 야경(night-view): 레이더 차트를 빼고, 왼쪽 위 빈 하늘에만 달이 떠오르는 레이어를 넣는다.
   - 달은 배경 사각형 바로 뒤(3D 막대보다 앞 순서)에 넣어 빌딩 뒤에서 떠오르게 한다.
   - clipPath로 범위를 제한해 달과 달빛이 지정한 영역 밖으로 나가지 않는다.
   - 다른 요소의 색, 스타일, 필터는 건드리지 않는다.
2) 라이트 모드용: 같은 폴더의 profile-green-animate.svg가 있으면 레이더 차트만 뺀
   profile-green-clean.svg를 함께 만든다.
"""

import os
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


# 레이더 차트 그룹은 <g transform="translate(...)"> 바로 안에 <line>이 오는 유일한 그룹이다.
RADAR_START = re.compile(r'<g transform="translate\([^)]*\)">\s*<line\b')
G_TAG = re.compile(r"<g\b|</g>")


def remove_radar(svg: str) -> str:
    m = RADAR_START.search(svg)
    if not m:
        sys.exit("radar chart group not found")
    depth = 0
    for t in G_TAG.finditer(svg, m.start()):
        depth += 1 if t.group() != "</g>" else -1
        if depth == 0:
            block = svg[m.start(): t.end()]
            if 'class="radar"' not in block:
                sys.exit("matched group is not the radar chart")
            return svg[: m.start()] + svg[t.end():]
    sys.exit("radar chart group is not closed")


def add_moon(svg: str) -> str:
    if 'id="moonrise"' in svg:
        sys.exit("already contains moonrise layer")
    m = BG_RECT.search(svg)
    if not m:
        sys.exit("background rect (class=fill-bg) not found")
    return svg[: m.end()] + "\n" + MOON + svg[m.end():]


def convert(src: str, dst: str, moon: bool) -> None:
    with open(src, encoding="utf-8") as f:
        svg = f.read()
    svg = remove_radar(svg)
    if moon:
        svg = add_moon(svg)
    with open(dst, "w", encoding="utf-8") as f:
        f.write(svg)
    print(f"wrote {dst}")


def main() -> None:
    if len(sys.argv) != 3:
        sys.exit("usage: add_moon.py <input.svg> <output.svg>")
    src, dst = sys.argv[1], sys.argv[2]

    convert(src, dst, moon=True)

    folder = os.path.dirname(src)
    light = os.path.join(folder, "profile-green-animate.svg")
    if os.path.exists(light):
        convert(light, os.path.join(folder, "profile-green-clean.svg"), moon=False)


if __name__ == "__main__":
    main()
