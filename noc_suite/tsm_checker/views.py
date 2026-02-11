from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import TSMCheckerService

@login_required
def tsm_checker_view(request):
    context = {
        'result': None,
        'period': 'AM' # Default
    }

    if request.method == 'POST' and request.FILES.get('csv_file'):
        period = request.POST.get('period', 'AM')
        uploaded_file = request.FILES['csv_file']
        
        service = TSMCheckerService()
        result = service.process_file(uploaded_file, period)
        
        context['result'] = result
        context['period'] = period
    
    return render(request, 'tsm_checker/index.html', context)