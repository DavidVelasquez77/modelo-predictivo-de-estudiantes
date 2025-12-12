"""
student_classifier.py
modelo propio de clasificacion para predecir riesgo academico
implementacion desde cero usando solo numpy
"""

import numpy as np
import pickle
import os


class ClasificadorEstudiante:
    """
    clasificador propio basado en regresion logistica multinomial
    implementado desde cero sin usar modelos preentrenados
    """
    
    def __init__(self, learning_rate=0.01, max_iterations=1000, regularization=0.01):
        self.learning_rate = learning_rate
        self.max_iterations = max_iterations
        self.regularization = regularization
        self.weights = None
        self.bias = None
        self.classes = None
        self.feature_names = None
        self.is_fitted = False
        self.training_history = []
        
    def _softmax(self, z):
        """aplica funcion softmax"""
        # prevenir overflow numerico
        z_shifted = z - np.max(z, axis=1, keepdims=True)
        exp_z = np.exp(z_shifted)
        return exp_z / np.sum(exp_z, axis=1, keepdims=True)
        
    def _one_hot_encode(self, y):
        """codifica etiquetas en formato one-hot"""
        n_classes = len(self.classes)
        n_samples = len(y)
        y_encoded = np.zeros((n_samples, n_classes))
        
        class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        for i, cls in enumerate(y):
            y_encoded[i, class_to_idx[cls]] = 1
            
        return y_encoded
        
    def _compute_cost(self, y_true, y_pred):
        """calcula costo usando entropia cruzada"""
        # evitar log(0) agregando pequeño epsilon
        epsilon = 1e-15
        y_pred = np.clip(y_pred, epsilon, 1 - epsilon)
        
        # entropia cruzada
        cost = -np.mean(np.sum(y_true * np.log(y_pred), axis=1))
        
        # agregar regularizacion l2
        if self.weights is not None:
            l2_penalty = self.regularization * np.sum(self.weights ** 2)
            cost += l2_penalty
            
        return cost
        
    def fit(self, X, y):
        """entrena el modelo"""
        # convertir a numpy arrays
        X = np.array(X, dtype=np.float64)
        y = np.array(y)
        
        # obtener dimensiones
        n_samples, n_features = X.shape
        self.classes = np.unique(y)
        n_classes = len(self.classes)
        
        # guardar nombres de caracteristicas
        if hasattr(X, 'columns'):
            self.feature_names = list(X.columns)
        else:
            self.feature_names = [f'feature_{i}' for i in range(n_features)]
            
        # inicializar pesos aleatoriamente
        np.random.seed(42)
        self.weights = np.random.normal(0, 0.01, (n_features, n_classes))
        self.bias = np.zeros((1, n_classes))
        
        # codificar etiquetas
        y_encoded = self._one_hot_encode(y)
        
        # entrenamiento por descenso de gradiente
        self.training_history = []
        
        for iteration in range(self.max_iterations):
            # forward pass
            z = np.dot(X, self.weights) + self.bias
            predictions = self._softmax(z)
            
            # calcular costo
            cost = self._compute_cost(y_encoded, predictions)
            self.training_history.append(cost)
            
            # calcular gradientes
            dw = np.dot(X.T, (predictions - y_encoded)) / n_samples
            db = np.mean(predictions - y_encoded, axis=0, keepdims=True)
            
            # agregar regularizacion a los pesos
            dw += self.regularization * self.weights
            
            # actualizar parametros
            self.weights -= self.learning_rate * dw
            self.bias -= self.learning_rate * db
            
            # verificar convergencia cada 100 iteraciones
            if iteration % 100 == 0:
                print(f'iteracion {iteration}, costo: {cost:.4f}')
                
        self.is_fitted = True
        print(f'entrenamiento completado. costo final: {self.training_history[-1]:.4f}')
        
    def predict(self, X):
        """predice clases"""
        if not self.is_fitted:
            raise ValueError("modelo no entrenado. ejecuta fit() primero")
            
        X = np.array(X, dtype=np.float64)
        z = np.dot(X, self.weights) + self.bias
        probabilities = self._softmax(z)
        
        # retornar clase con mayor probabilidad
        predictions = np.argmax(probabilities, axis=1)
        return np.array([self.classes[pred] for pred in predictions])
        
    def predict_proba(self, X):
        """predice probabilidades"""
        if not self.is_fitted:
            raise ValueError("modelo no entrenado. ejecuta fit() primero")
            
        X = np.array(X, dtype=np.float64)
        z = np.dot(X, self.weights) + self.bias
        return self._softmax(z)
        
    def get_feature_importance(self):
        """calcula importancia de caracteristicas"""
        if not self.is_fitted:
            raise ValueError("modelo no entrenado")
            
        # usar magnitud promedio de los pesos como importancia
        importance = np.mean(np.abs(self.weights), axis=1)
        
        # normalizar
        importance = importance / np.sum(importance)
        
        feature_importance = {}
        for i, feature_name in enumerate(self.feature_names):
            feature_importance[feature_name] = float(importance[i])
            
        return feature_importance
        
    def save_model(self, filepath):
        """guarda el modelo"""
        if not self.is_fitted:
            raise ValueError("modelo no entrenado")
            
        model_data = {
            'weights': self.weights,
            'bias': self.bias,
            'classes': self.classes,
            'feature_names': self.feature_names,
            'learning_rate': self.learning_rate,
            'max_iterations': self.max_iterations,
            'regularization': self.regularization,
            'training_history': self.training_history
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
            
    def load_model(self, filepath):
        """carga el modelo"""
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
            
        self.weights = model_data['weights']
        self.bias = model_data['bias']
        self.classes = model_data['classes']
        self.feature_names = model_data['feature_names']
        self.learning_rate = model_data['learning_rate']
        self.max_iterations = model_data['max_iterations']
        self.regularization = model_data['regularization']
        self.training_history = model_data.get('training_history', [])
        self.is_fitted = True
        
    def get_model_info(self):
        """retorna informacion del modelo"""
        return {
            'tipo': 'StudentClassifier (Regresion Logistica Multinomial)',
            'autor': 'Implementacion Propia',
            'caracteristicas': len(self.feature_names) if self.feature_names else 0,
            'clases': list(self.classes) if self.classes is not None else [],
            'parametros': {
                'learning_rate': self.learning_rate,
                'max_iterations': self.max_iterations,
                'regularization': self.regularization
            },
            'entrenado': self.is_fitted
        }