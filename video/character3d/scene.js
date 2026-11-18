// 라피치 캐릭터 '라피' 3D 모델(three.js). 주소 #뒤의 JSON으로 자세·표정·카메라를 바꿔 렌더한다.
// 몸 = 로고의 아래쪽 삼각형(둥근 모서리 입체), 머리 위 줄무늬 볏 = 로고의 줄무늬 삼각형, 한쪽 귀 헤드셋 = 대화형 AI(콜봇) 상담
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";

const P = Object.assign({ view: "hero", expr: "happy", w: 1600, h: 1600, bg: true }, JSON.parse(decodeURIComponent(location.hash.slice(1) || "{}")));
const C = {
  deep: new THREE.Color("#4a1bc9"), light: new THREE.Color("#8f66ff"), pink: new THREE.Color("#d43cf0"),
  limb: "#5a29d6", ink: "#1e1245", crest: "#9d79ff", crestTip: "#ff7ae0", cup: "#ff3cbf", white: "#ffffff", cheek: "#ff8fc8",
};

const renderer = new THREE.WebGLRenderer({ antialias: true, preserveDrawingBuffer: true, alpha: !P.bg });
renderer.setPixelRatio(1);
renderer.setSize(P.w, P.h);
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 0.92;
renderer.outputColorSpace = THREE.SRGBColorSpace;
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
document.body.appendChild(renderer.domElement);

const scene = new THREE.Scene();
if (P.bg) {
  const c = document.createElement("canvas"); c.width = 16; c.height = 512;
  const g = c.getContext("2d"), gr = g.createLinearGradient(0, 0, 0, 512);
  gr.addColorStop(0, "#fff3ea"); gr.addColorStop(1, "#ffdcea");
  g.fillStyle = gr; g.fillRect(0, 0, 16, 512);
  const t = new THREE.CanvasTexture(c); t.colorSpace = THREE.SRGBColorSpace;
  scene.background = t;
}
const pmrem = new THREE.PMREMGenerator(renderer);
scene.environment = pmrem.fromScene(new RoomEnvironment(), 0.04).texture;
scene.environmentIntensity = 0.32;

scene.add(new THREE.HemisphereLight("#fff4ff", "#ffd2e4", 1.1));
const key = new THREE.DirectionalLight("#ffffff", 2.4);
key.position.set(3, 5.5, 4.5); key.castShadow = true;
key.shadow.mapSize.set(2048, 2048); key.shadow.radius = 8;
Object.assign(key.shadow.camera, { left: -3, right: 3, top: 3, bottom: -3, near: 1, far: 20 });
scene.add(key);
const rim = new THREE.DirectionalLight("#ff8be6", 1.6); rim.position.set(-3.5, 2.5, -4); scene.add(rim);
const fill = new THREE.DirectionalLight("#bcc8ff", 0.7); fill.position.set(-4, 0.5, 3); scene.add(fill);

const mat = (color, o = {}) => new THREE.MeshPhysicalMaterial(Object.assign({ color, roughness: 0.42, clearcoat: 0.35, clearcoatRoughness: 0.35, sheen: 0.15, sheenColor: new THREE.Color("#ffd6f6") }, o));
const mesh = (geo, m, parent, pos = [0, 0, 0], rot = [0, 0, 0], scl = [1, 1, 1]) => {
  const o = new THREE.Mesh(geo, m); o.position.set(...pos); o.rotation.set(...rot); o.scale.set(...scl);
  o.castShadow = true; o.receiveShadow = true; parent.add(o); return o;
};

