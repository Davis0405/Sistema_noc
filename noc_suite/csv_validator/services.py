import os
import time
from datetime import datetime
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class CSVValidatorService:
    def __init__(self, custom_date=None):
        # NOTA: En producción, esto debería ir en variables de entorno o base de datos
        self.base_path = settings.CSV_BASE_PATH
        
        if custom_date:
            try:
                datetime.strptime(custom_date, "%Y-%m-%d")
                self.current_date = custom_date
            except ValueError:
                self.current_date = datetime.now().strftime("%Y-%m-%d")
        else:
            self.current_date = datetime.now().strftime("%Y-%m-%d")
        
        # Tu diccionario de asociaciones
        self.asociaciones = {
            "02": "Guayacán", "04": "Coosajo", "05": "Unión Popular",
            "06": "UPA", "07": "Gualán", "08": "Cobán", "09": "Cootecu",
            "11": "Tonantel", "12": "Horizontes", "13": "Copecom",
            "14": "Bienestar", "15": "Moyután", "16": "Chiquimuljá",
            "17": "Cosami", "18": "Salcajá", "19": "Acredicom",
            "20": "Colua", "21": "Coosanjer", "22": "Coopsama",
            "23": "San Pedro Soloma", "24": "Encarnación",
            "25": "Ecosaba", "26": "Yaman Kutx", "27": "Cotoneb",
            "55": "Fenacoac", "56": "Credipyme"
        }
        
        self.archivos_criticos = [
            "DatosTransacciones", "DatosColocaciones", "DatosTransacInter",
            "DatosCaptaciones", "DatosClientes", "DatosCtasInternas"
        ]
        self.min_size_kb = 5

    def get_file_path(self, asociacion_id, archivo_nombre):
        correlativo = f"1{asociacion_id}"
        filename = f"{self.current_date}_{correlativo}_{archivo_nombre}.csv"
        return os.path.join(self.base_path, f"{asociacion_id}$", filename)
    
    def validate_file(self, file_path):
        try:
            if os.path.exists(file_path):
                size_bytes = os.path.getsize(file_path)
                size_kb = size_bytes / 1024
                return True, size_kb
            return False, 0
        except Exception as e:
            logger.error(f"Error checking file {file_path}: {str(e)}")
            return False, 0
    
    def validate_all_files(self):
        # Lógica principal de validación
        validation_results = []
        
        for asociacion_id, asociacion_name in self.asociaciones.items():
            for archivo in self.archivos_criticos:
                file_path = self.get_file_path(asociacion_id, archivo)
                exists, size_kb = self.validate_file(file_path)
                status = 1 if exists and size_kb >= self.min_size_kb else 0
                
                result = {
                    'asociacion_id': asociacion_id,
                    'asociacion_name': asociacion_name,
                    'file_name': archivo,
                    'file_path': file_path,
                    'exists': exists,
                    'size_kb': round(size_kb, 2),
                    'status': status,
                    'status_text': 'OK' if status == 1 else ('Faltante' if not exists else 'Tamaño irregular')
                }
                validation_results.append(result)
                
        return validation_results

    def get_summary_stats(self, results):
        total_files = len(results)
        files_ok = len([r for r in results if r['status'] == 1])
        files_error = total_files - files_ok
        
        # Agrupar por cooperativa
        cooperativas_data = {}
        for result in results:
            coop_id = result['asociacion_id']
            if coop_id not in cooperativas_data:
                cooperativas_data[coop_id] = {
                    'name': result['asociacion_name'],
                    'files': [],
                    'ok_count': 0,
                    'error_count': 0
                }
            cooperativas_data[coop_id]['files'].append(result)
            if result['status'] == 1:
                cooperativas_data[coop_id]['ok_count'] += 1
            else:
                cooperativas_data[coop_id]['error_count'] += 1
                
        return {
            "total_files": total_files,
            "files_ok": files_ok,
            "files_error": files_error,
            "success_rate": round((files_ok / total_files) * 100, 2) if total_files > 0 else 0,
            "cooperativas_data": cooperativas_data
        }