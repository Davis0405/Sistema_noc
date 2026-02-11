import requests
from datetime import datetime
from .config import SERVERS_AM, SERVERS_PM
from django.conf import settings

API_URL = settings.TSM_API_URL

class TSMMonitorLogic:
    def get_current_shift(self):
        """Determina el turno actual basado en la hora"""
        hour = datetime.now().hour
        
        # Mismo cambio aquí: 6 AM a 8 PM es AM
        if 6 <= hour < 20:
            return "AM"
        else:
            return "PM"

    def get_expected_servers(self, shift):
        return set(SERVERS_PM) if shift == "PM" else set(SERVERS_AM)

    def fetch_data(self):
        """Consulta la API externa"""
        try:
            response = requests.get(API_URL, timeout=5)
            response.raise_for_status()
            return response.json().get('body', [])
        except Exception as e:
            print(f"Error fetching API: {e}")
            return []

    def analyze_status(self):
        """Analiza el estado actual (Snapshot)"""
        services_data = self.fetch_data()
        current_shift = self.get_current_shift()
        expected_servers = self.get_expected_servers(current_shift)
        
        # Filtrar solo los servidores que están RUNNING
        active_servers = set()
        for service in services_data:
            if service.get('Status') == 'RUNNING':
                active_servers.add(service.get('Server'))

        # Comparar
        found_servers = expected_servers.intersection(active_servers)
        missing_servers = expected_servers - active_servers
        
        # Calcular porcentaje
        total_expected = len(expected_servers)
        total_found = len(found_servers)
        compliance = (total_found / total_expected * 100) if total_expected > 0 else 0

        return {
            'shift': current_shift,
            'compliance': round(compliance, 2),
            'total_expected': total_expected,
            'total_found': total_found,
            'missing_count': len(missing_servers),
            'missing_list': sorted(list(missing_servers)),
            'found_list': sorted(list(found_servers))
        }