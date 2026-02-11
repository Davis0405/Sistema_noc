import re

class TSMCheckerService:
    # Copiamos tus constantes de JS y las convertimos a Diccionarios de Python
    AM_SERVERS = {
        'APPLCAPUPG18': '10.138.7.201', 'T24Prod01SE01': '10.138.7.201', 'T24Prod02SE01': '10.138.7.201',
        'T24Prod01SE02': '10.138.7.202', 'T24Prod02SE02': '10.138.7.202', 'APPLCAPUPG19': '10.138.7.202',
        'APPLCAPUPG20': '10.138.7.203', 'T24Prod01SE03': '10.138.7.203', 'T24Prod02SE03': '10.138.7.203',
        'APPLCAPUPG21': '10.138.7.204', 'T24Prod01SE04': '10.138.7.204', 'T24Prod02SE04': '10.138.7.204',
        'APPLCAPUPG02': '10.138.7.205', 'T24Prod01SE05': '10.138.7.205', 'T24Prod02SE05': '10.138.7.205',
        'APPLCAPUPG23': '10.138.7.206', 'T24Prod01SE06': '10.138.7.206', 'T24Prod02SE06': '10.138.7.206',
        'APPLCAPUPG22': '10.138.7.210', 'T24Prod01SE10': '10.138.7.210', 'T24Prod02SE10': '10.138.7.210',
        'T24Prod01F': '10.138.7.227', 'APPLCAPUPG08': '10.138.7.229', 'T24Prod01H': '10.138.7.229',
        'T24Prod02H': '10.138.7.229'
        # ... (Puedes agregar el resto de la lista AM aquí)
    }

    PM_SERVERS = {
        'APPLCAPUPG24': '10.138.7.245',
    'T24Prod01R1A': '10.138.7.245',
    'T24Prod02R1A': '10.138.7.245',
    'APPLCAPUPG06': '10.138.7.227',
    'T24Prod01F': '10.138.7.227',
    'T24Prod02F': '10.138.7.227',
    'APPLCAPUPG34': '10.138.7.253',
    'T24Prod01BB': '10.138.7.253',
    'T24Prod02BB': '10.138.7.253',
    'APPLCAPUPG07': '10.138.7.228',
    'T24Prod01G': '10.138.7.228',
    'T24Prod02G': '10.138.7.228',
    'APPLCAPUPG26': '10.137.7.247',
    'T24Prod01R1C': '10.137.7.247',
    'T24Prod02R1C': '10.137.7.247',
    'APPLCAPUPG11': '10.138.7.240',
    'T24Prod01K': '10.138.7.240',
    'T24Prod02K': '10.138.7.240',
    'APPLCAPUPG35': '10.138.7.213',
    'T24Prod01EE': '10.138.7.213',
    'T24Prod02EE': '10.138.7.213',
    'APPLCAPUPG36': '10.138.7.214',
    'T24Prod01FF': '10.138.7.214',
    'T24Prod02FF': '10.138.7.214',
    'APPLCAPUPG05': '10.138.7.234',
    'T24Prod01E': '10.138.7.234',
    'T24Prod02E': '10.138.7.234',
    'APPLCAPUPG27': '10.138.7.248',
    'T24Prod01R2A': '10.138.7.248',
    'T24Prod02R2A': '10.138.7.248',
    'APPLCAPUPG10': '10.138.7.235',
    'T24Prod01J': '10.138.7.235',
    'T24Prod02J': '10.138.7.235',
    'APPLCAPUPG30': '10.138.7.237',
    'T24Prod01R2B': '10.138.7.237',
    'T24Prod02R2B': '10.138.7.237',
    'APPLCAPUPG37': '10.138.7.215',
    'T24Prod01GG': '10.138.7.215',
    'T24Prod02GG': '10.138.7.215',
    'APPLCAPUPG38': '10.138.7.216',
    'T24Prod01HH': '10.138.7.216',
    'T24Prod02HH': '10.138.7.216',
    'APPLCAPUPG15': '10.138.7.244',
    'T24Prod01O': '10.138.7.244',
    'T24Prod02O': '10.138.7.244',
    'APPLCAPUPG29': '10.138.7.251',
    'T24Prod01CRP': '10.138.7.251',
    'T24Prod02CRP': '10.138.7.251',
    'APPLCAPUPG25': '10.138.7.246',
    'T24Prod01R1B': '10.138.7.246',
    'T24Prod02R1B': '10.138.7.246',
    'APPLCAPUPG12': '10.138.7.241',
    'T24Prod01L': '10.138.7.241',
    'T24Prod02L': '10.138.7.241',
    'APPLCAPUPG03': '10.138.7.238',
    'T24Prod01C': '10.138.7.238',
    'T24Prod02C': '10.138.7.238',
    'APPLCAPUPG13': '10.138.7.242',
    'T24Prod01M': '10.138.7.242',
    'T24Prod02M': '10.138.7.242',
    'APPLCAPUPG14': '10.138.7.243',
    'T24Prod01N': '10.138.7.243',
    'T24Prod02N': '10.138.7.243',
    'APPLCAPUPG08': '10.138.7.229',
    'T24Prod01H': '10.138.7.229',
    'T24Prod02H': '10.138.7.229',
    'APPLCAPUPG33': '10.138.7.252',
    'T24Prod01AA': '10.138.7.252',
    'T24Prod02AA': '10.138.7.252',
    'APPLCAPUPG28': '10.138.7.230',
    'T24Prod01R3A': '10.138.7.230',
    'T24Prod02R3A': '10.138.7.230',
    'APPLCAPUPG31': '10.138.7.249',
    'T24Prod01R3B': '10.138.7.249',
    'T24Prod02R3B': '10.138.7.249',
    'APPLCAPUPG22': '10.138.7.210',
    'T24Prod01SE10': '10.138.7.210',
    'T24Prod02SE10': '10.138.7.210',
    'PRODAPPL1AGCORP': '10.138.3.121',
    'T24Prod01AG7': '10.138.3.121',
    'T24Prod02AG7': '10.138.3.121',
    'PRODAPPL2AGCORP': '10.138.3.122',
    'T24Prod01AG8': '10.138.3.122',
    'T24Prod02AG8': '10.138.3.122',
    'PRODAPPL2AGEN': '10.138.3.102',
    'T24Prod01AG2': '10.138.3.102',
    'T24Prod02AG2': '10.138.3.102',
    'PRODAPPL5AGEN': '10.138.3.105',
    'T24Prod01AG5': '10.138.3.105',
    'T24Prod02AG5': '10.138.3.105',
    'PRODAPPL3AGEN': '10.138.3.103',
    'T24Prod01AG3': '10.138.3.103',
    'T24Prod02AG3': '10.138.3.103',
    'PRODAPPL6AGEN': '10.138.3.106',
    'T24Prod01AG6': '10.138.3.106',
    'T24Prod02AG6': '10.138.3.106',
    'PRODAPPL3AGCORP': '10.138.3.123',
    'T24Prod01AG9': '10.138.3.123',
    'T24Prod02AG9': '10.138.3.123',
    'APPLCAPUPG23': '10.138.7.206',
    'T24Prod01SE06': '10.138.7.206',
    'T24Prod02SE06': '10.138.7.206',
    'PRODAPPL1AGEN': '10.138.3.101',
    'T24Prod01AG1': '10.138.3.101',
    'T24Prod02AG1': '10.138.3.101',
    'PRODAPPL4AGCORP': '10.138.3.124',
    'T24Prod01AG10': '10.138.3.124',
    'T24Prod02AG10': '10.138.3.124',
    'APPLCAPUPG21': '10.138.7.204',
    'T24Prod01SE04': '10.138.7.204',
    'T24Prod02SE04': '10.138.7.204',
    'APPLCAPUPG02': '10.138.7.205',
    'T24Prod01SE05': '10.138.7.205',
    'T24Prod02SE05': '10.138.7.205',
    'APPLCAPUPG18': '10.138.7.201',
    'T24Prod01SE01': '10.138.7.201',
    'T24Prod02SE01': '10.138.7.201',
    'APPLCAPUPG19': '10.138.7.202',
    'T24Prod01SE02': '10.138.7.202',
    'T24Prod02SE02': '10.138.7.202',
    'APPLCAPUPG20': '10.138.7.203',
    'T24Prod01SE03': '10.138.7.203',
    'T24Prod02SE03': '10.138.7.203',
    'APPLCAPUPG01': '10.138.7.236',
    'T24Prod01A': '10.138.7.236',
    'T24Prod02A': '10.138.7.236',
    'DSSIMWS02UP': '10.138.7.222',
    'DSSIMWS03': '10.138.7.223',
    'DSSIMWS04': '10.138.7.224',
    'DSSIMWS05': '10.138.7.225',
    'DSSIMWS06': '10.138.7.220',
    'DSSIMWS07': '10.138.7.221',
    'DSSIMWS11': '10.138.7.190',
    'DSSIMWS12': '10.138.7.191',
    'DSSIMWS10': '10.138.7.217',  
    'PRODAPPL4AGEN': '10.138.3.104',  
    'T24Prod01AG4': '10.138.3.104',
    'T24Prod02AG4': '10.138.3.104',
    }

    def process_file(self, file_obj, period):
        # 1. Leer el archivo
        try:
            # Decodificamos el archivo a string
            content = file_obj.read().decode('utf-8')
        except UnicodeDecodeError:
            # Intentar con latin-1 si utf-8 falla (común en windows)
            content = file_obj.read().decode('latin-1')

        lines = content.split('\n')
        servers_found = set()

        # 2. Extraer servidores (Lógica idéntica a tu JS regex)
        # Tu regex era /"([^"]+)"/
        regex = r'"([^"]+)"'

        for index, line in enumerate(lines):
            if index < 3: continue # Saltamos cabeceras igual que en tu JS
            
            match = re.search(regex, line)
            if match:
                servers_found.add(match.group(1))

        # 3. Comparar
        expected_dict = self.AM_SERVERS if period == 'AM' else self.PM_SERVERS
        expected_names = set(expected_dict.keys())
        
        missing_names = list(expected_names - servers_found)
        
        # Preparar reporte de faltantes con sus IPs
        missing_report = []
        for name in missing_names:
            missing_report.append({
                'name': name,
                'ip': expected_dict.get(name, 'N/A')
            })

        return {
            'complete': len(missing_report) == 0,
            'missing': missing_report,
            'total_expected': len(expected_names),
            'found_count': len(expected_names) - len(missing_report),
            'period': period
        }