import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

# ── Configuración SMTP desde .env ──
SMTP_HOST = os.getenv('SMTP_HOST', 'smtp.gmail.com')
SMTP_PORT = int(os.getenv('SMTP_PORT', 587))
SMTP_USER = os.getenv('SMTP_USER', '')
SMTP_PASSWORD = os.getenv('SMTP_PASSWORD', '')
SMTP_FROM = os.getenv('SMTP_FROM', SMTP_USER)


def enviar_email(destinatario: str, asunto: str, mensaje_html: str) -> dict:
    """
    Envía un email vía SMTP.
    Retorna {'ok': True} o {'ok': False, 'error': '...'}.
    """
    if not SMTP_USER or not SMTP_PASSWORD:
        return {'ok': False, 'error': 'SMTP no configurado en .env (SMTP_USER / SMTP_PASSWORD)'}

    try:
        msg = MIMEMultipart('alternative')
        msg['From'] = SMTP_FROM
        msg['To'] = destinatario
        msg['Subject'] = asunto

        parte_html = MIMEText(mensaje_html, 'html')
        msg.attach(parte_html)

        context = ssl.create_default_context()
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
            server.starttls(context=context)
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.sendmail(SMTP_FROM, destinatario, msg.as_string())

        return {'ok': True}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def enviar_whatsapp(telefono: str, mensaje: str) -> dict:
    """
    Envía un mensaje de WhatsApp usando WhatsApp Cloud API (Meta).
    Requiere en .env:
      WA_PHONE_NUMBER_ID  — ID del número de teléfono en Meta Business
      WA_ACCESS_TOKEN     — Token de acceso permanente o de prueba
    """
    import json
    from urllib import request as req
    from urllib.error import URLError

    phone_number_id = os.getenv('WA_PHONE_NUMBER_ID', '')
    access_token = os.getenv('WA_ACCESS_TOKEN', '')

    if not phone_number_id or not access_token:
        return {'ok': False, 'error': 'WhatsApp no configurado — falta WA_PHONE_NUMBER_ID / WA_ACCESS_TOKEN en .env'}

    # Limpiar el número: dejar solo dígitos
    tel = ''.join(filter(str.isdigit, telefono))
    if not tel.startswith('57'):
        tel = f'57{tel}'

    url = f'https://graph.facebook.com/v18.0/{phone_number_id}/messages'
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    payload = json.dumps({
        "messaging_product": "whatsapp",
        "to": tel,
        "type": "text",
        "text": { "body": mensaje }
    }).encode('utf-8')

    try:
        r = req.Request(url, data=payload, headers=headers, method='POST')
        with req.urlopen(r) as resp:
            resultado = json.loads(resp.read().decode('utf-8'))
            return {'ok': True, 'id': resultado.get('messages', [{}])[0].get('id', '')}
    except URLError as e:
        error_body = ''
        if hasattr(e, 'read'):
            try:
                error_body = e.read().decode('utf-8')
            except Exception:
                pass
        return {'ok': False, 'error': f'Error WhatsApp API: {str(e)} | {error_body}'}
    except Exception as e:
        return {'ok': False, 'error': str(e)}


