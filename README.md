# ANIMADR

Motor de animación 2.5D para convertir una imagen estática en video mediante capas, máscaras, mapas de profundidad y deformaciones por píxel.

## Qué hace el MVP

- Carga escenas declaradas en JSON.
- Trabaja con capas RGBA del mismo canvas.
- Encadena movimientos independientes por capa.
- Incluye `rotate`, `translate`, `breathe`, `liquid`, `sway` y `depth_parallax`.
- Carga mapas de profundidad una sola vez antes de renderizar.
- Compone frame por frame con alpha.
- Renderiza MP4 vertical, incluyendo 1080x1920 para Canvas.

```text
imagen -> máscara/depth map -> capa RGBA -> motion chain -> compositor -> MP4
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

Para deformación líquida píxel por píxel:

```json
{
  "liquid": {
    "amplitude": 7.0,
    "frequency": 0.014,
    "speed": 0.8
  }
}
```

## Depth map + parallax 2.5D

`scene.depth.example.json` muestra el contrato completo. El mapa de profundidad puede ser PNG gris, RGB o RGBA:

- negro (`0`) = plano lejano
- blanco (`255`) = plano cercano
- los píxeles cercanos recorren más distancia que los lejanos
- el mapa se normaliza a `float32` en el rango `[0, 1]`
- si no coincide con el canvas, se redimensiona de forma determinista

```json
{
  "name": "depth_scene",
  "file": "assets/layers/full_scene.png",
  "z": 0,
  "motions": [
    {
      "depth_parallax": {
        "depth_map": "assets/depth/full_scene.png",
        "x_px": 22.0,
        "y_px": 10.0,
        "cycles": 1.0,
        "phase_offset": 0.0,
        "depth_gamma": 1.15,
        "invert_depth": false
      }
    }
  ]
}
```

Parámetros:

- `x_px`, `y_px`: amplitud máxima de la órbita de cámara.
- `cycles`: número de recorridos durante la duración de la escena.
- `phase_offset`: desplazamiento inicial en radianes.
- `depth_gamma`: curva de separación entre planos; debe ser mayor que cero.
- `invert_depth`: invierte cercano y lejano cuando el mapa viene al revés.

El mapa se resuelve antes del loop de frames. El renderer no lee el disco en cada cuadro.

## Render

```bash
animadr scene.example.json -o psychedelic.mp4
animadr scene.depth.example.json -o depth-parallax.mp4
```

También funciona como módulo:

```bash
python -m animadr.cli scene.example.json -o psychedelic.mp4
```

## Diseño del sistema

```text
ANIMADR
├── scene.py       # contrato de escena
├── depth.py       # carga y normalización de mapas de profundidad
├── motion.py      # transformaciones y pixel warps
├── composite.py   # composición RGBA
├── extract.py     # máscara -> capa RGBA
├── render.py      # timeline + assets + frames + video
└── cli.py         # entrada de terminal
```

## Estado del roadmap

- [x] Motor determinista de capas RGBA.
- [x] Transformaciones y deformación líquida.
- [x] Depth map + parallax 2.5D.
- [ ] Segmentación automática con SAM 2.
- [ ] Inpainting del fondo detrás de objetos recortados.
- [ ] Mesh/puppet deformation para pelo, ropa, plantas y fluidos.
- [ ] Preview interactivo con PySide6.
- [ ] Capa semántica: `haz girar Saturno`, `mueve el río`, `haz respirar el sol` -> escena reproducible.

La regla del proyecto es mantener el render determinista: la IA puede proponer máscaras, depth maps y movimientos, pero el video final se genera desde parámetros explícitos y repetibles.
