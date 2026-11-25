"""Generate the SWFC reference geometry study with Blender 4.x."""
import json
from pathlib import Path

import bpy
import bmesh
from mathutils import Vector
from mathutils.bvhtree import BVHTree

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "AssetSources/Processed/SWFC"
OUT.mkdir(parents=True, exist_ok=True)

# Metres, in the building's local coordinates. Only the overall height is sourced
# as a numeric dimension. Section dimensions are visual estimates.
HEIGHT = 492.0
SILL = 438.0
LINTEL = 474.0


def section(z):
    t = z / HEIGHT
    half_width = 29.0 + 1.4 * t * t
    half_depth = 29.0 * (1.0 - t) ** 1.45 + 3.8 * t
    core = 17.0 + 6.0 * min(1.0, max(0.0, (z - SILL) / (LINTEL - SILL)))
    return (
        (-half_width, -half_depth, z), (-core, -half_depth, z),
        (core, -half_depth, z), (half_width, -half_depth, z),
        (half_width, half_depth, z), (core, half_depth, z),
        (-core, half_depth, z), (-half_width, half_depth, z),
    )


def tower_mesh():
    levels = sorted({0.0, SILL, LINTEL, HEIGHT} | set(range(5, 492, 5)))
    vertices = [point for z in levels for point in section(z)]
    faces = []
    for level, (low, high) in enumerate(zip(levels, levels[1:])):
        start = level * 8
        end = start + 8
        in_portal = low >= SILL and high <= LINTEL
        for i in range(8):
            if in_portal and i in (1, 5):
                continue
            j = (i + 1) % 8
            faces.append((start + i, start + j, end + j, end + i))
        if in_portal:
            faces.extend([
                (start + 1, end + 1, end + 6, start + 6),
                (start + 2, start + 5, end + 5, end + 2),
            ])
    for z in (SILL, LINTEL):
        i = levels.index(z) * 8
        faces.append((i + 1, i + 2, i + 5, i + 6))
    faces.extend([tuple(reversed(range(8))), tuple(range(len(vertices) - 8, len(vertices)))])

    mesh = bpy.data.meshes.new("SWFC | tapered tower with through aperture")
    mesh.from_pydata(vertices, [], faces)
    mesh.update()
    with_mesh = bmesh.new()
    with_mesh.from_mesh(mesh)
    bmesh.ops.recalc_face_normals(with_mesh, faces=list(with_mesh.faces))
    if not all(edge.is_manifold for edge in with_mesh.edges):
        raise RuntimeError("Non-manifold tower geometry")
    if with_mesh.calc_volume(signed=True) <= 0:
        raise RuntimeError("Invalid tower winding")
    with_mesh.to_mesh(mesh)
    with_mesh.free()
    mesh.update()
    add_surface_uvs(mesh)
    return mesh


def add_surface_uvs(mesh):
    """Project faces in metre units for later material studies."""
    uv_layer = mesh.uv_layers.new(name="Surface metres")
    for face in mesh.polygons:
        normal = face.normal
        projection = max(range(3), key=lambda axis: abs(normal[axis]))
        horizontal, vertical = ((1, 2), (0, 2), (0, 1))[projection]
        for loop_index in face.loop_indices:
            point = mesh.vertices[mesh.loops[loop_index].vertex_index].co
            uv_layer.data[loop_index].uv = (point[horizontal], point[vertical])


def verify(mesh):
    tree = BVHTree.FromPolygons([v.co.copy() for v in mesh.vertices],
                                [tuple(p.vertices) for p in mesh.polygons])
    samples = [
        ("front_to_back_portal", 0, -80, 453, 1, False),
        ("back_to_front_portal", 0, 80, 453, -1, False),
        ("solid_portal_jamb", 27, -80, 453, 1, True),
        ("solid_below_sill", 0, -80, 432, 1, True),
        ("solid_above_lintel", 0, -80, 480, 1, True),
        ("narrower_at_bottom", 20, -80, 440, 1, True),
        ("wider_at_top", 20, -80, 472, 1, False),
    ]
    results = {}
    for name, x, y, z, direction, expected in samples:
        hit = tree.ray_cast(Vector((x, y, z)), Vector((0, direction, 0)), 160)[0]
        if (hit is not None) != expected:
            raise RuntimeError(f"Failed geometry probe: {name}")
        results[name] = "pass"
    if max(v.co.z for v in mesh.vertices) != HEIGHT:
        raise RuntimeError("Unexpected tower height")
    uv_layer = mesh.uv_layers.active
    if uv_layer is None or len(uv_layer.data) != len(mesh.loops):
        raise RuntimeError("Missing surface UV coordinates")
    results.update(height_m=HEIGHT, vertices=len(mesh.vertices), faces=len(mesh.polygons),
                   uv_corners=len(uv_layer.data))
    return results


bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
mesh = tower_mesh()
results = verify(mesh)
obj = bpy.data.objects.new("SWFC geometry study", mesh)
obj["source"] = "https://www.kpf.com/project/shanghai-world-financial-center"
obj["status"] = "Reference geometry study, estimated section dimensions, not production"
scene.collection.objects.link(obj)
obj.select_set(True)
bpy.context.view_layer.objects.active = obj
bpy.ops.wm.save_as_mainfile(filepath=str(OUT / "SWFC-geometry-study.blend"))
bpy.ops.export_scene.gltf(filepath=str(OUT / "SWFC-geometry-study.glb"), use_selection=True)
# Reimport the actual interchange file and repeat spatial probes.
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.import_scene.gltf(filepath=str(OUT / "SWFC-geometry-study.glb"))
imported = next(item for item in bpy.context.scene.objects if item.type == "MESH")
imported.data.transform(imported.matrix_world)
results["glb_reimport"] = verify(imported.data)
(OUT / "geometry-test.json").write_text(json.dumps(results, indent=2) + "\n")
