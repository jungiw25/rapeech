"""캐릭터 영상 v5(10초, 24fps): 레퍼런스 분석을 반영해 처음부터 다시.

바뀐 점(레퍼런스와의 차이 5가지를 메움)
1. 연출: 장면 7개(눈 극단 클로즈업 → 낮은 각도 중간 → 옆에서 따라가는 질주 → 기운 각도 점프·회전 →
   바닥 높이 착지 → 영웅 클로즈업 → 와이드 마무리). 장면마다 카메라 크기·각도가 다르고, 카메라도 움직인다.
2. 움직임: 예비동작 → 동작 → 넘침 → 정착, 질주 다리 동작, 점프 회전 중 잠깐 느려짐, 착지 눌림·반동,
   모션 블러, 속도선, 회전 궤적, 바닥 충격파.
3. 색: 캐릭터는 따뜻한 코랄·분홍, 배경은 보라(반대색 대비).
4. 캐릭터: 넓적한 블록 몸, 굵고 짧은 다리, 통통한 팔, 눈을 반쯤 덮는 두꺼운 눈썹.
5. 마감: 피사계 심도(배경 흐림), 장면 전환 섬광·와이프·빛 번짐은 finish.py에서.
사용법: video/.venv-bpy/bin/python video/character_v5/build.py [--test 초,초,...]
"""
import math
import sys
from pathlib import Path

import bpy  # noqa: I001  (bmesh는 bpy 다음)
import bmesh  # noqa: E402
from mathutils import Vector  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "character_soft"))
import build as B  # noqa: E402  재질·도형 함수 재사용

FPS, SEC = 24, 10.0
F = lambda t: 1 + round(t * FPS)
R = math.radians
CUTS = [0.0, 1.25, 2.75, 4.25, 6.0, 7.0, 8.2, SEC]


def K(ob, path, t, val):
    setattr(ob, path, val)
    ob.keyframe_insert(path, frame=F(t))


def empty(name, loc=(0, 0, 0), parent=None):
    e = B.link(bpy.data.objects.new(name, None))
    e.location = loc
    if parent:
        e.parent = parent
    return e


def par(ob, p):
    ob.parent = p
    return ob


def emit(name, hexc, s=1.0, alpha_anim=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = B.lin(hexc); em.inputs["Strength"].default_value = s
    if alpha_anim:   # 서서히 사라지게: 투명과 섞는 비율을 키프레임
        tr = nt.nodes.new("ShaderNodeBsdfTransparent")
        mx = nt.nodes.new("ShaderNodeMixShader"); mx.name = "Fade"
        nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2])
        nt.links.new(mx.outputs[0], out.inputs[0])
    else:
        nt.links.new(em.outputs[0], out.inputs[0])
    return m


def star(name, size, m):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    pts = []
    for i in range(8):
        r = size if i % 2 == 0 else size * 0.22
        a = i * math.pi / 4
        pts.append(bm.verts.new((r * math.cos(a), 0, r * math.sin(a))))
    bm.faces.new(pts); bm.to_mesh(me); bm.free()
    ob = B.link(bpy.data.objects.new(name, me)); me.materials.append(m)
    return ob


