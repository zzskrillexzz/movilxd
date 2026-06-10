"""
Gestor de ngrok para exponer el backend mediante un túnel público.

Busca ngrok.exe en rutas predecibles, lo inicia como subproceso,
obtiene la URL pública y la mantiene disponible para el resto de la app.
Si ngrok no está instalado, funciona silenciosamente en modo localhost.
"""

import os
import sys
import subprocess
import time
import threading
import json
import urllib.request
import urllib.error
from utils.logger import get_logger

log = get_logger(__name__)

# ── Rutas donde buscar ngrok.exe ──
RUTAS_NGROK = [
    # Junto al backend (empaquetado)
    os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'bin', 'ngrok.exe'),
    # Descargas (desarrollo)
    os.path.join(os.path.expanduser('~'), 'Downloads', 'ngrok_test', 'ngrok.exe'),
    # PATH del sistema
    'ngrok.exe',
]

# Puerto de la API local de ngrok
NGROK_API_PORT = 4040
NGROK_API_URL = f'http://localhost:{NGROK_API_PORT}/api/tunnels'

# Puerto del backend Flask
BACKEND_PORT = int(os.getenv('PORT', 5000))


class NgrokManager:
    def __init__(self):
        self.proceso = None
        self.url_publica = None
        self._detenido = False

    def buscar_ngrok(self):
        """Retorna la ruta de ngrok.exe o None si no se encuentra."""
        for ruta in RUTAS_NGROK:
            if os.path.isfile(ruta):
                log.info("ngrok encontrado en: %s", ruta)
                return ruta
        log.info("ngrok no encontrado — modo localhost")
        return None

    def iniciar(self):
        """
        Busca ngrok.exe y lo inicia como subproceso en background.
        Espera hasta 10 segundos a que la API local responda.
        """
        ruta = self.buscar_ngrok()
        if not ruta:
            self.url_publica = f'http://localhost:{BACKEND_PORT}'
            return False

        try:
            # Iniciar ngrok apuntando al backend
            self.proceso = subprocess.Popen(
                [ruta, 'http', str(BACKEND_PORT)],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
            )
            log.info("ngrok iniciado (PID: %s)", self.proceso.pid)

            # Esperar a que la API local de ngrok esté disponible
            for intento in range(20):
                if self._detenido:
                    return False
                try:
                    resp = urllib.request.urlopen(NGROK_API_URL, timeout=2)
                    data = json.loads(resp.read().decode())
                    túneles = data.get('tunnels', [])
                    for tunel in túneles:
                        addr = tunel.get('config', {}).get('addr', '')
                        if f'localhost:{BACKEND_PORT}' in addr or f'127.0.0.1:{BACKEND_PORT}' in addr:
                            self.url_publica = tunel.get('public_url', '').rstrip('/')
                            break
                    if self.url_publica:
                        log.info("URL pública ngrok: %s", self.url_publica)
                        return True
                except (urllib.error.URLError, json.JSONDecodeError, OSError):
                    time.sleep(0.5)

            log.warning("ngrok iniciado pero no se obtuvo la URL pública en 10s")
            return False

        except Exception as e:
            log.error("Error al iniciar ngrok: %s", e)
            self.url_publica = f'http://localhost:{BACKEND_PORT}'
            return False

    def obtener_url(self):
        """Retorna la URL pública actual (ngrok o localhost)."""
        if self.url_publica:
            return self.url_publica
        return f'http://localhost:{BACKEND_PORT}'

    def detener(self):
        """Detiene el proceso de ngrok."""
        self._detenido = True
        if self.proceso:
            try:
                self.proceso.terminate()
                self.proceso.wait(timeout=3)
                log.info("ngrok detenido")
            except Exception:
                try:
                    self.proceso.kill()
                except Exception:
                    pass
            self.proceso = None

    def refrescar_url(self):
        """
        Vuelve a consultar la API de ngrok para obtener la URL actual.
        Útil si ngrok se reinicia o cambia la URL.
        """
        if not self.proceso:
            return self.obtener_url()
        try:
            resp = urllib.request.urlopen(NGROK_API_URL, timeout=3)
            data = json.loads(resp.read().decode())
            for tunel in data.get('tunnels', []):
                addr = tunel.get('config', {}).get('addr', '')
                if f'localhost:{BACKEND_PORT}' in addr or f'127.0.0.1:{BACKEND_PORT}' in addr:
                    self.url_publica = tunel.get('public_url', '').rstrip('/')
                    break
        except Exception:
            pass
        return self.obtener_url()


# ── Instancia global ──
gestor = NgrokManager()


def iniciar():
    """Función de conveniencia para iniciar ngrok desde app.py."""
    return gestor.iniciar()


def obtener_url_publica():
    """Función de conveniencia para obtener la URL pública."""
    return gestor.obtener_url()


def detener():
    """Función de conveniencia para detener ngrok."""
    gestor.detener()


def refrescar_url():
    """Función de conveniencia para refrescar la URL."""
    return gestor.refrescar_url()
