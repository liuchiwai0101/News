#!/usr/bin/env python3
"""Generate 3D-printable meshes of the mecha joint assembly.

Reconstructed from the user-provided assembly diagram (parts D1-2, F2, F4,
F5, F6). Dimensions are original and scaled for FDM printing with a 0.4 mm
nozzle; they are not measurements of any commercial kit.

Units: millimetres.
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
from shapely.geometry import Polygon

# ---------------------------------------------------------------------------
# Tunable dimensions (mm)
# ---------------------------------------------------------------------------

SECTIONS = 64

# Central joint body F2 (keyhole / paddle)
F2_THICK = 3.2
F2_HUB_OD = 12.0
F2_HUB_ID = 5.0
F2_UPPER_W = 9.6
F2_UPPER_H = 11.6
F2_OVERLAP = 4.2
F2_SQUARE = 3.8
F2_UPPER_CY = F2_HUB_OD / 2.0 + F2_UPPER_H / 2.0 - F2_OVERLAP
F2_SQUARE_Y = F2_UPPER_CY

# Side plates F5 / F6
PLATE_T = 2.0
PLATE_W = 12.0
PLATE_L = F2_SQUARE_Y + F2_HUB_OD / 2.0 + 4.2
F6_PEG_HUB_D = 4.70
F6_PEG_SQ_D = 3.50
F6_PEG_LEN = 2.2
F5_AXLE_D = 6.0
F5_AXLE_L = 5.2

# Ball joint F4
F4_BALL_R = 4.0
F4_NECK_R = 2.05
F4_NECK_H = 3.2
F4_PLAT_X = 8.2
F4_PLAT_Y = 6.2
F4_PLAT_Z = 2.2
F4_PEG_D = 3.80
F4_PEG_H = 3.4

# Receiving frame D1-2
D_THICK = 10.0
D_TOP_SOCKET_D = 12.40
D_TOP_SOCKET_DEPTH = 7.5
D_BOT_SOCKET_D = 4.00
D_BOT_SOCKET_DEPTH = 3.5
D_TOP_SOCKET_Y = 10.6
D_BOT_SOCKET_Y = -11.0

CLEAR = 0.25  # extra cutter length so booleans fully pierce


# ---------------------------------------------------------------------------
# CSG helpers
# ---------------------------------------------------------------------------

def cyl(r: float, h: float, sections: int = SECTIONS) -> trimesh.Trimesh:
    return trimesh.creation.cylinder(radius=r, height=h, sections=sections)


def sph(r: float, sub: int = 3) -> trimesh.Trimesh:
    return trimesh.creation.icosphere(subdivisions=sub, radius=r)


def box(sx: float, sy: float, sz: float) -> trimesh.Trimesh:
    return trimesh.creation.box(extents=[sx, sy, sz])


def move(mesh: trimesh.Trimesh, x: float = 0.0, y: float = 0.0, z: float = 0.0) -> trimesh.Trimesh:
    m = mesh.copy()
    m.apply_translation([x, y, z])
    return m


def union(meshes) -> trimesh.Trimesh:
    meshes = [m for m in meshes if m is not None]
    if len(meshes) == 1:
        return meshes[0]
    return trimesh.boolean.union(meshes, engine="manifold")


def diff(a: trimesh.Trimesh, b: trimesh.Trimesh) -> trimesh.Trimesh:
    return a.difference(b, engine="manifold")


def stadium_xy(length_y: float, width_x: float, thick_z: float) -> trimesh.Trimesh:
    """Capsule / stadium in XY, extruded along Z, centered at origin."""
    r = width_x / 2.0
    straight = max(length_y - width_x, 0.2)
    return union(
        [
            box(width_x, straight, thick_z),
            move(cyl(r, thick_z), y=straight / 2.0),
            move(cyl(r, thick_z), y=-straight / 2.0),
        ]
    )


def ensure_volume(mesh: trimesh.Trimesh, name: str) -> trimesh.Trimesh:
    mesh = mesh.copy()
    mesh.remove_unreferenced_vertices()
    mesh.merge_vertices()
    mesh.process(validate=True)
    if not mesh.is_watertight:
        mesh.fill_holes()
        mesh.process(validate=True)
    mesh.fix_normals()
    if mesh.volume < 0:
        mesh.invert()
    if not mesh.is_volume or mesh.volume <= 0:
        raise RuntimeError(
            f"{name} is not a printable solid "
            f"(volume={mesh.volume}, watertight={mesh.is_watertight})"
        )
    mesh.metadata["name"] = name
    return mesh


def drop_to_bed(mesh: trimesh.Trimesh) -> trimesh.Trimesh:
    m = mesh.copy()
    m.apply_translation([0.0, 0.0, -m.bounds[0, 2]])
    return m


# ---------------------------------------------------------------------------
# Parts
# ---------------------------------------------------------------------------

def part_f2_joint_body() -> trimesh.Trimesh:
    """Keyhole body: rectangular upper block + circular hub."""
    hub = cyl(F2_HUB_OD / 2.0, F2_THICK)
    upper = move(box(F2_UPPER_W, F2_UPPER_H, F2_THICK), y=F2_UPPER_CY)
    # Soften the shoulder where the block meets the hub.
    blend = move(box(F2_UPPER_W, F2_OVERLAP + 0.8, F2_THICK), y=F2_HUB_OD / 2.0 - 0.4)
    body = union([hub, upper, blend])
    square = move(box(F2_SQUARE, F2_SQUARE, F2_THICK + 2 * CLEAR), y=F2_SQUARE_Y)
    hole = cyl(F2_HUB_ID / 2.0, F2_THICK + 2 * CLEAR)
    body = diff(body, square)
    body = diff(body, hole)
    return ensure_volume(body, "F2_joint_body")


def _plate_blank() -> trimesh.Trimesh:
    return stadium_xy(PLATE_L, PLATE_W, PLATE_T)


def part_f6_inner_plate() -> trimesh.Trimesh:
    """Stadium cap with two inner locating pegs (print: pegs +Z)."""
    plate = _plate_blank()
    # Shift so the hub peg sits at y=0, matching F2.
    # Stadium is centered; hub hole is not at the stadium midpoint.
    hub_y_in_plate = -(PLATE_L / 2.0 - PLATE_W / 2.0)
    # We want hub peg at y=0, so move plate by -hub_y_in_plate if stadium
    # center were used. Easier: rebuild pegs at F2 hole locations and
    # shift the stadium so it covers both holes.
    mid_y = F2_SQUARE_Y / 2.0
    plate = move(_plate_blank(), y=mid_y)
    z_peg = PLATE_T / 2.0 + F6_PEG_LEN / 2.0
    peg_hub = move(cyl(F6_PEG_HUB_D / 2.0, F6_PEG_LEN), y=0.0, z=z_peg)
    peg_sq = move(cyl(F6_PEG_SQ_D / 2.0, F6_PEG_LEN), y=F2_SQUARE_Y, z=z_peg)
    body = union([plate, peg_hub, peg_sq])
    return ensure_volume(body, "F6_inner_plate")


def part_f5_outer_plate() -> trimesh.Trimesh:
    """Stadium cap with a large exterior axle (print: plate on bed, axle +Z)."""
    mid_y = F2_SQUARE_Y / 2.0
    plate = move(_plate_blank(), y=mid_y)
    z_axle = PLATE_T / 2.0 + F5_AXLE_L / 2.0
    axle = move(cyl(F5_AXLE_D / 2.0, F5_AXLE_L), y=0.0, z=z_axle)
    collar = move(cyl(F5_AXLE_D / 2.0 + 0.7, 0.9), y=0.0, z=PLATE_T / 2.0 + 0.4)
    body = union([plate, axle, collar])
    return ensure_volume(body, "F5_outer_plate")


def part_f4_ball_joint() -> trimesh.Trimesh:
    """Peg + platform + neck + ball. Print: platform on the bed, peg +Z."""
    platform = box(F4_PLAT_X, F4_PLAT_Y, F4_PLAT_Z)
    peg = move(cyl(F4_PEG_D / 2.0, F4_PEG_H), z=F4_PLAT_Z / 2.0 + F4_PEG_H / 2.0)
    neck = move(
        cyl(F4_NECK_R, F4_NECK_H),
        z=-(F4_PLAT_Z / 2.0 + F4_NECK_H / 2.0),
    )
    ball = move(
        sph(F4_BALL_R, sub=4),
        z=-(F4_PLAT_Z / 2.0 + F4_NECK_H + F4_BALL_R * 0.72),
    )
    body = union([platform, peg, neck, ball])
    return ensure_volume(body, "F4_ball_joint")


def _d12_outline() -> Polygon:
    """Notched inner-frame silhouette, Y up, X right, origin at center."""
    pts = [
        (-7.5, -18.5),
        (7.5, -18.5),
        (7.5, -16.0),
        (10.2, -16.0),
        (10.2, -10.2),
        (7.2, -10.2),
        (7.2, -3.6),
        (9.8, -3.6),
        (9.8, 4.2),
        (7.2, 4.2),
        (7.2, 9.0),
        (10.4, 9.0),
        (10.4, 16.4),
        (6.2, 16.4),
        (6.2, 18.8),
        (-6.2, 18.8),
        (-6.2, 16.4),
        (-10.4, 16.4),
        (-10.4, 9.0),
        (-7.2, 9.0),
        (-7.2, 4.2),
        (-9.8, 4.2),
        (-9.8, -3.6),
        (-7.2, -3.6),
        (-7.2, -10.2),
        (-10.2, -10.2),
        (-10.2, -16.0),
        (-7.5, -16.0),
    ]
    poly = Polygon(pts)
    if not poly.is_valid:
        poly = poly.buffer(0)
    # Round sharp corners so walls print cleanly.
    poly = poly.buffer(1.15, join_style=1).buffer(-1.15, join_style=1)
    if poly.geom_type == "MultiPolygon":
        poly = max(poly.geoms, key=lambda g: g.area)
    return poly


def _socket_rim(y: float, inner_d: float, outer_d: float, height: float, z_face: float) -> trimesh.Trimesh:
    ring = move(cyl(outer_d / 2.0, height), y=y, z=z_face + height / 2.0 - 0.15)
    hole = move(cyl(inner_d / 2.0, height + 2 * CLEAR), y=y, z=z_face + height / 2.0 - 0.15)
    return diff(ring, hole)


def part_d12_frame() -> trimesh.Trimesh:
    """Structural frame with two front-face sockets."""
    outline = _d12_outline()
    body = trimesh.creation.extrude_polygon(outline, height=D_THICK)
    body.apply_translation([0.0, 0.0, -D_THICK / 2.0])

    z_face = D_THICK / 2.0
    body = union(
        [
            body,
            _socket_rim(D_TOP_SOCKET_Y, D_TOP_SOCKET_D, D_TOP_SOCKET_D + 2.8, 1.1, z_face),
            _socket_rim(D_BOT_SOCKET_Y, D_BOT_SOCKET_D, D_BOT_SOCKET_D + 2.6, 1.1, z_face),
        ]
    )

    top_cut = move(
        cyl(D_TOP_SOCKET_D / 2.0, D_TOP_SOCKET_DEPTH + CLEAR),
        y=D_TOP_SOCKET_Y,
        z=z_face - D_TOP_SOCKET_DEPTH / 2.0 + CLEAR / 2.0,
    )
    body = diff(body, top_cut)

    bot_cut = move(
        cyl(D_BOT_SOCKET_D / 2.0, D_BOT_SOCKET_DEPTH + CLEAR),
        y=D_BOT_SOCKET_Y,
        z=z_face - D_BOT_SOCKET_DEPTH / 2.0 + CLEAR / 2.0,
    )
    body = diff(body, bot_cut)

    back = move(box(6.5, 8.5, 2.4), y=1.5, z=-(D_THICK / 2.0 - 1.1))
    body = diff(body, back)
    return ensure_volume(body, "D1-2_frame")


# ---------------------------------------------------------------------------
# Assembly / print layout
# ---------------------------------------------------------------------------

def assembled_parts() -> dict[str, trimesh.Trimesh]:
    """Place parts in the assembled pose (D1-2 at the origin)."""
    d12 = part_d12_frame()
    f2 = part_f2_joint_body()
    f6 = part_f6_inner_plate()
    f5 = part_f5_outer_plate()
    f4 = part_f4_ball_joint()

    # Sandwich sits in the top socket, F6 against the pocket floor, F5 facing out.
    z_floor = D_THICK / 2.0 - D_TOP_SOCKET_DEPTH
    z_f6 = z_floor + PLATE_T / 2.0
    z_f2 = z_f6 + PLATE_T / 2.0 + F2_THICK / 2.0
    z_f5 = z_f2 + F2_THICK / 2.0 + PLATE_T / 2.0

    f2.apply_translation([0.0, D_TOP_SOCKET_Y, z_f2])
    f6.apply_translation([0.0, D_TOP_SOCKET_Y, z_f6])
    f5.apply_translation([0.0, D_TOP_SOCKET_Y, z_f5])

    # F4 peg into the bottom socket, ball sticking out of the front face.
    # Modeled with peg +Z, ball -Z. Rotate 180° about X so peg points -Z? 
    # Front face is +Z; peg should point -Z into the pocket (from the front).
    # Rotate 180° about Y: peg goes to -Z, ball to +Z. Then ball would be behind.
    # Rotate 180° about X: (x,y,z)->(x,-y,-z): peg -Z, ball +Z. Peg enters from
    # +Z toward -Z. Place platform just outside the front face.
    rx = trimesh.transformations.rotation_matrix(np.pi, [1, 0, 0])
    f4.apply_transform(rx)
    # After rotation: peg points -Z. Platform center should sit so the peg
    # occupies the socket. Peg extends from platform: originally +Z from
    # plat_z/2, so after 180° about X it extends -Z from -plat_z/2.
    # We want peg tip near the socket floor.
    z_front = D_THICK / 2.0
    # Platform outer face (toward +Z, away from frame) at z_front + plat_z,
    # platform center at z_front + plat_z/2, peg going -Z into the socket.
    f4.apply_translation(
        [0.0, D_BOT_SOCKET_Y, z_front + F4_PLAT_Z / 2.0]
    )

    return {
        "D1-2_frame": d12,
        "F2_joint_body": f2,
        "F6_inner_plate": f6,
        "F5_outer_plate": f5,
        "F4_ball_joint": f4,
    }


def exploded_parts(gap: float = 8.0) -> dict[str, trimesh.Trimesh]:
    """Assembled pose with the sandwich and ball joint pulled apart for viewing."""
    parts = assembled_parts()
    parts["F6_inner_plate"].apply_translation([0.0, 0.0, -gap])
    parts["F2_joint_body"].apply_translation([0.0, 0.0, 0.4 * gap])
    parts["F5_outer_plate"].apply_translation([0.0, 0.0, 1.6 * gap])
    parts["F4_ball_joint"].apply_translation([0.0, 0.0, gap])
    return parts


def print_oriented() -> dict[str, trimesh.Trimesh]:
    """Largest face on the bed; pegs / sockets facing up where possible."""
    return {
        "D1-2_frame": drop_to_bed(part_d12_frame()),
        "F2_joint_body": drop_to_bed(part_f2_joint_body()),
        "F5_outer_plate": drop_to_bed(part_f5_outer_plate()),
        "F6_inner_plate": drop_to_bed(part_f6_inner_plate()),
        "F4_ball_joint": drop_to_bed(part_f4_ball_joint()),
    }


def make_print_plate(parts: dict[str, trimesh.Trimesh], gap: float = 6.0) -> trimesh.Trimesh:
    x = 0.0
    placed = []
    order = [
        "D1-2_frame",
        "F2_joint_body",
        "F5_outer_plate",
        "F6_inner_plate",
        "F4_ball_joint",
    ]
    for name in order:
        m = parts[name].copy()
        extents = m.extents
        # Sit with min-x at current x, centered in Y.
        m.apply_translation(
            [
                x - m.bounds[0, 0],
                -0.5 * (m.bounds[0, 1] + m.bounds[1, 1]),
                -m.bounds[0, 2],
            ]
        )
        placed.append(m)
        x += extents[0] + gap
    plate = union(placed)
    plate.apply_translation([-0.5 * (plate.bounds[0, 0] + plate.bounds[1, 0]), 0.0, 0.0])
    return ensure_volume(plate, "print_plate")


def make_assembly_mesh(parts: dict[str, trimesh.Trimesh]) -> trimesh.Trimesh:
    return ensure_volume(union(list(parts.values())), "assembly_preview")


COLORS = {
    "D1-2_frame": (74, 85, 104),
    "F2_joint_body": (226, 232, 240),
    "F5_outer_plate": (125, 211, 252),
    "F6_inner_plate": (56, 189, 248),
    "F4_ball_joint": (203, 213, 225),
    "print_plate": (148, 163, 184),
}


def _orbit(verts: np.ndarray, azim_deg: float, elev_deg: float) -> np.ndarray:
    """Rotate Y-up vertices for an orbit camera. Camera looks toward -Z after this."""
    az = np.radians(azim_deg)
    el = np.radians(elev_deg)
    ca, sa = np.cos(az), np.sin(az)
    ce, se = np.cos(el), np.sin(el)
    ry = np.array([[ca, 0.0, sa], [0.0, 1.0, 0.0], [-sa, 0.0, ca]])
    rx = np.array([[1.0, 0.0, 0.0], [0.0, ce, -se], [0.0, se, ce]])
    return verts @ (rx @ ry).T


def render_scene(
    items: list[tuple[str, trimesh.Trimesh]],
    path: Path,
    size: tuple[int, int] = (1100, 900),
    azim: float = -38.0,
    elev: float = 22.0,
    titles: bool = False,
) -> None:
    w, h = size
    img = Image.new("RGB", (w, h), (15, 23, 42))
    draw = ImageDraw.Draw(img)

    all_faces = []
    for name, mesh in items:
        color = COLORS.get(name, (148, 163, 184))
        verts = _orbit(np.asarray(mesh.vertices, dtype=np.float64), azim, elev)
        faces = np.asarray(mesh.faces, dtype=np.int64)
        tri = verts[faces]
        n = np.cross(tri[:, 1] - tri[:, 0], tri[:, 2] - tri[:, 0])
        nlen = np.linalg.norm(n, axis=1)
        nlen[nlen == 0] = 1.0
        n = n / nlen[:, None]
        # Keep faces that point toward the camera (+Z after orbit... actually
        # camera looks at origin from +Z, so visible faces have n_z > 0).
        visible = n[:, 2] > 0.02
        if not np.any(visible):
            continue
        tri = tri[visible]
        n = n[visible]
        depth = tri[:, :, 2].mean(axis=1)
        all_faces.append((depth, tri, n, color))

    if not all_faces:
        img.save(path)
        return

    depths = np.concatenate([f[0] for f in all_faces])
    tris = np.concatenate([f[1] for f in all_faces])
    norms = np.concatenate([f[2] for f in all_faces])
    cols = np.concatenate(
        [np.repeat([f[3]], len(f[0]), axis=0) for f in all_faces]
    )

    order = np.argsort(depths)
    tris, norms, cols = tris[order], norms[order], cols[order]

    pts = tris.reshape(-1, 3)
    c = pts.mean(axis=0)
    r = 0.55 * (pts.max(axis=0) - pts.min(axis=0)).max()
    r = max(r, 1.0)
    scale = 0.42 * min(w, h) / r
    cx, cy = w * 0.5, h * 0.52

    light = np.array([0.35, 0.8, 0.5], dtype=np.float64)
    light = light / np.linalg.norm(light)
    ndotl = np.clip(norms @ light, 0.12, 1.0)

    for tri, shade, rgb in zip(tris, ndotl, cols):
        u = (tri[:, 0] - c[0]) * scale + cx
        v = -(tri[:, 1] - c[1]) * scale + cy
        fill = tuple(int(np.clip(ch * (0.28 + 0.72 * shade), 0, 255)) for ch in rgb)
        draw.polygon(list(zip(u, v)), fill=fill)

    if titles:
        try:
            font = ImageFont.truetype(
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18
            )
        except OSError:
            font = ImageFont.load_default()
        draw.text((24, 20), path.stem.replace("_", " "), fill=(226, 232, 240), font=font)

    img.save(path)


def render_parts_grid(parts: dict[str, trimesh.Trimesh], path: Path) -> None:
    names = list(parts.keys())
    cols, rows = 3, 2
    tile_w, tile_h = 420, 400
    img = Image.new("RGB", (cols * tile_w, rows * tile_h), (15, 23, 42))
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 16)
    except OSError:
        font = ImageFont.load_default()
    for i, name in enumerate(names):
        tile_path = path.parent / f"_tile_{name}.png"
        render_scene([(name, parts[name])], tile_path, size=(tile_w, tile_h))
        tile = Image.open(tile_path)
        x, y = (i % cols) * tile_w, (i // cols) * tile_h
        img.paste(tile, (x, y))
        draw = ImageDraw.Draw(img)
        draw.text((x + 16, y + 12), name, fill=(226, 232, 240), font=font)
        tile_path.unlink()
    img.save(path)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def export_mesh(mesh: trimesh.Trimesh, stl_path: Path) -> None:
    mesh.export(stl_path)


def main() -> None:
    root = Path(__file__).resolve().parent
    stl_dir = root / "stl"
    preview_dir = root / "preview"
    stl_dir.mkdir(parents=True, exist_ok=True)
    preview_dir.mkdir(parents=True, exist_ok=True)

    print("Modeling parts...")
    individuals = {
        "D1-2_frame": part_d12_frame(),
        "F2_joint_body": part_f2_joint_body(),
        "F5_outer_plate": part_f5_outer_plate(),
        "F6_inner_plate": part_f6_inner_plate(),
        "F4_ball_joint": part_f4_ball_joint(),
    }

    print("Building assembly and print plate...")
    assembled = assembled_parts()
    oriented = print_oriented()
    plate = make_print_plate(oriented)
    assembly = make_assembly_mesh(assembled)

    stats = []
    for name, mesh in {**individuals, "print_plate": plate, "assembly_preview": assembly}.items():
        out = stl_dir / f"{name}.stl"
        export_mesh(mesh, out)
        info = {
            "name": name,
            "triangles": int(len(mesh.faces)),
            "volume_mm3": round(float(mesh.volume), 2),
            "extents_mm": [round(float(x), 2) for x in mesh.extents],
            "watertight": bool(mesh.is_watertight),
            "file": str(out.relative_to(root)),
        }
        stats.append(info)
        print(
            f"  {name:20s}  {info['extents_mm']} mm  "
            f"{info['triangles']:6d} tris  V={info['volume_mm3']} mm³"
        )

    (root / "manifest.json").write_text(json.dumps(stats, indent=2) + "\n")

    print("Rendering previews...")
    render_parts_grid(individuals, preview_dir / "parts.png")
    render_scene(list(assembled.items()), preview_dir / "assembly.png", size=(1100, 980))
    exploded = exploded_parts()
    render_scene(list(exploded.items()), preview_dir / "exploded.png", size=(1100, 980))
    render_scene(
        [("print_plate", plate)],
        preview_dir / "print_plate.png",
        size=(1400, 720),
        azim=-18.0,
        elev=42.0,
    )
    print("Done.")


if __name__ == "__main__":
    main()
