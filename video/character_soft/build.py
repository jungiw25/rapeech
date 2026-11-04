"""라피치 캐릭터 시안 4: 부드러운 그림 같은 3D(외곽선 없음, 무광, 따뜻한 색 그라데이션).

레퍼런스의 '느낌'만 따른다: 둥근 블록 몸, 크고 동그란 눈 + 굵은 눈썹, 짧은 국수 같은 팔다리, 힘 있는 자세.
라피치다운 점: 보라→분홍 몸, 한쪽 귀 헤드셋, 칼 대신 수정처럼 빛나는 말풍선을 번쩍.
캐릭터는 Blender(Cycles)로 투명 배경에 렌더하고, 배경(그라데이션·빛줄기·점·별)은 PIL로 그려 합친다.
사용법: video/.venv-bpy/bin/python video/character_soft/build.py && python3 video/character_soft/compose.py
"""
import math
from pathlib import Path

import bpy  # bmesh는 bpy를 먼저 불러야 쓸 수 있음
import bmesh  # noqa: E402
from mathutils import Vector

HERE = Path(__file__).resolve().parent
OUT = HERE / "out"
OUT.mkdir(exist_ok=True)


def lin(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def principled(name, color=None, rough=0.55, sss=0.0, ramp=None, axis="Z", rng=(-0.6, 0.6), trans=0.0, emit=None):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    nt = m.node_tree
    b = nt.nodes["Principled BSDF"]
    b.inputs["Roughness"].default_value = rough
    b.inputs["Subsurface Weight"].default_value = sss
    b.inputs["Subsurface Radius"].default_value = (0.4, 0.2, 0.15)
    b.inputs["Subsurface Scale"].default_value = 0.08
    b.inputs["Coat Weight"].default_value = 0.0
    if trans:
        b.inputs["Transmission Weight"].default_value = trans
        b.inputs["IOR"].default_value = 1.3
    if emit:
        b.inputs["Emission Color"].default_value = lin(emit[0])
        b.inputs["Emission Strength"].default_value = emit[1]
    if ramp:   # 물체 좌표의 한 축을 따라 색이 바뀜(위는 밝게, 아래는 따뜻하게)
        tc = nt.nodes.new("ShaderNodeTexCoord")
        sx = nt.nodes.new("ShaderNodeSeparateXYZ")
        mr = nt.nodes.new("ShaderNodeMapRange")
        mr.inputs["From Min"].default_value, mr.inputs["From Max"].default_value = rng
        cr = nt.nodes.new("ShaderNodeValToRGB")
        els = cr.color_ramp.elements
        els[0].position, els[0].color = ramp[0][0], lin(ramp[0][1])
        els[1].position, els[1].color = ramp[-1][0], lin(ramp[-1][1])
        for pos, col in ramp[1:-1]:
            e = els.new(pos); e.color = lin(col)
        nt.links.new(tc.outputs["Object"], sx.inputs[0])
        nt.links.new(sx.outputs[axis], mr.inputs["Value"])
        nt.links.new(mr.outputs["Result"], cr.inputs["Fac"])
        nt.links.new(cr.outputs["Color"], b.inputs["Base Color"])
    else:
        b.inputs["Base Color"].default_value = lin(color)
    return m


def link(ob):
    bpy.context.scene.collection.objects.link(ob)
    return ob


def smooth(me):
    for p in me.polygons:
        p.use_smooth = True


def block(name, size, bevel, m, loc=(0, 0, 0), rot=(0, 0, 0), seg=10):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    for v in bm.verts:
        v.co = Vector((v.co.x * 2 * size[0], v.co.y * 2 * size[1], v.co.z * 2 * size[2]))   # size = 반 길이
    bm.to_mesh(me); bm.free(); smooth(me)
    ob = link(bpy.data.objects.new(name, me))
    md = ob.modifiers.new("Bevel", "BEVEL"); md.width, md.segments, md.limit_method = bevel, seg, "NONE"
    ob.modifiers.new("Sub", "SUBSURF").levels = 2
    ob.location, ob.rotation_euler = loc, rot
    me.materials.append(m)
    return ob


def ball(name, r, m, loc, scl=(1, 1, 1), rot=(0, 0, 0)):
    me = bpy.data.meshes.new(name); bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=32, radius=r)
    for v in bm.verts:
        v.co = Vector((v.co.x * scl[0], v.co.y * scl[1], v.co.z * scl[2]))
    bm.to_mesh(me); bm.free(); smooth(me)
    ob = link(bpy.data.objects.new(name, me))
    ob.location, ob.rotation_euler = loc, rot
    me.materials.append(m)
    return ob


