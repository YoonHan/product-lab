// Validates sprites/*.json and events.json, then writes:
//   dist/pet-data.js            bundle for viewer.html (works from file://)
//   dist/<name>.png             sprite sheet, one row per animation
//   dist/<name>-outlined.png    same sheet with the 1px white 4-direction outline baked in
//   dist/<name>.sheet.json      frame rects and animation timing for apps
// Usage: node tools/build.mjs
import { readFileSync, writeFileSync, readdirSync, mkdirSync } from "node:fs";
import { join, dirname } from "node:path";
import { fileURLToPath } from "node:url";
import { deflateSync } from "node:zlib";

const ROOT = join(dirname(fileURLToPath(import.meta.url)), "..");
let TICK_MS = 100;   // taken from the sprites (all sprites must share one tick)
const OUTLINE = [255, 255, 255, 255];

const errors = [];
const warnings = [];

function load(path) {
  try {
    return JSON.parse(readFileSync(path, "utf8"));
  } catch (e) {
    errors.push(`${path}: ${e.message}`);
    return null;
  }
}

function validateSprite(s, file, reactionNames) {
  const [w, h] = s.size;
  const chars = new Set(Object.keys(s.palette));
  for (const [name, rows] of Object.entries(s.frames)) {
    if (rows.length !== h) errors.push(`${file}: frame "${name}" has ${rows.length} rows, expected ${h}`);
    rows.forEach((r, y) => {
      if (r.length !== w) errors.push(`${file}: frame "${name}" row ${y} has ${r.length} columns, expected ${w}`);
      for (const ch of r) if (ch !== "." && !chars.has(ch)) errors.push(`${file}: frame "${name}" row ${y} uses "${ch}", which is not in the palette`);
    });
  }
  for (const [name, a] of Object.entries(s.animations)) {
    if (!a.seq?.length) errors.push(`${file}: animation "${name}" has no steps`);
    for (const [frame, ticks, dx] of a.seq ?? []) {
      if (!s.frames[frame]) errors.push(`${file}: animation "${name}" refers to missing frame "${frame}"`);
      if (!Number.isInteger(ticks) || ticks < 1) errors.push(`${file}: animation "${name}" step "${frame}" needs a whole number of ticks`);
      if (dx !== undefined && !Number.isInteger(dx)) errors.push(`${file}: animation "${name}" step "${frame}" has a non-integer move "${dx}"`);
    }
    if (a.loopFrom !== undefined) {
      if (!a.loop) errors.push(`${file}: animation "${name}" has loopFrom but is not a loop`);
      if (!Number.isInteger(a.loopFrom) || a.loopFrom < 0 || a.loopFrom >= (a.seq?.length ?? 0)) errors.push(`${file}: animation "${name}" loopFrom ${a.loopFrom} is outside its ${a.seq?.length} steps`);
    }
  }
  for (const v of s.idleVariants ?? []) if (!s.animations[v]) errors.push(`${file}: idle variant "${v}" is not an animation`);
  for (const [name, a] of Object.entries(s.animations)) {
    if (a.flipAt !== undefined && (!Number.isInteger(a.flipAt) || a.flipAt < 0 || a.flipAt >= a.seq.length)) errors.push(`${file}: animation "${name}" flipAt ${a.flipAt} is outside its steps`);
  }
  for (const ch of s.outline?.skip ?? []) if (!s.palette[ch]) errors.push(`${file}: outline skip colour "${ch}" is not in the palette`);
  if (s.blink) {
    for (const k of ["eye", "closed"]) if (!s.palette[s.blink[k]]) errors.push(`${file}: blink ${k} colour "${s.blink[k]}" is not in the palette`);
    for (const a of s.blink.animations ?? []) if (!s.animations[a]) errors.push(`${file}: blink applies to unknown animation "${a}"`);
  }
  for (const [name, a] of Object.entries(s.animations)) {
    if (a.hold !== undefined && (!Number.isInteger(a.hold) || a.hold < 0)) errors.push(`${file}: animation "${name}" hold must be a whole number of ticks`);
    if (a.hold !== undefined && a.loop) warnings.push(`${file}: animation "${name}" loops, so its hold is ignored`);
  }
  // poses: every transition must really go between its two poses, and every pose must lead back to standing
  const poseOf = n => s.animations[n]?.pose ?? ["stand", "stand"];
  const poses = new Set(Object.keys(s.animations).flatMap(n => poseOf(n)));
  for (const [from, tos] of Object.entries(s.transitions ?? {})) for (const [to, path] of Object.entries(tos)) {
    let at = from;
    for (const n of path) {
      if (!s.animations[n]) { errors.push(`${file}: transition ${from} → ${to} uses unknown animation "${n}"`); break; }
      if (poseOf(n)[0] !== at) errors.push(`${file}: transition ${from} → ${to}: "${n}" starts in "${poseOf(n)[0]}", not "${at}"`);
      at = poseOf(n)[1];
    }
    if (at !== to) errors.push(`${file}: transition ${from} → ${to} ends in "${at}"`);
  }
  for (const p of poses) {
    const seen = new Set([p]), todo = [p];
    while (todo.length) for (const nxt of Object.keys(s.transitions?.[todo.shift()] ?? {})) if (!seen.has(nxt)) { seen.add(nxt); todo.push(nxt); }
    if (!seen.has("stand")) errors.push(`${file}: no transition path from pose "${p}" back to "stand"`);
  }
  if (s.look) {
    const lk = s.look, dirs = new Set(Object.keys(lk.frames ?? {}));
    for (const a of lk.animations ?? []) if (!s.animations[a]) errors.push(`${file}: look applies to unknown animation "${a}"`);
    for (const sec of lk.sectors ?? []) if (sec.dir !== "fwd" && !dirs.has(sec.dir)) errors.push(`${file}: look sector "${sec.dir}" has no frames`);
    for (const [dir, map] of Object.entries(lk.frames ?? {})) for (const [from, to] of Object.entries(map)) {
      if (!s.frames[from]) errors.push(`${file}: look "${dir}" replaces missing frame "${from}"`);
      if (!s.frames[to]) errors.push(`${file}: look "${dir}" uses missing frame "${to}"`);
    }
    const mins = (lk.sectors ?? []).map(x => x.min);
    if (mins.some((m, i) => i && m >= mins[i - 1])) errors.push(`${file}: look sectors must be listed from the highest angle down`);
  }
  const planned = new Set(s.planned ?? []);
  for (const [reaction, anims] of Object.entries(s.reactions ?? {})) {
    if (!reactionNames.has(reaction)) errors.push(`${file}: reaction "${reaction}" is not defined in events.json`);
    for (const a of anims) {
      if (s.animations[a]) continue;
      if (planned.has(a)) warnings.push(`${file}: reaction "${reaction}" uses "${a}", which is planned but not drawn yet`);
      else errors.push(`${file}: reaction "${reaction}" uses unknown animation "${a}"`);
    }
  }
  for (const r of reactionNames) if (!s.reactions?.[r]) warnings.push(`${file}: no animation for reaction "${r}"`);
}

