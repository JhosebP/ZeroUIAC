# ZeroUI-AC

ZeroUI-AC es un sistema de interfaz humano-computadora multimodal orientado a
personas con discapacidad motriz de extremidades superiores.

El sistema busca permitir el control de una computadora mediante:

- movimientos de cabeza;
- gestos de la extremidad superior remanente;
- comandos de voz offline;
- emulación de mouse y teclado;
- interacción multimodal;
- adaptación automática de parámetros de interacción.

El proyecto se desarrolla principalmente en Python y está orientado a
computadoras con Windows 10 y Windows 11.

---

## Estado actual

El proyecto se encuentra actualmente en el desarrollo del **Sprint 1**.

Las principales funcionalidades contempladas en este Sprint son:

- captura de video mediante cámara web;
- detección facial mediante MediaPipe Face Mesh;
- estimación de orientación de cabeza;
- control del cursor mediante movimientos de cabeza;
- calibración de posición neutra;
- calibración del rango cervical;
- reconocimiento offline de comandos de voz;
- corpus cerrado de 20 comandos en español;
- emulación de clic izquierdo;
- integración inicial de los componentes.

---

## Tecnologías utilizadas

- Python 3.11
- OpenCV
- MediaPipe
- NumPy
- PyAutoGUI
- Vosk
- SoundDevice
- PyTest

Posteriormente se incorporarán tecnologías relacionadas con:

- aprendizaje por refuerzo;
- estimación de fatiga;
- fusión multimodal;
- dashboard local;
- empaquetado portable para Windows.

---

## Requisitos

Se recomienda utilizar:

- Windows 10 o Windows 11;
- Python 3.11;
- cámara web de al menos 720p;
- micrófono;
- entorno virtual de Python.

---

## Crear entorno virtual

Desde la raíz del proyecto:

```powershell
python -m venv .venv