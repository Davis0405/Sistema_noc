from django.core.management.base import BaseCommand
from prometheus_client import start_http_server, Gauge
import requests
import time
import logging
from datetime import datetime
from typing import Dict, Set, List
from tsm_monitor.config import SERVERS_AM, SERVERS_PM

# Configuración
API_URL = "http://10.138.11.185:8077/api/v1/status"
SCRAPE_INTERVAL = 30
SERVICE_RETENTION_TIME = 120
EXPORTER_PORT = 9182

logger = logging.getLogger(__name__)

# --- DEFINICIÓN DE MÉTRICAS (Igual que el script original) ---
service_status = Gauge(
    'service_status', 
    'Estado del servicio (1=RUNNING, 0=DOWN)',
    ['service_name', 'server', 'recid']
)

service_last_seen = Gauge(
    'service_last_seen_timestamp',
    'Timestamp de última vez que se vio el servicio activo',
    ['service_name', 'server', 'recid']
)

services_total = Gauge('services_total', 'Total de servicios monitoreados')
services_running = Gauge('services_running', 'Total de servicios corriendo')
services_down = Gauge('services_down', 'Total de servicios caídos')

# Métricas de Turnos
shift_services_expected = Gauge('shift_services_expected', 'Cantidad de servicios esperados por turno', ['shift'])
shift_services_active = Gauge('shift_services_active', 'Cantidad de servicios activos del turno', ['shift'])
shift_services_missing = Gauge('shift_services_missing', 'Cantidad de servicios faltantes del turno', ['shift'])
shift_service_status = Gauge('shift_service_status', 'Estado del servicio esperado', ['shift', 'server'])
shift_compliance_percentage = Gauge('shift_compliance_percentage', 'Porcentaje de cumplimiento del turno', ['shift'])

class ServiceMonitor:
    def __init__(self, retention_time: int, servers_pm: List[str], servers_am: List[str]):
        self.known_services: Dict[str, dict] = {}
        self.retention_time = retention_time
        self.servers_pm = set(servers_pm)
        self.servers_am = set(servers_am)
    
    def get_service_key(self, service: dict) -> str:
        return f"{service['Current_Service']}_{service['Server']}_{service['RECID']}"
    
    def get_current_shift(self) -> str:
        hour = datetime.now().hour
        
        # Lógica Nueva:
        # AM es de 06:00 a 19:59 (6 AM a 8 PM)
        # PM es el resto (20:00 a 05:59)
        if 6 <= hour < 20:
            return "AM"
        else:
            return "PM"
    
    def get_expected_servers(self, shift: str) -> Set[str]:
        return self.servers_pm if shift == "PM" else self.servers_am
    
    def check_shift_compliance(self, active_services: Set[str]):
        current_shift = self.get_current_shift()
        expected = self.get_expected_servers(current_shift)
        
        # Extraer servidores activos con TSM en estado RUNNING
        active_servers = set()
        for service_data in self.known_services.values():
            if service_data['is_active'] and service_data['status'] == 'RUNNING':
                active_servers.add(service_data['server'])
        
        # Calcular métricas
        expected_count = len(expected)
        active_count = len(active_servers.intersection(expected))
        missing_count = expected_count - active_count
        compliance = (active_count / expected_count * 100) if expected_count > 0 else 100
        
        # Actualizar métricas globales del turno
        shift_services_expected.labels(shift=current_shift).set(expected_count)
        shift_services_active.labels(shift=current_shift).set(active_count)
        shift_services_missing.labels(shift=current_shift).set(missing_count)
        shift_compliance_percentage.labels(shift=current_shift).set(compliance)
        
        # Actualizar estado individual de cada servidor esperado
        for server in expected:
            is_active = server in active_servers
            shift_service_status.labels(
                shift=current_shift,
                server=server
            ).set(1 if is_active else 0)
        
        return {
            'shift': current_shift,
            'compliance': compliance,
            'missing': missing_count
        }
    
    def update_services(self, api_response: dict):
        current_time = datetime.now()
        active_services: Set[str] = set()
        
        # Procesar servicios activos del API
        for service in api_response.get('body', []):
            key = self.get_service_key(service)
            active_services.add(key)
            
            self.known_services[key] = {
                'service_name': service['Current_Service'],
                'server': service['Server'],
                'recid': service['RECID'],
                'status': service['Status'],
                'last_seen': current_time,
                'is_active': True
            }
            
            # Actualizar métricas individuales
            service_status.labels(
                service_name=service['Current_Service'],
                server=service['Server'],
                recid=service['RECID']
            ).set(1 if service['Status'] == 'RUNNING' else 0)
            
            service_last_seen.labels(
                service_name=service['Current_Service'],
                server=service['Server'],
                recid=service['RECID']
            ).set(current_time.timestamp())
        
        # Marcar servicios ausentes como DOWN y limpiar antiguos
        services_to_remove = []
        for key, service_data in self.known_services.items():
            if key not in active_services:
                time_since_seen = (current_time - service_data['last_seen']).total_seconds()
                
                if time_since_seen < self.retention_time:
                    service_data['is_active'] = False
                    service_status.labels(
                        service_name=service_data['service_name'],
                        server=service_data['server'],
                        recid=service_data['recid']
                    ).set(0)
                else:
                    services_to_remove.append(key)
        
        # Limpiar métricas de servicios eliminados
        for key in services_to_remove:
            service_data = self.known_services[key]
            try:
                service_status.remove(
                    service_data['service_name'],
                    service_data['server'],
                    service_data['recid']
                )
                service_last_seen.remove(
                    service_data['service_name'],
                    service_data['server'],
                    service_data['recid']
                )
            except:
                pass # Ya fue eliminado
            del self.known_services[key]
        
        # Actualizar contadores totales
        running = sum(1 for s in self.known_services.values() if s['is_active'] and s['status'] == 'RUNNING')
        down = sum(1 for s in self.known_services.values() if not s['is_active'])
        
        services_total.set(len(self.known_services))
        services_running.set(running)
        services_down.set(down)
        
        # Verificar Turnos
        return self.check_shift_compliance(active_services)

def fetch_services(url: str) -> dict:
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Error al consultar API: {e}")
        return {'body': []}

class Command(BaseCommand):
    help = 'Corre el Prometheus Exporter completo para TSM'

    def handle(self, *args, **options):
        # Iniciar servidor HTTP
        start_http_server(EXPORTER_PORT)
        self.stdout.write(self.style.SUCCESS(f'Exporter TSM iniciado en puerto {EXPORTER_PORT}'))
        
        monitor = ServiceMonitor(
            retention_time=SERVICE_RETENTION_TIME,
            servers_pm=SERVERS_PM,
            servers_am=SERVERS_AM
        )

        while True:
            try:
                api_data = fetch_services(API_URL)
                stats = monitor.update_services(api_data)
                
                # Log opcional para ver que está vivo
                logger.info(f"Turno {stats['shift']}: {stats['compliance']:.1f}% cumplimiento. Running: {services_running._value.get()}")
                
                time.sleep(SCRAPE_INTERVAL)
                
            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING("Deteniendo exporter..."))
                break
            except Exception as e:
                logger.error(f"Error crítico en loop: {e}")
                time.sleep(SCRAPE_INTERVAL)