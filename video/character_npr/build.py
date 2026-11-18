"""라피치 캐릭터 시안 3: Blender로 만든 3D, 단 '툰(셀) 셰이딩 + 외곽선'으로 손으로 칠한 듯한 느낌.

반짝이는 플라스틱 재질(물리 기반 렌더) 대신 blender-stylized-npr 스킬의 toon_setup으로
그림자 두 단계 + 차분한 보라 그림자색 + 가장자리 빛 + 바깥 외곽선을 입힌다.
말랑한 말풍선 몸(왼쪽 아래 작은 꼬리), 큰 헤드폰과 작은 마이크, 머리 위 잎 세 가닥(로고 줄무늬를 살짝).
사용법: video/.venv-bpy/bin/python video/character_npr/build.py → out/*.png
"""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

HERE = Path(__file__).resolve().parent
REPO = HERE.parent.parent
sys.path.insert(0, str(REPO / ".claude/skills/blender-stylized-npr/scripts"))
import toon_setup  # noqa: E402

OUT = HERE / "out"
OUT.mkdir(exist_ok=True)


def srgb(h):
    h = h.lstrip("#")
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple(x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c) + (1.0,)


def mat(name, hexc):
    m = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    m.use_nodes = True
    m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = srgb(hexc)
    m.node_tree.nodes["Principled BSDF"].inputs["Roughness"].default_value = 0.8
    return m


def sphere(name, loc, scl, m, rot=(0, 0, 0), sub=2):
    me = bpy.data.meshes.new(name)
    import bmesh
    bm = bmesh.new()
    bmesh.ops.create_uvsphere(bm, u_segments=48, v_segments=24, radius=1.0)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    ob = bpy.data.objects.new(name, me)
    bpy.context.scene.collection.objects.link(ob)
    ob.location, ob.scale, ob.rotation_euler = loc, scl, rot
    me.materials.append(m)
    if sub:
        ob.modifiers.new("Sub", "SUBSURF").levels = sub
    return ob


def tube(name, pts, radius, m):
    cu = bpy.data.curves.new(name, "CURVE"); cu.dimensions = "3D"
    cu.bevel_depth, cu.bevel_resolution = radius, 6
    sp = cu.splines.new("NURBS"); sp.points.add(len(pts) - 1)
    for p, c in zip(sp.points, pts):
        p.co = (*c, 1)
    sp.use_endpoint_u = True; sp.order_u = 3; sp.use_smooth = True
    ob = bpy.data.objects.new(name, cu)
    bpy.context.scene.collection.objects.link(ob)
    cu.materials.append(m)
    return ob


def to_mesh(ob):
    dg = bpy.context.evaluated_depsgraph_get()
    me = bpy.data.meshes.new_from_object(ob.evaluated_get(dg))
    for p in me.polygons:
        p.use_smooth = True
    new = bpy.data.objects.new(ob.name + "_m", me)
    new.matrix_world = ob.matrix_world.copy()
    bpy.context.scene.collection.objects.link(new)
    bpy.data.objects.remove(ob)
    return new


def apply_scale(ob):
    me = ob.data
    s = ob.scale.copy()
    for v in me.vertices:
        v.co = Vector((v.co.x * s.x, v.co.y * s.y, v.co.z * s.z))
    ob.scale = (1, 1, 1)


