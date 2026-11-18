"""캐릭터 영상 v6(10초, 24fps): 귀여운 캐릭터가 장난감 칼을 이리저리 휘두름(레퍼런스 모티브).

v5에서 어색했던 '막대 팔'을 고친 핵심
- 팔이 어깨·팔꿈치 두 마디로 굽는다. 손이 갈 자리와 칼이 향할 방향만 정하면 팔꿈치 위치를 계산(2관절 IK)해서
  매 프레임 위팔·아래팔·주먹·칼을 붙여 놓는다(관절이 벌어지지 않음).
- 칼을 휘두를 때 몸이 반대로 비틀리고 기울며, 예비동작 → 휘두르기 → 넘침 → 정착 순서를 지킨다.
- 칼끝이 실제로 지나간 길을 매 프레임 계산해 빛 궤적(트레일)으로 그린다.
장면: 눈 클로즈업 → 칼 뽑아 내려베기(낮은 각도) → 깡총 뛰며 좌우 베기(따라가기) → 회전 베기(카메라가 돎)
     → 찌르기 세 번(정면, 흔들림) → 점프 내려찍기 + 충격파(바닥 높이) → 영웅 자세(와이드)
사용법: video/.venv-bpy/bin/python video/character_v6/build.py [--test 초,초,...] [--from 프레임]
"""
import importlib.util
import math
import random
import sys
from pathlib import Path

import bpy  # noqa: I001
import bmesh  # noqa: E402
from mathutils import Quaternion, Vector  # noqa: E402

HERE = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("soft_build", HERE.parent / "character_soft/build.py")
B = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(B)

FPS, SEC = 24, 10.0
F = lambda t: 1 + round(t * FPS)
R = math.radians
V = lambda *a: Vector(a)
CUTS = [0.0, 1.2, 2.6, 4.2, 6.0, 7.2, 8.4, SEC]
L1, L2 = 0.3, 0.28                      # 위팔·아래팔 길이
SH = {1: V(0.74, -0.02, 1.02), -1: V(-0.74, -0.02, 1.02)}   # 어깨(몸 좌표)


def K(ob, path, t, val):
    setattr(ob, path, val)
    ob.keyframe_insert(path, frame=F(t))


def empty(name, loc=(0, 0, 0), parent=None):
    e = B.link(bpy.data.objects.new(name, None)); e.location = loc
    if parent:
        e.parent = parent
    return e


def par(ob, p):
    ob.parent = p
    return ob


def emit(name, hexc, s=1.0, fade=False):
    m = bpy.data.materials.new(name); m.use_nodes = True
    nt = m.node_tree; nt.nodes.clear()
    out = nt.nodes.new("ShaderNodeOutputMaterial")
    em = nt.nodes.new("ShaderNodeEmission"); em.inputs["Color"].default_value = B.lin(hexc); em.inputs["Strength"].default_value = s
    if fade:
        tr = nt.nodes.new("ShaderNodeBsdfTransparent"); mx = nt.nodes.new("ShaderNodeMixShader"); mx.name = "Fade"
        nt.links.new(em.outputs[0], mx.inputs[1]); nt.links.new(tr.outputs[0], mx.inputs[2]); nt.links.new(mx.outputs[0], out.inputs[0])
    else:
        nt.links.new(em.outputs[0], out.inputs[0])
    return m


def star(name, size, m):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    vs = [bm.verts.new(((size if i % 2 == 0 else size * 0.22) * math.cos(i * math.pi / 4), 0, (size if i % 2 == 0 else size * 0.22) * math.sin(i * math.pi / 4))) for i in range(8)]
    bm.faces.new(vs); bm.to_mesh(me); bm.free()
    ob = B.link(bpy.data.objects.new(name, me)); me.materials.append(m)
    return ob


def show(ob, windows):
    ob.hide_render = True; ob.keyframe_insert("hide_render", frame=1)
    for a, b in windows:
        ob.hide_render = False; ob.keyframe_insert("hide_render", frame=F(a))
        ob.hide_render = True; ob.keyframe_insert("hide_render", frame=F(b))


