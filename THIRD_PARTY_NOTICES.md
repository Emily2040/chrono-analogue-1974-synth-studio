# Third-Party Notices

## Three.js (`public/vendor/three/`)

This repository bundles the ES module build of [Three.js](https://github.com/mrdoob/three.js) (`r169`) and its `GLTFLoader` and `OrbitControls` addons under the MIT License:

- Copyright © 2010–2024 Three.js authors (https://threejs.org/)
- License: MIT

## Classical Musical Works Performed in the Showcase

The four symphonic movements arranged and synthesised in `scripts/showcase_choreography.py` are public-domain compositions:

1. Ludwig van Beethoven — *Symphony No. 5 in C Minor, Op. 67* (1808)
2. Johann Sebastian Bach — *Toccata and Fugue in D Minor, BWV 565* / Antonio Vivaldi — *The Four Seasons: Winter in F Minor, Op. 8, No. 4, RV 297* (1725)
3. Wolfgang Amadeus Mozart — *Symphony No. 40 in G Minor, K. 550* (1788)
4. Ludwig van Beethoven — *Symphony No. 9 in D Minor, Op. 125 ("Ode to Joy" Finale)* (1824)

All audio buffers (`public/assets/audio/chrono_analogue_1974_lp.wav` and `evidence/social_showcase_1974_symphonies_48k.wav`) are generated deterministically from mathematical oscillator, ladder filter, ADSR envelope, and BBD delay equations in Python and Web Audio API.
