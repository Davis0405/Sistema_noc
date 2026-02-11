from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .services import TSMMonitorLogic

@login_required
def tsm_monitor_dashboard(request):
    logic = TSMMonitorLogic()
    data = logic.analyze_status()
    
    context = {
        'data': data
    }
    return render(request, 'tsm_monitor/dashboard.html', context)