def rod(name, length, r0, r1, m):
    """원점에서 +Z로 length만큼 뻗는 둥근 막대(팔 마디)."""
    return B.noodle(name, [(0, 0, 0), (0, 0, length / 2), (0, 0, length)], r0, r1, m)


def build():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.use_scripts_auto_execute = True
    sc = bpy.context.scene
    M = dict(
        body=B.principled("Body", ramp=[(0.12, "#ff4f8b"), (0.48, "#ff6f61"), (1.0, "#ffa86a")], rng=(-0.46, 0.46), rough=0.6, sss=0.08),
        limb=B.principled("Limb", ramp=[(0.0, "#ff4f8b"), (1.0, "#ff7466")], rng=(-0.3, 0.6), rough=0.6, sss=0.08),
        ink=B.principled("Ink", "#2a1660", rough=0.35), white=B.principled("White", "#fffaf6", rough=0.3),
        purple=B.principled("Purple", "#6a3df0", rough=0.35), pad=B.principled("Pad", "#d9ccff", rough=0.6),
        gold=B.principled("Gold", "#ffc23d", rough=0.25, emit=("#ffb02e", 0.5)),
        blade=B.principled("Blade", ramp=[(0.0, "#7d5cff"), (0.55, "#a98bff"), (1.0, "#e6dcff")], axis="Z", rng=(0.0, 0.95), rough=0.2, emit=("#b49cff", 0.2)),
        pink=B.principled("PinkGem", "#ff5fa8", rough=0.2, emit=("#ff5fa8", 0.4)),
    )
    root = empty("Root")
    sq = empty("Squash", parent=root)            # 발바닥 기준 눌림·기울기
    par(B.block("Body", (0.72, 0.48, 0.46), 0.2, M["body"], (0, 0, 1.0)), sq)
    look = empty("Look", parent=sq)
    for x in (-0.24, 0.24):
        par(B.ball(f"Eye{x}", 0.25, M["white"], (x, -0.42, 1.24), (1, 0.62, 1.1)), sq)
        par(B.ball(f"Pupil{x}", 0.13, M["ink"], (x, -0.57, 1.22), (1, 0.5, 1.28)), look)
        par(B.ball(f"Glint{x}", 0.032, M["white"], (x + 0.045, -0.635, 1.29)), look)
    brows = []
    for x, a in ((-0.25, 22), (0.25, -22)):
        b = par(B.block(f"Brow{x}", (0.17, 0.055, 0.065), 0.05, M["ink"], (x, -0.46, 1.5), (0, R(a), 0), seg=5), sq)
        b["angry"] = a; brows.append(b)
    for s in (-1, 1):
        par(B.ball(f"Cup{s}", 0.15, M["purple"], (s * 0.76, -0.02, 1.12), (0.5, 1, 1)), sq)
        par(B.ball(f"Pad{s}", 0.11, M["pad"], (s * 0.71, -0.02, 1.12), (0.35, 0.85, 0.85)), sq)
    par(B.noodle("Band", [(0.76, 0.0, 1.24), (0.6, 0.08, 1.56), (0.0, 0.12, 1.64), (-0.6, 0.08, 1.56), (-0.76, 0.0, 1.24)], 0.04, 0.04, M["purple"]), sq)
    par(B.noodle("Mic", [(-0.78, -0.1, 1.02), (-0.7, -0.4, 0.86), (-0.44, -0.5, 0.84)], 0.022, 0.022, M["purple"]), sq)
    par(B.ball("MicTip", 0.05, M["ink"], (-0.42, -0.5, 0.84)), sq)
    hips = []
    for s in (-1, 1):
        h = empty(f"Hip{s}", (s * 0.34, 0, 0.7), sq)
        par(B.noodle(f"Leg{s}", [(0, 0, 0.05), (0, 0, -0.3), (0, -0.02, -0.58)], 0.17, 0.15, M["limb"]), h)
        par(B.ball(f"Foot{s}", 0.17, M["limb"], (0, -0.07, -0.6), (1.1, 1.35, 0.65)), h)
        h.rotation_euler.y = s * R(-10); hips.append(h)
    arms = {}
    for s in (-1, 1):                            # 위팔·아래팔·주먹은 매 프레임 IK로 자리를 잡음(몸 좌표)
        ua = par(rod(f"Upper{s}", L1, 0.125, 0.115, M["limb"]), sq)
        fa = par(rod(f"Fore{s}", L2, 0.115, 0.11, M["limb"]), sq)
        fist = par(B.ball(f"Fist{s}", 0.16, M["limb"], (0, 0, 0)), sq)
        par(B.ball(f"Elbow{s}", 0.118, M["limb"], (0, 0, L1)), ua)
        arms[s] = (ua, fa, fist)
    # 장난감 칼: 둥근 손잡이(보라) + 노란 가드 + 분홍 보석 + 통통한 반투명 칼날(끝이 둥근)
    sword = empty("Sword", parent=sq)
    par(B.noodle("Grip", [(0, 0, -0.14), (0, 0, 0.0), (0, 0, 0.12)], 0.05, 0.05, M["purple"]), sword)
    par(B.ball("Pommel", 0.07, M["pink"], (0, 0, -0.17)), sword)
    par(B.block("Guard", (0.2, 0.06, 0.055), 0.045, M["gold"], (0, 0, 0.15), seg=5), sword)
    par(B.ball("Gem", 0.055, M["pink"], (0, -0.06, 0.15)), sword)
    par(B.block("BladeM", (0.12, 0.05, 0.38), 0.045, M["blade"], (0, 0, 0.57), seg=6), sword)
    par(B.ball("BladeTip", 0.12, M["blade"], (0, 0, 0.93), (1, 0.42, 0.9)), sword)
    sword.scale = (1.25, 1.25, 1.25)   # 화면에서 또렷한 장난감 칼
    tip = empty("Tip", (0, 0, 0.98), sword)
    spark = par(star("Sparkle", 0.16, emit("SparkM", "#ffffff", 5.0)), sword); spark.location = (0, -0.08, 1.05)
    # 무대
    me = bpy.data.meshes.new("Floor"); bm = bmesh.new(); bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=40); bm.to_mesh(me); bm.free()
    fl = B.link(bpy.data.objects.new("Floor", me)); me.materials.append(B.principled("FloorM", "#9a80ff", rough=0.95))
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = B.lin("#cbbcff")
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.85
    B.ball("BigCircle", 2.6, emit("CircM", "#ad92ff", 1.0), (0, 7, 2.2), (1, 0.02, 1))
    rnd = random.Random(9)
    cols = ["#8f6bff", "#ffffff", "#ff8a7a", "#9b7dff", "#ffffff"]
    for i in range(16):
        x, y, z = rnd.uniform(-9, 9), rnd.uniform(3.5, 9), rnd.uniform(0.6, 4.2)
        b = B.block(f"Streak{i}", (rnd.uniform(0.6, 1.6), 0.01, rnd.uniform(0.015, 0.06)), 0.0, emit(f"StM{i}", cols[i % 5], 1.0), (x, y, z), (0, R(-28), 0), seg=1)
        b.modifiers.clear()
    for i in range(10):
        B.ball(f"Fleck{i}", rnd.uniform(0.05, 0.11), emit(f"FlM{i}", ["#ff5d7a", "#7c5cff"][i % 2], 1.2), (rnd.uniform(-7, 7), rnd.uniform(2.5, 7), rnd.uniform(0.8, 3.8)))
    for i in range(14):                          # 깡총 베기 장면의 속도선
        b = B.block(f"Speed{i}", (rnd.uniform(0.8, 2.2), 0.01, rnd.uniform(0.008, 0.025)), 0.0, emit(f"SpM{i}", "#ffffff", 2.0),
                    (rnd.uniform(-6, 6), rnd.uniform(-1.4, 2.5), rnd.uniform(0.2, 2.6)), seg=1)
        b.modifiers.clear(); x0 = b.location.x + 6
        K(b, "location", 2.6, (x0, b.location.y, b.location.z)); K(b, "location", 4.2, (x0 - 14, b.location.y, b.location.z))
        show(b, [(2.6, 4.2)])
    for k, col in enumerate(("#7c5cff", "#ff6f61", "#ffffff")):   # 내려찍기 충격파
        tor = bpy.data.meshes.new(f"Tor{k}"); bm = bmesh.new(); segs, tt = 96, 0.035 - k * 0.008
        for i in range(segs):
            a = 2 * math.pi * i / segs
            for dr, dz in ((-tt, 0), (0, tt * 0.4), (tt, 0)):
                bm.verts.new(((1 + dr) * math.cos(a), (1 + dr) * math.sin(a), dz))
        bm.verts.ensure_lookup_table()
        for i in range(segs):
            n = (i + 1) % segs
            for j in range(2):
                bm.faces.new((bm.verts[i * 3 + j], bm.verts[n * 3 + j], bm.verts[n * 3 + j + 1], bm.verts[i * 3 + j + 1]))
        bm.to_mesh(tor); bm.free()
        ring = B.link(bpy.data.objects.new(f"Ring{k}", tor)); m = emit(f"RgM{k}", col, 2.0, fade=True); tor.materials.append(m)
        t0 = 7.8 + k * 0.08; ring.location = (0.3, -0.6, 0.02 + k * 0.005)
        K(ring, "scale", t0, (0.3, 0.3, 1)); K(ring, "scale", t0 + 0.65, (3.4 + k * 0.8, 3.4 + k * 0.8, 1))
        fd = m.node_tree.nodes["Fade"].inputs[0]
        fd.default_value = 0.0; fd.keyframe_insert("default_value", frame=F(t0)); fd.default_value = 1.0; fd.keyframe_insert("default_value", frame=F(t0 + 0.65))
        show(ring, [(t0, 8.5)])
    glint = star("EyeGlint", 0.075, emit("GlM", "#ffffff", 6.0)); glint.parent = look; glint.location = (-0.21, -0.66, 1.27)
    for t, s in ((0.0, 0), (0.75, 0), (0.95, 1.4), (1.2, 3.6)):
        K(glint, "scale", t, (s, s, s))
    show(glint, [(0.7, 1.2)])
    for t, s in ((0, 0), (8.7, 0), (8.95, 1.4), (9.2, 0.9)):
        K(spark, "scale", t, (s, s, s))
    K(spark, "rotation_euler", 8.7, (0, 0, 0)); K(spark, "rotation_euler", SEC, (0, R(90), 0))
    show(spark, [(8.7, SEC)])

    def area(name, loc, energy, color, size):
        Lg = bpy.data.lights.new(name, "AREA"); Lg.energy, Lg.color, Lg.size = energy, B.lin(color)[:3], size
        o = B.link(bpy.data.objects.new(name, Lg)); o.location = loc
        o.rotation_euler = (V(0, 0, 1.0) - V(*loc)).to_track_quat("-Z", "Y").to_euler()
    area("Key", (-3.0, -4.0, 5.0), 900, "#fff1e6", 3.0)
    area("Fill", (4.0, -3.0, 1.6), 260, "#c9b8ff", 3.0)
    area("Rim", (2.5, 4.0, 3.2), 750, "#ff9ad6", 2.0)
    return sc, dict(root=root, sq=sq, look=look, brows=brows, hips=hips, arms=arms, sword=sword, tip=tip)


