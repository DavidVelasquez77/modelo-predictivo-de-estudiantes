"""
entrenador.py
modulo principal para entrenamiento del modelo studentguard
"""

import numpy as np
import pandas as pd
import os
from .clasificador_estudiante import ClasificadorEstudiante
from .evaluador import EvaluadorModelo


class EntrenadorModelo:
    """entrenador principal del modelo"""
    
    def __init__(self):
        self.modelo = None
        self.evaluador = None
        self.X_train = None
        self.X_test = None
    
    def __init__(self):
        self.modelo = None
        self.evaluador = None
        self.X_train = None
        self.X_test = None
        self.y_train = None
        self.y_test = None
        self.scaler_stats = None
        self.entrenado = False
        
    def preparar_datos(self, datos_limpios):
        """prepara datos para entrenamiento"""
        if 'riesgo' not in datos_limpios.columns:
            raise ValueError("columna riesgo no encontrada")
            
        # separar caracteristicas y target
        X = datos_limpios.drop('riesgo', axis=1)
        y = datos_limpios['riesgo']
        
        # verificar distribucion de clases
        distribucion = y.value_counts()
        if len(distribucion) < 2:
            raise ValueError("se necesitan al menos 2 clases diferentes")
            
        # dividir train/test (80/20)
        np.random.seed(42)
        n_samples = len(X)
        indices = np.random.permutation(n_samples)
        split_idx = int(0.8 * n_samples)
        
        train_idx = indices[:split_idx]
        test_idx = indices[split_idx:]
        
        self.X_train = X.iloc[train_idx].values
        self.X_test = X.iloc[test_idx].values
        self.y_train = y.iloc[train_idx].values
        self.y_test = y.iloc[test_idx].values
        
        # estandarizar datos
        self._estandarizar_datos()
        
        return {
            'train_samples': int(len(self.X_train)),
            'test_samples': int(len(self.X_test)),
            'features': X.columns.tolist(),
            'distribucion_train': {k: int(v) for k, v in pd.Series(self.y_train).value_counts().items()},
            'distribucion_test': {k: int(v) for k, v in pd.Series(self.y_test).value_counts().items()}
        }
        
    def _estandarizar_datos(self):
        """estandariza caracteristicas"""
        # calcular media y std del conjunto de entrenamiento
        self.scaler_stats = {
            'mean': np.mean(self.X_train, axis=0),
            'std': np.std(self.X_train, axis=0)
        }
        
        # evitar division por cero
        self.scaler_stats['std'] = np.where(self.scaler_stats['std'] == 0, 1, self.scaler_stats['std'])
        
        # aplicar estandarizacion
        self.X_train = (self.X_train - self.scaler_stats['mean']) / self.scaler_stats['std']
        self.X_test = (self.X_test - self.scaler_stats['mean']) / self.scaler_stats['std']
        
    def entrenar(self, learning_rate=0.01, max_iterations=1000, regularization=0.01):
        """entrena el modelo studentguard"""
        if self.X_train is None:
            raise ValueError("preparar datos primero")
            
        # crear modelo
        self.modelo = ClasificadorEstudiante(
            learning_rate=learning_rate,
            max_iterations=max_iterations,
            regularization=regularization
        )
        
        # entrenar
        print("iniciando entrenamiento del modelo studentguard...")
        self.modelo.fit(self.X_train, self.y_train)
        
        self.entrenado = True
        print("entrenamiento completado!")
        
        return self.modelo.get_model_info()
        
    def evaluar(self):
        """evalua el modelo entrenado"""
        if not self.entrenado:
            raise ValueError("modelo no entrenado")
            
        # predicciones en conjunto de prueba
        y_pred = self.modelo.predict(self.X_test)
        y_proba = self.modelo.predict_proba(self.X_test)
        
        # crear evaluador
        self.evaluador = EvaluadorModelo()
        self.evaluador.set_predictions(self.y_test, y_pred, y_proba)
        
        # obtener metricas
        metricas = self.evaluador.obtener_resumen_metricas()
        reporte_completo = self.evaluador.classification_report()
        
        # validacion cruzada en datos de entrenamiento
        cv_scores = self.evaluador.cross_validation_score(
            self.modelo, self.X_train, self.y_train, cv=5
        )
        
        return {
            'metricas_principales': metricas,
            'reporte_completo': reporte_completo,
            'validacion_cruzada': {
                'scores': cv_scores,
                'mean': float(np.mean(cv_scores)),
                'std': float(np.std(cv_scores))
            },
            'importancia_caracteristicas': self.modelo.get_feature_importance()
        }
        
    def guardar_modelo(self, ruta_base):
        """guarda el modelo y scaler"""
        if not self.entrenado:
            raise ValueError("modelo no entrenado")
            
        # crear directorio
        os.makedirs(ruta_base, exist_ok=True)
        
        # guardar modelo
        modelo_path = os.path.join(ruta_base, 'modelo_studentguard.pkl')
        self.modelo.save_model(modelo_path)
        
        # guardar estadisticas del scaler
        scaler_path = os.path.join(ruta_base, 'scaler_stats.pkl')
        import pickle
        with open(scaler_path, 'wb') as f:
            pickle.dump(self.scaler_stats, f)
            
        return {
            'modelo_path': modelo_path,
            'scaler_path': scaler_path
        }
        
    def cargar_modelo(self, ruta_base):
        """carga modelo y scaler guardados"""
        modelo_path = os.path.join(ruta_base, 'modelo_studentguard.pkl')
        scaler_path = os.path.join(ruta_base, 'scaler_stats.pkl')
        
        if not os.path.exists(modelo_path):
            raise ValueError("modelo no encontrado")
            
        # cargar modelo
        self.modelo = ClasificadorEstudiante()
        self.modelo.load_model(modelo_path)
        
        # cargar scaler
        if os.path.exists(scaler_path):
            import pickle
            with open(scaler_path, 'rb') as f:
                self.scaler_stats = pickle.load(f)
                
        self.entrenado = True
        
    def predecir(self, datos_estudiante):
        """predice riesgo para un estudiante individual"""
        if not self.entrenado:
            raise ValueError("modelo no entrenado")
            
        # convertir a array
        X = np.array([datos_estudiante])
        
        # aplicar mismo escalado que en entrenamiento
        if self.scaler_stats:
            X = (X - self.scaler_stats['mean']) / self.scaler_stats['std']
            
        # predecir
        prediccion = self.modelo.predict(X)[0]
        probabilidades = self.modelo.predict_proba(X)[0]
        
        # mapear probabilidades a clases
        prob_dict = {}
        for i, clase in enumerate(self.modelo.classes):
            prob_dict[clase] = float(probabilidades[i])
            
        return {
            'riesgo': prediccion,
            'probabilidades': prob_dict,
            'confianza': float(max(probabilidades))
        }