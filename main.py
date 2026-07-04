import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Copiloto Financiero WhatsApp MVP")

# Variables de entorno y Credenciales Directas
WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mi_token_secreto_123")
# Aquí están tus credenciales para que el bot pueda hablar
META_ACCESS_TOKEN = "EAAOl65mcRj0BR89TM2UJBkA0RqpW3IZBoxvl4ItRkWZAA433jS7FnKs11cbgMMGN89K63zMJn474F7fEjSqWCD3LO2EaPVdHTfkp65B99Bn5MybC9FgCKaZCQRp4PUHSxqaspMZA9D512nug7u4BqMJoctlZC1rGI1IGGC6acbO8T83PpTDZAw9pzzgydPcs5FvMuY05RvYvbXoFNNPvmmJel23kBTf8oqVAFK2uGV8zZBWPeYB299FV6l7iXYO12J1ylylEXcQqbZC5YQydGcJa"
PHONE_NUMBER_ID = "1097267976812653"

@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print("Webhook verificado exitosamente por Meta.")
        return Response(content=challenge, media_type="text/plain")
    
    raise HTTPException(status_code=403, detail="Token de verificación inválido")

@app.post("/webhook")
async def recibir_mensaje_whatsapp(request: Request):
    body = await request.json()
    
    # 1. Filtramos para asegurarnos de que es un mensaje válido
    if not body.get("entry") or not body["entry"][0].get("changes"):
        return {"status": "ignored"}
        
    change = body["entry"][0]["changes"][0]["value"]
    if "messages" not in change:
        return {"status": "ignored"}
        
    message_data = change["messages"][0]
    
    # 2. Extraemos quién nos mandó el mensaje y qué tipo de mensaje es
    remitente_telefono = message_data["from"]
    tipo_mensaje = message_data["type"]

    # 3. Solo respondemos si nos mandaron un texto
    if tipo_mensaje == "text":
        texto_usuario = message_data["text"]["body"]
        print(f"Mensaje extraído: '{texto_usuario}' del número {remitente_telefono}")
        
        # 4. Construimos la respuesta del bot
        mensaje_respuesta = f"¡Hola! Soy tu Copiloto Financiero. Recibí tu mensaje: '{texto_usuario}'. Mi conexión está lista para recibir fotos de tickets."
        
        # 5. Enviamos la respuesta de regreso a Meta
        await enviar_mensaje_whatsapp(remitente_telefono, mensaje_respuesta)

    return {"status": "success"}

async def enviar_mensaje_whatsapp(telefono_destino: str, texto: str):
    """
    Esta función agarra tu token y el ID de teléfono y dispara el mensaje de vuelta a WhatsApp.
    """
    url = f"https://graph.facebook.com/v20.0/{PHONE_NUMBER_ID}/messages"
    
    headers = {
        "Authorization": f"Bearer {META_ACCESS_TOKEN}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "messaging_product": "whatsapp",
        "to": telefono_destino,
        "type": "text",
        "text": {"body": texto}
    }
    
    async with httpx.AsyncClient() as client:
        # Hacemos la petición a los servidores de Meta
        response = await client.post(url, json=payload, headers=headers)
        print("Respuesta de Meta al enviar mensaje:", response.json())
