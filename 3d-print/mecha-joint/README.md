# Mecha joint — 3D printable parts

Printable reconstruction of the joint assembly in the reference diagram
(parts **D1-2**, **F2**, **F4**, **F5**, **F6**). Dimensions are original and
scaled for FDM printing with a 0.4 mm nozzle. They are **not** 1:1 copies of a
commercial kit.

Units are millimetres.

## Files to print

| File | What it is |
|---|---|
| `stl/print_plate.stl` | All parts laid out on one plate (easiest) |
| `stl/D1-2_frame.stl` | Receiving frame with two sockets |
| `stl/F2_joint_body.stl` | Keyhole joint body |
| `stl/F5_outer_plate.stl` | Stadium cap with axle |
| `stl/F6_inner_plate.stl` | Stadium cap with two locating pegs |
| `stl/F4_ball_joint.stl` | Peg + platform + ball |

`stl/assembly_preview.stl` is a fused view of the assembled joint. Do not print it.

## Suggested print settings

- Layer height: 0.16–0.20 mm
- Nozzle: 0.4 mm
- Walls: 3
- Infill: 20–30% gyroid
- Material: PLA or PETG
- Supports: **yes** for `F4_ball_joint` (the ball hangs off the platform)
- Other parts print without supports (flat face on the bed, pegs/axle pointing up)

If pegs are too tight after printing, scale XY by 100.5–101% in the slicer, or
sand the pegs. If they are loose, print at 99.5%.

## Assembly

1. Press **F6** and **F5** onto either side of **F2** (pegs into the round and square holes).
2. Press that sandwich into the large upper socket of **D1-2**. The F5 axle faces out.
3. Press the **F4** peg into the small lower socket of **D1-2**.

F1 / F2 runner numbers in the diagram are left/right copies of the same parts.
Print a second set of F2/F4/F5/F6 if you need both sides.

## Regenerating

```bash
pip install -r requirements.txt
python3 generate.py
```
