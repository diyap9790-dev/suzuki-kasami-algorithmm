"""
ring_view.py
------------
Builds the animated SVG "ring of processes" visual used on the Simulator
page — this is the unique/attractive centerpiece of the project. Pure SVG
+ CSS (no external assets), so it renders instantly inside Streamlit.
"""

import math

# Node colors
COLOR_IDLE = "#3a3f58"
COLOR_HOLDER_IDLE = "#f5b544"     # gold = holding token, not executing
COLOR_IN_CS = "#39d98a"           # green = actively inside critical section
COLOR_QUEUED = "#ff7a59"          # orange outline = waiting in queue
TEXT_LIGHT = "#f4f6fb"

NODE_R = 46
CENTER = 200
RADIUS = 140


def _node_pos(i: int, n: int):
    """Evenly space n nodes around a circle, starting at the top."""
    angle = -90 + (360 / n) * i
    rad = math.radians(angle)
    x = CENTER + RADIUS * math.cos(rad)
    y = CENTER + RADIUS * math.sin(rad)
    return x, y


def build_ring_svg(sim) -> str:
    n = sim.n
    positions = [_node_pos(i, n) for i in range(n)]

    # ---- connecting ring edges (P0-P1-P2-...-P0) ----
    edges = []
    for i in range(n):
        x1, y1 = positions[i]
        x2, y2 = positions[(i + 1) % n]
        edges.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'class="ring-edge" />')

    # ---- process nodes ----
    nodes = []
    for i in range(n):
        x, y = positions[i]
        is_holder = (i == sim.current_holder)
        is_in_cs = is_holder and sim.in_cs
        # A process is shown as "waiting" the moment it has an outstanding
        # request (RN[i] > LN[i]) and isn't the holder — this reflects intent
        # immediately, even on the step before the core algorithm formally
        # adds it to token_queue (which happens lazily, on the next grant
        # check). Purely a visual cue; does not touch the algorithm itself.
        has_pending_request = (not is_holder) and (sim.RN[i] > sim.token_LN[i])
        is_queued = (i in sim.token_queue) or has_pending_request

        if is_in_cs:
            fill = COLOR_IN_CS
            css_class = "node glow-cs"
        elif is_holder:
            fill = COLOR_HOLDER_IDLE
            css_class = "node glow-token"
        elif is_queued:
            fill = COLOR_IDLE
            css_class = "node queued-pulse"
        else:
            fill = COLOR_IDLE
            css_class = "node"

        nodes.append(
            f'<g class="{css_class}">'
            f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{NODE_R}" fill="{fill}" '
            f'stroke="{COLOR_QUEUED if is_queued else "#1b1e2e"}" '
            f'stroke-width="{4 if is_queued else 2}" '
            f'stroke-dasharray="{"6,5" if is_queued else "0"}" />'
            f'<text x="{x:.1f}" y="{y+6:.1f}" text-anchor="middle" '
            f'font-size="22" font-weight="700" fill="{TEXT_LIGHT}" '
            f'font-family="Trebuchet MS, sans-serif">P{i}</text>'
            + (f'<text x="{x:.1f}" y="{y-NODE_R-12:.1f}" text-anchor="middle" '
               f'font-size="26">🔑</text>' if is_holder else "")
            + (f'<circle cx="{x+NODE_R-10:.1f}" cy="{y-NODE_R+10:.1f}" r="12" '
               f'fill="{COLOR_QUEUED}" />'
               f'<text x="{x+NODE_R-10:.1f}" y="{y-NODE_R+15:.1f}" '
               f'text-anchor="middle" font-size="13" font-weight="700" '
               f'fill="#1b1e2e">{(sim.token_queue.index(i)+1) if i in sim.token_queue else "~"}</text>'
               if is_queued else "")
            + "</g>"
        )

    svg = f"""
<div class="ring-wrapper">
<style>
.ring-wrapper {{
    display:flex; justify-content:center; padding: 8px 0 4px 0;
}}
.ring-edge {{
    stroke: #4a5072; stroke-width: 2; stroke-dasharray: 4,4;
}}
.node circle {{ transition: all 0.4s ease; }}
.glow-token circle:first-child {{
    filter: drop-shadow(0 0 10px {COLOR_HOLDER_IDLE});
    animation: pulseGold 1.8s ease-in-out infinite;
}}
.glow-cs circle:first-child {{
    filter: drop-shadow(0 0 16px {COLOR_IN_CS});
    animation: pulseGreen 1.1s ease-in-out infinite;
}}
.queued-pulse circle:first-child {{
    animation: queuedBlink 1.4s ease-in-out infinite;
}}
@keyframes pulseGold {{
    0%,100% {{ filter: drop-shadow(0 0 6px {COLOR_HOLDER_IDLE}); }}
    50%     {{ filter: drop-shadow(0 0 18px {COLOR_HOLDER_IDLE}); }}
}}
@keyframes pulseGreen {{
    0%,100% {{ filter: drop-shadow(0 0 10px {COLOR_IN_CS}); }}
    50%     {{ filter: drop-shadow(0 0 24px {COLOR_IN_CS}); }}
}}
@keyframes queuedBlink {{
    0%,100% {{ opacity: 1; }}
    50%     {{ opacity: 0.55; }}
}}
</style>
<svg viewBox="0 0 400 400" width="100%" height="340" xmlns="http://www.w3.org/2000/svg">
    {''.join(edges)}
    {''.join(nodes)}
</svg>
</div>
"""
    return svg