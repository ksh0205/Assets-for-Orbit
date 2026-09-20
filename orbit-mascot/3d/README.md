# Orbit Mascot — 3D Wave Prototype

This replaces the earlier flat Lottie proof-of-concept with a true 3D articulated mascot prototype.

## Character direction

- Hoodie-first silhouette; no hair
- No Orbit logo on the hoodie
- Warm ivory clothing with teal/cyan accents (no purple)
- Glossy dark visor
- Emissive cyan facial expressions
- Human-like arms, hands, legs, shoes, and body language
- Standalone character with no decorative rings/stars around it

## Sample animation

`Wave_Hello_3s` is a 3-second greeting animation containing:

- arm raise
- bent-elbow wave
- wrist motion
- head tilt
- subtle torso bob
- two visor blinks
- return to neutral pose

The generated GLB contains 38 scene nodes, 34 meshes, seven PBR materials, and seven animation channels.

## Rebuilding

The reproducible source is `build_wave_sample.py`.

Requirements:

```bash
pip install numpy trimesh
python build_wave_sample.py
```

It creates:

- `orbit-mascot-wave-3d.glb` — recommended runtime asset
- `orbit-mascot-wave-3d.gltf` — self-contained glTF source

## Why GLB instead of Lottie

The approved mascot relies on actual geometry, dimensional materials, a glossy visor, and articulated body motion. Lottie can imitate this visually but cannot preserve true 3D geometry. The GLB is therefore the source of truth.

For lightweight UI placements we can later render approved animations from this 3D source into optimized 2D/Lottie-compatible deliverables without redesigning the mascot.

## Status

This is a **3D rig/motion prototype**, not the final production sculpt. The next fidelity pass should be done in a dedicated DCC tool (Blender/C4D/Maya) to refine:

- hoodie folds and cloth silhouette
- hand/finger anatomy
- shoe construction
- visor thickness/reflections
- topology and deformation
- polished lighting/materials
- additional expression states
