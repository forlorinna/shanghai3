"""Render eight orthographic geometry-review views in Blender Cycles on CPU."""
import math
from pathlib import Path

import bpy
from mathutils import Vector

OUT = Path(__file__).resolve().parents[1] / "AssetSources/Processed/SWFC"
bpy.ops.wm.open_mainfile(filepath=str(OUT / "SWFC-geometry-study.blend"))
scene = bpy.context.scene
scene.render.engine = "CYCLES"
scene.cycles.device = "CPU"
scene.cycles.samples = 8
scene.cycles.use_denoising = False
scene.render.threads_mode = "FIXED"
scene.render.threads = 2
scene.render.resolution_x = 210
scene.render.resolution_y = 320
scene.render.resolution_percentage = 100
scene.world = bpy.data.worlds.new("Geometry review fill")
scene.world.use_nodes = True
scene.world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.35, 0.35, 0.35, 1)
scene.world.node_tree.nodes["Background"].inputs["Strength"].default_value = 0.65

bpy.ops.object.camera_add()
camera = bpy.context.object
camera.data.type = "ORTHO"
camera.data.ortho_scale = 530
camera.data.clip_end = 2000
scene.camera = camera
bpy.ops.object.light_add(type="SUN")
sun = bpy.context.object
sun.data.energy = 2
target = Vector((0, 0, 246))
output = OUT / "review-views"
output.mkdir(exist_ok=True)
for angle in range(0, 360, 45):
    azimuth = math.radians(angle)
    camera.location = (700 * math.sin(azimuth), -700 * math.cos(azimuth), 246)
    camera.rotation_euler = (target - camera.location).to_track_quat("-Z", "Y").to_euler()
    sun.rotation_euler = (math.radians(32), math.radians(-28), azimuth)
    scene.render.filepath = str(output / f"swfc-{angle:03d}.png")
    bpy.ops.render.render(write_still=True)
