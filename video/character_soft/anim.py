"""캐릭터 시안 4 짧은 영상(6초, 24fps): 떨어져 착지 → 두리번 → 결심 → 수정 말풍선을 번쩍 → 점 세 개가 차례로 반짝.

build.py의 영웅 자세 장면을 그대로 만든 뒤, 부품을 묶는 축(어깨, 말풍선)을 추가해 키프레임을 건다.
투명 배경 PNG로 렌더하고, ffmpeg로 compose.py의 그림 배경 위에 얹어 mp4를 만든다.
사용법: video/.venv-bpy/bin/python video/character_soft/anim.py [--test]
"""
import math
import subprocess
import sys
from pathlib import Path

import bpy

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import build as B  # noqa: E402

FPS, SEC = 24, 6.0
END = int(FPS * SEC)
FR = HERE / "out/frames"
f = lambda t: 1 + round(t * FPS)


def key(ob, path, t, val, interp="BEZIER", ease="AUTO"):
    setattr(ob, path, val) if not isinstance(path, tuple) else None
    ob.keyframe_insert(path, frame=f(t))
    for fc in (ob.animation_data.action.layers[0].strips[0].channelbag(ob.animation_data.action.slots[0]).fcurves
               if hasattr(ob.animation_data.action, "layers") else ob.animation_data.action.fcurves):
        if fc.data_path == path:
            for kp in fc.keyframe_points:
                if int(kp.co.x) == f(t):
                    kp.interpolation, kp.easing = interp, ease


def pivot(name, loc, children):
    e = bpy.data.objects.new(name, None)
    bpy.context.scene.collection.objects.link(e)
    rig = bpy.data.objects["Rig"]
    e.parent = rig
    e.location = loc
    bpy.context.view_layer.update()          # 축의 위치를 먼저 계산해야 자식이 제자리를 지킴
    for n in children:
        o = bpy.data.objects[n]
        mw = o.matrix_world.copy()
        o.parent = e
        o.matrix_world = mw
    return e


def main(test=False):
    sc = B.build("hero", "brave")
    rig = bpy.data.objects["Rig"]
    bpy.context.view_layer.update()
    # 말풍선 묶음(크기 조절) → 오른팔 묶음(어깨에서 회전)
    bub = pivot("BubbleG", (1.06, -0.2, 1.78), ["Bubble", "BTail", "Dot0", "Dot1", "Dot2"])
    sh = pivot("ShoulderR", (0.58, -0.1, 0.96), ["ArmR", "FistR", "BubbleG"])
    bpy.context.view_layer.update()
    # 점 세 개는 각자 재질(차례로 반짝)
    for i in range(3):
        d = bpy.data.objects[f"Dot{i}"]
        m = d.data.materials[0].copy(); d.data.materials[0] = m
        b = m.node_tree.nodes["Principled BSDF"].inputs["Emission Strength"]
        for t, v in ((0, 0.3), (3.6 + i * 0.25, 0.3), (3.75 + i * 0.25, 4.0), (4.1 + i * 0.25, 0.4), (5.0 + i * 0.25, 0.4), (5.15 + i * 0.25, 3.0), (5.5 + i * 0.25, 0.4)):
            b.default_value = v; b.keyframe_insert("default_value", frame=f(t))
    # ── 1. 위에서 떨어져 착지(눌렸다가 돌아옴)
    base_rot = tuple(rig.rotation_euler)
    for t, z, s in ((0.0, 2.4, (0.9, 0.9, 1.15)), (0.42, 0.0, (1.0, 1.0, 1.0)), (0.5, -0.02, (1.12, 1.12, 0.82)), (0.68, 0.0, (0.96, 0.96, 1.06)), (0.85, 0.0, (1, 1, 1))):
        rig.location = (0, 0, z); rig.scale = s
        rig.keyframe_insert("location", frame=f(t)); rig.keyframe_insert("scale", frame=f(t))
    # 착지 전까지 팔은 아래로(어깨 축 회전), 말풍선은 없음
    for t, ang in ((0.0, -150), (2.3, -150), (2.75, 8), (2.9, -4), (3.05, 0)):
        sh.rotation_euler = (0, math.radians(ang), 0); sh.keyframe_insert("rotation_euler", frame=f(t))
    for t, s in ((0.0, 0.0), (2.8, 0.0), (3.05, 1.18), (3.22, 0.94), (3.38, 1.0)):
        bub.scale = (s, s, s); bub.keyframe_insert("scale", frame=f(t))
    # ── 2. 두리번(눈동자) → 3. 결심(눈썹이 내려옴)
    for n in ("Pupil-0.17", "Pupil0.19", "Glint-0.17", "Glint0.19"):
        o = bpy.data.objects[n]; x0 = o.location.x
        for t, dx in ((0.0, 0), (1.0, 0), (1.2, -0.05), (1.6, -0.05), (1.8, 0.05), (2.15, 0.05), (2.35, 0.0)):
            o.location.x = x0 + dx; o.keyframe_insert("location", frame=f(t))
    for n, a in (("Brow-0.18", 24), ("Brow0.2", -26)):
        o = bpy.data.objects[n]; z0 = o.location.z
        for t, ang, dz in ((0.0, 0, 0.06), (2.1, 0, 0.06), (2.4, a, 0.0)):
            o.rotation_euler = (0, math.radians(ang), 0); o.location.z = z0 + dz
            o.keyframe_insert("rotation_euler", frame=f(t)); o.keyframe_insert("location", frame=f(t))
    # ── 4. 영웅 자세 유지: 숨 쉬듯 살짝
    for t, s in ((3.4, 1.0), (4.2, 1.02), (5.0, 1.0), (5.8, 1.02)):
        rig.scale = (1, 1, s); rig.keyframe_insert("scale", frame=f(t))
    rig.rotation_euler = base_rot
    # 카메라: 조금 넓게 시작해 천천히 다가감
    cam = bpy.data.objects.new("Cam", bpy.data.cameras.new("Cam")); sc.collection.objects.link(cam); sc.camera = cam
    cam.data.lens = 50
    from mathutils import Vector
    for t, loc in ((0.0, (1.1, -7.2, 1.0)), (SEC, (0.95, -6.2, 0.98))):
        cam.location = loc
        cam.rotation_euler = (Vector((0.22, 0, 0.98)) - Vector(loc)).to_track_quat("-Z", "Y").to_euler()
        cam.keyframe_insert("location", frame=f(t)); cam.keyframe_insert("rotation_euler", frame=f(t))
    sc.render.resolution_x, sc.render.resolution_y = 1280, 720
    sc.cycles.samples = 16
    sc.cycles.use_adaptive_sampling = True
    sc.render.fps = FPS
    sc.frame_start, sc.frame_end = (f(3.3), f(3.3)) if test else (1, END)
    FR.mkdir(parents=True, exist_ok=True)
    sc.render.filepath = str(FR / "f_")
    sc.render.image_settings.file_format = "PNG"
    sc.render.image_settings.color_mode = "RGBA"
    bpy.ops.render.render(animation=True)


if __name__ == "__main__":
    main(test="--test" in sys.argv)