def noodle(name, pts, r0, r1, m):
    """국수 같은 팔다리: 곡선을 따라 굵기가 r0→r1로 가늘어지는 관."""
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth, cu.bevel_resolution, cu.use_fill_caps = 1.0, 8, True
    sp = cu.splines.new("BEZIER"); sp.bezier_points.add(len(pts) - 1)
    for i, (bp, p) in enumerate(zip(sp.bezier_points, pts)):
        bp.co = p; bp.handle_left_type = bp.handle_right_type = "AUTO"
        bp.radius = r0 + (r1 - r0) * i / (len(pts) - 1)
    ob = link(bpy.data.objects.new(name, cu))
    cu.materials.append(m)
    return ob


# 표정: 눈썹(각도, 높이) · 눈동자(좌우, 위아래, 크기) · 입
EXPR = {
    "brave":    dict(brow=((24, 0), (-26, 0)), look=(0.035, 0.0, 1.0), mouth=None),
    "happy":    dict(brow=((8, 0.07), (-8, 0.07)), look=(0.0, 0.02, 1.0), mouth="smile"),
    "surprise": dict(brow=((-6, 0.09), (6, 0.09)), look=(0.0, 0.0, 0.72), mouth="o"),
    "listen":   dict(brow=((10, 0.0), (-20, 0.07)), look=(0.06, 0.03, 1.0), mouth=None),
}


