// Nodos del DOM
const btnHablar = document.getElementById('btn-hablar');
const statusIndicator = document.getElementById('status-indicator');
const chatBox = document.getElementById('chat-box');
const chatContainer = document.getElementById('chat-container');

// Configuración de Web Speech API
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const miReconocimiento = SpeechRecognition ? new SpeechRecognition() : null;
const miSintetizador = window.speechSynthesis;

// Inicializar y validar soporte
if (!miReconocimiento) {
    agregarMensaje("Error Crítico: Tu navegador no soporta Reconocimiento de Voz.", "error");
    btnHablar.disabled = true;
    btnHablar.style.opacity = "0.5";
} else {
    miReconocimiento.lang = 'es-CO'; // Español Colombia (o es-ES)
    miReconocimiento.continuous = false; // Se detiene al dejar de hablar
    miReconocimiento.interimResults = false; // Solo traemos el resultado final

    // Eventos de Reconocimiento
    miReconocimiento.onstart = function () {
        setEstadoUI("Escuchando...", "listening");
    };

    miReconocimiento.onspeechend = function () {
        // Al terminar de hablar, frenamos e indicamos que estamos procesando
        miReconocimiento.stop();
        setEstadoUI("Procesando...", "");
    };

    miReconocimiento.onresult = function (event) {
        // Extraemos el texto captado
        const transcripcion = event.results[0][0].transcript;
        agregarMensaje(transcripcion, "user");
        enviarComando(transcripcion);
    };

    miReconocimiento.onerror = function (event) {
        setEstadoUI("Inactivo", "");
        agregarMensaje("Ocurrió un error al escuchar: " + event.error, "error");
    };
}

// Escuchador de evento del Botón Principal
btnHablar.addEventListener('click', escuchar);

/**
 * Función que inicializa el micrófono
 */
function escuchar() {
    if (miReconocimiento) {
        // Si Greqo está hablando y el usuario aprieta volver a hablar, abortamos el habla
        if (miSintetizador.speaking) {
            miSintetizador.cancel();
        }
        miReconocimiento.start();
    }
}

/**
 * Función para imprimir mensajes en el log tipo Chat
 * @param {string} texto El contenido a inyectar en pantalla
 * @param {string} tipo La clase CSS que define si es 'user', 'greqo' o 'error'
 */
function agregarMensaje(texto, tipo) {
    const div = document.createElement('div');
    div.className = `message ${tipo}`;
    div.textContent = texto;
    chatBox.appendChild(div);
    // Auto-scroll al fondo de la consola
    chatContainer.scrollTop = chatContainer.scrollHeight;
}

/**
 * Administra las clases CSS para las animaciones y colores de la UI
 * @param {string} texto Mensaje descriptivo superior ("Inactivo", "Escuchando", etc)
 * @param {string} estado Puede ser 'listening', 'speaking', o ''
 */
function setEstadoUI(texto, estado) {
    statusIndicator.textContent = texto;

    // Limpiamos las clases animadas tanto del indicador como del botón
    statusIndicator.className = "";
    btnHablar.className = "btn-ia";

    if (estado === "listening") {
        btnHablar.classList.add("listening");
        statusIndicator.classList.add("listening-text");
    } else if (estado === "speaking") {
        btnHablar.classList.add("speaking");
        statusIndicator.classList.add("speaking-text");
    }
}

/**
 * Envía el comando al endpoint real usando la API indicada
 * @param {string} texto El string de voz reconocido
 */
async function enviarComando(texto) {

    const url = "https://greqo-production.up.railway.app/comando"; "; // 🔥 TU URL DE RAILWAY
    const token = "x9#Greqo!2026_secure";

    try {
        const response = await fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + token
            },
            body: JSON.stringify({
                texto: texto
            })
        });

        const data = await response.json();

        manejarRespuesta(data);

    } catch (error) {
        console.error("Error:", error);
        hablar("Hubo un error conectando con el servidor.");
    }
}

/**
 * Identifica la acción dictaminada por el backend y procede
 * @param {object} json Objeto respuesta ({ accion, respuesta, app })
 */
function manejarRespuesta(json) {
    if (json.accion === "hablar") {
        agregarMensaje(json.respuesta, "greqo");
        hablar(json.respuesta);
    } else if (json.accion === "abrir_app" || json.accion === "llamar") {
        const accionStr = json.accion.replace('_', ' ').toUpperCase();
        agregarMensaje(`Ejecutando protocolo: [${accionStr}] ${json.app ? '- ' + json.app : ''}`, "greqo");
        hablar("Entendido, ejecutando la acción solicitada.");
    } else {
        const errorMsg = "Acción del sistema no reconocida por Greqo.";
        agregarMensaje(errorMsg, "error");
        hablar("Lo siento, la estructura del servidor no es reconocida.");
    }
}

/**
 * Sintetiza un string y lo emite en voz alta
 * @param {string} texto Mensaje que el asistente dirá
 */
function hablar(texto) {
    if (!miSintetizador) {
        agregarMensaje("Error: Tu navegador no soporta Sintesis de Voz", "error");
        return;
    }

    const locucion = new SpeechSynthesisUtterance(texto);
    locucion.lang = 'es-CO'; // Idioma Español
    locucion.pitch = 0.9; // Tono levemente más grave estilo IA
    locucion.rate = 1.0; // Velocidad normal

    // Al iniciar que se prenda azul
    locucion.onstart = () => {
        setEstadoUI("Respondiendo...", "speaking");
    };

    // Al terminar, vuelve a inactivo
    locucion.onend = () => {
        setEstadoUI("Inactivo", "");
    };

    // Al haber error o cancelarse
    locucion.onerror = () => {
        setEstadoUI("Inactivo", "");
    };

    miSintetizador.speak(locucion);
}

/**
 * [HELPER PROTOTIPO] Crea respuestas fake basadas en las palabras clave del usuario
 */
function procesarComandoOffline(cmd) {
    const texto = cmd.toLowerCase();
    if (texto.includes("hola") || texto.includes("saludos")) {
        return "Hola señor. Sistemas en línea y operando. ¿En qué le puedo asistir?";
    }
    if (texto.includes("estado") || texto.includes("cómo estás")) {
        return "Todos los sistemas funcionan a capacidad óptima, mis protocolos están listos.";
    }
    if (texto.includes("clima")) {
        return "Actualmente carezco de conexión al servidor meteorológico, pero calculo buenas probabilidades.";
    }
    return "He procesado el siguiente comando e intentado enviarlo: " + cmd;
}
