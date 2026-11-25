import { mkdirSync, readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

// News-image entry: "The World in One Day" — Wednesday 25 November 2026.
// The front-page image is bundled in this repository as entry.png and is
// copied verbatim to /output/entry.png. The program runs with no network,
// so the image must travel with the repo; nothing is fetched at run time.
const here = dirname(fileURLToPath(import.meta.url));
const srcPath = join(here, "entry.png");

const arg = process.argv[2];
const outPath = arg
  ? arg.endsWith(".png")
    ? arg
    : join(arg, "entry.png")
  : "/output/entry.png";

const png = readFileSync(srcPath);

// Validate the PNG before writing it out: magic bytes, and the IHDR
// dimensions must fit the gate (at most 1024 by 1024 pixels).
if (
  png[0] !== 0x89 ||
  png[1] !== 0x50 ||
  png[2] !== 0x4e ||
  png[3] !== 0x47
) {
  throw new Error("entry.png is not a PNG file");
}
const width = png.readUInt32BE(16);
const height = png.readUInt32BE(20);
if (width > 1024 || height > 1024) {
  throw new Error(`entry.png is ${width}x${height}, over the 1024x1024 cap`);
}
if (png.length > 1048576) {
  throw new Error(`entry.png is ${png.length} bytes, over the 1 MiB cap`);
}
// The file must be a whole image: the last 12 bytes are the IEND chunk.
const tail = png.subarray(png.length - 12);
if (
  tail[4] !== 0x49 ||
  tail[5] !== 0x45 ||
  tail[6] !== 0x4e ||
  tail[7] !== 0x44
) {
  throw new Error("entry.png has no IEND chunk: not a whole PNG");
}

mkdirSync(dirname(outPath), { recursive: true });
writeFileSync(outPath, png);
console.log(`wrote ${outPath} (${width}x${height}, ${png.length} bytes)`);