# ───────────────────────────── 동작
# 오른손 자세: (손 위치 = 어깨 + 오프셋, 칼 방향, 팔꿈치가 향할 쪽)  — 몸 좌표, 팔 길이 안(0.56 이내)
POSE = {
    "rest":   (V(0.12, -0.12, -0.5), V(0.25, -0.75, 0.6), V(0.3, 0.6, -0.4)),
    "ready":  (V(0.1, -0.42, -0.25), V(0.3, -0.7, 0.65), V(0.6, 0.3, -0.6)),
    "wind":   (V(0.0, 0.12, 0.52), V(-0.35, 0.45, 0.82), V(0.8, 0.2, -0.1)),
    "chop":   (V(-0.08, -0.5, -0.12), V(-0.45, -0.55, -0.7), V(0.7, 0.4, -0.3)),
    "right":  (V(0.42, -0.32, 0.05), V(0.95, -0.25, 0.1), V(0.0, 0.5, -0.8)),
    "left":   (V(-0.12, -0.52, 0.05), V(-0.85, -0.5, 0.12), V(0.6, 0.0, -0.8)),
    "poke":   (V(0.02, -0.55, 0.03), V(0.0, -1.0, 0.04), V(0.6, 0.2, -0.7)),
    "hero":   (V(0.18, -0.18, 0.5), V(0.28, -0.1, 0.95), V(0.8, 0.2, -0.2)),
}
LEFT = {   # 왼손: 균형을 잡는 자세(주먹)
    "down":  V(-0.12, -0.18, -0.48), "guard": V(-0.05, -0.45, -0.22), "out": V(-0.48, -0.08, -0.12), "hip": V(-0.18, 0.05, -0.45),
}
# (시각, 오른손 자세, 왼손 자세)
RKEYS = [(0.0, "rest", "down"), (1.2, "rest", "down"), (1.4, "ready", "guard"), (1.7, "wind", "guard"), (1.86, "chop", "out"),
         (1.95, "chop", "out"), (2.3, "ready", "guard"),
         (2.65, "ready", "guard"), (2.85, "right", "out"), (3.1, "left", "guard"), (3.35, "right", "out"), (3.6, "left", "guard"),
         (3.85, "right", "out"), (4.15, "ready", "guard"),
         (4.35, "right", "out"), (5.65, "right", "out"), (5.95, "ready", "guard"),
         (6.05, "ready", "guard"), (6.18, "poke", "hip"), (6.32, "ready", "hip"), (6.46, "poke", "hip"), (6.6, "ready", "hip"),
         (6.74, "poke", "hip"), (7.0, "ready", "guard"),
         (7.25, "ready", "guard"), (7.5, "wind", "out"), (7.78, "chop", "out"), (8.1, "chop", "out"), (8.45, "hero", "hip"),
         (SEC, "hero", "hip")]