def build(expr="happy", pose="wave"):
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.preferences.filepaths.use_scripts_auto_execute = True   # 툰 셰이딩의 해 방향 드라이버가 돌게
    sc = bpy.context.scene
    M = dict(body=mat("Body", "#9a7cff"), limb=mat("Limb", "#8466f2"), pink=mat("Pink", "#ff7cc4"),
             band=mat("Band", "#ffc6e6"), ink=mat("Ink", "#2b1d55"), cheek=mat("Cheek", "#ff9ec4"), white=mat("White", "#ffffff"))
    parts = []
    # 몸: 말랑한 떡(아래가 살짝 넓고 납작)
    body = sphere("Body", (0, 0, 0.56), (0.56, 0.5, 0.5), M["body"])
    for v in body.data.vertices:
        if v.co.z < 0:
            v.co.x *= 1.06; v.co.y *= 1.04; v.co.z *= 0.86
    parts.append(body)
    # 말풍선 꼬리(왼쪽 아래)
    import bmesh
    me = bpy.data.meshes.new("Tail"); bm = bmesh.new()
    bmesh.ops.create_cone(bm, cap_ends=True, segments=24, radius1=0.13, radius2=0.015, depth=0.26)
    bm.to_mesh(me); bm.free()
    for p in me.polygons:
        p.use_smooth = True
    tail = bpy.data.objects.new("Tail", me); sc.collection.objects.link(tail)
    tail.location, tail.rotation_euler = (-0.5, 0.02, 0.2), (0, math.radians(-128), math.radians(-10))
    me.materials.append(M["body"]); tail.modifiers.new("Sub", "SUBSURF").levels = 2
    parts.append(tail)
    # 발, 팔
    for x in (-0.19, 0.19):
        parts.append(sphere(f"Foot{x}", (x, -0.06, 0.07), (0.15, 0.17, 0.075), M["limb"]))
    arm_r = {"wave": ((0.56, -0.12, 0.9), (math.radians(-15), math.radians(-42), 0)), "stand": ((0.6, -0.06, 0.4), (0, math.radians(25), 0)),
             "listen": ((0.58, -0.12, 0.72), (0, math.radians(-40), 0)), "cheer": ((0.56, -0.12, 0.9), (math.radians(-15), math.radians(-42), 0))}[pose]
    arm_l = ((-0.56, -0.12, 0.9), (math.radians(-15), math.radians(42), 0)) if pose == "cheer" else ((-0.6, -0.06, 0.4), (0, math.radians(-25), 0))
    parts.append(sphere("ArmR", arm_r[0], (0.1, 0.09, 0.14), M["limb"], arm_r[1]))
    parts.append(sphere("ArmL", arm_l[0], (0.1, 0.09, 0.14), M["limb"], arm_l[1]))
    # 잎 세 가닥
    for i, (x, h, tilt) in enumerate(((-0.08, 0.12, 22), (0.02, 0.16, 12), (0.12, 0.11, -2))):
        parts.append(sphere(f"Leaf{i}", (x, -0.1, 1.02 + h * 0.75), (0.05, 0.035, h * 1.15), M["pink"] if i < 2 else M["band"], (0, math.radians(tilt), 0)))
    # 헤드폰
    for s in (-1, 1):
        cup = sphere(f"Cup{s}", (s * 0.57, 0.0, 0.62), (0.07, 0.15, 0.17), M["pink"])
        parts.append(cup)
        parts.append(sphere(f"Pad{s}", (s * 0.52, 0.0, 0.62), (0.05, 0.12, 0.14), M["band"]))
    band = tube("Band", [(-0.6, 0.06, 0.66), (-0.62, 0.08, 1.0), (-0.3, 0.1, 1.12), (0.3, 0.1, 1.12), (0.62, 0.08, 1.0), (0.6, 0.06, 0.66)], 0.035, M["band"])
    parts.append(to_mesh(band))
    mic = tube("Mic", [(0.6, -0.08, 0.55), (0.56, -0.32, 0.42), (0.34, -0.47, 0.42), (0.2, -0.49, 0.44)], 0.016, M["ink"])
    parts.append(to_mesh(mic))
    parts.append(sphere("MicTip", (0.18, -0.5, 0.44), (0.035, 0.035, 0.035), M["ink"]))
    # 얼굴(앞 = -Y)
    if expr == "happy":
        for x in (-0.17, 0.17):
            parts.append(to_mesh(tube(f"EyeArc{x}", [(x - 0.06, -0.47, 0.6), (x, -0.5, 0.66), (x + 0.06, -0.47, 0.6)], 0.016, M["ink"])))
        parts.append(sphere("Mouth", (0, -0.49, 0.47), (0.05, 0.02, 0.035), M["ink"]))
    else:
        for x in (-0.17, 0.17):
            parts.append(sphere(f"Eye{x}", (x, -0.47, 0.6), (0.045, 0.025, 0.065), M["ink"], (math.radians(12), 0, x * -1.2)))
            parts.append(sphere(f"Hi{x}", (x + 0.015, -0.495, 0.635), (0.014, 0.008, 0.014), M["white"], sub=0))
        parts.append(to_mesh(tube("Smile", [(-0.045, -0.5, 0.49), (0, -0.515, 0.465), (0.045, -0.5, 0.49)], 0.012, M["ink"])))
    for x in (-0.33, 0.33):
        parts.append(sphere(f"Cheek{x}", (x, -0.43, 0.5), (0.075, 0.03, 0.042), M["cheek"], (0, 0, math.copysign(0.55, x))))
    for o in parts:
        apply_scale(o) if o.type == "MESH" else None
    toon = [o.name for o in parts if not o.name.startswith(("Hi", "Cheek", "Eye", "Smile", "Mouth"))]   # 얼굴 부품은 외곽선 없이
    toon_setup.run(objects=toon, bands=2, shadow_tint=(0.62, 0.55, 0.85), softness=0.03, rim=0.35, outline=0.012,
                   outline_color=(0.17, 0.11, 0.33))
    # 주의: toon_setup을 두 번 부르면 공유 노드 그룹이 다시 만들어져 앞의 값이 0으로 돌아감 → 한 번만 부른다(볼·눈 반짝임은 그대로)
    sun = bpy.data.objects.get("NPR_Key")
    sun.rotation_euler = (math.radians(50), math.radians(-25), math.radians(-35))
    # 바닥 그림자(번지지 않는 납작한 원)
    sh = sphere("Shadow", (0.02, 0.02, 0.001), (0.62, 0.5, 0.002), mat("ShadowM", "#e8cfd9"), sub=0)
    w = bpy.data.worlds.new("W"); sc.world = w; w.use_nodes = True
    w.node_tree.nodes["Background"].inputs["Color"].default_value = srgb("#fff3ea")
    w.node_tree.nodes["Background"].inputs["Strength"].default_value = 1.0
    sh.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Color"].default_value = srgb("#f1d9e0")
    sh.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Emission Strength"].default_value = 1.0
    sh.data.materials[0].node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (0, 0, 0, 1)
    sc.render.engine = "CYCLES"
    sc.cycles.samples = 48
    sc.cycles.use_denoising = True
    sc.render.film_transparent = False
    return sc


def shoot(sc, name, cam_loc, look=(0, 0, 0.55), size=1200, lens=60):
    cam = bpy.data.objects.get("Cam")
    if not cam:
        cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = lens
    cam.location = cam_loc
    cam.rotation_euler = (Vector(look) - Vector(cam_loc)).to_track_quat("-Z", "Y").to_euler()
    sc.render.resolution_x = sc.render.resolution_y = size
    sc.render.filepath = str(OUT / f"{name}.png")
    bpy.ops.render.render(write_still=True)
    print("rendered", name)


if __name__ == "__main__":
    sc = build("look", "wave")
    shoot(sc, "hero", (1.3, -3.4, 1.2))
    sc = build("look", "stand")
    shoot(sc, "front", (0, -3.6, 0.75), size=800)
    shoot(sc, "side", (3.6, 0, 0.75), size=800)
    shoot(sc, "back", (-1.0, 3.5, 0.9), size=800)
    sc = build("happy", "cheer")
    shoot(sc, "cheer", (0.8, -3.5, 0.9), size=800)
