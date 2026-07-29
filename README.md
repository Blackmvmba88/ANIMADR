# ANIMADR

Motor de animación 2.5D para convertir una imagen estática en video mediante capas, máscaras y deformaciones por píxel.

## Objetivo

1. Separar una imagen en objetos/capas RGBA.
2. Aplicar movimiento independiente por capa: mover, rotar, escalar, respirar, parallax y deformación líquida.
3. Componer cada frame de forma determinista.
4. Renderizar un MP4 vertical 9:16 listo para Spotify Canvas u otros formatos.

## Arquitectura prevista

```text
imagen -> segmentación/máscaras -> capas RGBA -> motion engine -> compositor -> FFmpeg -> MP4
```

La primera versión se enfocará en un renderer reproducible basado en OpenCV/NumPy y archivos de escena JSON. La segmentación automática (SAM 2), profundidad y puppet/mesh deformation entrarán después de validar el núcleo.

## Estado

Repositorio inicializado. El MVP del motor se desarrolla en una rama de trabajo antes de integrarse a `main`.
