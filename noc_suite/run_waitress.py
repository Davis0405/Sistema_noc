from waitress import serve
from noc_suite.wsgi import application
import os

if __name__ == '__main__':
    # Puedes cambiar el puerto si quieres, el 8000 es el estándar
    port = int(os.environ.get("PORT", 8000))
    print(f"Iniciando Servidor de Producción en puerto {port}...")

    # threads=6 permite atender a varias personas a la vez
    serve(application, host='0.0.0.0', port=port, threads=6)