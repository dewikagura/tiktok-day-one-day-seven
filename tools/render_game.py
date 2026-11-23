#!/usr/bin/env python3
"""Render STAR HOP gameplay frames for the make.fun TikTok bounty
(post-tiktok-day-one-day-seven-20261123-0327).

STAR HOP is an original tiny fixed-screen hopping game: one round hero hops
across three platforms collecting stars. The camera never moves. Day 1 is
bare; Day 7 is the same map, same start, same hero path, visibly more going
on (more stars, enemies, particles, clouds, combo, level badge).

Frames: 1080x1920, 30 fps, PNG. Deterministic: the hero path, stars,
enemies and particles are pure functions of time.
"""
import math
import os

from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
FPS = 30

DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# ---------------------------------------------------------------- game state
# Platforms: (x0, y0, x1, y1). Hero radius 48, so standing y = top - 48.
PLATFORMS = [
    (80, 1620, 1000, 1656),   # P1 bottom
    (120, 1240, 620, 1276),   # P2 mid-left
    (560, 900, 1000, 936),    # P3 upper-right
]

# Hero waypoints (centres) and leg schedule: (duration, from, to, lift).
A = (200, 1572)
B = (540, 1572)
C = (880, 1572)
D = (360, 1192)
E = (780, 852)
LEGS = [
    (1.0, A, B, 150),
    (1.0, B, C, 150),
    (1.0, C, D, 150),
    (1.0, D, E, 150),
    (1.2, E, A, 60),
]
PAUSE = 0.16  # pause at each waypoint after arriving
LOOP = 6.0    # sum of legs + 5 pauses = 6.0s


def hero_pos(t):
    """Hero centre at loop-time t (0..6)."""
    t = t % LOOP
    cursor = 0.0
    for dur, p0, p1, lift in LEGS:
        if t < cursor + dur:
            u = (t - cursor) / dur
            x = p0[0] + (p1[0] - p0[0]) * u
            y = p0[1] + (p1[1] - p0[1]) * u
            y -= 4 * lift * u * (1 - u)
            return x, y, u
        cursor += dur
        if t < cursor + PAUSE:
            return p1[0], p1[1], 1.0
        cursor += PAUSE
    return A[0], A[1], 0.0


# Stars: (x, y). Day 1 has 5, Day 7 has all 12 (same first five).
STARS = [
    (370, 1450), (710, 1450), (620, 1300), (570, 1000), (490, 1200),
    (300, 1400), (860, 1470), (404, 1358), (656, 1367), (704, 755),
    (880, 1502), (509, 1058),
]


def collection_times(stars, seg_len):
    """First time (from segment start) the hero comes within 90px of each star."""
    times = []
    step = 0.02
    n = int(seg_len / step) + 1
    path = [hero_pos(i * step)[:2] for i in range(n)]
    for sx, sy in stars:
        found = None
        for i, (hx, hy) in enumerate(path):
            if (hx - sx) ** 2 + (hy - sy) ** 2 <= 90 ** 2:
                found = i * step
                break
        times.append(found if found is not None else float("inf"))
    return times


# ---------------------------------------------------------------- backgrounds
def lerp_color(c0, c1, u):
    return tuple(int(c0[i] + (c1[i] - c0[i]) * u) for i in range(3))


def make_day1_bg():
    img = Image.new("RGB", (W, H), (232, 236, 241))
    d = ImageDraw.Draw(img)
    for (x0, y0, x1, y1) in PLATFORMS:
        d.rectangle([x0, y0, x1, y1], fill=(90, 100, 112))
        d.rectangle([x0, y0, x1, y0 + 8], fill=(120, 130, 142))
    return img


