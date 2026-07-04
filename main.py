import os
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

# Carga las variables de entorno desde un archivo .env (útil para desarrollo local)
load_dotenv()

# Instancia de la aplicación FastAPI
app = FastAPI(title="Copiloto Financiero WhatsApp MVP")

# Variables de entorno esenciales
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mi_token_secreto_123")

@app.get("/webhook")
async def verificar_webhook(request: Request):
    """
    Endpoint GET: Meta lo utiliza una sola vez (o cuando actualizas la URL) 
    para verificar que eres el dueño de este endpoint.
    """
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    # Verificamos que el modo sea 'subscribe' y el token coincida con el nuestro
    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print("Webhook verificado exitosamente por Meta.")
        # Retornamos el challenge en texto plano como exige la documentación de Meta
        return Response(content=challenge, media_type="text/plain")
    
    # Si el token no coincide, rechazamos la petición
    raise HTTPException(status_code=403, detail="Token de verificación inválido")


@app.post("/webhook")
async def recibir_mensaje_whatsapp(request: Request):
    """
    Endpoint POST: Meta enviará aquí todo el tráfico de WhatsApp 
    (mensajes de texto, imágenes, estados de lectura, etc.).
    """
    body = await request.json()
    @app.post("/webhook")
async def recibir_mensaje_whatsapp(request: Request):
    body = await request.json()
    print("¡ALERTA! Llegó un mensaje de Meta:", body) # <--- ¡ESTA ES LA LÍNEA MÁGICA!

    # ... (el resto de tu código)
    # Imprimimos el JSON entrante en la consola para depuración
    print("=== NUEVO EVENTO RECIBIDO DESDE META ===")
    print(body)
    print("========================================")
    
    # Meta requiere que siempre respondamos con un status 200 (éxito) rápidamente
    return {"status": "success"}
