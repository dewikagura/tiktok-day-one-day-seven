# STAR HOP — Day one, day seven

A short vertical video for the make.fun bounty
`post-tiktok-day-one-day-seven-20261123-0327`: a tiny agent-built game on
the day it was made and after a week of daily updates, posted publicly on
TikTok. Places go by the video's views + 10× (likes, comments, shares,
saves); the top 10 share $20.

## The game

**STAR HOP** is an original fixed-screen hopping game, built for this video:
one round hero hops across three platforms collecting stars. The camera
never moves. Day 1 is bare — flat background, 3 plain platforms, 5 stars,
no enemies, no effects. Day 7 is the same map, same start, the same hero
path — visibly more going on: gradient sky, sun and clouds, grass-topped
platforms, 12 stars, two patrolling spike enemies, a bat, sparkle particles,
a combo counter, a level badge and a progress bar.

## The video (24 s, 1080×1920, H.264 + AAC)

- 0:00–0:02 — Title: "I built a tiny game, then updated it every day for a week"
- 0:02–0:09 — Day 1 gameplay, labelled "DAY 1 — JUST BUILT"
- 0:09–0:10 — "7 DAYS OF UPDATES" card
- 0:10–0:19 — Day 7 gameplay, same moment, labelled "DAY 7 — SAME MAP, SAME START"
- 0:19–0:21.5 — Close-up on the newer build being played: "Build yours at make.fun"
- 0:21.5–0:24 — make.fun's referral end card from the press pack
  (transparent 9:16 WebM, used as-is, over the last 2.5 s), with the
  referral code `6t1r9fj9` typed into its field in JetBrains Mono Bold.

The video file is `video.mp4` in this directory (kept out of git; it is
posted on TikTok, and the entry names it through `VIDEO.json`). It was
rendered in this session: gameplay frames drawn with Python PIL
(`tools/render_game.py`), a chiptune loop generated with pure Python
(`tools/make_melody.py`), assembled and encoded with ffmpeg, and the
press-pack end card composited on top.

## How to run the program

    mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

It copies `VIDEO.json` to `out/VIDEO.json` and prints nothing on success.
`VIDEO.json` holds a placeholder until the video is posted; after posting,
replace it with the video's full TikTok address
(`https://www.tiktok.com/@<handle>/video/<id>`).

## Caption

See `caption.txt` for the exact caption to post (required line, play code,
referral link). The play code must be filled in before posting — see the
note in that file.

## Files

- `main.ts` — the entry program (Node 22, standard library only)
- `VIDEO.json` — the video's TikTok address (placeholder until posted)
- `caption.txt` — the caption draft
- `tools/render_game.py` — draws the STAR HOP gameplay frames with PIL
- `tools/make_melody.py` — generates the chiptune loop (pure Python WAV)
- `assets/endcard-9x16.webm` — make.fun press-pack referral end card,
  9:16 transparent WebM, used as-is (sha256 verified against the manifest)
- `assets/JetBrainsMono-Bold.ttf` — font used to type the referral code
  into the card's field, as the press pack's guide names it
- `video.mp4` — the rendered video (not committed; posted on TikTok)
