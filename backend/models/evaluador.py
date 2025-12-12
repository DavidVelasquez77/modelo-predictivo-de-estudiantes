"""
evaluator.py
modulo para evaluacion de metricas de rendimiento del modelo
"""

import numpy as np
from collections import Counter


class EvaluadorModelo:
    """evaluador de metricas para clasificacion"""
    
    def __init__(self):
        self.y_true = None
        self.y_pred = None
        self.y_proba = None
        self.classes = None
        
    def set_predictions(self, y_true, y_pred, y_proba=None):
        """establece predicciones para evaluacion"""
        self.y_true = np.array(y_true)
        self.y_pred = np.array(y_pred)
        self.y_proba = y_proba
        self.classes = np.unique(np.concatenate([self.y_true, self.y_pred]))
        
    def accuracy(self):
        """calcula exactitud"""
        if self.y_true is None or self.y_pred is None:
            raise ValueError("establecer predicciones primero")
            
        correct = np.sum(self.y_true == self.y_pred)
        total = len(self.y_true)
        return correct / total
        
    def precision(self, average='weighted'):
        """calcula precision"""
        if self.y_true is None or self.y_pred is None:
            raise ValueError("establecer predicciones primero")
            
        if average == 'weighted':
            precisions = []
            weights = []
            
            for cls in self.classes:
                # verdaderos positivos
                tp = np.sum((self.y_true == cls) & (self.y_pred == cls))
                # falsos positivos
                fp = np.sum((self.y_true != cls) & (self.y_pred == cls))
                
                if tp + fp == 0:
                    precision_cls = 0.0
                else:
                    precision_cls = tp / (tp + fp)
                    
                precisions.append(precision_cls)
                weights.append(np.sum(self.y_true == cls))
                
            # promedio ponderado
            total_weight = sum(weights)
            if total_weight == 0:
                return 0.0
                
            weighted_precision = sum(p * w for p, w in zip(precisions, weights)) / total_weight
            return weighted_precision
            
        return 0.0
        
    def recall(self, average='weighted'):
        """calcula recall"""
        if self.y_true is None or self.y_pred is None:
            raise ValueError("establecer predicciones primero")
            
        if average == 'weighted':
            recalls = []
            weights = []
            
            for cls in self.classes:
                # verdaderos positivos
                tp = np.sum((self.y_true == cls) & (self.y_pred == cls))
                # falsos negativos
                fn = np.sum((self.y_true == cls) & (self.y_pred != cls))
                
                if tp + fn == 0:
                    recall_cls = 0.0
                else:
                    recall_cls = tp / (tp + fn)
                    
                recalls.append(recall_cls)
                weights.append(np.sum(self.y_true == cls))
                
            # promedio ponderado
            total_weight = sum(weights)
            if total_weight == 0:
                return 0.0
                
            weighted_recall = sum(r * w for r, w in zip(recalls, weights)) / total_weight
            return weighted_recall
            
        return 0.0
        
    def f1_score(self, average='weighted'):
        """calcula f1-score"""
        prec = self.precision(average)
        rec = self.recall(average)
        
        if prec + rec == 0:
            return 0.0
            
        return 2 * (prec * rec) / (prec + rec)
        
    def confusion_matrix(self):
        """calcula matriz de confusion"""
        if self.y_true is None or self.y_pred is None:
            raise ValueError("establecer predicciones primero")
            
        # crear mapeo de clases a indices
        class_to_idx = {cls: idx for idx, cls in enumerate(self.classes)}
        n_classes = len(self.classes)
        
        # inicializar matriz
        cm = np.zeros((n_classes, n_classes), dtype=int)
        
        # llenar matriz
        for true_cls, pred_cls in zip(self.y_true, self.y_pred):
            true_idx = class_to_idx[true_cls]
            pred_idx = class_to_idx[pred_cls]
            cm[true_idx, pred_idx] += 1
            
        return cm
        
    def classification_report(self):
        """genera reporte de clasificacion detallado"""
        metrics = {}
        
        # metricas globales
        metrics['accuracy'] = self.accuracy()
        metrics['precision_weighted'] = self.precision('weighted')
        metrics['recall_weighted'] = self.recall('weighted')
        metrics['f1_score_weighted'] = self.f1_score('weighted')
        
        # metricas por clase
        metrics['per_class'] = {}
        for cls in self.classes:
            # calcular metricas para esta clase
            tp = np.sum((self.y_true == cls) & (self.y_pred == cls))
            fp = np.sum((self.y_true != cls) & (self.y_pred == cls))
            fn = np.sum((self.y_true == cls) & (self.y_pred != cls))
            
            precision_cls = tp / (tp + fp) if (tp + fp) > 0 else 0.0
            recall_cls = tp / (tp + fn) if (tp + fn) > 0 else 0.0
            f1_cls = 2 * (precision_cls * recall_cls) / (precision_cls + recall_cls) if (precision_cls + recall_cls) > 0 else 0.0
            support = np.sum(self.y_true == cls)
            
            metrics['per_class'][cls] = {
                'precision': float(precision_cls),
                'recall': float(recall_cls),
                'f1_score': float(f1_cls),
                'support': int(support)
            }
            
        # matriz de confusion
        metrics['confusion_matrix'] = self.confusion_matrix().tolist()
        metrics['classes'] = list(self.classes)
        
        return metrics
        
    def obtener_resumen_metricas(self):
        """resumen de metricas principales para mostrar en frontend"""
        accuracy = self.accuracy()
        precision = self.precision('weighted')
        recall = self.recall('weighted')
        f1 = self.f1_score('weighted')
        
        # convertir a porcentajes
        return {
            'exactitud': float(round(accuracy * 100, 2)),
            'precision': float(round(precision * 100, 2)),
            'recall': float(round(recall * 100, 2)),
            'f1_score': float(round(f1 * 100, 2))
        }
        
    def cross_validation_score(self, model, X, y, cv=5):
        """validacion cruzada simple"""
        if len(X) < cv:
            cv = len(X)
            
        n_samples = len(X)
        fold_size = n_samples // cv
        scores = []
        
        for i in range(cv):
            # dividir datos
            start_idx = i * fold_size
            end_idx = start_idx + fold_size if i < cv - 1 else n_samples
            
            # crear conjuntos de validacion y entrenamiento
            X_train = np.concatenate([X[:start_idx], X[end_idx:]])
            y_train = np.concatenate([y[:start_idx], y[end_idx:]])
            X_val = X[start_idx:end_idx]
            y_val = y[start_idx:end_idx]
            
            # entrenar modelo temporal
            from .clasificador_estudiante import ClasificadorEstudiante
            temp_model = ClasificadorEstudiante(
                learning_rate=model.learning_rate,
                max_iterations=model.max_iterations,
                regularization=model.regularization
            )
            
            temp_model.fit(X_train, y_train)
            y_pred = temp_model.predict(X_val)
            
            # calcular accuracy
            accuracy = float(np.sum(y_val == y_pred) / len(y_val))
            scores.append(accuracy)
            
        return [float(score) for score in scores]