"""Generate the Nova AI showcase infographics in docs/assets/.

Run from the repository root:  python tools/make_showcase_svgs.py
"""

from __future__ import annotations

import math
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path("docs/assets")
FONT = "font-family=\"Inter, 'Segoe UI', Roboto, Helvetica, Arial, sans-serif\""
INK, MUTED, LINE, PAPER, BAND = "#1b1f2a", "#5b6472", "#d9dee5", "#ffffff", "#f6f7fb"
NOVA, NOVA_BG = "#6d3fd6", "#efe8fd"      # violet: AI and agents
BLUE, BLUE_BG = "#2f5bd3", "#e3eafc"      # app and API
TEAL, TEAL_BG = "#0f766e", "#d5f5ef"      # data and ingestion
AMBER, AMBER_BG = "#a15c07", "#fdf0d5"    # storage
ROSE, ROSE_BG = "#b42318", "#fde8e6"      # blocked / safety
SLATE, SLATE_BG = "#334155", "#e6eaf0"


def svg(w: int, h: int, body: str, title: str, desc: str) -> str:
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" width="{w}" height="{h}" '
        f'role="img" aria-labelledby="t d" {FONT}>\n<title id="t">{escape(title)}</title>\n'
        f'<desc id="d">{escape(desc)}</desc>\n<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" '
        f'markerWidth="7" markerHeight="7" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" '
        f'fill="{MUTED}"/></marker></defs>\n'
        f'<rect x="0.5" y="0.5" width="{w - 1}" height="{h - 1}" rx="16" fill="{PAPER}" stroke="{LINE}"/>\n{body}</svg>\n'
    )


def t(x, y, s, size=14, fill=INK, weight=400, anchor="start", spacing=0):
    ls = f' letter-spacing="{spacing}"' if spacing else ""
    return (f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" font-weight="{weight}" fill="{fill}" '
            f'text-anchor="{anchor}"{ls}>{escape(s)}</text>\n')


def box(x, y, w, h, fill, stroke, rx=10, sw=1.5):
    return (f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>\n')


def arr(x1, y1, x2, y2, dashed=False, both=False):
    d = ' stroke-dasharray="5 4"' if dashed else ""
    s = ' marker-start="url(#a)"' if both else ""
    return (f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="{MUTED}" '
            f'stroke-width="1.6" marker-end="url(#a)"{s}{d}/>\n')


def node(x, y, w, h, title, sub, fill, stroke, size=15):
    out = box(x, y, w, h, fill, stroke)
    if sub:
        out += t(x + w / 2, y + h / 2 - 3, title, size, INK, 700, "middle")
        out += t(x + w / 2, y + h / 2 + 16, sub, 12.5, MUTED, 400, "middle")
    else:
        out += t(x + w / 2, y + h / 2 + 5, title, size, INK, 700, "middle")
    return out


# --------------------------------------------------------------------------- banner
def banner(W: int = 1200, H: int = 340) -> str:
    s = min(W / 1200, H / 340)
    ox, oy = (W - 1200 * s) / 2, (H - 340 * s) / 2
    bg = ('<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#12142b"/>'
          '<stop offset="0.6" stop-color="#2a1b5e"/><stop offset="1" stop-color="#5b2fc2"/></linearGradient>'
          '<radialGradient id="glow"><stop offset="0" stop-color="#b79cff" stop-opacity="0.9"/>'
          '<stop offset="1" stop-color="#b79cff" stop-opacity="0"/></radialGradient></defs>\n'
          f'<rect x="0" y="0" width="{W}" height="{H}" rx="22" fill="url(#g)"/>\n')
    b = t(60, 76, "SHOWCASE · APEX INTELLIGENCE", 15, "#c9b8ff", 700, spacing=2)
    b += t(60, 150, "Nova AI", 72, "#ffffff", 800)
    b += t(60, 196, "An AI analyst for business data: connect your sources,", 23, "#e9e3ff")
    b += t(60, 228, "trust the numbers, ask questions in plain English.", 23, "#e9e3ff")
    cx = 60
    for c in ["Multi-agent · LangGraph", "Grounded Ask-AI", "1M rows in 58 s", "FastAPI · Next.js · PostgreSQL"]:
        w = len(c) * 8.4 + 34
        b += (f'<rect x="{cx:.1f}" y="262" width="{w:.1f}" height="36" rx="18" fill="#ffffff" fill-opacity="0.12" '
              f'stroke="#ffffff" stroke-opacity="0.35"/>\n')
        b += t(cx + w / 2, 286, c, 15, "#ffffff", 600, "middle")
        cx += w + 10
    # a "nova": glowing core with orbiting agent dots
    gx, gy = 1010, 170
    b += f'<circle cx="{gx}" cy="{gy}" r="120" fill="url(#glow)" opacity="0.55"/>\n'
    for r, op in [(118, 0.25), (84, 0.35)]:
        b += f'<circle cx="{gx}" cy="{gy}" r="{r}" fill="none" stroke="#ffffff" stroke-opacity="{op}" stroke-width="1.5"/>\n'
    b += f'<circle cx="{gx}" cy="{gy}" r="34" fill="#ffffff"/>\n'
    b += t(gx, gy + 6, "AI", 20, "#2a1b5e", 800, "middle")
    agents = ["Discover", "Build", "Check", "Deploy", "Monitor", "Reason"]
    for i, name in enumerate(agents):
        a = math.radians(-90 + i * 60)
        nx, ny = gx + 118 * math.cos(a), gy + 118 * math.sin(a)
        b += f'<circle cx="{nx:.1f}" cy="{ny:.1f}" r="9" fill="#d9ccff" stroke="#ffffff" stroke-width="2"/>\n'
        lx, ly = gx + 84 * math.cos(a), gy + 84 * math.sin(a)
        b += t(lx, ly + 4, name, 11.5, "#efeaff", 600, "middle")
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" '
            f'aria-labelledby="t" {FONT}>\n<title id="t">Nova AI: an AI analyst for business data</title>\n{bg}'
            f'<g transform="translate({ox:.1f},{oy:.1f}) scale({s:.4f})">\n{b}</g>\n</svg>\n')


