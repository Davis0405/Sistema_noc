import json
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Especialista, Turno
from datetime import datetime, timedelta

def calendario_view(request):
    # Enviar lista de especialistas al sidebar para arrastrarlos
    especialistas = Especialista.objects.all()
    return render(request, 'calendario/main.html', {'especialistas': especialistas})

def api_eventos(request):
    # Obtener todos los turnos para pintarlos en el calendario
    turnos = Turno.objects.all()
    eventos = []
    for turno in turnos:
        # Formato: nombre|área|horario
        horario_texto = f"{turno.horario_inicio.strftime('%H:%M')}-{turno.horario_fin.strftime('%H:%M')}"
        area = turno.especialista.area if turno.especialista.area else 'Sin área'
        eventos.append({
            'id': turno.id,
            'title': f"{turno.especialista.nombre}|{area}|{horario_texto}",
            'start': f"{turno.fecha}T{turno.horario_inicio}",
            'end': f"{turno.fecha}T{turno.horario_fin}",
            'color': turno.especialista.color,
            'backgroundColor': turno.especialista.color,
            'allDay': False
        })
    return JsonResponse(eventos, safe=False)

@csrf_exempt # Simplificamos para el ejemplo, en prod usar CSRF token en JS
def api_guardar_evento(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        
        # Datos que vienen del frontend
        especialista_id = data.get('especialista_id')
        fecha_str = data.get('fecha') # YYYY-MM-DD
        horario = data.get('horario') # "07:00-16:00" o "09:00-18:00"
        
        start_time, end_time = horario.split('-')
        
        especialista = Especialista.objects.get(id=especialista_id)
        
        # Crear o Actualizar turno
        Turno.objects.update_or_create(
            especialista=especialista,
            fecha=fecha_str,
            defaults={
                'horario_inicio': start_time,
                'horario_fin': end_time
            }
        )
        
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@csrf_exempt
def api_eliminar_evento(request):
    """Elimina un turno basado en su ID"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            turno_id = data.get('id')
            
            # Buscamos y borramos
            Turno.objects.get(id=turno_id).delete()
            
            return JsonResponse({'status': 'success'})
        except Turno.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Turno no encontrado'}, status=404)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
    return JsonResponse({'status': 'error'}, status=400)