def make_day7_bg():
    # vertical gradient via a 1px-wide strip resized to full width
    strip = Image.new("RGB", (1, H))
    top = (125, 211, 252)
    mid = (191, 219, 254)
    bot = (254, 243, 199)
    spx = strip.load()
    for y in range(H):
        if y < 900:
            spx[0, y] = lerp_color(top, mid, y / 900)
        else:
            spx[0, y] = lerp_color(mid, bot, (y - 900) / (H - 900))
    img = strip.resize((W, H))
    d = ImageDraw.Draw(img, "RGBA")
    # sun
    d.ellipse([770, 150, 990, 370], fill=(253, 230, 138, 255))
    d.ellipse([800, 180, 960, 340], fill=(254, 249, 195, 255))
    # hills
    d.ellipse([-260, 1680, 700, 2050], fill=(134, 239, 172, 255))
    d.ellipse([480, 1740, 1340, 2080], fill=(74, 222, 128, 255))
    # platforms: brown body, green grass top
    for (x0, y0, x1, y1) in PLATFORMS:
        d.rectangle([x0, y0, x1, y1], fill=(146, 64, 14))
        d.rectangle([x0, y0 - 10, x1, y0 + 10], fill=(34, 197, 94))
        d.ellipse([x0, y0 - 14, x0 + 28, y0 + 14], fill=(34, 197, 94))
        d.ellipse([x1 - 28, y0 - 14, x1, y0 + 14], fill=(34, 197, 94))
    return img


def draw_star(d, x, y, r, fill, outline=None):
    pts = []
    for i in range(10):
        ang = -math.pi / 2 + i * math.pi / 5
        rr = r if i % 2 == 0 else r * 0.45
        pts.append((x + rr * math.cos(ang), y + rr * math.sin(ang)))
    d.polygon(pts, fill=fill, outline=outline)


def draw_spike_ball(d, x, y, r):
    for i in range(8):
        ang = i * math.pi / 4
        tx, ty = x + (r + 16) * math.cos(ang), y + (r + 16) * math.sin(ang)
        ax, ay = x + (r - 6) * math.cos(ang - 0.25), y + (r - 6) * math.sin(ang - 0.25)
        bx, by = x + (r - 6) * math.cos(ang + 0.25), y + (r - 6) * math.sin(ang + 0.25)
        d.polygon([(tx, ty), (ax, ay), (bx, by)], fill=(220, 38, 38))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(239, 68, 68), outline=(127, 29, 29), width=3)
    d.ellipse([x - 10, y - 12, x + 2, y], fill=(255, 255, 255))
    d.ellipse([x + 4, y - 12, x + 14, y - 2], fill=(255, 255, 255))
    d.ellipse([x - 8, y - 10, x + 0, y - 2], fill=(15, 23, 42))
    d.ellipse([x + 6, y - 10, x + 12, y - 4], fill=(15, 23, 42))


def draw_hero(d, x, y, r=48, trail=None):
    if trail:
        for i, (tx, ty) in enumerate(trail):
            a = 90 - i * 18
            d.ellipse([tx - r + 8, ty - r + 8, tx + r - 8, ty + r - 8],
                      fill=(255, 140, 66, max(a, 0)))
    d.ellipse([x - r, y - r, x + r, y + r], fill=(255, 140, 66), outline=(194, 65, 12), width=4)
    d.ellipse([x - 26, y - 16, x - 2, y + 8], fill=(255, 255, 255))
    d.ellipse([x + 4, y - 16, x + 28, y + 8], fill=(255, 255, 255))
    d.ellipse([x - 18, y - 8, x - 6, y + 4], fill=(15, 23, 42))
    d.ellipse([x + 12, y - 8, x + 24, y + 4], fill=(15, 23, 42))
    d.arc([x - 18, y + 8, x + 20, y + 32], 20, 160, fill=(124, 45, 18), width=4)


def pill(d, cx, y, text, fnt, bg, fg, pad_x=28, pad_y=14):
    bbox = d.textbbox((0, 0), text, font=fnt)
    w = bbox[2] - bbox[0] + pad_x * 2
    h = bbox[3] - bbox[1] + pad_y * 2
    d.rounded_rectangle([cx - w / 2, y, cx + w / 2, y + h], radius=h / 2, fill=bg)
    d.text((cx - (bbox[2] - bbox[0]) / 2, y + pad_y), text, font=fnt, fill=fg)