// ── 몸: 로고의 아래 삼각형을 둥근 모서리로 깎아 두툼하게 뽑음
const tri = [[-1.0, 0.86], [1.06, 0.62], [-0.12, -1.16]];
const shape = new THREE.Shape(), R = 0.3;
for (let i = 0; i < 3; i++) {
  const p = tri[i], a = tri[(i + 2) % 3], b = tri[(i + 1) % 3];
  const ua = new THREE.Vector2(a[0] - p[0], a[1] - p[1]).normalize(), ub = new THREE.Vector2(b[0] - p[0], b[1] - p[1]).normalize();
  const s = [p[0] + ua.x * R, p[1] + ua.y * R], e = [p[0] + ub.x * R, p[1] + ub.y * R];
  if (i === 0) shape.moveTo(...s); else shape.lineTo(...s);
  shape.quadraticCurveTo(p[0], p[1], ...e);
}
shape.closePath();
const DEPTH = 0.86, BEV = 0.24;
const bodyGeo = new THREE.ExtrudeGeometry(shape, { depth: DEPTH, bevelEnabled: true, bevelThickness: BEV, bevelSize: 0.22, bevelSegments: 12, curveSegments: 28 });
bodyGeo.translate(0, 0, -DEPTH / 2);
bodyGeo.computeVertexNormals();
{ // 위는 밝은 보라, 아래는 짙은 보라, 왼쪽 위에 분홍 기운(로고 그라데이션)
  const pos = bodyGeo.attributes.position, col = [];
  for (let i = 0; i < pos.count; i++) {
    const x = pos.getX(i), y = pos.getY(i);
    const t = THREE.MathUtils.clamp((y + 1.2) / 2.1, 0, 1);
    const c = C.deep.clone().lerp(C.light, Math.pow(t, 0.9));
    c.lerp(C.pink, THREE.MathUtils.clamp((-x - 0.2) * 0.35 + (0.2 - y) * 0.15, 0, 0.32));
    col.push(c.r, c.g, c.b);
  }
  bodyGeo.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
}
const rig = new THREE.Group(); scene.add(rig);
const body = new THREE.Group(); rig.add(body);
mesh(bodyGeo, mat("#ffffff", { vertexColors: true }), body);
const FZ = DEPTH / 2 + BEV;   // 앞면 z

// ── 볏: 로고 위쪽의 줄무늬 삼각형(오른쪽으로 갈수록 길어지는 막대)
const crest = new THREE.Group(); body.add(crest);
const topY = (x) => 0.86 + (x + 1.0) / 2.06 * (0.62 - 0.86);
[-0.58, -0.3, -0.02, 0.26, 0.54].forEach((x, i) => {
  const L = 0.16 + i * 0.1;
  const g = new THREE.CapsuleGeometry(0.095, L, 8, 16);
  const pos = g.attributes.position, col = [], a = new THREE.Color(C.crest), b = new THREE.Color(C.crestTip);
  for (let k = 0; k < pos.count; k++) { const c = a.clone().lerp(b, THREE.MathUtils.clamp((pos.getY(k) + L / 2) / L, 0, 1)); col.push(c.r, c.g, c.b); }
  g.setAttribute("color", new THREE.Float32BufferAttribute(col, 3));
  const ang = -0.5;
  mesh(g, mat("#ffffff", { vertexColors: true, roughness: 0.3 }), crest, [x + Math.sin(-ang) * (L / 2), topY(x) + 0.06 + Math.cos(ang) * (L / 2), -0.18], [0, 0, ang], [1, 1, 0.45]);
});

// ── 얼굴
const face = new THREE.Group(); face.position.z = FZ - 0.06; body.add(face);
const eyes = [], pupils = [], brows = [];
[[-0.33, 0.2], [0.42, 0.16]].forEach(([x, y], i) => {
  const e = mesh(new THREE.SphereGeometry(0.27, 48, 32), mat("#fbf9ff", { roughness: 0.25, clearcoat: 0.8 }), face, [x, y, 0.02], [0, 0, 0], [1, 1.08, 0.55]);
  eyes.push(e);
  const pg = new THREE.Group(); pg.position.set(x, y, 0.13); face.add(pg); pupils.push(pg);
  mesh(new THREE.SphereGeometry(0.135, 32, 24), mat(C.ink, { roughness: 0.2, clearcoat: 1 }), pg, [0, -0.02, 0], [0, 0, 0], [1, 1.12, 0.5]);
  mesh(new THREE.SphereGeometry(0.042, 16, 12), new THREE.MeshBasicMaterial({ color: "#ffffff" }), pg, [0.05, 0.05, 0.07]);
  const bg = new THREE.Group(); bg.position.set(x, y + 0.36, 0.1); face.add(bg); brows.push(bg);
  mesh(new THREE.CapsuleGeometry(0.06, 0.26, 8, 16), mat(C.ink), bg, [0, 0, 0], [0, 0, Math.PI / 2]);
});
[[-0.62, -0.08], [0.68, -0.12]].forEach(([x, y]) => mesh(new THREE.SphereGeometry(0.1, 24, 16), mat(C.cheek, { roughness: 0.6, transparent: true, opacity: 0.85 }), face, [x, y, -0.02], [0, 0, 0], [1.3, 0.75, 0.3]));
const mouth = new THREE.Group(); mouth.position.set(0.05, -0.2, 0.06); face.add(mouth);

