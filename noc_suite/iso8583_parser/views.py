from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import ISO8583ParserService

@login_required
def parser_individual(request):
    context = {}
    if request.method == 'POST':
        trama = request.POST.get('trama', '').strip()
        if trama:
            service = ISO8583ParserService()
            data, summary, error = service.parse(trama)
            
            if error:
                context['error'] = f"Error procesando la trama: {error}"
            else:
                context['data'] = data
                context['summary'] = summary
                context['trama_original'] = trama
    
    return render(request, 'iso8583_parser/individual.html', context)

@login_required
def parser_masivo(request):
    context = {}
    if request.method == 'POST':
        texto_tramas = ""
        
        # Caso 1: Archivo subido
        if 'archivo' in request.FILES:
            archivo = request.FILES['archivo']
            # Intentar decodificar utf-8, si falla usar latin-1
            try:
                texto_tramas = archivo.read().decode('utf-8')
            except:
                texto_tramas = archivo.read().decode('latin-1')

        # Caso 2: Texto pegado
        elif 'texto_tramas' in request.POST:
            texto_tramas = request.POST.get('texto_tramas')
            
        if texto_tramas:
            service = ISO8583ParserService()
            tramas_raw = service.extract_tramas_from_log(texto_tramas)
            
            resultados = []
            contadores = {'aprobadas': 0, 'rechazadas': 0}
            
            for trama in tramas_raw:
                _, summary, _ = service.parse(trama)
                if summary:
                    # Contadores simples
                    code = summary.get('response_code', '')
                    if code == '00':
                        contadores['aprobadas'] += 1
                    else:
                        contadores['rechazadas'] += 1

                    # Limpiar respuesta para la tabla
                    resp_clean = summary.get('response', '').split('|')[0]
                    
                    resultados.append({
                        'mti': summary.get('mti'),
                        'pan': summary.get('pan'),
                        'monto': summary.get('amount'),
                        'respuesta': resp_clean,
                        'codigo': code,
                        'terminal': summary.get('terminal'),
                        'trama_raw': trama[:60] + "..." # Preview
                    })
            
            context['resultados'] = resultados
            context['total_encontradas'] = len(tramas_raw)
            context['contadores'] = contadores

    return render(request, 'iso8583_parser/masivo.html', context)