// sheet.html을 PNG로 찍는다. 사용법: node shot.mjs
import path from "node:path";
import fs from "node:fs";
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright");
const ROOT = path.dirname(new URL(import.meta.url).pathname);
fs.mkdirSync(path.join(ROOT, "out"), { recursive: true });
const b = await chromium.launch();
const p = await b.newPage({ viewport: { width: 2400, height: 1500 } });
await p.goto("file://" + path.join(ROOT, "sheet.html"));
await p.evaluate(() => document.fonts.ready);
await p.locator("#s").screenshot({ path: path.join(ROOT, "out/rapi2_sheet.png") });
await b.close();
console.log("ok");
