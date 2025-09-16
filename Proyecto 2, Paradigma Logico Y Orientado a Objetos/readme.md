TankAttack – Proyecto 2 (Paradigma Lógico y OO)

Juego de tanques por niveles donde enemigos defienden objetivos y calculan rutas hacia el jugador usando Prolog para pathfinding.
Implementado en Python (pygame) con un diseño orientado a objetos. Incluye documentación y recursos gráficos.

✨ Características

Mapa por niveles con muros y objetivos.

Tanque jugador vs. tanques enemigos con IA de persecución.

Integración Python ↔ Prolog para el cálculo de rutas (pathfinding.pl).

Arquitectura modular (clases Tanque, TanqueEnemigo, Bala, Muro, Objetivo).

Assets incluidos (sprites e imágenes).

Documentación del proyecto en /docs.

🧱 Estructura del proyecto (parcial)
/Proyecto 2, Paradigma Logico Y Orientado a Objetos
├─ main.py
├─ tanque.py
├─ tanque_enemigo.py
├─ bala.py
├─ muro.py
├─ objetivo.py
├─ pathfinding.pl
├─ docs/
│  ├─ Documentacion 2do Proyecto.pdf
│  └─ Enunciado 2do Proyecto (Lógico y OO).docx
└─ assets (sprites *.png en el raíz)

🧩 Requisitos

Python 3.10+

pygame (para la interfaz del juego)

SWI-Prolog (probado con versiones recientes)

(Opcional) pyswip o interfaz equivalente para invocar Prolog desde Python

Instale dependencias de Python:

pip install pygame pyswip

▶️ Ejecución

Asegure que SWI-Prolog esté instalado y accesible en el sistema.

Desde la carpeta del proyecto, ejecute:

python main.py


Controles básicos:

Flechas/WASD: mover tanque.

Barra espaciadora: disparar.

🧠 Integración con Prolog

Lógica de rutas en: pathfinding.pl.

Estrategia típica:

El módulo tanque_enemigo.py invoca consultas a Prolog para obtener el siguiente movimiento óptimo.

Se carga con consult('pathfinding.pl') (vía pyswip u otra interfaz).

✅ Pruebas y depuración

Aislar la lógica de pathfinding con grafos pequeños en Prolog.

Para Python: usar pytest o pruebas manuales en main.py.