// ---- PNG ---------------------------------------------------------------------
const CRC = new Uint32Array(256).map((_, n) => {
  let c = n;
  for (let k = 0; k < 8; k++) c = c & 1 ? 0xedb88320 ^ (c >>> 1) : c >>> 1;
  return c >>> 0;
});
function crc32(buf) {
  let c = 0xffffffff;
  for (const b of buf) c = CRC[(c ^ b) & 0xff] ^ (c >>> 8);
  return (c ^ 0xffffffff) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, "ascii"), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
function encodePNG(w, h, rgba) {
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 6; ihdr[10] = 0; ihdr[11] = 0; ihdr[12] = 0;
  const raw = Buffer.alloc((w * 4 + 1) * h);
  for (let y = 0; y < h; y++) rgba.copy(raw, y * (w * 4 + 1) + 1, y * w * 4, (y + 1) * w * 4);
  return Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a]),
    chunk("IHDR", ihdr), chunk("IDAT", deflateSync(raw, { level: 9 })), chunk("IEND", Buffer.alloc(0)),
  ]);
}
const hex = h => [parseInt(h.slice(1, 3), 16), parseInt(h.slice(3, 5), 16), parseInt(h.slice(5, 7), 16), 255];

// ---- sheets ------------------------------------------------------------------
function buildSheet(s, pad) {
  const [w, h] = s.size;
  const cw = w + pad * 2, chh = h + pad * 2;
  // row 0 holds frames no animation uses (e.g. "stand"); then one row per animation
  const used = new Set(Object.values(s.animations).flatMap(a => a.seq.map(([f]) => f)));
  const lookRows = Object.entries(s.look?.frames ?? {}).map(([d, m]) => [`look_${d}`, Object.values(m)]);
  lookRows.forEach(([, fs]) => fs.forEach(f => used.add(f)));
  const rows = [["_frames", Object.keys(s.frames).filter(f => !used.has(f))], ...Object.entries(s.animations).map(([n, a]) => [n, [...new Set(a.seq.map(([f]) => f))]]), ...lookRows].filter(([, fs]) => fs.length);
  const cols = Math.max(...rows.map(([, fs]) => fs.length));
  const W = cols * cw, H = rows.length * chh;
  const px = Buffer.alloc(W * H * 4);
  const put = (x, y, c) => { const i = (y * W + x) * 4; px[i] = c[0]; px[i + 1] = c[1]; px[i + 2] = c[2]; px[i + 3] = c[3]; };
  const rects = {};
  rows.forEach(([, fs], r) => fs.forEach((f, c) => {
    const ox = c * cw + pad, oy = r * chh + pad;
    rects[f] = { x: ox, y: oy, w, h };
    const rowsTxt = s.frames[f];
    const skip = new Set(s.outline?.skip ?? []);
    if (pad) {
      for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
        if (rowsTxt[y][x] === "." || skip.has(rowsTxt[y][x])) continue;
        for (const [dx, dy] of [[1, 0], [-1, 0], [0, 1], [0, -1]]) put(ox + x + dx, oy + y + dy, OUTLINE);
      }
    }
    for (let y = 0; y < h; y++) for (let x = 0; x < w; x++) {
      const ch = rowsTxt[y][x];
      if (ch !== ".") put(ox + x, oy + y, hex(s.palette[ch].hex));
    }
  }));
  return { png: encodePNG(W, H, px), rects, W, H };
}

