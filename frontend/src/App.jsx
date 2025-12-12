import 'bootstrap/dist/css/bootstrap.min.css';
import React, { useState, useRef } from 'react';
import './App.css';

function App() {
  const [activeTab, setActiveTab] = useState('carga'); 

  // Ref y estado para el input de archivo
  const fileInputRef = useRef(null);
  const [uploadMessage, setUploadMessage] = useState('');
  const [limpiezaLogs, setLimpiezaLogs] = useState('');
  const [trainMessage, setTrainMessage] = useState('');

  const handleFileChange = async (e) => {
    const file = e.target.files && e.target.files[0];
    if (!file) return;
    const name = file.name || '';
    const isCsv = name.toLowerCase().endsWith('.csv') || file.type === 'text/csv';
    if (!isCsv) {
      setUploadMessage('Tipo de archivo no válido. Selecciona un .csv');
      setTimeout(() => setUploadMessage(''), 3500);
      e.target.value = null;
      return;
    }

    try {
      const form = new FormData();
      form.append('file', file);

      const resp = await fetch('http://localhost:5000/upload-csv', {
        method: 'POST',
        body: form,
      });

      const body = await resp.json();
      if (!resp.ok) {
        setUploadMessage(body.error || 'Error al subir el archivo');
      } else {
        setUploadMessage(body.message || 'Archivo subido correctamente');
      }
    } catch (err) {
      setUploadMessage('Error de conexión con el servidor');
    }

    setTimeout(() => setUploadMessage(''), 3500);
    e.target.value = null;
  };

  const tabClass = (tab) => 
    tab === activeTab ? 'nav-link active text-white' : 'nav-link text-white-75';

  // hooks para metricas de evaluacion
  const [metricas, setMetricas] = useState(null);
  const [cargandoMetricas, setCargandoMetricas] = useState(false);
  const [errorMetricas, setErrorMetricas] = useState('');

  React.useEffect(() => {
    if (activeTab === 'evaluaciones') {
      setMetricas(null);
      setErrorMetricas('');
      setCargandoMetricas(true);
      fetch('http://localhost:5000/modelo/evaluacion')
        .then(resp => resp.json())
        .then(data => {
          if (data.metricas) {
            setMetricas(data.metricas);
          } else {
            setErrorMetricas(data.error || 'Error al obtener metricas');
          }
          setCargandoMetricas(false);
        })
        .catch(() => {
          setErrorMetricas('Error de conexion con el servidor');
          setCargandoMetricas(false);
        });
    }
  }, [activeTab]);

  const renderTab = () => {
    switch (activeTab) {
      case 'carga':
        return (
          <div className="tab-view text-center p-4 w-100">
            <h4 className="mb-4 text-dark">Carga Masiva</h4>
            {uploadMessage && (
              <div className="alert alert-success mt-2" role="alert" style={{maxWidth: '720px', margin: '0 auto'}}>
                {uploadMessage}
              </div>
            )}
            {/* input oculto para seleccionar archivo CSV */}
            <div className="d-flex flex-column align-items-center w-100">
              {/* Primera fila: botones uno al lado del otro */}
              <div className="d-flex flex-row justify-content-center align-items-center mb-4 gap-3">
                <button
                  className="btn btn-primary px-4 py-2"
                  style={{minWidth: '220px', fontWeight: 'bold', fontSize: '1.1rem'}}
                  onClick={async () => {
                    setLimpiezaLogs('ejecutando: conversion de formatos...\n');
                    try {
                      const resp = await fetch('http://localhost:5000/datos/limpieza', { method: 'POST' });
                      const body = await resp.json();
                      if (!resp.ok) {
                        setLimpiezaLogs(prev => prev + `error: ${body.error || 'error en limpieza'}\n`);
                        return;
                      }
                      if (body.logs && Array.isArray(body.logs)) {
                        body.logs.forEach((ln) => {
                          setLimpiezaLogs(prev => prev + ln + '\n');
                        });
                      }
                    } catch (err) {
                      setLimpiezaLogs(prev => prev + 'error de conexion con el servidor\n');
                    }
                  }}
                >
                  Limpiar Datos
                </button>
                <button
                  className="btn btn-success px-4 py-2"
                  style={{minWidth: '220px', fontWeight: 'bold', fontSize: '1.1rem'}}
                  onClick={async () => {
                    setTrainMessage('Entrenando modelo...');
                    try {
                      const resp = await fetch('http://localhost:5000/modelo/entrenar', { method: 'POST' });
                      const body = await resp.json();
                      if (!resp.ok) {
                        setTrainMessage(body.error || 'Error al entrenar el modelo');
                        return;
                      }
                      setTrainMessage('Modelo entrenado');
                    } catch (err) {
                      setTrainMessage('Error de conexión con el servidor');
                    }
                    setTimeout(() => setTrainMessage(''), 4000);
                  }}
                >
                  Entrenar Modelo
                </button>
                {trainMessage && (
                  <div className="alert alert-success mt-2" role="alert" style={{maxWidth: '720px', margin: '8px auto 0'}}>
                    {trainMessage}
                  </div>
                )}
              </div>
              {/* Segunda fila: upload a la izquierda, textarea a la derecha */}
              <div className="d-flex flex-row justify-content-center align-items-start w-100">
                {/* upload-card centrado a la izquierda */}
                <div className="d-flex justify-content-start align-items-center me-4" style={{flex: '0 0 30%'}}>
                  <div
                    className="border p-5 d-flex flex-column align-items-center shadow upload-card"
                    style={{background: '#fff', borderRadius: '16px', minWidth: '260px'}}
                    onClick={() => fileInputRef.current && fileInputRef.current.click()}
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" width="80" height="80" fill="#007bff" viewBox="0 0 24 24">
                      <path d="M19.35 10.04C18.67 6.59 15.64 4 12 4 9.11 4 6.6 5.64 5.35 8.04 2.34 8.36 0 10.91 0 14c0 3.31 2.69 6 6 6h13c2.76 0 5-2.24 5-5 0-2.64-2.05-4.78-4.65-4.96zM14 13v4h-4v-4H7l5-5 5 5h-3z"/>
                    </svg>
                    <span className="mt-2" style={{color: '#007bff', fontWeight: 'bold'}}>Subir Archivo</span>
                  </div>
                  {/* input oculto: solo .csv */}
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv,text/csv"
                    style={{display: 'none'}}
                    onChange={handleFileChange}
                  />
                </div>
                {/* textarea a la derecha */}
                <div className="d-flex justify-content-center align-items-center" style={{flex: '0 0 65%'}}>
                  <div style={{width: '100%', maxWidth: '900px'}}>
                    <label className="form-label">logs de limpieza</label>
                    <textarea className="form-control" rows={20} value={limpiezaLogs} readOnly style={{width: '100%'}} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      case 'ajustes':
        return (
          <div className="tab-view text-center p-4 w-100">
            <h4 className="mb-4 text-dark">Ajustes</h4>
            <div className="mt-4">
              <div className="card mx-auto" style={{maxWidth: '600px'}}>
                <div className="card-body">
                </div>
              </div>
            </div>
          </div>
        );
      case 'evaluaciones':
        return (
          <div className="tab-view text-center p-4 w-100">
            <h4 className="mb-4 text-dark">Evaluacion de Rendimiento</h4>
            <div className="mt-4">
              <div className="card mx-auto" style={{maxWidth: '700px'}}>
                <div className="card-body">
                  {cargandoMetricas && (
                    <div className="mb-3">Cargando metricas...</div>
                  )}
                  {errorMetricas && (
                    <div className="alert alert-danger mb-3">{errorMetricas}</div>
                  )}
                  {metricas && (
                    <div className="row justify-content-center align-items-center" style={{gap: '24px'}}>
                      <div className="col-12 col-md-5 col-lg-3 mb-3">
                        <div className="border rounded p-4 text-center shadow-sm metric-card" style={{fontSize: '2rem', fontWeight: 'bold', background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)'}}>
                          {metricas.exactitud}
                          <div style={{fontSize: '1.1rem', fontWeight: 'normal', marginTop: '8px', color: '#007bff'}}>Exactitud</div>
                        </div>
                      </div>
                      <div className="col-12 col-md-5 col-lg-3 mb-3">
                        <div className="border rounded p-4 text-center shadow-sm metric-card" style={{fontSize: '2rem', fontWeight: 'bold', background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)'}}>
                          {metricas.precision}
                          <div style={{fontSize: '1.1rem', fontWeight: 'normal', marginTop: '8px', color: '#007bff'}}>Precision</div>
                        </div>
                      </div>
                      <div className="col-12 col-md-5 col-lg-3 mb-3">
                        <div className="border rounded p-4 text-center shadow-sm metric-card" style={{fontSize: '2rem', fontWeight: 'bold', background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)'}}>
                          {metricas.recall}
                          <div style={{fontSize: '1.1rem', fontWeight: 'normal', marginTop: '8px', color: '#007bff'}}>Recall</div>
                        </div>
                      </div>
                      <div className="col-12 col-md-5 col-lg-3 mb-3">
                        <div className="border rounded p-4 text-center shadow-sm metric-card" style={{fontSize: '2rem', fontWeight: 'bold', background: 'linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%)'}}>
                          {metricas.f1_score}
                          <div style={{fontSize: '1.1rem', fontWeight: 'normal', marginTop: '8px', color: '#007bff'}}>F1-Score</div>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        );
      case 'prediccion':
        return (
          <div className="tab-view p-4 w-100 d-flex flex-column align-items-center justify-content-center" style={{minHeight: '80vh'}}>
            <h2 className="mb-4 text-dark" style={{fontWeight: 'bold', letterSpacing: '1px'}}>Prediccion de Riesgo</h2>
            <div className="d-flex flex-column flex-lg-row align-items-start justify-content-center w-100" style={{gap: '48px'}}>
              <form className="prediction-form p-4 rounded shadow-lg" style={{minWidth: '340px', maxWidth: '420px', width: '100%'}}>
                <div className="row g-3 mb-2">
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Promedio actual" />
                  </div>
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Asistencia a clases" />
                  </div>
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Tareas entregadas" />
                  </div>
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Participacion en clase" />
                  </div>
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Horas de estudio" />
                  </div>
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Actividades extracurriculares" />
                  </div>
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Cursos reprobados" />
                  </div>
                  <div className="col-12 col-md-6">
                    <input type="text" className="form-control form-control-lg" placeholder="Reportes disciplinarios" />
                  </div>
                </div>
                <hr className="my-3" />
                <div className="d-flex justify-content-center gap-3">
                  <button type="button" className="btn btn-dark px-4 py-2" style={{fontWeight: 'bold', fontSize: '1.1rem'}}>Predecir</button>
                  <button type="button" className="btn btn-secondary px-4 py-2" style={{fontWeight: 'bold', fontSize: '1.1rem'}}>Cancelar</button>
                </div>
              </form>
              <div className="result-area d-flex flex-column align-items-center justify-content-center p-5 rounded shadow-lg" style={{minWidth: '260px', minHeight: '260px'}}>
                <div className="mb-3" style={{fontSize: '4rem'}}>
                  <span style={{marginRight: '16px'}}>
                    <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" fill="#222" viewBox="0 0 16 16">
                      <path d="M6.956 1.745C7.021.81 7.908.081 8.864.325l.088.02c.98.245 1.712 1.07 1.646 2.005l-.345 4.708a.5.5 0 0 1-.5.462h-2.5a.5.5 0 0 1-.5-.462L6.956 1.745z"/>
                      <path d="M4.5 8.5A.5.5 0 0 1 5 8h6a.5.5 0 0 1 .5.5v.5a.5.5 0 0 1-.5.5H5a.5.5 0 0 1-.5-.5v-.5z"/>
                    </svg>
                  </span>
                  <span>
                    <svg xmlns="http://www.w3.org/2000/svg" width="56" height="56" fill="#222" viewBox="0 0 16 16">
                      <path d="M9.044 14.255c-.065.935-.952 1.664-1.908 1.419l-.088-.02c-.98-.245-1.712-1.07-1.646-2.005l.345-4.708a.5.5 0 0 1 .5-.462h2.5a.5.5 0 0 1 .5.462l-.345 4.708z"/>
                      <path d="M11.5 7.5a.5.5 0 0 1-.5.5H5a.5.5 0 0 1-.5-.5v-.5a.5.5 0 0 1 .5-.5h6a.5.5 0 0 1 .5.5v.5z"/>
                    </svg>
                  </span>
                </div>
                <div style={{fontSize: '1.5rem', fontWeight: 'bold', color: '#222'}}>Resultado</div>
              </div>
            </div>
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="app-root vh-100 w-100 d-flex flex-column overflow-hidden">
      {/* Navbar */}
      <nav className="navbar navbar-expand-lg navbar-dark w-100 py-3" 
           style={{background: 'linear-gradient(90deg, #007bff 0%, #6610f2 100%)'}}>
        <div className="container-fluid">
          <a className="navbar-brand d-flex align-items-center" href="#" 
             onClick={(e)=>{e.preventDefault(); setActiveTab('carga')}}>
            <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill="#fff" 
                 className="bi bi-house-door-fill me-2" viewBox="0 0 16 16">
              <path d="M6.5 10.995V14.5a.5.5 0 0 0 .5.5h2a.5.5 0 0 0 .5-.5v-3.505a.5.5 0 0 1 .5-.5h2a.5.5 0 0 0 .5-.5V7.293l-5-4.5-5 4.5V10a.5.5 0 0 0 .5.5h2a.5.5 0 0 1 .5.5z"/>
            </svg>
            <span className="h4 mb-0 text-white">StudentGuard</span>
          </a>
          
          <button className="navbar-toggler" type="button" data-bs-toggle="collapse" 
                  data-bs-target="#navbarNav" aria-controls="navbarNav" aria-expanded="false" 
                  aria-label="Toggle navigation">
            <span className="navbar-toggler-icon"></span>
          </button>
          
          <div className="collapse navbar-collapse" id="navbarNav">
            <ul className="navbar-nav ms-auto">
              <li className="nav-item">
                <a className={tabClass('carga')} href="#" 
                   onClick={(e)=>{e.preventDefault(); setActiveTab('carga')}}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-upload me-2" viewBox="0 0 16 16">
                    <path d="M.5 9.9a.5.5 0 0 1 .5.5v2.5a1 1 0 0 0 1 1h12a1 1 0 0 0 1-1v-2.5a.5.5 0 0 1 1 0v2.5a2 2 0 0 1-2 2H2a2 2 0 0 1-2-2v-2.5a.5.5 0 0 1 .5-.5z"/>
                    <path d="M7.646 1.146a.5.5 0 0 1 .708 0l3 3a.5.5 0 0 1-.708.708L8.5 2.707V11.5a.5.5 0 0 1-1 0V2.707L5.354 4.854a.5.5 0 1 1-.708-.708l3-3z"/>
                  </svg>
                  Carga Masiva
                </a>
              </li>
              <li className="nav-item">
                <a className={tabClass('ajustes')} href="#" 
                   onClick={(e)=>{e.preventDefault(); setActiveTab('ajustes')}}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-gear me-2" viewBox="0 0 16 16">
                    <path d="M8 4.754a3.246 3.246 0 1 0 0 6.492 3.246 3.246 0 0 0 0-6.492zM5.754 8a2.246 2.246 0 1 1 4.492 0 2.246 2.246 0 0 1-4.492 0z"/>
                    <path d="M9.796 1.343c-.527-1.79-3.065-1.79-3.592 0l-.094.319a.873.873 0 0 1-1.255.52l-.292-.16c-1.64-.892-3.433.902-2.54 2.541l.159.292a.873.873 0 0 1-.52 1.255l-.319.094c-1.79.527-1.79 3.065 0 3.592l.319.094a.873.873 0 0 1 .52 1.255l-.16.292c-.892 1.64.901 3.434 2.541 2.54l.292-.159a.873.873 0 0 1 1.255.52l.094.319c.527 1.79 3.065 1.79 3.592 0l.094-.319a.873.873 0 0 1 1.255-.52l.292.16c1.64.893 3.434-.902 2.54-2.541l-.159-.292a.873.873 0 0 1 .52-1.255l.319-.094c1.79-.527 1.79-3.065 0-3.592l-.319-.094a.873.873 0 0 1-.52-1.255l.16-.292c.893-1.64-.902-3.433-2.541-2.54l-.292.159a.873.873 0 0 1-1.255-.52l-.094-.319zm-2.633.283c.246-.835 1.428-.835 1.674 0l.094.319a1.873 1.873 0 0 0 2.693 1.115l.291-.16c.764-.415 1.6.42 1.184 1.185l-.159.292a1.873 1.873 0 0 0 1.116 2.692l.318.094c.835.246.835 1.428 0 1.674l-.319.094a1.873 1.873 0 0 0-1.115 2.693l.16.291c.415.764-.42 1.6-1.185 1.184l-.291-.159a1.873 1.873 0 0 0-2.693 1.116l-.094.318c-.246.835-1.428.835-1.674 0l-.094-.319a1.873 1.873 0 0 0-2.692-1.115l-.292.16c-.764.415-1.6-.42-1.184-1.185l.159-.291A1.873 1.873 0 0 0 1.945 8.93l-.319-.094c-.835-.246-.835-1.428 0-1.674l.319-.094A1.873 1.873 0 0 0 3.06 4.377l-.16-.292c-.415-.764.42-1.6 1.185-1.184l.292.159a1.873 1.873 0 0 0 2.692-1.115l.094-.319z"/>
                  </svg>
                  Ajustes
                </a>
              </li>
              <li className="nav-item">
                <a className={tabClass('evaluaciones')} href="#" 
                   onClick={(e)=>{e.preventDefault(); setActiveTab('evaluaciones')}}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-bar-chart me-2" viewBox="0 0 16 16">
                    <path d="M4 11H2v3h2v-3zm5-4H7v7h2V7zm5-5v12h-2V2h2zm-2-1a1 1 0 0 0-1 1v12a1 1 0 0 0 1 1h2a1 1 0 0 0 1-1V2a1 1 0 0 0-1-1h-2zM6 7a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v5a1 1 0 0 1-1 1H7a1 1 0 0 1-1-1V7zm-5 4a1 1 0 0 1 1-1h2a1 1 0 0 1 1 1v3a1 1 0 0 1-1 1H2a1 1 0 0 1-1-1v-3z"/>
                  </svg>
                  Evaluaciones
                </a>
              </li>
              <li className="nav-item">
                <a className={tabClass('prediccion')} href="#" 
                   onClick={(e)=>{e.preventDefault(); setActiveTab('prediccion')}}>
                  <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="currentColor" className="bi bi-eye me-2" viewBox="0 0 16 16">
                    <path d="M16 8s-3-5.5-8-5.5S0 8 0 8s3 5.5 8 5.5S16 8 16 8zM1.173 8a13.133 13.133 0 0 1 1.66-2.043C4.12 4.668 5.88 3.5 8 3.5c2.12 0 3.879 1.168 5.168 2.457A13.133 13.133 0 0 0 14.828 8c-.058.087-.122.183-.195.288-.335.48-.83 1.12-1.465 1.755C11.879 11.332 10.119 12.5 8 12.5c-2.12 0-3.879-1.168-5.168-2.457A13.134 13.134 0 0 0 1.172 8z"/>
                    <path d="M8 5.5a2.5 2.5 0 1 0 0 5 2.5 2.5 0 0 0 0-5zM4.5 8a3.5 3.5 0 1 1 7 0 3.5 3.5 0 0 1-7 0z"/>
                  </svg>
                  Predicción
                </a>
              </li>
            </ul>
          </div>
        </div>
      </nav>

      {/* Contenido Principal */}
      <div className="flex-grow-1 w-100 d-flex justify-content-center align-items-center bg-light">
        <div className="container-fluid h-100 d-flex flex-column justify-content-center align-items-center">
          <div className="w-100 h-100 d-flex flex-column justify-content-center align-items-center p-3">
            {renderTab()}
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;