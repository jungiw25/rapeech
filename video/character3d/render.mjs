// 장면을 헤드리스 크로미움에서 렌더해 PNG로 저장한다.
// 사용법: node render.mjs  → out/*.png, out/rapi_sheet.png
import http from "node:http";
import fs from "node:fs";
import path from "node:path";
import { createRequire } from "node:module";
const { chromium } = createRequire(import.meta.url)("playwright");

const ROOT = path.dirname(new URL(import.meta.url).pathname);
const OUT = path.join(ROOT, "out");
fs.mkdirSync(OUT, { recursive: true });
const TYPES = { ".html": "text/html", ".js": "text/javascript", ".mjs": "text/javascript", ".png": "image/png" };
const srv = http.createServer((q, r) => {
  const f = path.join(ROOT, decodeURIComponent(q.url.split("?")[0].split("#")[0]));
  if (!f.startsWith(ROOT) || !fs.existsSync(f)) { r.writeHead(404); return r.end(); }
  r.writeHead(200, { "content-type": TYPES[path.extname(f)] || "application/octet-stream" });
  fs.createReadStream(f).pipe(r);
}).listen(0);
const port = srv.address().port;

const SHOTS = JSON.parse(fs.readFileSync(path.join(ROOT, "shots.json"), "utf8"));
const browser = await chromium.launch({ args: ["--use-angle=swiftshader", "--enable-unsafe-swiftshader", "--ignore-gpu-blocklist"] });
for (const s of SHOTS) {
  const page = await browser.newPage({ viewport: { width: s.w, height: s.h } });
  page.on("pageerror", (e) => console.error(s.name, e.message));
  await page.goto(`http://127.0.0.1:${port}/scene.html#${encodeURIComponent(JSON.stringify(s))}`);
  await page.waitForFunction(() => window.__done === true, null, { timeout: 120000 });
  await page.locator("canvas").screenshot({ path: path.join(OUT, `${s.name}.png`), omitBackground: !s.bg });
  await page.close();
  console.log("rendered", s.name);
}
await browser.close();
srv.close();