def smooth(u):
    return u * u * (3 - 2 * u)


def blend(keys, t, getter):
    for (t0, *a), (t1, *b) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            u = smooth((t - t0) / max(1e-6, t1 - t0))
            return getter(a, b, u)
    return getter(keys[-1][1:], keys[-1][1:], 0)


def ik(shoulder, target, pole):
    d = target - shoulder
    dist = min(d.length, L1 + L2 - 1e-3)
    u = d.normalized(); target = shoulder + u * dist
    a = (L1 * L1 + dist * dist - L2 * L2) / (2 * dist)
    h = math.sqrt(max(0.0, L1 * L1 - a * a))
    pv = (pole - u * pole.dot(u)).normalized()
    return shoulder + u * a + pv * h, target


def place(ob, start, end):
    ob.location = start
    ob.rotation_euler = (end - start).to_track_quat("Z", "Y").to_euler()


def animate(sc, P):
    root, sq, look, brows, hips = P["root"], P["sq"], P["look"], P["brows"], P["hips"]
    # 몸: (시각, 위치, 회전Z°, 기울기X°, 기울기Y°, 눌림)
    body = [(0.0, (0, 0, 0), 0, 0, 0, 1.0), (1.2, (0, 0, 0), 0, 0, 0, 1.0), (1.45, (0, 0, 0), 8, 0, 0, 0.92), (1.7, (0, 0, 0), 18, -8, 6, 1.06),
            (1.86, (0, 0, 0), -20, 12, -8, 0.86), (2.0, (0, 0, 0), -24, 9, -6, 1.04), (2.35, (0, 0, 0), -6, 2, 0, 1.0),
            (2.6, (-2.4, 0, 0), 10, 0, 0, 1.0)]
    x, hop = -2.4, 0
    for k, t in enumerate((2.85, 3.1, 3.35, 3.6, 3.85)):
        x += 0.95
        body.append((t, (x, 0, 0), -38 if k % 2 == 0 else 30, 4, 0, 1.0))
    body += [(4.15, (2.4, 0, 0), 0, 0, 0, 1.0), (4.2, (0, 0, 0), 0, 0, 0, 1.0), (4.35, (0, 0, 0), 30, 0, 0, 0.88),
             (4.75, (0, 0, 0.35), -110, 0, 0, 1.06), (5.25, (0, 0, 0.45), -230, 0, 0, 1.06), (5.65, (0, 0, 0.1), -350, 0, 0, 1.0),
             (5.95, (0, 0, 0), -360, 0, 0, 0.94), (6.0, (0, 0, 0), 0, 0, 0, 1.0)]
    for t, lean in ((6.18, 10), (6.32, 0), (6.46, 11), (6.6, 0), (6.74, 12), (7.0, 0)):
        body.append((t, (0, 0, 0), 0, lean, 0, 1.0))
    body += [(7.2, (0, 0, 0), -10, 0, 0, 1.0), (7.35, (0, 0, 0), -10, -4, 0, 0.84), (7.55, (0, 0, 0.95), -6, -10, 4, 1.1),
             (7.78, (0, 0, 0), -4, 14, -4, 1.0), (7.84, (0, 0, 0), -4, 14, -4, 0.74), (8.05, (0, 0, 0), -6, 6, 0, 1.06),
             (8.4, (0, 0, 0), -14, 0, 0, 1.0), (9.2, (0, 0, 0), -14, 0, 0, 1.02), (SEC, (0, 0, 0), -14, 0, 0, 1.0)]
    for t, loc, rz, rx, ry, s in body:
        K(root, "location", t, loc); K(root, "rotation_euler", t, (0, 0, R(rz)))
        K(sq, "rotation_euler", t, (R(rx), R(ry), 0)); K(sq, "scale", t, (1 / math.sqrt(s), 1 / math.sqrt(s), s))
    for k in range(5):                          # 깡총: 베기마다 살짝 떠오름
        t = 2.72 + k * 0.25
        K(sq, "location", t, (0, 0, 0.0)); K(sq, "location", t + 0.12, (0, 0, 0.22)); K(sq, "location", t + 0.24, (0, 0, 0.0))
        for i, h in enumerate(hips):
            K(h, "rotation_euler", t + 0.12, (R(25 if (k + i) % 2 else -25), h.rotation_euler.y, 0))
    for h in hips:
        K(h, "rotation_euler", 2.6, (0, h.rotation_euler.y, 0)); K(h, "rotation_euler", 4.2, (0, h.rotation_euler.y, 0))
    # 눈·눈썹
    for t, lx, ang, dz in ((0.0, 0.0, 0, 0.06), (0.3, 0.0, 0, 0.06), (0.5, 0.05, 0, 0.06), (0.75, 0.05, 1, 0), (1.2, 0.05, 1, 0),
                            (6.0, 0.0, 1, 0), (8.6, 0.0, 1, 0), (8.9, 0.0, 0.5, 0.03)):
        K(look, "location", t, (lx, 0, 0))
        for b in brows:
            K(b, "rotation_euler", t, (0, R(b["angry"] * ang), 0)); K(b, "location", t, (b.location.x, b.location.y, 1.5 + dz))
    # 팔·칼: 매 프레임 IK로 붙여 넣음
    ua_r, fa_r, fist_r = P["arms"][1]; ua_l, fa_l, fist_l = P["arms"][-1]
    sword = P["sword"]
    for fr in range(1, F(SEC) + 1):
        t = (fr - 1) / FPS
        hand, sdir, pole = blend(RKEYS, t, lambda a, b, u: tuple(POSE[a[0]][i].lerp(POSE[b[0]][i], u) for i in range(3)))
        lh = blend(RKEYS, t, lambda a, b, u: LEFT[a[1]].lerp(LEFT[b[1]], u))
        el, hp = ik(SH[1], SH[1] + hand, pole)
        place(ua_r, SH[1], el); place(fa_r, el, hp); fist_r.location = hp
        sword.location = hp
        q = sdir.normalized().to_track_quat("Z", "Y") @ Quaternion((0, 0, 1), math.pi / 2)
        sword.rotation_euler = q.to_euler()
        el2, hp2 = ik(SH[-1], SH[-1] + lh, V(-0.6, 0.3, -0.6))
        place(ua_l, SH[-1], el2); place(fa_l, el2, hp2); fist_l.location = hp2
        for ob in (ua_r, fa_r, ua_l, fa_l, sword):
            ob.keyframe_insert("location", frame=fr); ob.keyframe_insert("rotation_euler", frame=fr)
        for ob in (fist_r, fist_l):
            ob.keyframe_insert("location", frame=fr)


