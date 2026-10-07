# Biblioteca maestra de recursos

Esta carpeta contiene activos canónicos reutilizables del framework. No reemplaza el manifiesto local de cada proyecto: al seleccionar un recurso, se congela una copia dentro del proyecto para que preview y render sean autocontenidos.

## Fuente única

- `catalog.json`: metadatos editoriales y técnicos de cada recurso.
- `CATALOGO.md`: índice legible generado.
- `catalogo.html`: galería local con búsqueda, filtros, imágenes y reproducción de audio.
- `icons/`, `sfx/`, `music/`: archivos canónicos actuales.

No editar manualmente `CATALOGO.md` ni `catalogo.html`; se reconstruyen con:

```bash
python3 scripts/build_asset_catalog.py
```

## Integración con Media Use

El catálogo maestro responde “qué significa y cuándo conviene usarlo”. Media Use responde “dónde está la copia congelada y cuál es su procedencia técnica”. Para un proyecto nuevo:

1. Consultar candidatos reutilizables antes de buscar o generar.
2. Elegir por descripción, intención, restricciones y contexto; no solo por apariencia.
3. Ingerir o reutilizar el archivo en el manifiesto `.media/` del proyecto.
4. Mantener el mismo hash e ID global en el manifiesto editorial del proyecto.
5. Registrar uso, fecha y proyecto en `catalog.json`.

Los logos requieren coincidencia exacta de entidad. Los datos y capturas auténticas no se reutilizan fuera de su contexto solo porque “se parecen”.

## Estados

`status: approved` significa que el archivo puede vivir en la biblioteca; no implica por sí solo que el usuario haya aprobado ese recurso individual. QA, aprobación editorial, aprobación del usuario, reutilización y rendimiento se registran por separado.

## Versionado

- Un ID permanece estable mientras el recurso conserve identidad y significado.
- Una corrección técnica compatible crea una nueva versión del archivo.
- Una reinterpretación semántica recibe un ID nuevo.
- Un recurso aprobado nunca se sobrescribe silenciosamente.
- Una derivación registra su recurso padre y la transformación aplicada.