# ---------------------------------------------------------------- frame render
def render_frame(version, t, bg, stars, coll_times):
    """Render one gameplay frame at segment time t (seconds)."""
    img = bg.copy()
    d = ImageDraw.Draw(img, "RGBA")
    n_stars = len(stars)
    collected = [ct <= t for ct in coll_times]
    n_col = sum(collected)

    if version == 7:
        # drifting clouds
        for (cx, cy, s) in [(200, 300, 1.0), (700, 180, 0.8), (450, 430, 1.2)]:
            x = (cx + 12 * t) % 1250 - 100
            d.ellipse([x, cy, x + 220 * s, cy + 70 * s], fill=(255, 255, 255, 235))
            d.ellipse([x + 50, cy - 30, x + 190 * s, cy + 40 * s], fill=(255, 255, 255, 235))
        # ambient dust
        for i in range(15):
            dx = (i * 137) % 1080
            dy = (i * 211 + 1920 - 25 * t) % 1920
            d.ellipse([dx, dy, dx + 7, dy + 7], fill=(255, 255, 255, 170))

    # stars not yet collected
    for i, (sx, sy) in enumerate(stars):
        if collected[i]:
            continue
        if version == 7:
            d.ellipse([sx - 42, sy - 42, sx + 42, sy + 42], fill=(251, 191, 36, 60))
            draw_star(d, sx, sy, 34, (251, 191, 36), (180, 130, 10))
        else:
            draw_star(d, sx, sy, 30, (242, 201, 76), (150, 120, 40))

    if version == 7:
        # enemies
        e1x = 370 + 220 * math.sin(2 * math.pi * t / 5)
        draw_spike_ball(d, e1x, 1210, 30)
        e2x = 780 + 180 * math.sin(2 * math.pi * t / 7 + 1)
        draw_spike_ball(d, e2x, 870, 30)
        # bat crossing the sky
        bx = ((t * 135) % 1200) - 60
        by = 480 + 30 * math.sin(2 * math.pi * t / 3)
        flap = 14 * math.sin(2 * math.pi * t * 6)
        d.polygon([(bx, by), (bx - 46, by - 18 - flap), (bx - 20, by + 8)], fill=(76, 29, 149))
        d.polygon([(bx, by), (bx + 46, by - 18 - flap), (bx + 20, by + 8)], fill=(76, 29, 149))
        d.ellipse([bx - 14, by - 12, bx + 14, by + 12], fill=(109, 40, 217))
        # sparkles from recent collections
        for i, ct in enumerate(coll_times):
            if ct == float("inf") or not (ct <= t <= ct + 0.6):
                continue
            sx, sy = stars[i]
            age = t - ct
            for k in range(8):
                ang = k * math.pi / 4
                r = 18 + 90 * age
                px, py = sx + r * math.cos(ang), sy + r * math.sin(ang)
                a = int(255 * (1 - age / 0.6))
                d.ellipse([px - 7, py - 7, px + 7, py + 7], fill=(253, 224, 71, a))

    # hero (with trail on day 7)
    hx, hy, _ = hero_pos(t)
    trail = None
    if version == 7:
        trail = [hero_pos(max(t - 0.05 * (k + 1), 0))[:2] for k in range(4)]
    draw_hero(d, hx, hy, trail=trail)

    # HUD: row 1 score / LV, row 2 combo + stars, row 3 pill, row 4 progress
    f_big = font(DEJAVU_BOLD, 54)
    f_mid = font(DEJAVU_BOLD, 40)
    f_small = font(DEJAVU, 36)
    if version == 1:
        score = n_col * 10
        d.text((60, 45), f"SCORE {score}", font=f_big, fill=(31, 41, 55))
        d.text((60, 125), f"★ {n_col}/5", font=f_mid, fill=(31, 41, 55))
        pill(d, 540, 185, "DAY 1  —  JUST BUILT", f_mid, (31, 41, 55), (255, 255, 255))
    else:
        # combo: collections within 2s of the previous one
        combo, score, last = 0, 0, None
        for ct in sorted(c for c in coll_times if c <= t):
            combo = combo + 1 if (last is not None and ct - last <= 2.0) else 1
            combo = min(combo, 5)
            score += 10 * combo
            last = ct
        d.text((60, 45), f"SCORE {score}", font=f_big, fill=(31, 41, 55))
        d.text((60, 125), f"COMBO x{combo}", font=f_mid, fill=(194, 65, 12))
        d.text((330, 125), f"★ {n_col}/{n_stars}", font=f_mid, fill=(31, 41, 55))
        pill(d, 900, 45, "LV 7", f_big, (22, 163, 74), (255, 255, 255))
        pill(d, 540, 185, "DAY 7  —  SAME MAP, SAME START", f_mid, (34, 197, 94),
             (255, 255, 255))
        # progress bar: stars collected / 12
        d.rounded_rectangle([240, 270, 840, 294], radius=12, fill=(255, 255, 255, 220))
        d.rounded_rectangle([240, 270, 240 + 600 * n_col / n_stars, 294], radius=12,
                            fill=(34, 197, 94))
    return img


