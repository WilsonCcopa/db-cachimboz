# Puntajes históricos de admisión · Cachimboz

Datos agregados para el panel de preparación de Cachimboz. El cliente descarga `index.json` al iniciar y solo descarga el archivo de la universidad elegida. Las universidades sin una serie histórica analizada usan el archivo liviano `reference.json` y muestran una advertencia visible.

## Archivos

- `index.json`: catálogo de universidades públicas con licencia vigente según SUNEDU y ruta de datos.
- `unmsm.json`: Universidad Nacional Mayor de San Marcos.
- `unsaac.json`: Universidad Nacional de San Antonio Abad del Cusco.
- `unsa.json`: Universidad Nacional de San Agustín de Arequipa.
- `uni.json`: Universidad Nacional de Ingeniería.
- `reference.json`: referencia nacional orientativa para universidades sin historial analizado.

## Convenciones

- `cutoff`: puntaje mínimo de ingreso en la escala nativa del proceso.
- `normalizedCutoff`: el mismo corte convertido a una escala comparable de 0 a 20.
- `scoreScaleMax`: puntaje máximo de la escala nativa de ese registro.
- `examType`: modalidad que debe compararse únicamente consigo misma.
- `source`: publicación usada para el agregado.

Los promedios deben calcularse con `normalizedCutoff`, filtrando por universidad, carrera y modalidad exactas. La interfaz debe volver a convertir el resultado a la escala nativa para mostrarlo.

## Metodología y límites

El corte de un proceso es el menor puntaje entre quienes obtuvieron una vacante dentro del mismo grupo de carrera, modalidad, sede y fase. No se mezclan modalidades con escalas o poblaciones distintas. La línea de meta de la aplicación es una referencia histórica y no garantiza vacante ni puntaje mínimo futuro.

Las fuentes principales son los portales oficiales de resultados de [UNMSM](https://admision.unmsm.edu.pe/), [UNSA](https://www.unsa.edu.pe/), [UNI](https://puntajes.admision.uni.edu.pe/) y [UNSAAC](https://ccomputo.unsaac.edu.pe/admision/). El catálogo nacional se toma de la [lista de universidades licenciadas de SUNEDU](https://www.sunedu.gob.pe/lista-de-universidades-licenciadas/).

## Privacidad

Estos archivos contienen únicamente agregados por proceso y carrera. No se publican nombres, DNI, códigos de postulante ni filas individuales.