def trails(sc, P):
    """칼끝이 실제로 지나간 길을 따라 빛 궤적을 만들고, 그려졌다가 꼬리부터 사라지게."""
    tip = P["tip"]
    pts = {}
    for fr in range(1, F(SEC) + 1):
        sc.frame_set(fr); pts[fr] = tip.matrix_world.translation.copy()
    swings = [(1.72, 2.0), (2.78, 3.0), (3.03, 3.25), (3.28, 3.5), (3.53, 3.75), (3.78, 3.98), (4.4, 5.7), (7.55, 7.9)]
    for k, (a, b) in enumerate(swings):
        frs = list(range(F(a), F(b) + 1))
        cu = bpy.data.curves.new(f"Trail{k}", "CURVE"); cu.dimensions = "3D"; cu.bevel_depth = 0.075; cu.bevel_resolution = 3
        sp = cu.splines.new("POLY"); sp.points.add(len(frs) - 1)
        for i, (p, fr) in enumerate(zip(sp.points, frs)):
            p.co = (*pts[fr], 1); p.radius = 0.25 + 0.75 * math.sin(math.pi * i / max(1, len(frs) - 1))
        ob = B.link(bpy.data.objects.new(f"Trail{k}", cu)); cu.materials.append(emit(f"TrM{k}", "#ffffff", 3.0))
        dur = b - a
        cu.bevel_factor_start, cu.bevel_factor_end = 0.0, 0.0
        cu.keyframe_insert("bevel_factor_end", frame=F(a)); cu.keyframe_insert("bevel_factor_start", frame=F(a))
        cu.bevel_factor_end = 1.0; cu.keyframe_insert("bevel_factor_end", frame=F(b))
        cu.bevel_factor_start = 0.0; cu.keyframe_insert("bevel_factor_start", frame=F(a + dur * 0.5))
        cu.bevel_factor_start = 1.0; cu.keyframe_insert("bevel_factor_start", frame=F(b + 0.18))
        show(ob, [(a, b + 0.2)])