def generar_mensaje_factura_envio(pedido: dict, cliente: dict) -> tuple:
    """
    Genera el asunto y cuerpo HTML para la notificación de factura
    cuando el pedido está en camino.
    Retorna (asunto, html, texto_whatsapp).
    """
    nombre_cliente = f"{cliente.get('cli_nombre', '')} {cliente.get('cli_apellido', '')}".strip() or 'Cliente'
    pedido_id = pedido.get('ped_id', '')
    total = pedido.get('ped_total', 0)
    metodo = pedido.get('ped_metodo_pago', '')
    fecha = pedido.get('ped_fecha', '')

    asunto = f"🧾 Factura {pedido_id} — Pedido en camino — San Diego Distribuidora"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #059669; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">San Diego Distribuidora</h1>
        </div>
        <div style="background-color: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 8px 8px;">
            <p style="font-size: 16px; color: #334155;">Hola <strong>{nombre_cliente}</strong>,</p>
            <p style="font-size: 14px; color: #475569;">Tu pedido <strong>{pedido_id}</strong> ya está en camino y te compartimos los detalles de tu factura:</p>

            <div style="background-color: white; border: 1px solid #e2e8f0; border-radius: 12px; padding: 20px; margin: 20px 0;">
                <table style="width: 100%; font-size: 14px; color: #334155;">
                    <tr>
                        <td style="padding: 8px 0; color: #94a3b8;">Pedido</td>
                        <td style="padding: 8px 0; font-weight: bold; text-align: right;">{pedido_id}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #94a3b8;">Fecha</td>
                        <td style="padding: 8px 0; font-weight: bold; text-align: right;">{fecha}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #94a3b8;">Método de pago</td>
                        <td style="padding: 8px 0; font-weight: bold; text-align: right;">{metodo}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px 0; color: #94a3b8;">Estado</td>
                        <td style="padding: 8px 0; font-weight: bold; text-align: right; color: #059669;">🚚 En camino</td>
                    </tr>
                    <tr style="border-top: 2px solid #e2e8f0;">
                        <td style="padding: 12px 0; font-size: 16px; color: #334155;">Total</td>
                        <td style="padding: 12px 0; font-size: 16px; font-weight: bold; text-align: right; color: #059669;">${float(total):,.2f}</td>
                    </tr>
                </table>
            </div>

            <p style="font-size: 14px; color: #475569;">Gracias por tu preferencia. Si tienes alguna duda, contáctanos.</p>
            <p style="font-size: 12px; color: #94a3b8; margin-top: 30px;">San Diego Distribuidora · Cali, Colombia</p>
        </div>
    </div>
    """

    texto_whatsapp = (
        f"🧾 *Factura {pedido_id} — San Diego Distribuidora*\n\n"
        f"Hola {nombre_cliente},\n"
        f"tu pedido {pedido_id} por *${float(total):,.2f}* ya está en camino 🚚\n\n"
        f"Gracias por tu compra."
    )

    return asunto, html, texto_whatsapp


def generar_mensaje_pedido_listo(pedido: dict, cliente: dict) -> tuple:
    """
    Genera el asunto y cuerpo HTML/texto para la notificación.
    Retorna (asunto, html, texto_whatsapp).
    """
    nombre_cliente = f"{cliente.get('cli_nombre', '')} {cliente.get('cli_apellido', '')}".strip() or 'Cliente'
    pedido_id = pedido.get('ped_id', '')
    total = pedido.get('ped_total', 0)

    asunto = f"✅ Pedido {pedido_id} listo para enviar — San Diego Distribuidora"

    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <div style="background-color: #1d4ed8; padding: 20px; text-align: center; border-radius: 8px 8px 0 0;">
            <h1 style="color: white; margin: 0; font-size: 24px;">San Diego Distribuidora</h1>
        </div>
        <div style="background-color: #f8fafc; padding: 30px; border: 1px solid #e2e8f0; border-top: none; border-radius: 0 0 8px 8px;">
            <p style="font-size: 16px; color: #334155;">Hola <strong>{nombre_cliente}</strong>,</p>
            <p style="font-size: 14px; color: #475569;">Tu pedido <strong>{pedido_id}</strong> por un total de <strong>${float(total):,.2f}</strong> ya está listo para ser enviado.</p>
            <div style="background-color: #dcfce7; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center;">
                <p style="font-size: 14px; color: #166534; font-weight: bold; margin: 0;">✅ Pago verificado — Pedido listo para envío</p>
            </div>
            <p style="font-size: 14px; color: #475569;">Gracias por confiar en nosotros.</p>
            <p style="font-size: 12px; color: #94a3b8; margin-top: 30px;">San Diego Distribuidora · Cali, Colombia</p>
        </div>
    </div>
    """

    texto_whatsapp = (
        f"✅ *San Diego Distribuidora*\n\n"
        f"Hola {nombre_cliente}, tu pedido *{pedido_id}* por *${float(total):,.2f}* "
        f"ya está listo para ser enviado.\n"
        f"¡Gracias por tu compra!"
    )

    return asunto, html, texto_whatsapp
