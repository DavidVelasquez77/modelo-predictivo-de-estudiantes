# StudentGuard - Sistema de Prediccion de Riesgo Academico

aplicacion de aprendizaje supervisado para identificar estudiantes en riesgo de abandono academico

## descripcion del proyecto

studentguard es una aplicacion que utiliza tecnicas de machine learning para predecir el riesgo de abandono academico de estudiantes basandose en sus metricas de desempeno. el sistema implementa tres algoritmos de clasificacion (randomforest, logisticregression y svm) y selecciona automaticamente el mejor modelo basado en metricas de evaluacion.

## caracteristicas principales

- carga masiva de datos desde archivos csv
- limpieza automatica de datos (valores faltantes, duplicados, outliers)
- entrenamiento de multiples modelos de clasificacion
- validacion cruzada para evaluar estabilidad del modelo
- metricas de evaluacion completas (accuracy, precision, recall, f1-score)
- matriz de confusion para analisis detallado
- prediccion individual de riesgo para nuevos estudiantes
- api rest con flask para integracion con frontend

## estructura del proyecto

```
OLC2_2SEVD25_ML_-29/
├── backend/
│   ├── app.py                      # servidor flask con todas las rutas
│   ├── requirements.txt            # dependencias python
│   ├── data/
│   │   ├── datos_limpios.csv      # datos procesados
│   │   ├── modelo_studentguard.pkl # modelo entrenado
│   │   └── scaler.pkl              # escalador para normalizacion
│   ├── sample_students.csv         # datos de ejemplo
│   └── studentguard_examples.csv   # mas ejemplos
├── frontend/
│   └── src/                        # aplicacion react (interfaz)
└── README.md                       # este archivo
```

## columnas de datos

el sistema espera un csv con las siguientes columnas:

- **promedio_actual**: promedio general del estudiante (0-100)
- **asistencia_clases**: porcentaje de asistencia (0-100)
- **tareas_entregadas**: porcentaje de tareas entregadas (0-100)
- **participacion_clase**: nivel de participacion (baja/media/alta)
- **horas_estudio**: horas de estudio semanal
- **promedio_evaluaciones**: promedio en evaluaciones (0-100)
- **cursos_reprobados**: numero de cursos reprobados
- **actividades_extracurriculares**: participacion en actividades (si/no)
- **reportes_disciplinarios**: numero de reportes disciplinarios
- **riesgo**: etiqueta objetivo (bajo/medio/alto) - solo para entrenamiento

## instalacion

### requisitos previos

- python 3.8 o superior
- pip (gestor de paquetes de python)

### pasos de instalacion

1. clonar el repositorio:
```bash
git clone https://github.com/NF-Pab10/OLC2_2SEVD25_ML_-29.git
cd OLC2_2SEVD25_ML_-29
```

2. instalar dependencias del backend:
```bash
cd backend
pip install -r requirements.txt
```

3. iniciar el servidor flask:
```bash
python app.py
```

el servidor estara disponible en `http://localhost:5000`

## uso del sistema

### fase 1: limpieza de datos

1. **cargar archivo csv**
   - endpoint: `POST /upload-csv`
   - envia un archivo csv con los datos de estudiantes
   - el sistema carga los datos en memoria

2. **limpiar datos**
   - endpoint: `POST /datos/limpieza`
   - ejecuta el proceso de limpieza:
     - convierte columnas numericas a tipo numerico
     - asegura porcentajes entre 0 y 100
     - mapea variables categoricas a numericas
     - imputa valores faltantes (mediana para numericos, moda para categoricos)
     - elimina outliers en horas_estudio usando metodo iqr
     - elimina registros duplicados
     - guarda datos limpios en `backend/data/datos_limpios.csv`

### fase 2: entrenamiento del modelo