// ── 헤드셋(오른쪽 귀 하나 + 입 쪽으로 오는 마이크)
const hs = new THREE.Group(); body.add(hs);
const NRM = new THREE.Vector3(0.83, -0.55, 0);   // 몸 오른쪽 면의 바깥 방향
const cupPos = new THREE.Vector3(1.1, 0.12, 0.08);
mesh(new THREE.CylinderGeometry(0.24, 0.24, 0.17, 40), mat(C.cup, { roughness: 0.3 }), hs, cupPos.toArray(), [0, 0, -2.16]);
mesh(new THREE.CylinderGeometry(0.14, 0.14, 0.05, 32), mat("#ffd6f3"), hs, cupPos.clone().addScaledVector(NRM, 0.09).toArray(), [0, 0, -2.16]);
const boom = new THREE.CatmullRomCurve3([cupPos.clone().add(new THREE.Vector3(-0.02, -0.08, 0.16)), new THREE.Vector3(0.98, -0.2, 0.55), new THREE.Vector3(0.62, -0.3, FZ + 0.08)]);
mesh(new THREE.TubeGeometry(boom, 40, 0.035, 12), mat("#f4ecff"), hs);
mesh(new THREE.SphereGeometry(0.075, 24, 16), mat(C.ink, { roughness: 0.5 }), hs, [0.6, -0.3, FZ + 0.1]);
// 볏 뒤로 넘어가는 머리띠
const band = new THREE.CatmullRomCurve3([cupPos.clone().add(new THREE.Vector3(-0.05, 0.2, -0.05)), new THREE.Vector3(1.0, 0.75, -0.3), new THREE.Vector3(0.7, 1.0, -0.38), new THREE.Vector3(0.0, 1.12, -0.42), new THREE.Vector3(-0.8, 1.0, -0.36), new THREE.Vector3(-1.0, 0.7, -0.2)]);
mesh(new THREE.TubeGeometry(band, 60, 0.045, 12), mat("#f4ecff"), hs);

// ── 팔다리(짧고 통통하게)
const limb = mat(C.limb);
const arm = (x, y, side) => {
  const g = new THREE.Group(); g.position.set(x, y, 0); body.add(g);
  mesh(new THREE.CapsuleGeometry(0.12, 0.26, 8, 16), limb, g, [0, -0.2, 0]);
  mesh(new THREE.SphereGeometry(0.17, 32, 24), limb, g, [0, -0.44, 0.02], [0, 0, 0], [1, 0.92, 0.95]);
  g.userData.side = side; return g;
};
const armL = arm(-0.8, -0.05, -1), armR = arm(0.84, -0.05, 1);
armL.position.z = 0.25; armR.position.z = 0.3;
const toEar = () => armR.position.set(0.78, -0.42, 0.3);   // 헤드셋을 잡는 자세
const leg = (x, side) => {
  const g = new THREE.Group(); g.position.set(x, -0.95, 0); rig.add(g);
  mesh(new THREE.CapsuleGeometry(0.13, 0.28, 8, 16), limb, g, [0, -0.2, 0]);
  mesh(new THREE.SphereGeometry(0.19, 32, 24), limb, g, [side * 0.03, -0.42, 0.07], [0, 0, 0], [1.05, 0.62, 1.25]);
  return g;
};
const legL = leg(-0.3, -1), legR = leg(0.08, 1);
legL.rotation.z = -0.32; legR.rotation.z = 0.3;