def render_title():
    img = Image.new("RGB", (W, H), (17, 24, 39))
    d = ImageDraw.Draw(img)
    f_title = font(DEJAVU_BOLD, 70)
    f_sub = font(DEJAVU, 44)
    f_game = font(DEJAVU_BOLD, 72)
    f_tag = font(DEJAVU_BOLD, 58)
    d.text((540, 620), "I BUILT A TINY GAME", font=f_title, fill=(255, 255, 255),
           anchor="ma")
    d.text((540, 780), "then updated it every day for a week", font=f_sub,
           fill=(156, 163, 175), anchor="ma")
    d.text((540, 980), "★  STAR HOP  ★", font=f_game, fill=(251, 191, 36), anchor="ma")
    d.text((540, 1160), "DAY 1  →  DAY 7", font=f_tag, fill=(255, 255, 255), anchor="ma")
    d.text((540, 1300), "same map. same start. way more going on.", font=f_sub,
           fill=(156, 163, 175), anchor="ma")
    return img


def render_transition():
    img = Image.new("RGB", (W, H), (230, 0, 126))
    d = ImageDraw.Draw(img)
    f_big = font(DEJAVU_BOLD, 84)
    f_sub = font(DEJAVU, 52)
    d.text((540, 800), "7 DAYS OF UPDATES", font=f_big, fill=(255, 255, 255), anchor="ma")
    d.text((540, 960), "same map — way more going on", font=f_sub,
           fill=(255, 255, 255), anchor="ma")
    return img


def main():
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frames")
    os.makedirs(os.path.join(out, "day1"), exist_ok=True)
    os.makedirs(os.path.join(out, "day7"), exist_ok=True)
    bg1 = make_day1_bg()
    bg7 = make_day7_bg()
    stars1 = STARS[:5]
    stars7 = STARS[:]
    coll1 = collection_times(stars1, 7.0)
    coll7 = collection_times(stars7, 11.5)
    print("day1 collection times:", [round(c, 2) if c != float("inf") else None for c in coll1])
    print("day7 collection times:", [round(c, 2) if c != float("inf") else None for c in coll7])

    render_title().save(os.path.join(out, "title.png"))
    render_transition().save(os.path.join(out, "transition.png"))

    n1 = 7 * FPS
    for i in range(n1):
        t = i / FPS
        render_frame(1, t, bg1, stars1, coll1).save(
            os.path.join(out, "day1", f"f{i:04d}.png"))
    n7 = int(11.5 * FPS)
    for i in range(n7):
        t = i / FPS
        render_frame(7, t, bg7, stars7, coll7).save(
            os.path.join(out, "day7", f"f{i:04d}.png"))
    print(f"rendered {n1} day-1 frames, {n7} day-7 frames + title + transition")


if __name__ == "__main__":
    main()
