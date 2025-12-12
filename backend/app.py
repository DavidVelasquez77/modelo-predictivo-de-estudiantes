from flask import Flask, jsonify, request
from flask_cors import CORS
import pandas as pd
import numpy as np
import os

# importar modulos propios
from models.procesador_datos import ProcesadorDatos
from models.entrenador import EntrenadorModelo
from models.evaluador import EvaluadorModelo
from models.clasificador_estudiante import ClasificadorEstudiante

app = Flask(__name__)
# permitir llamadas desde el frontend durante el desarrollo
CORS(app)

# variables globales
datos = None
procesador = ProcesadorDatos()
entrenador = EntrenadorModelo()


@app.route('/')
def home():
    # esta es la ruta principal
    return jsonify({'mensaje': 'BACKEND FLASK FUNCIONANDO'})


@app.route('/upload-csv', methods=['POST'])
def upload_csv():
    global datos
    if 'file' not in request.files:
        return jsonify({'error': 'No se recibio ningun archivo '}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'archivo vacio'}), 400

    try:
        
        datos = pd.read_csv(file)
        return jsonify({'message': 'Archivo recibido'}), 200
    except Exception as e:
        return jsonify({'error': f'Error al leer CSV: {str(e)}'}), 500

@app.route('/datos/limpieza', methods=['POST'])
def limpieza_de_datos():
    """
    ejecuta limpieza de datos usando el modulo data_processor
    """
    global datos, procesador

    if datos is None:
        return jsonify({'error': 'no hay datos cargados en el servidor'}), 404

    try:
        # usar el procesador para limpiar datos
        procesador.cargar_datos(datos)
        datos_limpios = procesador.limpiar_datos()
        
        # guardar datos limpios
        outdir = os.path.join(os.path.dirname(__file__), 'data')
        outpath = os.path.join(outdir, 'datos_limpios.csv')
        procesador.guardar_datos_limpios(outpath)
        
        # obtener estadisticas
        estadisticas = procesador.obtener_estadisticas()
        
        return jsonify({
            'message': 'limpieza completada exitosamente',
            'logs': procesador.registros,
            'estadisticas': estadisticas,
            'clean_path': outpath
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/modelo/entrenar', methods=['POST'])
def entrenar_modelo():
    """
    entrena el modelo studentguard usando implementacion propia
    recibe hiperparametros dinamicos desde el frontend
    """
    global procesador, entrenador
    
    if procesador.datos_limpios is None:
        return jsonify({'error': 'no hay datos limpios, ejecuta limpieza primero'}), 404
    
    try:
        # obtener hiperparametros del request (con valores por defecto)
        datos_request = request.get_json() if request.is_json else {}
        learning_rate = datos_request.get('learning_rate', 0.01)
        max_iterations = datos_request.get('max_iterations', 1000)
        regularization = datos_request.get('regularization', 0.01)
        
        registros = ['iniciando entrenamiento del modelo studentguard...']
        registros.append(f'hiperparametros: learning_rate={learning_rate}, max_iterations={max_iterations}, regularization={regularization}')
        
        # preparar datos para entrenamiento
        registros.append('preparando datos para entrenamiento...')
        info_preparacion = entrenador.preparar_datos(procesador.datos_limpios)
        registros.append(f"datos preparados: {info_preparacion['train_samples']} entrenamiento, {info_preparacion['test_samples']} prueba")
        
        # entrenar modelo con parametros personalizados
        registros.append('entrenando modelo studentguard (implementacion propia)...')
        info_modelo = entrenador.entrenar(
            learning_rate=learning_rate,
            max_iterations=max_iterations,
            regularization=regularization
        )
        registros.append('entrenamiento completado!')
        
        # evaluar modelo
        registros.append('evaluando rendimiento del modelo...')
        evaluacion = entrenador.evaluar()
        registros.append('evaluacion completada!')
        
        # guardar modelo
        registros.append('guardando modelo entrenado...')
        directorio_datos = os.path.join(os.path.dirname(__file__), 'data')
        rutas = entrenador.guardar_modelo(directorio_datos)
        registros.append(f"modelo guardado en {rutas['modelo_path']}")
        
        return jsonify({
            'message': 'modelo entrenado exitosamente',
            'logs': registros,
            'model_info': info_modelo,
            'preparacion_datos': info_preparacion,
            'evaluacion': evaluacion,
            'rutas': rutas
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e), 'logs': registros if 'registros' in locals() else []}), 500


@app.route('/modelo/evaluacion', methods=['GET'])
def obtener_evaluacion():
    """
    obtiene metricas de evaluacion del modelo entrenado
    """
    global entrenador
    
    if not entrenador.entrenado:
        return jsonify({'error': 'modelo no entrenado'}), 404
        
    try:
        evaluacion = entrenador.evaluar()
        
        # formatear metricas principales para el frontend
        metricas_formateadas = {
            'exactitud': f"{evaluacion['metricas_principales']['exactitud']:.2f}%",
            'precision': f"{evaluacion['metricas_principales']['precision']:.2f}%",
            'recall': f"{evaluacion['metricas_principales']['recall']:.2f}%",
            'f1_score': f"{evaluacion['metricas_principales']['f1_score']:.2f}%"
        }
        
        return jsonify({
            'metricas': metricas_formateadas,
            'metricas_raw': evaluacion['metricas_principales'],
            'validacion_cruzada': evaluacion['validacion_cruzada'],
            'importancia_caracteristicas': evaluacion['importancia_caracteristicas'],
            'reporte_completo': evaluacion['reporte_completo']
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/modelo/predecir', methods=['POST'])
def predecir_individual():
    """
    realiza prediccion individual usando el modelo entrenado
    """
    global entrenador
    
    # intentar cargar modelo si no esta en memoria
    if not entrenador.entrenado:
        try:
            directorio_datos = os.path.join(os.path.dirname(__file__), 'data')
            entrenador.cargar_modelo(directorio_datos)
        except:
            return jsonify({'error': 'modelo no encontrado, entrena el modelo primero'}), 404
    
    try:
        # obtener datos del request
        datos_estudiante = request.get_json()
        
        # validar columnas requeridas
        columnas_requeridas = [
            'promedio_actual', 'asistencia_clases', 'tareas_entregadas',
            'participacion_clase', 'horas_estudio', 'promedio_evaluaciones',
            'cursos_reprobados', 'actividades_extracurriculares', 'reportes_disciplinarios'
        ]
        
        for col in columnas_requeridas:
            if col not in datos_estudiante:
                return jsonify({'error': f'falta columna {col}'}), 400
        
        # extraer valores en el orden correcto
        valores = [datos_estudiante[col] for col in columnas_requeridas]
        
        # realizar prediccion
        resultado = entrenador.predecir(valores)
        
        return jsonify({
            'riesgo': resultado['riesgo'],
            'probabilidades': resultado['probabilidades'],
            'confianza': resultado['confianza'],
            'datos_entrada': datos_estudiante
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    # inicia el servidor flask
    app.run(debug=True)