3. **entrenar modelo**
   - endpoint: `POST /modelo/entrenar`
   - ejecuta el entrenamiento:
     - separa caracteristicas (x) y etiqueta (y=riesgo)
     - divide datos en train (80%) y test (20%)
     - estandariza caracteristicas con standardscaler
     - entrena tres modelos: randomforest, logisticregression, svm
     - evalua cada modelo con validacion cruzada (5-fold)
     - calcula metricas: accuracy, precision, recall, f1-score
     - genera matriz de confusion
     - selecciona mejor modelo basado en f1-score
     - guarda modelo en `backend/data/modelo_studentguard.pkl`
     - guarda scaler en `backend/data/scaler.pkl`

### fase 3: prediccion

4. **predecir riesgo individual**
   - endpoint: `POST /modelo/predecir`
   - envia datos de un estudiante en formato json
   - retorna prediccion de riesgo (bajo/medio/alto)
   - incluye probabilidades para cada clase

ejemplo de request:
```json
{
  "promedio_actual": 75,
  "asistencia_clases": 85,
  "tareas_entregadas": 80,
  "participacion_clase": 1,
  "horas_estudio": 10,
  "promedio_evaluaciones": 72,
  "cursos_reprobados": 0,
  "actividades_extracurriculares": 1,
  "reportes_disciplinarios": 0
}
```

## algoritmos implementados

### 1. random forest classifier
- conjunto de arboles de decision
- reduce sobreajuste mediante promediado
- maneja bien datos no lineales
- parametros: 100 arboles, profundidad maxima 10

### 2. logistic regression
- modelo lineal de clasificacion
- simple y eficiente
- interpreta bien relaciones lineales
- parametros: max_iter=1000

### 3. support vector machine (svm)
- busca hiperplano optimo de separacion
- usa kernel rbf para no linealidad
- efectivo en espacios de alta dimension

## metricas de evaluacion

- **accuracy**: proporcion de predicciones correctas
- **precision**: de las predicciones positivas, cuantas son correctas
- **recall**: de los casos reales positivos, cuantos se detectaron
- **f1-score**: media armonica de precision y recall
- **matriz de confusion**: tabla que muestra predicciones vs valores reales
- **validacion cruzada**: evalua estabilidad con 5 particiones

## seleccion del modelo

el sistema selecciona automaticamente el modelo con mejor f1-score. el f1-score es ideal para este problema porque balancea precision y recall, lo cual es crucial cuando queremos identificar estudiantes en riesgo sin generar demasiadas falsas alarmas.

## proceso de limpieza de datos

1. **conversion de tipos**: asegura que columnas numericas sean numeros
2. **rangos validos**: limita porcentajes entre 0 y 100
3. **mapeo categorico**: convierte participacion_clase (baja->0, media->1, alta->2)
4. **variables booleanas**: convierte actividades_extracurriculares a 0/1
5. **imputacion**: rellena valores faltantes con mediana (numericos) o moda (categoricos)
6. **outliers**: recorta valores extremos en horas_estudio usando iqr
7. **duplicados**: elimina registros duplicados
8. **exportacion**: guarda datos limpios para uso posterior

## tecnologias utilizadas

- **python 3.x**: lenguaje de programacion
- **flask**: framework web para api rest
- **pandas**: manipulacion y analisis de datos
- **numpy**: operaciones numericas
- **scikit-learn**: algoritmos de machine learning
- **joblib**: serializacion de modelos
- **flask-cors**: manejo de cors para integracion con frontend

## estructura de archivos generados

- `datos_limpios.csv`: datos procesados listos para entrenamiento
- `modelo_studentguard.pkl`: mejor modelo entrenado serializado
- `scaler.pkl`: objeto standardscaler para normalizar nuevos datos

## limitaciones y consideraciones

- no usa apis externas ni modelos preentrenados
- implementacion desde cero de pipeline de ml
- requiere minimo 20-30 registros para entrenamiento efectivo
- las predicciones dependen de la calidad de los datos de entrenamiento
- se recomienda reentrenar periodicamente con nuevos datos

## autor

pablo fernando archila ramos
organizacion de lenguajes y compiladores 2
universidad de san carlos de guatemala

## licencia

este proyecto es parte de un trabajo academico
# modelo-predictivo-de-estudiantes
