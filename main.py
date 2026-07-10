import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Copiloto Financiero WhatsApp MVP")

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mi_token_secreto_123")
META_ACCESS_TOKEN = "EAAOl65mcRj0BR49fBvqYmYCxrnVwgioQ6iQMvxi3aTSsTaV1IV9VALw9ZB101d8gOR0ZAHu5Is6EGlnGcyklpb7IZBOYFwHj9c6Muz1y460kSY1TG3aKFIKUwyPvwxZCfKeUALi5vpcZBIhlFqlFDJS0kQ5WzZCSWB27dZBVzZCMUFAXY0yvKt3MjWwdcbgV5xq8ZBsHWoQfptgm5gfoZCZBeMtkZAXADXjGyFaMiNHkRm4OXP6RS7kD91Sp4OFpVQaiu1TSfjXEQ2V9kvtmdtavm3bX"
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
    
    print("\n🚀 🔥 ¡ALERTA! ACABA DE ENTRAR UN MENSAJE DESDE WHATSAPP! 🔥 🚀")
    print("DATOS RECIBIDOS EN CRUDO:", body)
    print("========================================================\n")
    
    try:
        if body.get("entry") and body["entry"][0].get("changes"):
            change = body["entry"][0]["changes"][0]["value"]
            if "messages" not in change:
                return {"status": "success", "reason": "No es un mensaje (puede ser estado de entrega)"}
                
            message_data = change["messages"][0]
            remitente_telefono = message_data["from"]
            tipo_mensaje = message_data["type"]

            if tipo_mensaje == "text":
                texto_usuario = message_data["text"]["body"]
                print(f"💬 Texto del usuario extraído con éxito: '{texto_usuario}'")
                
                mensaje_respuesta = f"🤖 ¡Hola! Soy tu Copiloto Financiero. Tu mensaje llegó perfecto a mi servidor. Escribiste: '{texto_usuario}'"
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