// ---- main --------------------------------------------------------------------
const events = load(join(ROOT, "events.json"));
const reactionNames = new Set(Object.keys(events?.reactions ?? {}));
for (const e of events?.events ?? []) if (!reactionNames.has(e.reaction)) errors.push(`events.json: event "${e.id}" uses unknown reaction "${e.reaction}"`);

const sprites = {};
const ticks = new Set();
for (const f of readdirSync(join(ROOT, "sprites")).filter(f => f.endsWith(".json")).sort()) {
  const s = load(join(ROOT, "sprites", f));
  if (!s) continue;
  ticks.add(s.tickMs ?? 100);
  validateSprite(s, `sprites/${f}`, reactionNames);
  sprites[s.name] = s;
}

if (ticks.size > 1) errors.push(`sprites use different ticks (${[...ticks].join(", ")} ms); use one tick for all animals`);
TICK_MS = [...ticks][0] ?? 100;
warnings.forEach(w => console.warn("warn  " + w));
if (errors.length) {
  errors.forEach(e => console.error("error " + e));
  console.error(`\n${errors.length} error(s); nothing was written.`);
  process.exit(1);
}

mkdirSync(join(ROOT, "dist"), { recursive: true });
writeFileSync(join(ROOT, "dist", "pet-data.js"),
  "// Generated by tools/build.mjs from sprites/*.json and events.json. Do not edit.\n" +
  `window.PET_DATA = ${JSON.stringify({ tickMs: TICK_MS, events, sprites })};\n`);

for (const s of Object.values(sprites)) {
  const plain = buildSheet(s, 0);
  const outlined = buildSheet(s, 1);
  writeFileSync(join(ROOT, "dist", `${s.name}.png`), plain.png);
  writeFileSync(join(ROOT, "dist", `${s.name}-outlined.png`), outlined.png);
  const anim = Object.fromEntries(Object.entries(s.animations).map(([n, a]) => [n, {
    loop: a.loop, ...(a.loopFrom !== undefined ? { loopFrom: a.loopFrom } : {}), ...(a.hold !== undefined ? { holdMs: a.hold * TICK_MS } : {}), ...(a.pose ? { pose: a.pose } : {}), ...(a.flipAt !== undefined ? { flipAt: a.flipAt } : {}), ...(a.moveX ? { moveXPerTick: a.moveX } : {}),
    steps: a.seq.map(([frame, ticks, dx]) => ({ frame, ms: ticks * TICK_MS, ...(dx ? { moveX: dx } : {}) })),
  }]));
  writeFileSync(join(ROOT, "dist", `${s.name}.sheet.json`), JSON.stringify({
    name: s.name, tickMs: TICK_MS, frameSize: s.size, anchor: s.anchor,
    images: {
      plain: { file: `${s.name}.png`, size: [plain.W, plain.H], frames: plain.rects },
      outlined: { file: `${s.name}-outlined.png`, size: [outlined.W, outlined.H], padding: 1, frames: outlined.rects },
    },
    animations: anim, outline: s.outline ?? null, blink: s.blink ?? null, transitions: s.transitions ?? {}, idleVariants: s.idleVariants ?? [], look: s.look ?? null, reactions: s.reactions,
  }, null, 2) + "\n");
  console.log(`built ${s.name}: ${Object.keys(s.frames).length} frames, ${Object.keys(s.animations).length} animations, sheet ${plain.W}x${plain.H}`);
}
