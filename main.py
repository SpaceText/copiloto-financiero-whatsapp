import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Copiloto Financiero WhatsApp MVP")

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mi_token_secreto_123")

# 🚨 AQUÍ PEGAREMOS LAS LLAVES NUEVAS EN EL PASO 3
META_ACCESS_TOKEN = "TU_TOKEN_TEMPORAL_AQUÍ"
PHONE_NUMBER_ID = "1097267976812653"

@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = request.query_params
    mode = params.get("hub.mode")
    token = params.get("hub.verify_token")
    challenge = params.get("hub.challenge")

    if mode == "subscribe" and token == WHATSAPP_VERIFY_TOKEN:
        print("✅ CONEXIÓN EXITOSA: Meta ha validado el Webhook.")
        return Response(content=challenge, media_type="text/plain")
    raise HTTPException(status_code=403, detail="Token inválido")

@app.post("/webhook")
async def recibir_mensaje_whatsapp(request: Request):
    body = await request.json()
    
    # 📢 ESTE ES EL GRAN GRITO EN LA CONSOLA
    print("\n🚀 🔥 ¡ALERTA! ACABA DE ENTRAR UN MENSAJE DESDE WHATSAPP! 🔥 🚀")
    print("DATOS RECIBIDOS EN CRUDO:", body)
    print("========================================================\n")
    
    try:
        if body.get("entry") and body["entry"][0].get("changes"):
            change = body["entry"][0]["changes"][0]["value"]
            if "messages" not in change:
                return {"status": "success", "reason": "No es un mensaje (puede ser un estado de entrega)"}
                
            message_data = change["messages"][0]
            remitente_telefono = message_data["from"]
            tipo_mensaje = message_data["type"]

            if tipo_mensaje == "text":
                texto_usuario = message_data["text"]["body"]
                print(f"💬 Texto del usuario extraído con éxito: '{texto_usuario}'")
                
                # Intentar responderle automáticamente al usuario
                mensaje_respuesta = f"🤖 ¡Hola! Soy tu Copiloto Financiero. Tu mensaje de texto llegó perfecto a mi servidor. Escribiste: '{texto_usuario}'"
                await enviar_mensaje_whatsapp(remitente_telefono, mensaje_respuesta)
    except Exception as e:
        print("❌ Error procesando el mensaje:", str(e))

    return {"status": "success"}

async def enviar_mensaje_whatsapp(telefono_destino: str, texto: str):
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
        response = await client.post(url, json=payload, headers=headers)
        print("✉️ Respuesta de Meta al intentar responder:", response.json())