def build(pose="hero", expr="brave"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    body_m = principled("Body", ramp=[(0.12, "#ff6fb4"), (0.38, "#8d5cff"), (1.0, "#b39aff")], rough=0.62, sss=0.05)
    limb_m = principled("Limb", ramp=[(0.0, "#ff79b6"), (1.0, "#8f5cff")], rng=(-1.3, 0.2), rough=0.62, sss=0.15)
    white = principled("White", "#fbf8ff", rough=0.35)
    ink = principled("Ink", "#22134a", rough=0.4)
    cup_m = principled("Cup", "#ff4fae", rough=0.45)
    pad_m = principled("Pad", "#ffd2ea", rough=0.7)
    crystal = principled("Crystal", "#bba3ff", rough=0.1, trans=0.75, emit=("#c9b6ff", 0.08))
    gem = principled("Gem", "#ffc24a", rough=0.25, emit=("#ffb02e", 0.4))

    rig = bpy.data.objects.new("Rig", None); link(rig)
    # 몸: 둥근 블록(앞 = -Y), 살짝 기울임
    body = block("Body", (0.62, 0.42, 0.44), 0.2, body_m, (0, 0, 0.62))
    body.parent = rig
    # 말풍선 꼬리(왼쪽 아래 모서리)
    me = bpy.data.meshes.new("Tail"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.12, radius2=0.02, depth=0.24)
    bm.to_mesh(me); bm.free(); smooth(me)
    tail = link(bpy.data.objects.new("Tail", me)); me.materials.append(body_m)
    tail.location, tail.rotation_euler = (-0.6, -0.02, 0.28), (0, math.radians(-125), 0)
    tail.modifiers.new("Sub", "SUBSURF").levels = 2
    tail.parent = rig
    # 눈(크고 동그랗게, 앞면 위쪽에 붙어 튀어나옴) + 굵은 눈썹
    E = EXPR[expr]
    lx, ly, ps = E["look"]
    for x in (-0.17, 0.19):
        ball(f"Eye{x}", 0.17, white, (x, -0.4, 0.78), (1, 0.75, 1.08)).parent = rig
        ball(f"Pupil{x}", 0.085 * ps, ink, (x + lx, -0.53, 0.79 + ly), (1, 0.6, 1.22)).parent = rig
        ball(f"Glint{x}", 0.022, white, (x + lx + 0.03 * ps, -0.575, 0.83 + ly)).parent = rig
    for x, (ang, dz) in zip((-0.18, 0.2), E["brow"]):   # brave: 안쪽 끝이 내려간 결심한 눈썹
        b = block(f"Brow{x}", (0.13, 0.04, 0.035), 0.03, ink, (x, -0.47, 1.0 + dz), (0, math.radians(ang), 0), seg=4)
        b.parent = rig
    if E["mouth"] == "smile":
        mo = ball("Mouth", 0.1, ink, (0.01, -0.43, 0.6), (1.15, 0.4, 0.85))   # 아랫부분만 남긴 반달 입(D)
        bm = bmesh.new(); bm.from_mesh(mo.data)
        bmesh.ops.delete(bm, geom=[v for v in bm.verts if v.co.z > 0.001], context="VERTS")
        bm.to_mesh(mo.data); bm.free(); mo.parent = rig
        ball("Tongue", 0.045, cup_m, (0.01, -0.455, 0.54), (1.2, 0.4, 0.55)).parent = rig
    elif E["mouth"] == "o":
        ball("Mouth", 0.045, ink, (0.01, -0.44, 0.55), (0.9, 0.35, 1.15)).parent = rig
    # 헤드셋(오른쪽 귀 하나 + 마이크)
    ball("Cup", 0.13, cup_m, (0.72, -0.02, 0.72), (0.55, 1, 1)).parent = rig
    ball("Pad", 0.1, pad_m, (0.665, -0.02, 0.72), (0.4, 0.85, 0.85)).parent = rig
    mic = noodle("Mic", [(0.74, -0.08, 0.64), (0.7, -0.38, 0.5), (0.42, -0.5, 0.5)], 0.018, 0.018, ink); mic.parent = rig
    ball("MicTip", 0.04, ink, (0.4, -0.5, 0.5)).parent = rig
    band = noodle("Band", [(0.72, 0.0, 0.84), (0.6, 0.06, 1.12), (0.0, 0.12, 1.16), (-0.55, 0.1, 1.08)], 0.028, 0.028, pad_m); band.parent = rig
    # 다리: 벌린 A자, 발끝이 둥글게
    for s, x in ((-1, -0.22), (1, 0.24)):
        noodle(f"Leg{s}", [(x, -0.02, 0.36), (x + s * 0.12, -0.05, 0.16), (x + s * 0.22, -0.08, 0.04)], 0.11, 0.1, limb_m).parent = rig
        ball(f"Foot{s}", 0.12, limb_m, (x + s * 0.26, -0.12, 0.04), (1.1, 1.3, 0.6)).parent = rig
    if pose == "hero":
        # 왼팔: 몸 앞쪽으로 굽혀 주먹 / 오른팔: 높이 들어 수정 말풍선
        noodle("ArmL", [(-0.6, -0.1, 0.62), (-0.82, -0.28, 0.55), (-0.72, -0.48, 0.66)], 0.085, 0.075, limb_m).parent = rig
        ball("FistL", 0.13, limb_m, (-0.7, -0.52, 0.7), (1, 1, 0.9)).parent = rig
        noodle("ArmR", [(0.58, -0.1, 0.8), (0.82, -0.14, 1.02), (0.9, -0.16, 1.3)], 0.085, 0.075, limb_m).parent = rig
        ball("FistR", 0.13, limb_m, (0.9, -0.17, 1.36), (1, 1, 1.05)).parent = rig
        bub = block("Bubble", (0.32, 0.07, 0.24), 0.11, crystal, (1.08, -0.18, 1.72), (0, math.radians(-28), 0), seg=8)
        bub.parent = rig
        tip = bpy.data.meshes.new("BTail"); bm = bmesh.new()
        bmesh.ops.create_cone(bm, cap_ends=True, segments=16, radius1=0.06, radius2=0.005, depth=0.14)
        bm.to_mesh(tip); bm.free(); smooth(tip)
        bt = link(bpy.data.objects.new("BTail", tip)); tip.materials.append(crystal)
        bt.location, bt.rotation_euler = (0.97, -0.18, 1.5), (0, math.radians(160), 0)
        bt.parent = rig
        for i in range(3):
            ball(f"Dot{i}", 0.032, gem, (0.98 + i * 0.09 + i * 0.0, -0.27, 1.72 - i * 0.048)).parent = rig
        rig.rotation_euler = (0, math.radians(-4), math.radians(-14))
    else:
        noodle("ArmL", [(-0.6, -0.05, 0.6), (-0.76, -0.08, 0.42), (-0.78, -0.1, 0.3)], 0.085, 0.075, limb_m).parent = rig
        ball("FistL", 0.12, limb_m, (-0.79, -0.1, 0.25)).parent = rig
        noodle("ArmR", [(0.6, -0.05, 0.6), (0.76, -0.08, 0.42), (0.78, -0.1, 0.3)], 0.085, 0.075, limb_m).parent = rig
        ball("FistR", 0.12, limb_m, (0.79, -0.1, 0.25)).parent = rig

    # 다리를 길게: 다리·발을 뺀 모든 부품을 위로 올림(다리 윗부분은 몸 속으로 들어감)
    for o in list(sc.objects):
        if o.parent == rig and not o.name.startswith(("Leg", "Foot")):
            o.location.z += 0.16
    # 그림자만 받는 바닥
    me = bpy.data.meshes.new("Floor"); bm = bmesh.new()
    bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=8); bm.to_mesh(me); bm.free()
    fl = link(bpy.data.objects.new("Floor", me)); fl.location.z = -0.06; fl.is_shadow_catcher = True
    # 조명: 크고 부드러운 키(왼쪽 위 앞), 연보라 보조, 분홍 테두리
    def area(name, loc, energy, color, size):
        L = bpy.data.lights.new(name, "AREA"); L.energy, L.color, L.size = energy, lin(color)[:3], size
        o = link(bpy.data.objects.new(name, L)); o.location = loc
        o.rotation_euler = (Vector((0, 0, 0.7)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
    area("Key", (-2.2, -3.0, 3.2), 520, "#fff1e6", 3.0)
    area("Fill", (3.2, -2.2, 1.2), 140, "#c9b8ff", 3.0)
    area("Rim", (2.0, 2.6, 2.6), 420, "#ff9ad6", 2.0)
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = lin("#d9ccff")
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.25
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 96
    sc.cycles.use_denoising = True
    sc.render.film_transparent = True
    sc.view_settings.view_transform = "Standard"   # AgX는 색을 바래게 함
    return sc


def shoot(sc, name, cam_loc, look, w=1600, h=1100, lens=55):
    cam = bpy.data.objects.get("Cam")
    if not cam:
        cam = link(bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam"))); sc.camera = cam
    cam.data.lens = lens
    cam.location = cam_loc
    cam.rotation_euler = (Vector(look) - Vector(cam_loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x, sc.render.resolution_y = w, h
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", name)


if __name__ == "__main__":
    sc = build("hero", "brave")
    shoot(sc, "hero_char", (1.0, -6.4, 0.95), (0.22, 0, 0.98), lens=50)
    sc = build("stand", "brave")
    for n, loc in (("front", (0, -5.4, 0.8)), ("side", (5.4, 0, 0.8)), ("back", (0.6, 5.4, 0.9))):
        shoot(sc, n, loc, (0, 0, 0.72), w=800, h=800, lens=70)
    for e in ("brave", "happy", "surprise", "listen"):
        sc = build("stand", e)
        shoot(sc, f"e_{e}", (0.2, -3.2, 1.05), (0, 0, 0.98), w=700, h=700, lens=75)
