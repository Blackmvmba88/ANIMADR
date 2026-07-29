# ANIMADR

Motor de animación 2.5D para convertir una imagen estática en video mediante capas, máscaras y deformaciones por píxel.

## Qué hace el MVP

- Carga escenas declaradas en JSON.
- Trabaja con capas RGBA del mismo canvas.
- Encadena movimientos independientes por capa.
- Incluye `rotate`, `translate`, `breathe`, `liquid` y `sway`.
- Compone frame por frame con alpha.
- Renderiza MP4 vertical, incluyendo 1080x1920 para Canvas.

```text
imagen -> máscara -> capa RGBA -> motion chain -> compositor -> MP4
```

## Instalación

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -e .
```

Para tests:

```bash
pip install pytest
pytest -q
```

## Preparar capas

La imagen original se separa mediante máscaras en escala de grises. Blanco = visible, negro = transparente.

```bash
python -m animadr.extract source.png mask_sun.png assets/layers/sun.png
python -m animadr.extract source.png mask_clouds.png assets/layers/clouds.png
python -m animadr.extract source.png mask_guitarist.png assets/layers/guitarist.png
```

Cada PNG generado conserva RGB de la imagen original y usa la máscara como canal alpha.

## Definir movimiento

`scene.example.json` contiene una escena psicodélica 9:16 de ejemplo.

```json
{
  "name": "sun",
  "file": "assets/layers/sun.png",
  "z": 10,
  "motions": [
    {"rotate": {"speed_deg_s": 0.6}},
    {"breathe": {"amount": 0.025, "cycles": 1.0}}
  ]
}
```

Para deformación píxel por píxel:

```json
{
  "liquid": {
    "amplitude": 7.0,
    "frequency": 0.014,
    "speed": 0.8
  }
}
```

## Render

```bash
animadr scene.example.json -o psychedelic.mp4
```

También funciona como módulo:

```bash
python -m animadr.cli scene.example.json -o psychedelic.mp4
```

## Diseño del sistema

```text
ANIMADR
├── scene.py       # contrato de escena
├── motion.py      # transformaciones y pixel warps
├── composite.py   # composición RGBA
├── extract.py     # máscara -> capa RGBA
├── render.py      # timeline + frames + video
└── cli.py         # entrada de terminal
```

## Siguiente etapa

1. Segmentación automática con SAM 2.
2. Inpainting del fondo detrás de objetos recortados.
3. Depth map + parallax 2.5D.
4. Mesh/puppet deformation para pelo, ropa, plantas y fluidos.
5. Preview interactivo con PySide6.
6. Capa semántica: `haz girar Saturno`, `mueve el río`, `haz respirar el sol` -> escena reproducible.

La regla del proyecto es mantener el render determinista: la IA puede proponer máscaras y movimientos, pero el video final se genera desde parámetros explícitos y repetibles.
