let map, combinedChart;
let currentUserId = null;

console.log("✅ Script cargado correctamente");

// ==========================================
// FUNCIONES DE AUTENTICACIÓN
// ==========================================

window.showLoginScreen = function() {
    document.getElementById('register-screen').style.display = 'none';
    document.getElementById('login-screen').style.display = 'block';
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('login-user').value = '';
    document.getElementById('login-pass').value = '';
};

window.showRegisterScreen = function() {
    document.getElementById('login-screen').style.display = 'none';
    document.getElementById('register-screen').style.display = 'block';
    document.getElementById('main-app').style.display = 'none';
    document.getElementById('register-user').value = '';
    document.getElementById('register-pass').value = '';
    document.getElementById('register-pass-confirm').value = '';
};

window.handleLogin = async function() {
    const username = document.getElementById('login-user').value.trim();
    const password = document.getElementById('login-pass').value.trim();

    if (!username || !password) {
        alert("Por favor, introduce usuario y contraseña.");
        return;
    }

    try {
        const response = await fetch('/login', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            currentUserId = data.id;
            document.getElementById('login-screen').style.display = 'none';
            document.getElementById('register-screen').style.display = 'none';
            document.getElementById('main-app').style.display = 'block';
            document.getElementById('user-welcome').innerText = `Hola, ${data.username} 🏃‍♂️`;
            
            limpiarInterfaz();
            showTab('new');
            setTimeout(configurarFileInput, 200);
        } else {
            alert(data.detail || "Error al iniciar sesión");
        }
    } catch (error) {
        console.error("Error de conexión:", error);
        alert("No se pudo conectar con el servidor.");
    }
};

window.handleRegister = async function() {
    const username = document.getElementById('register-user').value.trim();
    const password = document.getElementById('register-pass').value.trim();
    const passwordConfirm = document.getElementById('register-pass-confirm').value.trim();

    if (!username || !password || !passwordConfirm) {
        alert("Por favor, completa todos los campos.");
        return;
    }

    if (username.length < 3) {
        alert("El nombre de usuario debe tener al menos 3 caracteres.");
        return;
    }

    if (password.length < 6) {
        alert("La contraseña debe tener al menos 6 caracteres.");
        return;
    }

    if (password !== passwordConfirm) {
        alert("Las contraseñas no coinciden. Por favor, verifica que sean iguales.");
        return;
    }

    try {
        const response = await fetch('/register', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username, password })
        });

        const data = await response.json();

        if (response.ok) {
            alert("¡Cuenta creada correctamente! Ahora puedes iniciar sesión.");
            showLoginScreen();
            document.getElementById('login-user').value = username;
        } else {
            alert(data.detail || "Error al crear la cuenta");
        }
    } catch (error) {
        console.error("Error de conexión:", error);
        alert("No se pudo conectar con el servidor.");
    }
};

window.logout = function() {
    currentUserId = null;
    limpiarInterfaz();
    showLoginScreen();
};

function limpiarInterfaz() {
    if (map) map.remove();
    if (combinedChart) combinedChart.destroy();
    const resultsArea = document.getElementById('results-area');
    if (resultsArea) resultsArea.style.display = 'none';
    const recordsList = document.getElementById('records-list');
    if (recordsList) recordsList.innerHTML = '';
    const tcxFile = document.getElementById('tcx-file');
    if (tcxFile) tcxFile.value = '';
}

// ==========================================
// GESTIÓN DE PESTAÑAS
// ==========================================

window.showTab = function(tab) {
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    document.querySelectorAll('.btn-nav').forEach(btn => btn.classList.remove('active'));
    
    document.getElementById('tab-' + tab).style.display = 'block';
    
    if (tab === 'records') {
        document.querySelector('button[onclick="showTab(\'records\')"]').classList.add('active');
        loadRecords();
    } else if (tab === 'new') {
        document.getElementById('btn-new-tab').classList.add('active');
    } else if (tab === 'predictions') {
        document.querySelector('button[onclick="showTab(\'predictions\')"]').classList.add('active');
        loadPredictions();
    }
};

// ==========================================
// CARGAR RÉCORDS
// ==========================================

