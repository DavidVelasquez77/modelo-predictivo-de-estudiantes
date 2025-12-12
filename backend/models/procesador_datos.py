"""
procesador_datos.py
modulo para limpieza y preprocesamiento de datos en español
"""

import pandas as pd
import numpy as np
import os


class ProcesadorDatos:
    def __init__(self):
        self.datos_originales = None
        self.datos_limpios = None
        self.registros = []
        
    def cargar_datos(self, datos):
        """carga datos desde un dataframe"""
        self.datos_originales = datos.copy()
        self.registros.append("datos cargados exitosamente")
        
    def limpiar_datos(self):
        """ejecuta todo el pipeline de limpieza"""
        if self.datos_originales is None:
            raise ValueError("no hay datos cargados")
            
        self.registros = []
        
        # seleccionar columnas para el modelo
        columnas_modelo = [
            'promedio_actual', 'asistencia_clases', 'tareas_entregadas', 'participacion_clase',
            'horas_estudio', 'promedio_evaluaciones', 'cursos_reprobados', 
            'actividades_extracurriculares', 'reportes_disciplinarios', 'riesgo'
        ]
        
        # verificar columnas
        columnas_faltantes = [col for col in columnas_modelo if col not in self.datos_originales.columns]
        if columnas_faltantes:
            raise ValueError(f'columnas faltantes: {columnas_faltantes}')
            
        self.registros.append('paso 1: seleccion de columnas para el modelo')
        datos_trabajo = self.datos_originales[columnas_modelo].copy()
        self.registros.append(f'seleccionadas {len(columnas_modelo)} columnas')
        
        # limpiar columnas numericas
        datos_trabajo = self._limpiar_numericas(datos_trabajo)
        
        # limpiar actividades extracurriculares
        datos_trabajo = self._limpiar_actividades(datos_trabajo)
        
        # limpiar participacion en clase
        datos_trabajo = self._limpiar_participacion(datos_trabajo)
        
        # limpiar variable objetivo
        datos_trabajo = self._limpiar_riesgo(datos_trabajo)
        
        # imputar valores faltantes
        datos_trabajo = self._imputar_valores(datos_trabajo)
        
        # tratar outliers
        datos_trabajo = self._tratar_outliers(datos_trabajo)
        
        # eliminar duplicados
        datos_trabajo = self._eliminar_duplicados(datos_trabajo)
        
        # guardar datos limpios
        self.datos_limpios = datos_trabajo
        self.registros.append('limpieza completada exitosamente')
        
        return self.datos_limpios
        
    def _limpiar_numericas(self, datos):
        """limpia columnas numericas"""
        self.registros.append('paso 2: conversion de tipos numericos')
        
        columnas_numericas = [
            'promedio_actual', 'asistencia_clases', 'tareas_entregadas', 
            'horas_estudio', 'promedio_evaluaciones', 'cursos_reprobados', 
            'reportes_disciplinarios'
        ]
        
        for col in columnas_numericas:
            if col in datos.columns:
                antes = int(datos[col].isna().sum())
                datos[col] = datos[col].astype(str)
                datos[col] = datos[col].replace(['', ' ', 'nan', 'NaN', 'null'], pd.NA)
                datos[col] = pd.to_numeric(datos[col], errors='coerce')
                despues = int(datos[col].isna().sum())
                self.registros.append(f'columna {col}: nulos antes {antes}, despues {despues}')
                
        # limitar porcentajes a 0-100
        cols_porcentaje = ['asistencia_clases', 'tareas_entregadas']
        for col in cols_porcentaje:
            if col in datos.columns:
                datos[col] = datos[col].clip(lower=0, upper=100)
                self.registros.append(f'columna {col}: limitada a rango 0-100')
                
        return datos
        
    def _limpiar_actividades(self, datos):
        """limpia y cuenta actividades extracurriculares"""
        self.registros.append('paso 3: conteo de actividades extracurriculares')
        
        if 'actividades_extracurriculares' in datos.columns:
            datos['actividades_extracurriculares'] = datos['actividades_extracurriculares'].astype(str)
            
            def contar_actividades(texto):
                try:
                    texto = texto.strip()
                    if texto in ['[]', '', 'nan', 'none', 'null', 'NaN']:
                        return 0
                    if texto.startswith('[') and texto.endswith(']'):
                        contenido = texto[1:-1].strip()
                        if contenido == '':
                            return 0
                        elementos = contenido.split(',')
                        return len([e for e in elementos if e.strip().strip("'\"") != ''])
                    else:
                        return 1 if texto != '' else 0
                except:
                    return 0
            
            datos['actividades_extracurriculares'] = datos['actividades_extracurriculares'].apply(contar_actividades)
            self.registros.append('actividades convertidas a conteo numerico')
            
        return datos
        
    def _limpiar_participacion(self, datos):
        """normaliza participacion en clase"""
        self.registros.append('paso 4: normalizacion de participacion en clase')
        
        if 'participacion_clase' in datos.columns:
            datos['participacion_clase'] = pd.to_numeric(datos['participacion_clase'], errors='coerce')
            datos['participacion_clase'] = datos['participacion_clase'].clip(lower=0, upper=100)
            self.registros.append('participacion_clase normalizada a 0-100')
            
        return datos
        
    def _limpiar_riesgo(self, datos):
        """mapea variable objetivo riesgo"""
        self.registros.append('paso 5: mapeo de variable objetivo riesgo')
        
        if 'riesgo' in datos.columns:
            datos['riesgo'] = datos['riesgo'].astype(str).str.strip().str.lower()
            mapeo_riesgo = {
                'no riesgo': 'bajo',
                'riesgo': 'alto'
            }
            datos['riesgo'] = datos['riesgo'].map(mapeo_riesgo)
            datos['riesgo'] = datos['riesgo'].fillna('medio')
            self.registros.append('riesgo mapeado: no riesgo->bajo, riesgo->alto')
            
        return datos
        
    def _imputar_valores(self, datos):
        """imputa valores faltantes"""
        self.registros.append('paso 6: imputacion de valores faltantes')
        
        columnas_numericas = [
            'promedio_actual', 'asistencia_clases', 'tareas_entregadas', 
            'participacion_clase', 'horas_estudio', 'promedio_evaluaciones',
            'cursos_reprobados', 'actividades_extracurriculares', 'reportes_disciplinarios'
        ]
        
        for col in columnas_numericas:
            if col in datos.columns:
                antes = int(datos[col].isna().sum())
                if antes > 0:
                    mediana = datos[col].median()
                    if pd.isna(mediana):
                        datos[col] = datos[col].fillna(0)
                    else:
                        datos[col] = datos[col].fillna(mediana)
                    self.registros.append(f'{col}: {antes} valores imputados')
                    
        # imputar riesgo con moda
        if 'riesgo' in datos.columns:
            antes = int(datos['riesgo'].isna().sum())
            if antes > 0:
                moda = datos['riesgo'].mode()
                valor_relleno = moda.iloc[0] if not moda.empty else 'medio'
                datos['riesgo'] = datos['riesgo'].fillna(valor_relleno)
                self.registros.append(f'riesgo: {antes} valores imputados con {valor_relleno}')
                
        return datos
        
    def _tratar_outliers(self, datos):
        """trata outliers en horas de estudio"""
        self.registros.append('paso 7: tratamiento de outliers')
        
        if 'horas_estudio' in datos.columns:
            q1 = datos['horas_estudio'].quantile(0.25)
            q3 = datos['horas_estudio'].quantile(0.75)
            iqr = q3 - q1
            limite_inferior = max(0, q1 - 1.5 * iqr)
            limite_superior = q3 + 1.5 * iqr
            datos['horas_estudio'] = datos['horas_estudio'].clip(lower=limite_inferior, upper=limite_superior)
            self.registros.append(f'horas_estudio limitadas a [{limite_inferior:.1f}, {limite_superior:.1f}]')
            
        return datos
        
    def _eliminar_duplicados(self, datos):
        """elimina registros duplicados"""
        antes = len(datos)
        datos = datos.drop_duplicates()
        despues = len(datos)
        eliminados = antes - despues
        self.registros.append(f'paso 8: eliminados {eliminados} duplicados')
        return datos
        
    def guardar_datos_limpios(self, ruta):
        """guarda datos limpios en csv"""
        if self.datos_limpios is None:
            raise ValueError("no hay datos limpios para guardar")
            
        os.makedirs(os.path.dirname(ruta), exist_ok=True)
        self.datos_limpios.to_csv(ruta, index=False)
        self.registros.append(f'datos guardados en {ruta}')
        
    def obtener_estadisticas(self):
        """retorna estadisticas de los datos en español"""
        if self.datos_limpios is None:
            return {}
            
        estadisticas = {
            'filas': int(len(self.datos_limpios)),
            'columnas': list(self.datos_limpios.columns),
            'valores_nulos': int(self.datos_limpios.isnull().sum().sum()),
        }
        
        if 'riesgo' in self.datos_limpios.columns:
            distribucion = self.datos_limpios['riesgo'].value_counts()
            # convertir valores numpy a int de python
            estadisticas['distribucion_riesgo'] = {k: int(v) for k, v in distribucion.items()}
            
        return estadisticas