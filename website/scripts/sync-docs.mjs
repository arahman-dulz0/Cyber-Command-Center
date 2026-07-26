// Vendors the canonical repo docs into the website so /docs renders from a
// self-contained copy (works locally, in Docker, and on Vercel without needing
// the parent repo on disk at build time).
//
//   node scripts/sync-docs.mjs
//
// Runs automatically via the `prebuild` npm hook. Source of truth stays ../docs.

import fs from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const SRC = path.resolve(here, "..", "..", "docs");
const DEST = path.resolve(here, "..", "content", "docs");

function main() {
  if (!fs.existsSync(SRC)) {
    // Nothing to sync (e.g. deploying only the website tree). Keep the existing
    // vendored copy — do not fail the build.
    console.log("[sync-docs] source ../docs not found; using existing content/docs");
    return;
  }
  fs.mkdirSync(DEST, { recursive: true });
  const files = fs.readdirSync(SRC).filter((f) => f.endsWith(".md"));
  let n = 0;
  for (const f of files) {
    fs.copyFileSync(path.join(SRC, f), path.join(DEST, f));
    n++;
  }
  console.log(`[sync-docs] copied ${n} markdown files → content/docs/`);
}

main();
