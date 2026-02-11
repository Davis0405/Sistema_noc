from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from datetime import datetime
from .services import CSVValidatorService

@login_required
def dashboard_view(request):
    # 1. Obtenemos la fecha (por defecto hoy)
    date_param = request.GET.get('date', datetime.now().strftime("%Y-%m-%d"))
    
    # 2. DETECTAR SI EL USUARIO HIZO CLIC EN "EJECUTAR"
    # Buscamos un parámetro 'run' en la URL
    should_run = request.GET.get('run') == 'true'

    context = {
        'date': date_param,
        'has_run': False, # Bandera para saber si mostramos resultados o no
        'results': [],
        'files_ok': 0,
        'files_error': 0,
        'success_rate': 0,
        'cooperativas_data': {}
    }

    # 3. Solo si el usuario pidió correr, ejecutamos la lógica pesada
    if should_run:
        validator = CSVValidatorService(custom_date=date_param)
        results = validator.validate_all_files()
        stats = validator.get_summary_stats(results)
        
        # Actualizamos el contexto con los datos reales
        context.update(stats)
        context['has_run'] = True
        context['results'] = results

    return render(request, 'csv_validator/dashboard.html', context)