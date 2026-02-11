import re
from datetime import datetime

class ISO8583ParserService:
    def __init__(self):
        # Esquema técnico para T24 (Tu esquema original)
        self.schema = {
            2: ('LLVAR', 0, "Primary Account Number (PAN)"),
            3: ('FIXED', 6, "Processing Code"),
            4: ('FIXED', 12, "Amount, Transaction"),
            7: ('FIXED', 10, "Transmission Date & Time"),
            11: ('FIXED', 6, "System Trace Audit Number (STAN)"),
            12: ('FIXED', 6, "Time, Local Transaction"),
            13: ('FIXED', 4, "Date, Local Transaction"),
            18: ('FIXED', 4, "Merchant Type (MCC)"),
            22: ('FIXED', 3, "Point of Service Entry Mode"),
            28: ('FIXED', 8, "Amount, Transaction Fee"),
            32: ('LLVAR', 0, "Acquiring Institution ID Code"),
            35: ('LLVAR', 0, "Track 2 Data"),
            37: ('FIXED', 12, "Retrieval Reference Number (RRN)"),
            38: ('FIXED', 6, "Authorization Identification Response"),
            39: ('FIXED', 2, "Response Code"),
            41: ('FIXED', 8, "Card Acceptor Terminal ID"),
            42: ('FIXED', 15, "Card Acceptor Identification Code"),
            43: ('FIXED', 40, "Card Acceptor Name/Location"),
            48: ('LLLVAR', 0, "Additional Data - Private"),
            49: ('FIXED', 3, "Currency Code, Transaction"),
            51: ('FIXED', 3, "Currency Code, Reconciliation"),
            54: ('LLLVAR', 0, "Additional Amounts"),
            62: ('LLLVAR', 0, "Reserved Private"),
            63: ('LLLVAR', 0, "Reserved Private"),
            102: ('LLVAR', 0, "Account Identification 1"),
            103: ('LLVAR', 0, "Account Identification 2"),
            127: ('LLLVAR', 0, "Reserved Private Use"),
        }
        
        self.response_codes = {
            "00": "Transacción aprobada | Transacción exitosa",
            "01": "Referirse al emisor | Error genérico, se requiere consulta adicional",
            "02": "Número de tarjeta incorrecto | Tarjeta inválida o no reconocida",
            "03": "Comercio no permitido | Transacción no permitida para el comercio o terminal",
            "04": "Retiro excede límite | Límite diario o por transacción excedido",
            "05": "No autorizado | Transacción rechazada por el emisor",
            "12": "Transacción inválida | Datos erróneos o formato inválido",
            "13": "Monto inválido | Monto no válido o fuera de rango",
            "14": "Número de tarjeta inválido | Tarjeta no válida o no existe",
            "30": "Formato de mensaje inválido | Error en el formato ISO 8583",
            "33": "Tarjeta bloqueada | Cuenta o tarjeta bloqueada",
            "34": "Tarjeta no existente | Tarjeta no encontrada en el sistema",
            "41": "Tarjeta retenida | Tarjeta retenida por el ATM o banco",
            "43": "Tarjeta retenida por fraude | Sospecha de fraude",
            "51": "Fondos insuficientes | Saldo insuficiente",
            "54": "Cuenta expirada | Cuenta o tarjeta expirada",
            "55": "PIN incorrecto | PIN ingresado incorrecto",
            "57": "Transacción no permitida a la cuenta",
            "58": "Transacción no permitida al terminal",
            "61": "Excede límite de retiro",
            "62": "Tarjeta restringida",
            "91": "Banco no disponible | Emisor fuera de línea",
            "96": "Error de sistema | Fallo temporal del sistema"
        }
        
        self.mcc_types = {
            "6011": "ATM - Retiro en efectivo",
            "6010": "ATM - Retiro manual",
            "6012": "ATM - Otros servicios"
        }
        
        self.currency_codes = {
            "320": "GTQ - Quetzal Guatemalteco",
            "840": "USD - Dólar Estadounidense",
            "484": "MXN - Peso Mexicano"
        }
        
        self.cooperativas = {
            "22": "Bienestar", "16": "Colua", "21": "Yaman Kutx", "20": "Encarnación",
            "14": "Salcajá", "24": "San Pedro Soloma", "13": "Cosami", "25": "Cotoneb",
            "10": "Acredicom", "23": "Copecom", "15": "Moyután", "08": "Unión Popular",
            "12": "Tonantel", "05": "Horizontes", "04": "Ecosaba", "01": "UPA",
            "03": "Coosajo", "09": "Guayacán", "17": "Chiquimuljá", "19": "Coosanjer",
            "11": "Gualán", "07": "Coopsama", "18": "Cobán", "06": "Cootecu"
        }

    def get_cooperativa(self, pan):
        """Obtiene el nombre de la cooperativa basado en los dígitos 9-10 del PAN"""
        if pan and len(pan) >= 10:
            subbin = pan[8:10]
            return self.cooperativas.get(subbin, f"Desconocida ({subbin})")
        return "N/A"

    def decode_field(self, f_num, val):
        """Decodifica campos específicos con formato legible"""
        if f_num == 2: # PAN
            if len(val) >= 16:
                return f"{val[:6]}******{val[-4:]}"
            return val
        
        if f_num == 4: # Amount
            try:
                amount = float(val) / 100
                return f"Q{amount:,.2f}"
            except: return val
        
        if f_num == 7: # MMDDhhmmss
            try: return f"{val[2:4]}/{val[0:2]} {val[4:6]}:{val[6:8]}:{val[8:10]}"
            except: return val
        
        if f_num == 12: # Time
            try: return f"{val[0:2]}:{val[2:4]}:{val[4:6]}"
            except: return val
        
        if f_num == 13: # Date
            try: return f"{val[2:4]}/{val[0:2]}"
            except: return val
        
        if f_num == 18: return self.mcc_types.get(val, f"MCC {val}")
        
        if f_num == 3: # Proc Code
            tipos = {
                "00": "COMPRA", "01": "RETIRO EFECTIVO", "09": "COMPRA CON CASHBACK",
                "20": "DEVOLUCION", "30": "CONSULTA SALDO", "31": "CONSULTA", "40": "TRANSFERENCIA"
            }
            return tipos.get(val[:2], f"TIPO {val[:2]}")
        
        if f_num == 39: return self.response_codes.get(val, f"CODIGO {val} - DESCONOCIDO")
        
        if f_num == 41 or f_num == 43: return val.strip()
        
        if f_num == 49: return self.currency_codes.get(val, f"Moneda {val}")
        
        if f_num == 54: return self.parse_additional_amounts(val)
        
        if f_num == 127: return f"Private data ({len(val)} chars)"
        
        return val

    def parse_additional_amounts(self, data):
        try:
            amounts = []
            pos = 0
            while pos < len(data):
                if pos + 20 <= len(data):
                    amt_type = data[pos+2:pos+4]
                    sign = data[pos+7:pos+8]
                    amount = data[pos+8:pos+20]
                    
                    amt_val = float(amount) / 100
                    sign_str = "+" if sign == "C" else "-"
                    
                    amt_desc = {"01": "Saldo disponible", "02": "Saldo contable"}.get(amt_type, f"Tipo {amt_type}")
                    amounts.append(f"{amt_desc}: {sign_str}Q{amt_val:,.2f}")
                    pos += 20
                else: break
            return " | ".join(amounts) if amounts else data
        except: return data

    def parse(self, raw):
        """Parse completo de la trama ISO8583. Retorna (data, summary, error)"""
        data = []
        summary = {}
        
        try:
            mti = raw[0:4]
            msg_types = {
                "1200": "Req. Autorización Financiera", "1210": "Resp. Autorización Financiera",
                "1800": "Network Mgmt Req", "1810": "Network Mgmt Resp",
                "1420": "Reverso", "1430": "Resp. Reverso"
            }
            summary['mti'] = mti
            summary['msg_type'] = msg_types.get(mti, "Desconocido")
            
            # Bitmap
            p_bmp_hex = raw[4:20]
            binary = bin(int(p_bmp_hex, 16))[2:].zfill(64)
            
            cursor = 20
            # Bitmap secundario check
            if binary[0] == '1':
                s_bmp_hex = raw[20:36]
                s_binary = bin(int(s_bmp_hex, 16))[2:].zfill(64)
                binary += s_binary
                cursor = 36

            for i, bit in enumerate(binary):
                f_num = i + 1
                if bit == '1' and f_num > 1:
                    if f_num in self.schema:
                        ftype, flen, fname = self.schema[f_num]
                        
                        if ftype == 'FIXED':
                            val = raw[cursor:cursor+flen]
                            cursor += flen
                        elif ftype == 'LLVAR':
                            ll = int(raw[cursor:cursor+2])
                            val = raw[cursor+2:cursor+2+ll]
                            cursor += 2 + ll
                        else: # LLLVAR
                            lll = int(raw[cursor:cursor+3])
                            val = raw[cursor+3:cursor+3+lll]
                            cursor += 3 + lll
                        
                        interpreted = self.decode_field(f_num, val)
                        
                        data.append({
                            "campo": f"DE-{f_num:02d}",
                            "descripcion": fname,
                            "valor": val,
                            "interpretacion": interpreted
                        })
                        
                        # Llenar resumen
                        if f_num == 2: 
                            summary['pan'] = interpreted
                            summary['cooperativa'] = self.get_cooperativa(val)
                        elif f_num == 3: summary['proc_code'] = interpreted
                        elif f_num == 4: summary['amount'] = interpreted
                        elif f_num == 7: summary['datetime'] = interpreted
                        elif f_num == 11: summary['stan'] = val
                        elif f_num == 37: summary['rrn'] = val
                        elif f_num == 39: 
                            summary['response'] = interpreted
                            summary['response_code'] = val
                        elif f_num == 41: summary['terminal'] = val
                        elif f_num == 43: summary['location'] = val
            
            return data, summary, None
            
        except Exception as e:
            return None, None, str(e)

    def extract_tramas_from_log(self, log_content):
        """Extrae tramas ISO 8583 usando Regex"""
        pattern = r'(1[0-9]{3}[^\r\n]{100,})'
        tramas = re.findall(pattern, log_content, re.IGNORECASE)
        # Limpiar
        return [t.strip() for t in tramas if len(t.strip()) > 50]