const ground = new THREE.Mesh(new THREE.PlaneGeometry(30, 30), new THREE.ShadowMaterial({ opacity: 0.16 }));
ground.rotation.x = -Math.PI / 2; ground.position.y = -1.53; ground.receiveShadow = true; scene.add(ground);

// ── 표정
const setMouth = (kind) => {
  mouth.clear();
  const m = mat(C.ink, { roughness: 0.5 });
  if (kind === "smile") mesh(new THREE.TorusGeometry(0.12, 0.032, 12, 40, Math.PI), m, mouth, [0, 0.05, 0], [0, 0, Math.PI]);
  else if (kind === "grin") { mesh(new THREE.SphereGeometry(0.15, 32, 16, 0, Math.PI * 2, Math.PI / 2, Math.PI / 2), m, mouth, [0, 0.06, 0], [0, 0, 0], [1, 1, 0.35]);
    mesh(new THREE.SphereGeometry(0.07, 16, 12), mat("#ff7aa8"), mouth, [0.02, -0.05, 0.03], [0, 0, 0], [1.2, 0.6, 0.4]); }
  else if (kind === "o") mesh(new THREE.TorusGeometry(0.06, 0.028, 12, 32), m, mouth, [0, 0, 0], [0, 0, 0], [1, 1.25, 1]);
  else mesh(new THREE.CapsuleGeometry(0.025, 0.14, 6, 12), m, mouth, [0, 0, 0], [0, 0, Math.PI / 2 + 0.12]);
};
const EX = {
  happy:  { look: [0, 0.02], brow: [[0.14, 0.04], [-0.14, 0.04]], mouth: "grin" },
  brave:  { look: [-0.04, 0.0], brow: [[-0.32, -0.02], [0.32, -0.02]], mouth: "smile" },
  listen: { look: [0.07, 0.05], brow: [[0.2, 0.06], [-0.05, 0.08]], mouth: "o" },
  think:  { look: [-0.07, 0.07], brow: [[0.25, 0.08], [0.15, -0.03]], mouth: "flat" },
};
const ex = EX[P.expr] || EX.happy;
pupils.forEach((p) => { p.position.x += ex.look[0]; p.position.y += ex.look[1]; });
brows.forEach((b, i) => { b.rotation.z = ex.brow[i][0]; b.position.y += ex.brow[i][1]; });
setMouth(ex.mouth);

// ── 자세
const POSE = {
  hero:  () => { toEar(); armR.rotation.z = 2.25; armR.rotation.x = -0.45; armL.position.set(-0.86, 0.05, 0.4); armL.rotation.z = -2.2; armL.rotation.x = -0.5; body.rotation.z = -0.05; },
  stand: () => { armR.rotation.z = 0.32; armL.rotation.z = -0.32; },
  listen:() => { toEar(); armR.rotation.z = 2.25; armR.rotation.x = -0.45; armL.rotation.z = -0.25; body.rotation.z = 0.08; },
  think: () => { armL.rotation.z = -2.2; armL.rotation.x = -0.9; armR.rotation.z = 0.3; body.rotation.z = -0.06; },
};
(POSE[P.pose] || POSE.stand)();

// ── 카메라
const cam = new THREE.PerspectiveCamera(P.fov || 28, P.w / P.h, 0.1, 100);
const VIEW = {
  hero:  { pos: [2.4, 0.9, 6.4], at: [0.05, -0.15, 0] },
  front: { pos: [0, 0.25, 7.2], at: [0.05, -0.2, 0] },
  side:  { pos: [7.2, 0.35, 0.6], at: [0, -0.2, 0] },
  back:  { pos: [-2.6, 0.9, -6.4], at: [0, -0.1, 0] },
  bust:  { pos: [0.9, 0.55, 4.2], at: [0.08, 0.15, 0.3] },
};
const v = VIEW[P.view] || VIEW.hero;
cam.position.set(...v.pos); cam.lookAt(new THREE.Vector3(...v.at));
renderer.render(scene, cam);
window.__done = true;
