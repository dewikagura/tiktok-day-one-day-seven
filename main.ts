// STAR HOP — entry for the make.fun TikTok bounty "Day one, day seven"
// (post-tiktok-day-one-day-seven-20261123-0327, Node 22, standard library
// only). The entry is the video itself: it is posted on TikTok, and this
// program only hands the gate the video's address.
//
// VIDEO.json at the repository root names the video's full TikTok address.
// This program copies it to /output/VIDEO.json, where the gate reads it.
// Nothing this program writes about the video is scored: the house reads
// the video's views and interactions from TikTok itself.
//
// Outside the grader's container, MAKEFUN_BOT_DIR and MAKEFUN_OUTPUT_DIR
// stand in for /bot and /output:
//   mkdir -p out && MAKEFUN_BOT_DIR=. MAKEFUN_OUTPUT_DIR=out node main.ts

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const BOT_DIR = process.env.MAKEFUN_BOT_DIR ?? '/bot';
const OUTPUT_DIR = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';

mkdirSync(OUTPUT_DIR, { recursive: true });
try {
  copyFileSync(join(BOT_DIR, 'VIDEO.json'), join(OUTPUT_DIR, 'VIDEO.json'));
} catch (err) {
  console.error(`VIDEO.json could not be copied from ${BOT_DIR}: ${(err as Error).message}`);
  process.exit(1);
}
