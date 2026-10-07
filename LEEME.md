# Framework de edición · entrega portátil 2.1

**Para alumnos: abre `INICIO WINDOWS.cmd` o `INICIO MAC.command`.** Se abre automáticamente la guía de 15 pasos en el navegador. Si falta Python, primero se abre la ayuda `INICIO.html` y la terminal pide autorización para descargar lo necesario. No necesitas instalar Git.

La guía permite tachar acciones, escribir notas, ver ayudas e imprimir un informe. El asistente conserva también el cuestionario, colores, plantillas y rutas. **El guardado normal queda en `MI-PROGRESO/` dentro de esta carpeta**, con confirmación visible y copia anterior. No depende de la memoria del navegador.

- **Si no aparece el navegador:** tras iniciar, abre `MI-PROGRESO/ABRIR GUIA.html` y pulsa su botón. `INICIO.html` es el acceso de ayuda permanente.
- **Para aprender a grabar:** [GUIA_GRABACION_MASTER.html](./GUIA_GRABACION_MASTER.html) separa marcadores, guion y pausas. Incluye dibujo de encuadre, cuatro ejemplos, guion editable y checklist. Ábrela desde la guía conectada para guardar en la carpeta.
- **Para leer sin iniciar:** [GUIASUPERDETALLADA.html](./GUIASUPERDETALLADA.html). Mostrará Modo lectura; un HTML abierto solo no puede escribir automáticamente en la carpeta.
- **Referencia completa:** [INICIO Y CONFIGURACION DE FRAMEWORK.md](./INICIO%20Y%20CONFIGURACION%20DE%20FRAMEWORK.md).

Deja la terminal abierta. Espera a ver **Guardado en MI-PROGRESO** antes de cerrar. **Guardar copia del progreso** crea un respaldo en `MI-PROGRESO/copias/`; **Recuperar una copia** muestra esas copias y permite elegir una. Al abrir INICIO otro día se recupera el último estado. Si cambias de computadora, conserva la carpeta pero vuelve a comprobar su instalación. Las casillas no certifican que un equipo o video estén aprobados.

Esta misma carpeta conserva las 30 propuestas, referencias de código, reglas, recursos reutilizables, skills y memoria del trabajo. No incluye renders ni grabaciones de videos anteriores. Los masters nuevos se referencian sin duplicarlos.

Las herramientas se verifican e instalan con autorización. La configuración es propia de cada equipo. Conserva una copia local independiente en cada máquina; no trabajes simultáneamente sobre el mismo lote sincronizado.

- `INICIO_PARA_CODEX.md`: guía para continuar la edición con las reglas existentes.
- `proyecto/`: carpeta que abrir en Codex para editar.
- `entrada-masters/`: lugar opcional para los nuevos originales.
- `asistente/` y `tools/`: interfaz y automatización de esta entrega.
- `perfiles/`: diferencias entre las PC A/B y Mac.
- `evidencia/`: pruebas, hashes, historia y límites reales de validación.
- `CHANGELOG.md`: evolución de la entrega; las versiones documentales anteriores se conservan en `evidencia/historico-v1/`.

Si usas CLI avanzada: `python tools/windows.py --help`. El nombre `windows.py` se conserva por compatibilidad, pero ahora admite el runtime aislado de Mac. La aprobación requerida para render y el QA no cambian.