def cameras(sc):
    head = empty("FocusHead", (0, -0.4, 1.2))
    shots = [  # (시작, 끝, 렌즈, 시작 위치, 끝 위치, 시작 시선, 끝 시선, 기울기°, 조리개)
        (0.0, 1.2, 60, (0.05, -2.75, 1.34), (0.03, -2.35, 1.33), (0.0, 0, 1.33), (0.0, 0, 1.33), 0, 2.8),
        (1.2, 2.6, 26, (1.6, -3.7, 0.4), (1.2, -3.9, 0.35), (0.3, 0, 1.4), (0.3, 0, 1.45), 5, 4.0),
        (2.6, 4.2, 35, (-3.0, -6.3, 1.1), (3.0, -6.3, 1.1), (-2.4, 0, 1.0), (2.4, 0, 1.0), 0, 0),
        (4.2, 6.0, 30, (3.4, -4.6, 1.6), (-3.4, -4.6, 1.2), (0, 0, 1.3), (0, 0, 1.5), 12, 0),
        (6.0, 7.2, 40, (0.35, -4.0, 1.15), (0.3, -3.6, 1.15), (0.1, 0, 1.1), (0.1, 0, 1.1), 0, 3.5),
        (7.2, 8.4, 24, (1.6, -2.9, 0.15), (1.3, -3.2, 0.2), (0.2, 0, 1.0), (0.2, 0, 0.8), 6, 0),
        (8.4, 10.0, 38, (1.5, -7.2, 1.4), (1.3, -7.8, 1.4), (0.35, 0, 1.55), (0.35, 0, 1.55), 0, 5.6),
    ]
    for i, (a, b, lens, p0, p1, l0, l1, roll, fstop) in enumerate(shots):
        cam = B.link(bpy.data.objects.new(f"Cam{i}", bpy.data.cameras.new(f"Cam{i}")))
        cam.data.lens = lens
        if fstop:
            cam.data.dof.use_dof = True; cam.data.dof.focus_object = head; cam.data.dof.aperture_fstop = fstop
        for t, p, l in ((a, p0, l0), (b, p1, l1)):
            cam.location = p
            q = (V(*l) - V(*p)).to_track_quat("-Z", "Y").to_euler(); q.rotate_axis("Z", R(roll))
            cam.rotation_euler = q
            cam.keyframe_insert("location", frame=F(t)); cam.keyframe_insert("rotation_euler", frame=F(t))
        if i == 4:                               # 찌를 때마다 화면이 툭 흔들림
            for tt in (6.18, 6.46, 6.74):
                for dt, dx in ((0.0, 0.0), (0.04, 0.05), (0.08, -0.035), (0.13, 0.0)):
                    pos = V(*p0).lerp(V(*p1), (tt + dt - a) / (b - a)); pos.x += dx
                    cam.location = pos; cam.keyframe_insert("location", frame=F(tt + dt))
        sc.timeline_markers.new(f"S{i + 1}", frame=F(a)).camera = cam
        if i == 0:
            sc.camera = cam


