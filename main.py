import os
import httpx
from fastapi import FastAPI, Request, Response, HTTPException
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="Copiloto Financiero WhatsApp MVP")

WHATSAPP_VERIFY_TOKEN = os.getenv("WHATSAPP_VERIFY_TOKEN", "mi_token_secreto_123")
META_ACCESS_TOKEN = "EAAOl65mcRj0BR89TM2UJBkA0RqpW3IZBoxvl4ItRkWZAA433jS7FnKs11cbgMMGN89K63zMJn474F7fEjSqWCD3LO2EaPVdHTfkp65B99Bn5MybC9FgCKaZCQRp4PUHSxqaspMZA9D512nug7u4BqMJoctlZC1rGI1IGGC6acbO8T83PpTDZAw9pzzgydPcs5FvMuY05RvYvbXoFNNPvmmJel23kBTf8oqVAFK2uGV8zZBWPeYB299FV6l7iXYO12J1ylylEXcQqbZC5YQydGcJa"
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
    
    # Imprimimos TODO para ver qué llega exactamente
    print("\n🚀 🔥 ¡NUEVO EVENTO DESDE WHATSAPP! 🔥 🚀")
    print(body)
    print("========================================================\n")
    
    try:
        # Navegamos por el JSON con cuidado
        if "entry" in body and body["entry"]:
            entry = body["entry"][0]
            if "changes" in entry and entry["changes"]:
                change = entry["changes"][0]["value"]
                
                # Verificamos si hay mensajes
                if "messages" in change and change["messages"]:
                    message_data = change["messages"][0]
                    remitente_telefono = message_data.get("from")
                    tipo_mensaje = message_data.get("type")

                    if tipo_mensaje == "text":
                        texto_usuario = message_data["text"]["body"]
                        print(f"💬 Texto extraído: '{texto_usuario}' de {remitente_telefono}")
                        
                        mensaje_respuesta = f"🤖 ¡Hola! Soy tu Copiloto Financiero. Recibí tu mensaje: '{texto_usuario}'"
                        await enviar_mensaje_whatsapp(remitente_telefono, mensaje_respuesta)
                    else:
                        print(f"⚠️ Recibido mensaje de tipo: {tipo_mensaje}. Aún no lo proceso.")
                else:
                    print("ℹ️ El evento no contiene mensajes (probablemente es un status).")
    except Exception as e:
        print(f"❌ Error procesando el mensaje: {e}")

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
        print("✉️ Respuesta de Meta al responder:", response.json())
