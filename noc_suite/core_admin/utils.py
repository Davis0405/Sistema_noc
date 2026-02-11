import os
import sys
import subprocess
import psutil
import signal
from django.conf import settings

# Archivo donde guardaremos el ID del proceso para no perderlo
PID_FILE = os.path.join(settings.BASE_DIR, 'tsm_exporter.pid')
LOG_FILE = os.path.join(settings.BASE_DIR, 'tsm_exporter.log')

class ServiceManager:
    def is_running(self):
        """Verifica si el proceso está realmente vivo"""
        if not os.path.exists(PID_FILE):
            return False

        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            
            # Verificar si el proceso con ese PID existe y es python
            process = psutil.Process(pid)
            return process.is_running()
        except (ValueError, psutil.NoSuchProcess, FileNotFoundError):
            # Si el archivo existe pero el proceso no, borramos el archivo
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            return False

    def start(self):
        """Inicia el servicio en segundo plano"""
        if self.is_running():
            return False, "El servicio ya está corriendo."

        try:
            # Comando: python manage.py run_tsm_exporter
            cmd = [sys.executable, 'manage.py', 'run_tsm_exporter']
            
            # Abrir archivo de logs
            log = open(LOG_FILE, 'a')

            # Lanzar proceso independiente (creationflags es vital para Windows)
            # CREATE_NEW_CONSOLE permite que viva aunque cierres el server web
            process = subprocess.Popen(
                cmd,
                stdout=log,
                stderr=log,
                cwd=settings.BASE_DIR,
                creationflags=subprocess.CREATE_NEW_CONSOLE if os.name == 'nt' else 0
            )

            # Guardar PID
            with open(PID_FILE, 'w') as f:
                f.write(str(process.pid))

            return True, f"Servicio iniciado con PID {process.pid}"
        except Exception as e:
            return False, str(e)

    def stop(self):
        """Detiene el servicio"""
        if not os.path.exists(PID_FILE):
            return False, "El servicio no parece estar corriendo."

        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())

            parent = psutil.Process(pid)
            
            # Matar procesos hijos también (importante en Windows)
            for child in parent.children(recursive=True):
                child.kill()
            parent.kill()

            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            
            return True, "Servicio detenido correctamente."
        except psutil.NoSuchProcess:
            if os.path.exists(PID_FILE):
                os.remove(PID_FILE)
            return True, "El proceso ya no existía (se limpió el archivo PID)."
        except Exception as e:
            return False, str(e)

    def restart(self):
        self.stop()
        return self.start()