def show(ob, windows):
    """windows: [(시작초, 끝초)] 동안만 렌더에 보임."""
    ob.hide_render = True; ob.keyframe_insert("hide_render", frame=1)
    for a, b in windows:
        ob.hide_render = False; ob.keyframe_insert("hide_render", frame=F(a))
        ob.hide_render = True; ob.keyframe_insert("hide_render", frame=F(b))


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    # ── 재질
    body_m = B.principled("Body", ramp=[(0.12, "#ff4f8b"), (0.48, "#ff6f61"), (1.0, "#ffa86a")], rng=(-0.46, 0.46), rough=0.6, sss=0.08)
    limb_m = B.principled("Limb", ramp=[(0.0, "#ff4f8b"), (1.0, "#ff7466")], rng=(-0.7, 0.1), rough=0.6, sss=0.08)
    ink = B.principled("Ink", "#2a1660", rough=0.35)
    white = B.principled("White", "#fffaf6", rough=0.3)
    purple = B.principled("Purple", "#6a3df0", rough=0.35)
    pad = B.principled("Pad", "#d9ccff", rough=0.6)
    gold = B.principled("Gold", "#ffc23d", rough=0.25, emit=("#ffb02e", 0.6))
    crystal = B.principled("Crystal", "#cdb9ff", rough=0.08, trans=0.7, emit=("#d7c7ff", 0.25))

    # ── 캐릭터(발바닥 = z 0)
    root = empty("Root")
    sq = empty("Squash", parent=root)          # 눌림·늘어남은 발바닥 기준
    par(B.block("Body", (0.72, 0.48, 0.46), 0.2, body_m, (0, 0, 1.0)), sq)
    look = empty("Look", parent=sq)
    for x in (-0.24, 0.24):
        par(B.ball(f"Eye{x}", 0.25, white, (x, -0.42, 1.24), (1, 0.62, 1.1)), sq)
        par(B.ball(f"Pupil{x}", 0.13, ink, (x, -0.57, 1.22), (1, 0.5, 1.28)), look)
        par(B.ball(f"Glint{x}", 0.032, white, (x + 0.045, -0.635, 1.29)), look)
    brows = []
    for x, a in ((-0.25, 22), (0.25, -22)):
        b = par(B.block(f"Brow{x}", (0.17, 0.055, 0.065), 0.05, ink, (x, -0.46, 1.5), (0, R(a), 0), seg=5), sq)
        b["angry"] = a
        brows.append(b)
    for s in (-1, 1):                          # 헤드폰(양쪽 귀)
        par(B.ball(f"Cup{s}", 0.15, purple, (s * 0.76, -0.02, 1.12), (0.5, 1, 1)), sq)
        par(B.ball(f"Pad{s}", 0.11, pad, (s * 0.71, -0.02, 1.12), (0.35, 0.85, 0.85)), sq)
    par(B.noodle("Band", [(0.76, 0.0, 1.24), (0.6, 0.08, 1.56), (0.0, 0.12, 1.64), (-0.6, 0.08, 1.56), (-0.76, 0.0, 1.24)], 0.04, 0.04, purple), sq)
    par(B.noodle("Mic", [(0.78, -0.1, 1.02), (0.7, -0.4, 0.86), (0.44, -0.5, 0.84)], 0.022, 0.022, purple), sq)
    par(B.ball("MicTip", 0.05, ink, (0.42, -0.5, 0.84)), sq)
    hips = []
    for s in (-1, 1):                          # 굵고 짧은 다리
        h = empty(f"Hip{s}", (s * 0.34, 0, 0.7), sq)
        par(B.noodle(f"Leg{s}", [(0, 0, 0.05), (0, 0, -0.3), (0, -0.02, -0.58)], 0.17, 0.15, limb_m), h)
        par(B.ball(f"Foot{s}", 0.17, limb_m, (0, -0.07, -0.6), (1.1, 1.35, 0.65)), h)
        h.rotation_euler.y = s * R(-10)
        hips.append(h)
    sh = {}
    for s in (-1, 1):                          # 통통한 팔(어깨 축)
        e = empty(f"Shoulder{s}", (s * 0.72, -0.02, 1.02), sq)
        par(B.noodle(f"Arm{s}", [(0, 0, 0), (s * 0.16, -0.04, -0.18), (s * 0.2, -0.08, -0.36)], 0.125, 0.115, limb_m), e)
        par(B.ball(f"Fist{s}", 0.165, limb_m, (s * 0.21, -0.09, -0.42)), e)
        sh[s] = e
    # 오른손의 말풍선 지팡이(손잡이·가드·보석·수정 말풍선) — 팔이 뻗은 방향으로
    sc_g = empty("Scepter", (0.21, -0.09, -0.42), sh[1])
    from mathutils import Quaternion
    sc_g.rotation_euler = (Vector((0.2, -0.08, -0.36)).normalized().to_track_quat("Z", "Y") @ Quaternion((0, 0, 1), math.pi / 2)).to_euler()   # 말풍선 넓은 면이 앞을 보게
    sc_g.scale = (1.45, 1.45, 1.45)   # 화면에서 또렷하게
    par(B.noodle("Handle", [(0, 0, -0.1), (0, 0, 0.12), (0, 0, 0.3)], 0.05, 0.05, purple), sc_g)
    par(B.block("Guard", (0.17, 0.06, 0.05), 0.035, purple, (0, 0, 0.32), seg=4), sc_g)
    par(B.ball("Gem", 0.06, gold, (0, -0.06, 0.32)), sc_g)
    par(B.block("Bubble", (0.24, 0.08, 0.2), 0.11, crystal, (0, 0, 0.58), seg=8), sc_g)
    for i in range(3):
        par(B.ball(f"Dot{i}", 0.035, gold, (-0.09 + i * 0.09, -0.09, 0.6)), sc_g)
    tip = star("Sparkle", 0.16, emit("SparkM", "#ffffff", 4.0)); tip.parent = sc_g; tip.location = (0.0, -0.12, 0.85)

    # ── 무대(보라 대비)
    me = bpy.data.meshes.new("Floor"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40); bm.to_mesh(me); bm.free()
    fl = B.link(bpy.data.objects.new("Floor", me)); me.materials.append(B.principled("FloorM", "#9a80ff", rough=0.95))
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = B.lin("#cbbcff")
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.85
    deco = empty("Deco")
    circ = B.ball("BigCircle", 2.6, emit("CircM", "#ad92ff", 1.0), (0, 7, 2.2), (1, 0.02, 1)); circ.parent = deco
    import random
    rnd = random.Random(4)
    cols = ["#8f6bff", "#ffffff", "#ff8a7a", "#9b7dff", "#ffffff"]
    for i in range(16):                        # 대각선 빛줄기(앞뒤 깊이를 달리해 시차)
        x, y, z = rnd.uniform(-9, 9), rnd.uniform(3.5, 9), rnd.uniform(0.6, 4.2)
        L, th = rnd.uniform(1.2, 3.2), rnd.uniform(0.03, 0.12)
        b = B.block(f"Streak{i}", (L / 2, 0.01, th / 2), 0.0, emit(f"StM{i}", cols[i % 5], 1.0), (x, y, z), (0, R(-28), 0), seg=1)
        b.modifiers.clear(); b.parent = deco
    for i in range(10):
        B.ball(f"Fleck{i}", rnd.uniform(0.05, 0.11), emit(f"FlM{i}", ["#ff5d7a", "#7c5cff"][i % 2], 1.2),
               (rnd.uniform(-7, 7), rnd.uniform(2.5, 7), rnd.uniform(0.8, 3.8))).parent = deco
    # 속도선(질주 장면), 회전 궤적(점프 장면), 충격파(착지 장면), 눈 반짝임(첫 장면)
    for i in range(14):
        b = B.block(f"Speed{i}", (rnd.uniform(0.8, 2.2), 0.01, rnd.uniform(0.008, 0.025)), 0.0, emit(f"SpM{i}", "#ffffff", 2.0),
                    (rnd.uniform(-6, 6), rnd.uniform(-1.4, 2.5), rnd.uniform(0.2, 2.6)), seg=1)
        b.modifiers.clear()
        x0 = b.location.x + 6
        K(b, "location", 2.75, (x0, b.location.y, b.location.z)); K(b, "location", 4.25, (x0 - 14, b.location.y, b.location.z))
        show(b, [(2.75, 4.25)])
    cu = bpy.data.curves.new("Trail", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.035; cu.bevel_resolution = 4
    spl = cu.splines.new("POLY"); spl.points.add(40)
    for i, p in enumerate(spl.points):
        a = math.radians(-20 + i * 6.5); rr = 1.25
        p.co = (rr * math.cos(a), rr * math.sin(a), 1.0 + 0.0 * i, 1)
        p.radius = 0.2 + 0.8 * i / 40
    trail = B.link(bpy.data.objects.new("Trail", cu)); cu.materials.append(emit("TrM", "#ffffff", 3.0)); trail.parent = root
    show(trail, [(4.55, 5.85)])
    rings = []
    for k, col in enumerate(("#7c5cff", "#ff6f61", "#ffffff")):
        tor = bpy.data.meshes.new(f"Tor{k}"); bm = bmesh.new()
        segs, rr, tt = 96, 1.0, 0.035 - k * 0.008
        for i in range(segs):
            a = 2 * math.pi * i / segs
            for j, (dr, dz) in enumerate(((-tt, 0), (0, tt * 0.4), (tt, 0))):
                bm.verts.new(((rr + dr) * math.cos(a), (rr + dr) * math.sin(a), dz))
        bm.verts.ensure_lookup_table()
        for i in range(segs):
            n = (i + 1) % segs
            for j in range(2):
                bm.faces.new((bm.verts[i * 3 + j], bm.verts[n * 3 + j], bm.verts[n * 3 + j + 1], bm.verts[i * 3 + j + 1]))
        bm.to_mesh(tor); bm.free()
        ring = B.link(bpy.data.objects.new(f"Ring{k}", tor)); m = emit(f"RgM{k}", col, 2.0, alpha_anim=True); tor.materials.append(m)
        t0 = 6.3 + k * 0.08
        ring.location.z = 0.02 + k * 0.005
        K(ring, "scale", t0, (0.3, 0.3, 1)); K(ring, "scale", t0 + 0.65, (3.6 + k * 0.8, 3.6 + k * 0.8, 1))
        fd = m.node_tree.nodes["Fade"].inputs[0]
        fd.default_value = 0.0; fd.keyframe_insert("default_value", frame=F(t0))
        fd.default_value = 1.0; fd.keyframe_insert("default_value", frame=F(t0 + 0.65))
        show(ring, [(t0, 7.0)])
        rings.append(ring)
    glint = star("Glint", 0.075, emit("GlM", "#ffffff", 6.0)); glint.parent = look; glint.location = (-0.21, -0.66, 1.27)
    K(glint, "scale", 0.0, (0, 0, 0)); K(glint, "scale", 0.85, (0, 0, 0)); K(glint, "scale", 1.05, (1.4, 1.4, 1.4)); K(glint, "scale", 1.25, (3.5, 3.5, 3.5))
    show(glint, [(0.8, 1.25)])
    show(tip, [(8.6, 10.0)])
    K(tip, "scale", 8.6, (0, 0, 0)); K(tip, "scale", 8.85, (1.3, 1.3, 1.3)); K(tip, "scale", 9.1, (0.9, 0.9, 0.9)); K(tip, "rotation_euler", 8.6, (0, 0, 0)); K(tip, "rotation_euler", 10, (0, R(80), 0))

    # ── 조명
    def area(name, loc, energy, color, size):
        Lg = bpy.data.lights.new(name, "AREA"); Lg.energy, Lg.color, Lg.size = energy, B.lin(color)[:3], size
        o = B.link(bpy.data.objects.new(name, Lg)); o.location = loc
        o.rotation_euler = (Vector((0, 0, 1.0)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    area("Key", (-3.0, -4.0, 5.0), 900, "#fff1e6", 3.0)
    area("Fill", (4.0, -3.0, 1.6), 260, "#c9b8ff", 3.0)
    area("Rim", (2.5, 4.0, 3.2), 750, "#ff9ad6", 2.0)
    return sc, root, sq, look, brows, hips, sh


def animate(sc, root, sq, look, brows, hips, sh):
    up, down = (0, R(-138), 0), (0, 0, 0)
    bentL = (R(-55), R(28), 0)
    def pose(t, r_sh=up, l_sh=bentL, rz=0.0, loc=(0, 0, 0), s=(1, 1, 1), lk=-0.03, angry=1.0):
        K(sh[1], "rotation_euler", t, r_sh); K(sh[-1], "rotation_euler", t, l_sh)
        K(root, "rotation_euler", t, (0, 0, R(rz))); K(root, "location", t, loc); K(sq, "scale", t, s)
        K(look, "location", t, (lk, 0, 0))
        for b in brows:
            K(b, "rotation_euler", t, (0, R(b["angry"] * angry), 0)); K(b, "location", t, (b.location.x, b.location.y, 1.5 + 0.06 * (1 - angry)))
    # 1. 눈 클로즈업: 두리번 → 눈썹이 내려와 결심
    pose(0.0, down, (0, 0, 0), lk=0.0, angry=0.0); pose(0.3, down, (0, 0, 0), lk=0.0, angry=0.0)
    pose(0.55, down, (0, 0, 0), lk=-0.045, angry=0.0); pose(0.85, down, (0, 0, 0), lk=-0.045, angry=1.0); pose(1.24, down, (0, 0, 0), lk=-0.045)
    # 2. 낮은 각도: 웅크림(예비) → 지팡이 번쩍(넘침) → 정착
    pose(1.25, down, (0, 0, 0)); pose(1.5, (0, R(25), 0), (0, 0, 0), s=(1.07, 1.07, 0.9))
    pose(1.9, (0, R(-152), 0), bentL, s=(0.95, 0.95, 1.08)); pose(2.15, up, bentL); pose(2.74, up, bentL)
    # 3. 질주: 오른쪽으로, 다리 번갈아, 몸 위아래
    pose(2.75, (0, R(-95), 0), (R(-40), 0, 0), rz=70, loc=(-3.4, 0, 0))
    pose(4.24, (0, R(-95), 0), (R(-40), 0, 0), rz=70, loc=(3.2, 0, 0))
    for k in range(13):
        t = 2.75 + k * 0.115
        for i, h in enumerate(hips):
            K(h, "rotation_euler", t, (R(45 if (k + i) % 2 else -45), h.rotation_euler.y, 0))
        K(sq, "location", t, (0, 0, 0.08 if k % 2 else 0.0))
    for h in hips:
        K(h, "rotation_euler", 4.25, (0, h.rotation_euler.y, 0))
    K(sq, "location", 4.25, (0, 0, 0))
    # 4. 점프 + 회전(가운데서 잠깐 느려짐) + 지팡이 휘두름
    pose(4.25, up, bentL); pose(4.38, up, bentL, s=(1.12, 1.12, 0.84))
    pose(4.55, (0, R(-80), 0), bentL, loc=(0, 0, 0.6), s=(0.93, 0.93, 1.1))
    pose(4.95, (0, R(-75), 0), bentL, rz=170, loc=(0, 0, 1.45))
    pose(5.4, (0, R(-75), 0), bentL, rz=215, loc=(0, 0, 1.6))
    pose(5.8, (0, R(-120), 0), bentL, rz=360, loc=(0, 0, 1.9))
    pose(5.99, up, bentL, rz=360, loc=(0, 0, 2.4))
    # 5. 바닥 높이 착지: 쿵 → 눌림 → 반동
    pose(6.0, up, bentL, loc=(0, 0, 2.8), s=(0.9, 0.9, 1.15)); pose(6.3, up, bentL, loc=(0, 0, 0), s=(0.95, 0.95, 1.08))
    pose(6.36, up, bentL, s=(1.2, 1.2, 0.74)); pose(6.55, up, bentL, s=(0.95, 0.95, 1.07)); pose(6.75, up, bentL); pose(6.99, up, bentL)
    # 6·7. 영웅 자세: 숨 쉬듯
    pose(7.0, up, bentL, rz=-12); pose(7.6, up, bentL, rz=-12, s=(1, 1, 1.02)); pose(8.19, up, bentL, rz=-12)
    pose(8.2, up, bentL, rz=-14); pose(9.0, up, bentL, rz=-14, s=(1, 1, 1.02)); pose(10.0, up, bentL, rz=-14)


def cameras(sc):
    head = empty("FocusHead", (0, -0.4, 1.2))
    feet = empty("FocusFeet", (0, -0.4, 0.35))
    shots = [  # (시작, 끝, 렌즈, 시작 위치, 끝 위치, 시작 시선, 끝 시선, 기울기°, 조리개)
        (0.0, 1.25, 60, (0.05, -2.75, 1.34), (0.03, -2.35, 1.33), (0.0, 0, 1.33), (0.0, 0, 1.33), 0, 2.8),
        (1.25, 2.75, 26, (1.5, -3.5, 0.4), (1.05, -3.6, 0.35), (0.35, 0, 1.45), (0.4, 0, 1.6), 4, 4.0),
        (2.75, 4.25, 35, (-3.8, -6.2, 1.0), (3.6, -6.2, 1.0), (-3.4, 0, 0.9), (3.2, 0, 0.9), 0, 0),
        (4.25, 6.0, 30, (2.4, -4.2, 0.25), (-1.6, -4.4, 0.4), (0, 0, 1.4), (0, 0, 2.2), 16, 0),
        (6.0, 7.0, 24, (0.9, -1.9, 0.12), (0.8, -2.2, 0.15), (0.1, 0, 0.45), (0.1, 0, 0.5), 0, 3.0),
        (7.0, 8.2, 40, (0.9, -3.4, 1.3), (1.1, -4.3, 1.3), (0.25, 0, 1.5), (0.3, 0, 1.55), 0, 3.0),
        (8.2, 10.0, 38, (1.4, -6.4, 1.2), (1.2, -6.9, 1.2), (0.25, 0, 1.25), (0.25, 0, 1.25), 0, 5.6),
    ]
    for i, (a, b, lens, p0, p1, l0, l1, roll, fstop) in enumerate(shots):
        cam = B.link(bpy.data.objects.new(f"Cam{i}", bpy.data.cameras.new(f"Cam{i}")))
        cam.data.lens = lens
        if fstop:
            cam.data.dof.use_dof = True; cam.data.dof.focus_object = feet if i == 4 else head; cam.data.dof.aperture_fstop = fstop
        for t, p, l in ((a, p0, l0), (b, p1, l1)):
            cam.location = p
            q = (Vector(l) - Vector(p)).to_track_quat("-Z", "Y").to_euler()
            q.rotate_axis("Z", R(roll))
            cam.rotation_euler = q
            cam.keyframe_insert("location", frame=F(t)); cam.keyframe_insert("rotation_euler", frame=F(t))
        mk = sc.timeline_markers.new(f"S{i + 1}", frame=F(a)); mk.camera = cam
        if i == 0:
            sc.camera = cam


def setup_render(sc, out):
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 10; sc.cycles.use_adaptive_sampling = True; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; sc.cycles.transmission_bounces = 4
    sc.render.use_persistent_data = True
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = 1, F(SEC)
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = str(out / "f_")


if __name__ == "__main__":
    out = HERE / "out/frames"; out.mkdir(parents=True, exist_ok=True)
    sc, *rig = build()
    animate(sc, *rig)
    cameras(sc)
    setup_render(sc, out)
    if "--test" in sys.argv:
        ts = [float(x) for x in sys.argv[sys.argv.index("--test") + 1].split(",")]
        for t in ts:
            sc.frame_set(F(t))
            sc.camera = bpy.data.objects[f"Cam{max(i for i, c in enumerate(CUTS[:-1]) if t >= c)}"]
            sc.render.filepath = str(HERE / f"out/test_{t:.2f}.png")
            bpy.ops.render.render(write_still=True)
    else:
        bpy.ops.render.render(animation=True)