def setup_render(sc, out):
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 10; sc.cycles.use_adaptive_sampling = True; sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4; sc.cycles.transmission_bounces = 4
    sc.render.use_motion_blur = True; sc.render.motion_blur_shutter = 0.45
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.render.fps = FPS; sc.frame_start, sc.frame_end = 1, F(SEC)
    sc.view_settings.view_transform = "Standard"
    sc.render.image_settings.file_format = "PNG"
    sc.render.filepath = str(out / "f_")


def make():
    sc, P = build()
    animate(sc, P)
    trails(sc, P)
    cameras(sc)
    return sc


if __name__ == "__main__":
    out = HERE / "out/frames"; out.mkdir(parents=True, exist_ok=True)
    sc = make()
    setup_render(sc, out)
    if "--test" in sys.argv:
        for t in [float(x) for x in sys.argv[sys.argv.index("--test") + 1].split(",")]:
            sc.frame_set(F(t))
            sc.camera = bpy.data.objects[f"Cam{max(i for i, c in enumerate(CUTS[:-1]) if t >= c)}"]
            sc.render.filepath = str(HERE / f"out/test_{t:.2f}.png")
            bpy.ops.render.render(write_still=True)
    else:
        if "--from" in sys.argv:
            sc.frame_start = int(sys.argv[sys.argv.index("--from") + 1])
        bpy.ops.render.render(animation=True)