async function loadRecords() {
    try {
        const res = await fetch(`/records/${currentUserId}`);
        const data = await res.json();
        const list = document.getElementById('records-list');
        list.innerHTML = '';

        if(data.length === 0) {
            list.innerHTML = '<p class="text-center opacity-50 mt-4">Sube una sesión para calcular tus primeros récords</p>';
            return;
        }

        const recordsOrdenados = data.sort((a, b) => a.distancia_metros - b.distancia_metros);
        
        list.innerHTML = recordsOrdenados.map(r => {
            const m = Math.floor(r.tiempo_segundos / 60);
            const s = Math.floor(r.tiempo_segundos % 60);
            const h = Math.floor(m / 60);
            const mins = m % 60;
            
            let timeDisplay;
            if (h > 0) {
                timeDisplay = `${h}h ${mins}m ${s}s`;
            } else if (m > 0) {
                timeDisplay = `${m}:${s.toString().padStart(2,'0')}`;
            } else {
                timeDisplay = `${s}s`;
            }
            
            const ritmo_min = r.tiempo_segundos / (r.distancia_metros / 1000) / 60;
            const ritmo_m = Math.floor(ritmo_min);
            const ritmo_s = Math.floor((ritmo_min - ritmo_m) * 60);
            
            return `
                <div class="record-card-modern mb-3">
                    <div class="record-header">
                        <div class="record-badge">${r.distancia_nombre}</div>
                        <div class="record-time">${timeDisplay}</div>
                    </div>
                    <div class="record-stats">
                        <div class="stat-item">
                            <div class="stat-icon">⚡</div>
                            <div class="stat-content">
                                <div class="stat-label">Ritmo</div>
                                <div class="stat-value">${ritmo_m}:${ritmo_s.toString().padStart(2,'0')} /km</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-icon">❤️</div>
                            <div class="stat-content">
                                <div class="stat-label">Pulsaciones</div>
                                <div class="stat-value">${r.pulsaciones_medias || 'N/A'} ppm</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-icon">⛰️</div>
                            <div class="stat-content">
                                <div class="stat-label">Desnivel</div>
                                <div class="stat-value">+${Math.round(r.desnivel_positivo)}m</div>
                            </div>
                        </div>
                        <div class="stat-item">
                            <div class="stat-icon">📅</div>
                            <div class="stat-content">
                                <div class="stat-label">Fecha</div>
                                <div class="stat-value">${new Date(r.fecha_actividad).toLocaleDateString('es-ES', { day: 'numeric', month: 'short', year: 'numeric' })}</div>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    } catch (e) { 
        console.error("Error cargando récords:", e);
        alert("Error al cargar los récords");
    }
}

// ==========================================
// SUBIDA DE ARCHIVOS
// ==========================================

function configurarFileInput() {
    console.log("🔧 Configurando file input...");
    
    const fileInput = document.getElementById('tcx-file');
    
    if (!fileInput) {
        console.error("❌ No se encontró el file input");
        return;
    }
    
    console.log("✅ File input encontrado");
    fileInput.addEventListener('change', manejarSubidaArchivo);
    console.log("✅ Event listener configurado");
}

async function manejarSubidaArchivo(event) {
    console.log("📁 Archivo seleccionado");
    
    const fileInput = event.target;
    const archivo = fileInput.files[0];
    
    if (!archivo) return;
    if (!currentUserId) {
        alert("Error: No hay usuario autenticado");
        return;
    }

    const formData = new FormData();
    formData.append('file', archivo);

    try {
        const res = await fetch(`/upload/${currentUserId}`, { 
            method: 'POST', 
            body: formData 
        });

        if (!res.ok) {
            const errorData = await res.json();
            alert(errorData.detail || "Error al procesar el archivo");
            return;
        }

        const data = await res.json();
        
        document.getElementById('results-area').style.display = 'block';
        document.getElementById('stat-time').innerText = data.stats_globales.tiempo;
        document.getElementById('stat-dist').innerText = data.stats_globales.distancia_total;
        document.getElementById('stat-speed').innerText = data.stats_globales.ritmo_medio;
        document.getElementById('stat-ele').innerText = data.stats_globales.desnivel;
        
        renderizarMapa(data.path);
        renderizarGrafica(data);
        renderizarRecordsSesion(data.records);
        
        fileInput.value = '';
        console.log("✅ Archivo procesado");
    } catch (error) {
        console.error("❌ Error:", error);
        alert("Error al procesar el archivo");
    }
}

// ==========================================
// RENDERIZAR MAPA
// ==========================================

function renderizarMapa(path) {
    if (map) map.remove();
    map = L.map('map').setView(path[0], 13);
    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png').addTo(map);
    L.polyline(path, {color: '#00d2ff', weight: 5}).addTo(map);
    map.fitBounds(L.polyline(path).getBounds());
}

// ==========================================
// RENDERIZAR GRÁFICA
// ==========================================

function renderizarGrafica(data) {
    const ctx = document.getElementById('combinedChart').getContext('2d');
    if (combinedChart) combinedChart.destroy();

    combinedChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.hrs.map((_, i) => i),
            datasets: [
                {
                    label: 'Pulsaciones (ppm)',
                    data: data.hrs,
                    borderColor: '#f87171',
                    backgroundColor: 'rgba(248, 113, 113, 0.1)',
                    fill: true,
                    yAxisID: 'y',
                    pointRadius: 0,
                    borderWidth: 2
                },
                {
                    label: 'Altitud (m)',
                    data: data.altitudes,
                    borderColor: '#94a3b8',
                    borderDash: [5, 5],
                    fill: false,
                    yAxisID: 'y1',
                    pointRadius: 0,
                    borderWidth: 1
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { labels: { color: 'white' } } },
            scales: {
                y: { 
                    type: 'linear', position: 'left',
                    title: { display: true, text: 'PPM', color: '#f87171' },
                    grid: { color: 'rgba(255,255,255,0.05)' },
                    ticks: { color: 'white' }
                },
                y1: { 
                    type: 'linear', position: 'right',
                    title: { display: true, text: 'Altitud', color: '#94a3b8' },
                    grid: { display: false },
                    ticks: { color: 'white' }
                },
                x: { display: false }
            }
        }
    });
}

// ==========================================
// RENDERIZAR RÉCORDS DE SESIÓN
// ==========================================

function renderizarRecordsSesion(records) {
    const container = document.getElementById('session-records');
    if (!container) return;
    
    container.innerHTML = records.map(r => {
        const m = Math.floor(r.tiempo_segundos / 60);
        const s = Math.floor(r.tiempo_segundos % 60);
        
        let cardStyle, textClass, badge, icon;
        
        if (r.es_nuevo_record) {
            cardStyle = 'background: linear-gradient(135deg, #FFD700 0%, #FFA500 100%); border: 3px solid #FFD700; box-shadow: 0 0 30px rgba(255, 215, 0, 0.8); animation: pulse-glow 2s ease-in-out infinite;';
            textClass = 'text-dark fw-bold';
            badge = '<span class="badge bg-dark text-warning ms-2">🏆 NUEVO RÉCORD</span>';
            icon = '🔥';
        } else {
            cardStyle = 'background: rgba(255, 255, 255, 0.05); border: 1px solid rgba(255,255,255,0.1);';
            textClass = '';
            badge = '';
            icon = '';
        }
            
        return `
            <div class="p-3 mb-2 rounded" style="${cardStyle}">
                <div class="d-flex justify-content-between align-items-center">
                    <span class="fw-bold ${textClass}" style="font-size: 1.1rem;">
                        ${icon} ${r.distancia_nombre}
                    </span>
                    <span class="h4 mb-0 ${textClass}">${m}:${s.toString().padStart(2,'0')}</span>
                </div>
                ${r.es_nuevo_record ? `
                    <div class="mt-2">${badge}
                        ${r.diferencia_con_anterior ? 
                            `<div class="small text-dark fw-bold mt-1">⚡ Mejoraste ${r.diferencia_con_anterior.toFixed(1)}s</div>` : 
                            '<div class="small text-dark fw-bold mt-1">¡Tu primer récord en esta distancia!</div>'
                        }
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

// ==========================================
// PREDICCIONES - TARJETAS EN GRID
// ==========================================

async function loadPredictions() {
    try {
        const res = await fetch(`/records/${currentUserId}`);
        const records = await res.json();
        const predictionsList = document.getElementById('predictions-list');
        
        if (records.length === 0) {
            predictionsList.innerHTML = '<p class="text-center opacity-50 mt-4">Necesitas subir al menos una sesión para generar predicciones</p>';
            return;
        }
        
        const todasLasDistancias = ['100m', '200m', '500m', '1km', '2km', '5km', '10km', '15km', '21km', '42km'];
        const distanciasEnMetros = {
            '100m': 100, '200m': 200, '500m': 500, '1km': 1000, 
            '2km': 2000, '5km': 5000, '10km': 10000, '15km': 15000, 
            '21km': 21097, '42km': 42195
        };
        
        // PASO 1: Calcular TODAS las predicciones y promedios
        const prediccionesPromedio = {};
        
        todasLasDistancias.forEach(distanciaObjetivo => {
            const predicciones = [];
            
            records.forEach(record => {
                const distMetrosObjetivo = distanciasEnMetros[distanciaObjetivo];
                const distMetrosBase = distanciasEnMetros[record.distancia_nombre];
                const tiempoPredicho = record.tiempo_segundos * Math.pow(distMetrosObjetivo / distMetrosBase, 1.06);
                
                predicciones.push(tiempoPredicho);
            });
            
            const promedio = predicciones.reduce((sum, t) => sum + t, 0) / predicciones.length;
            prediccionesPromedio[distanciaObjetivo] = promedio;
        });
        
        // PASO 2: Generar tarjetas en grid de 3 columnas
        let html = '<div class="row g-4">';
        
        todasLasDistancias.forEach((distancia) => {
            const tieneRecord = records.find(r => r.distancia_nombre === distancia);
            const promedio = prediccionesPromedio[distancia];
            
            // Formatear tiempo promedio
            const h = Math.floor(promedio / 3600);
            const m = Math.floor((promedio % 3600) / 60);
            const s = Math.floor(promedio % 60);
            
            let tiempoFormateado;
            if (h > 0) {
                tiempoFormateado = `${h}:${m.toString().padStart(2,'0')}:${s.toString().padStart(2,'0')}`;
            } else if (m > 0) {
                tiempoFormateado = `${m}:${s.toString().padStart(2,'0')}`;
            } else {
                tiempoFormateado = `0:${s.toString().padStart(2,'0')}`;
            }
            
            // Calcular ritmo
            const ritmoMin = promedio / (distanciasEnMetros[distancia] / 1000) / 60;
            const ritmoM = Math.floor(ritmoMin);
            const ritmoS = Math.floor((ritmoMin - ritmoM) * 60);
            
            // Determinar estilo según si tiene récord
            let cardClass = 'card-glass';
            let badge = '';
            let comparacionHTML = '';
            
            if (tieneRecord) {
                const tiempoReal = tieneRecord.tiempo_segundos;
                const diferencia = tiempoReal - promedio;
                
                cardClass += ' border border-success';
                badge = '<span class="badge bg-success">✓ Récord actual</span>';
                
                // Formatear récord actual
                const hReal = Math.floor(tiempoReal / 3600);
                const mReal = Math.floor((tiempoReal % 3600) / 60);
                const sReal = Math.floor(tiempoReal % 60);
                
                let tiempoRealFormateado;
                if (hReal > 0) {
                    tiempoRealFormateado = `${hReal}:${mReal.toString().padStart(2,'0')}:${sReal.toString().padStart(2,'0')}`;
                } else if (mReal > 0) {
                    tiempoRealFormateado = `${mReal}:${sReal.toString().padStart(2,'0')}`;
                } else {
                    tiempoRealFormateado = `0:${sReal.toString().padStart(2,'0')}`;
                }
                
                // INVERTIDO: Menor tiempo = Mejor
                if (Math.abs(diferencia) < 5) {
                    comparacionHTML = `
                        <div class="mt-3 pt-3 border-top border-success">
                            <div class="small text-success fw-bold mb-1">🏆 Tu récord: ${tiempoRealFormateado}</div>
                            <div class="small text-success">✓ Predicción muy precisa</div>
                        </div>
                    `;
                } else if (diferencia < 0) {
                    // Tiempo real MENOR que predicción = VAS MÁS RÁPIDO (BUENO)
                    comparacionHTML = `
                        <div class="mt-3 pt-3 border-top border-warning">
                            <div class="small text-warning fw-bold mb-1">🏆 Tu récord: ${tiempoRealFormateado}</div>
                            <div class="small text-warning">⚡ ¡Vas ${Math.abs(diferencia).toFixed(0)}s más rápido que la predicción!</div>
                        </div>
                    `;
                } else {
                    // Tiempo real MAYOR que predicción = Puedes mejorar
                    comparacionHTML = `
                        <div class="mt-3 pt-3 border-top border-info">
                            <div class="small text-info fw-bold mb-1">🏆 Tu récord: ${tiempoRealFormateado}</div>
                            <div class="small text-info">📈 Potencial de mejora: ${Math.abs(diferencia).toFixed(0)}s más rápido</div>
                        </div>
                    `;
                }
            } else {
                badge = '<span class="badge bg-info">🎯 Objetivo</span>';
            }
            
            html += `
                <div class="col-lg-4 col-md-6">
                    <div class="${cardClass} p-4 h-100">
                        <div class="d-flex justify-content-between align-items-start mb-3">
                            <h4 class="text-white mb-0 fw-bold">${distancia}</h4>
                            ${badge}
                        </div>
                        <div class="mb-2">
                            <div class="h2 text-white mb-1">${tiempoFormateado}</div>
                            <div class="text-white-50 small">Predicción promedio</div>
                        </div>
                        <div class="d-flex align-items-center text-white-50">
                            <span class="me-2">⚡</span>
                            <span>${ritmoM}:${ritmoS.toString().padStart(2,'0')} min/km</span>
                        </div>
                        ${comparacionHTML}
                    </div>
                </div>
            `;
        });
        
        html += '</div>';
        predictionsList.innerHTML = html;
        
    } catch (e) {
        console.error("Error cargando predicciones:", e);
        alert("Error al cargar las predicciones");
    }
}

console.log("✅ Script completamente cargado");