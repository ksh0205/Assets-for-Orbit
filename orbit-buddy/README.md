# Orbit Buddy

A cosmic social character system for Orbit, designed to be warm, stylish, expressive, and reusable across product moments in the way a strong social mascot can become part of the product language.

> **Working name:** “Orbit Buddy”. The asset IDs are intentionally generic so the character can be renamed later without changing the animation contract.

## Character idea

Orbit Buddy is a small floating cosmic companion built around a few recognizable visual cues:

- **Orbit ring + satellite** — the signature silhouette and direct connection to Orbit.
- **Heart core** — makes warmth, care, friendship, and social connection part of the character itself.
- **North star** — a tiny “signal” above the head that can react to discovery, notifications, matching, navigation, and delight.
- **Big dark eyes + soft cheeks** — expressive at small sizes without relying on text.
- **Floating body** — avoids needing realistic walking/running mechanics and keeps animation lightweight.
- **Cosmic sparkles** — secondary particles that can be enabled only for celebratory moments.

The visual language uses Orbit’s primary **#7C73FF** plus supporting colors already present in the product system: aqua **#4ECDC4**, warm yellow **#FFE66D**, and a social/love pink **#FF7AA8**.

## Files

```
orbit-buddy/
├── source/
│   └── orbit-buddy.svg
├── animations/
│   └── orbit-buddy.json
├── examples/
│   └── OrbitBuddy.tsx
└── manifest.json
```

### `source/orbit-buddy.svg`

Editable vector master. Major parts use semantic IDs such as `face`, `arm_right`, `heart_core`, `orbit_front`, `satellite_moon`, and `north_star` so the artwork can be imported into Rive, After Effects, Figma, or another animation tool without having to rebuild the character.

### `animations/orbit-buddy.json`

Mobile-ready Lottie JSON. It is 512×512, 30 fps, transparent, and contains no raster images, fonts, or external assets.

The first file ships three frame segments:

| State | Frames | Duration | Suggested use |
| --- | ---: | ---: | --- |
| `idle` | 0–59 | 2s | Empty states, waiting, passive presence |
| `hello` | 60–119 | 2s | Onboarding, greeting, successful connection |
| `love` | 120–179 | 2s | Reactions, appreciation, friendship, celebration |

The Lottie file also includes named markers for these states.

### `examples/OrbitBuddy.tsx`

A small React Native wrapper showing how to play the character states with `lottie-react-native`. Orbit’s mobile app already uses that library, so no new runtime is required.

## Motion language

Keep the character expressive but not noisy:

1. **Idle = breathing in zero gravity.** Slow vertical drift, tiny scale change, orbit motion.
2. **Hello = one readable gesture.** One arm wave plus a little body lift; avoid full-body chaos.
3. **Love = emotion comes from the core.** Heart expands upward from the chest rather than appearing as unrelated confetti.
4. **Success = star reacts.** For future animations, make the north star brighten/pop before adding large particles.
5. **Error = concern, not punishment.** Soften the eyes and orbit speed; avoid aggressive shaking.
6. **Loading = orbit carries the motion.** Rotate the satellite/ring while keeping the face calm.

## Recommended future states

The rig is designed to extend into:

- `thinking`
- `searching`
- `found-something`
- `celebrate`
- `high-five`
- `sad`
- `oops`
- `sleep`
- `typing`
- `notification`
- `new-friend`
- `group-huddle`
- `creator`
- `verified`

For interactive experiences, import the SVG master into **Rive** and map these states to a state machine. For lightweight one-shot or looping product moments, continue exporting **Lottie**.

## Mobile usage

Copy `animations/orbit-buddy.json` into the mobile bundle (for example `mobile/assets/mascot/orbit-buddy.json`) and use the wrapper in `examples/OrbitBuddy.tsx`.

Basic direct usage:

```tsx
import LottieView from 'lottie-react-native';

<LottieView
  source={require('@/assets/mascot/orbit-buddy.json')}
  autoPlay
  loop
  style={{ width: 180, height: 180 }}
/>
```

For state-specific playback, use the frame segments in `manifest.json`.

## Design guardrails

- Keep the face high-contrast and readable at ~48–64 px.
- Preserve the orbit ring and heart core in almost every variant; they are the main identity anchors.
- Prefer shape animation over raster textures to keep assets crisp and small.
- Keep backgrounds transparent.
- Do not bake copy into the artwork.
- Avoid human gender cues; the character should feel universally social.
- Accessories can communicate context, but should not permanently change the base silhouette.

## Export notes

When re-exporting from an animation tool:

- Canvas: **512 × 512**
- Frame rate: **30 fps**
- Transparent background
- No text layers
- No external image assets unless absolutely necessary
- Prefer fills/strokes/paths supported by Lottie
- Keep each loop under ~3 seconds unless the experience needs a longer narrative
- Preserve semantic layer names where the exporter supports them