# --------------------------------------------------------------------------- architecture
def architecture() -> str:
    W, H = 1000, 640
    b = ""
    # sources column
    b += t(32, 44, "SOURCES", 13, TEAL, 700, spacing=1.2)
    sources = ["CSV and CSV bundles", "PostgreSQL · MySQL", "MongoDB", "S3 / MinIO", "Stripe", "Shopify", "Snowflake"]
    for i, s in enumerate(sources):
        b += box(32, 58 + i * 44, 170, 34, TEAL_BG, TEAL, rx=8) + t(117, 80 + i * 44, s, 13, INK, 600, "middle")
    # app column
    b += node(330, 34, 330, 66, "Next.js dashboard", "analytics · Ask AI · sources · agents · monitoring", BLUE_BG, BLUE)
    b += arr(495, 100, 495, 132, both=True)
    b += t(505, 122, "HTTPS + WebSocket", 12, MUTED)
    b += node(330, 134, 330, 72, "FastAPI backend", "Clerk JWT · workspace isolation · /api/v1", BLUE_BG, BLUE)
    # three engines
    y = 262
    b += node(250, y, 160, 92, "Analytics", "KPIs · forecasts", BLUE_BG, BLUE)
    b += node(420, y, 160, 92, "Ask-AI", "grounded answers", NOVA_BG, NOVA)
    b += node(590, y, 160, 92, "Agent workflow", "LangGraph", NOVA_BG, NOVA)
    for x in (330, 500, 670):
        b += arr(495, 206, x, y - 2)
    # LLM provider, used by Ask-AI and the agents
    b += node(790, y, 180, 92, "LLM provider", "narration only, no raw rows", PAPER, NOVA, 15)
    b += arr(752, y + 46, 788, y + 46)
    b += (f'<path d="M500,{y + 92} V{y + 118} H880 V{y + 94}" fill="none" stroke="{NOVA}" stroke-width="1.5" '
          'stroke-dasharray="5 4" marker-end="url(#a)"/>\n')
    # ingestion and workers
    b += node(250, 404, 500, 66, "Ingestion engine", "connectors → staging COPY → quality gate → canonical records", TEAL_BG, TEAL)
    for i in range(len(sources)):
        b += f'<line x1="203" y1="{75 + i * 44}" x2="226" y2="{75 + i * 44}" stroke="{TEAL}" stroke-width="1.4"/>\n'
    b += f'<line x1="226" y1="75" x2="226" y2="{75 + 6 * 44}" stroke="{TEAL}" stroke-width="1.4"/>\n'
    b += (f'<path d="M226,{75 + 3 * 44} V437 H246" fill="none" stroke="{TEAL}" stroke-width="1.4" '
          'marker-end="url(#a)"/>\n')
    b += node(790, 404, 180, 66, "Celery workers", "Redis queue", SLATE_BG, SLATE)
    b += arr(752, 437, 788, 437, both=True)
    # storage
    b += box(250, 500, 720, 112, AMBER_BG, AMBER, rx=14)
    b += t(268, 524, "POSTGRESQL", 12.5, AMBER, 700, spacing=1.2)
    b += t(952, 524, "read by analytics, Ask-AI and the agents", 12.5, MUTED, 400, "end")
    for i, (n, s) in enumerate([("Canonical revenue", "deduplicated records"), ("Daily metrics", "fast dashboards"),
                                ("Runs and audit", "pipelines · agent logs")]):
        b += node(268 + i * 230, 538, 214, 56, n, s, PAPER, AMBER, 14)
    b += arr(500, 470, 500, 536)
    # legend
    for i, (fill, stroke, lab) in enumerate([(BLUE_BG, BLUE, "app"), (NOVA_BG, NOVA, "AI"), (TEAL_BG, TEAL, "data"),
                                             (AMBER_BG, AMBER, "storage")]):
        lx, ly = 32 + (i % 2) * 86, 404 + (i // 2) * 24
        b += box(lx, ly - 11, 14, 14, fill, stroke, rx=3) + t(lx + 20, ly + 1, lab, 12.5, MUTED)
    return svg(W, H, b, "Nova AI architecture",
               "Sources feed an ingestion engine that writes to PostgreSQL. A FastAPI backend serves a Next.js "
               "dashboard and runs three engines: grounded Ask-AI, a LangGraph agent workflow and analytics. "
               "Celery workers handle background jobs; the LLM provider only narrates and never sees raw rows.")


# --------------------------------------------------------------------------- agents
def agents() -> str:
    W, H = 1000, 380
    b = ""
    names = [("Discovery", "understand the request"), ("Implementation", "build the pipeline"),
             ("Quality", "validate the output"), ("Deployment", "release it"), ("Monitoring", "watch it run")]
    w, gap, y = 160, 30, 92
    xs = [40 + i * (w + gap) for i in range(5)]
    for i, (n, s) in enumerate(names):
        fill, stroke = (NOVA_BG, NOVA) if i != 2 else (AMBER_BG, AMBER)
        b += node(xs[i], y, w, 72, n, s, fill, stroke)
        if i < 4:
            b += arr(xs[i] + w + 1, y + 36, xs[i + 1] - 1, y + 36)
    b += t(xs[2] + w + 15, y - 6, "pass", 12.5, TEAL, 700, "middle")
    b += t(40, 50, "Six specialised agents, one quality gate", 16, INK, 700)
    # retry loop
    ry = 248
    rx = xs[1] + 20
    b += node(rx, ry, 200, 64, "Reasoning", "propose a repair", NOVA_BG, NOVA)
    b += (f'<path d="M{xs[2] + w / 2},{y + 72} V{ry + 32} H{rx + 202}" fill="none" stroke="{AMBER}" '
          'stroke-width="1.8" marker-end="url(#a)"/>\n')
    b += t(xs[2] + w / 2 + 8, y + 108, "fail, retries left", 12.5, AMBER, 700)
    b += arr(xs[1] + 60, ry - 1, xs[1] + 60, y + 74)
    b += t(xs[1] + 52, ry - 30, "try again (max 3)", 12.5, NOVA, 700, "end")
    b += node(xs[3] + 10, ry, 200, 64, "Error handler", "stop and record why", ROSE_BG, ROSE)
    b += (f'<path d="M{xs[2] + w - 20},{y + 72} V{ry - 18} H{xs[3] + 110} V{ry - 2}" fill="none" stroke="{ROSE}" '
          'stroke-width="1.6" stroke-dasharray="5 4" marker-end="url(#a)"/>\n')
    b += t(xs[3] + 118, ry - 24, "fail, no retries left", 12.5, ROSE, 700)
    b += t(40, 350, "Every stage is persisted and streamed live to the dashboard over WebSocket.", 13.5, MUTED)
    return svg(W, H, b, "Agent workflow",
               "Discovery, Implementation, Quality, Deployment and Monitoring agents run in order. When the quality "
               "gate fails, a Reasoning agent proposes a repair and implementation retries up to three times; "
               "otherwise an error handler stops the run and records why.")


# --------------------------------------------------------------------------- trust
def trust() -> str:
    W, H = 1000, 470
    b = t(40, 50, "How Ask-AI stays truthful", 16, INK, 700)
    steps = [("Question", "plain English", PAPER, BLUE), ("Can we answer?", "answerability check", AMBER_BG, AMBER),
             ("Trusted context", "computed metrics only", TEAL_BG, TEAL), ("LLM narrates", "optional", NOVA_BG, NOVA),
             ("Sanitizer", "verify every number", AMBER_BG, AMBER), ("Answer", "+ evidence, limits", BLUE_BG, BLUE)]
    w, gap, y = 142, 14, 82
    for i, (n, s, f, st) in enumerate(steps):
        x = 40 + i * (w + gap)
        b += node(x, y, w, 70, n, s, f, st, 14.5)
        if i < 5:
            b += arr(x + w + 1, y + 35, x + w + gap - 1, y + 35)
    # side branch from answerability
    x1 = 40 + 1 * (w + gap)
    b += arr(x1 + w / 2, y + 72, x1 + w / 2, 214)
    b += box(x1 - 30, 216, w + 60, 62, ROSE_BG, ROSE)
    b += t(x1 + w / 2, 240, "Not answerable safely", 14, ROSE, 700, "middle")
    b += t(x1 + w / 2, 260, "say what's missing instead", 12.5, INK, 400, "middle")
    x4 = 40 + 4 * (w + gap)
    b += arr(x4 + w / 2, y + 72, x4 + w / 2, 214)
    b += box(x4 - 30, 216, w + 60, 62, ROSE_BG, ROSE)
    b += t(x4 + w / 2, 240, "Unverified figure removed", 14, ROSE, 700, "middle")
    b += t(x4 + w / 2, 260, "also SQL, URLs, secrets", 12.5, INK, 400, "middle")
    # rules
    b += box(40, 312, 920, 128, BAND, LINE, rx=14)
    b += t(60, 340, "HARD RULES IN CODE", 13, SLATE, 700, spacing=1.2)
    rules = ["Never executes model-generated SQL", "No raw records are sent to the model",
             "Every number must exist in the computed context", "Forecasts are statistics, never generated text",
             "Every query is scoped to the user's workspace", "Works with AI switched off (deterministic answers)"]
    for i, r in enumerate(rules):
        cx, cy = 60 + (i % 2) * 460, 368 + (i // 2) * 26
        b += f'<circle cx="{cx + 6}" cy="{cy - 5}" r="5" fill="{TEAL}"/>\n' + t(cx + 20, cy, r, 14.5, INK)
    return svg(W, H, b, "How Ask-AI stays truthful",
               "A question is first checked for answerability, then answered from a trusted, computed context. "
               "An optional LLM narrates, and a sanitizer removes any number not in the context, plus SQL, URLs "
               "and secrets. Hard rules are enforced in code.")


# --------------------------------------------------------------------------- evolution
def evolution() -> str:
    W, H = 1000, 330
    b = t(40, 48, "From idea to platform", 16, INK, 700)
    stages = [
        ("DataFlow AI", "Nov 2025", "The idea", ["Multi-agent pipelines from", "natural-language requirements"], SLATE_BG, SLATE),
        ("Nova AI", "Nov – Dec 2025", "First product", ["Shopify 'true profit' dashboard,", "LangGraph agents, DB connectors"], BLUE_BG, BLUE),
        ("Nova AI Analytics", "Jun – Jul 2026", "Hardened platform", ["Generic ingestion at scale,", "grounded Ask-AI, forecasting,", "auth, workers, 1,700+ tests"], NOVA_BG, NOVA),
    ]
    w, gap = 280, 40
    b += f'<line x1="70" y1="104" x2="930" y2="104" stroke="{LINE}" stroke-width="4" stroke-linecap="round"/>\n'
    for i, (name, when, tag, rows, f, st) in enumerate(stages):
        x = 40 + i * (w + gap)
        b += f'<circle cx="{x + w / 2}" cy="104" r="13" fill="{st}"/>\n'
        b += t(x + w / 2, 80, when, 13.5, MUTED, 600, "middle")
        b += box(x, 132, w, 160, f, st, rx=14)
        b += t(x + 20, 162, tag.upper(), 12, st, 700, spacing=1.2)
        b += t(x + 20, 190, name, 19, INK, 800)
        for k, r in enumerate(rows):
            b += t(x + 20, 220 + k * 21, r, 14, INK)
        if i < 2:
            b += arr(x + w + 4, 212, x + w + gap - 4, 212)
    return svg(W, H, b, "From idea to platform",
               "DataFlow AI (Nov 2025, the idea), Nova AI (Nov–Dec 2025, first product), Nova AI Analytics "
               "(Jun–Jul 2026, hardened platform).")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, fn in [("banner", banner), ("architecture", architecture), ("agents", agents),
                     ("trust", trust), ("evolution", evolution)]:
        (OUT / f"{name}.svg").write_text(fn(), encoding="utf-8")
    (OUT / "social-preview.svg").write_text(banner(1280, 640), encoding="utf-8")
    print("wrote", sorted(p.name for p in OUT.glob("*.svg")))
