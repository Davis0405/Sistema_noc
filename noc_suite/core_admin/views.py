from django.shortcuts import render, redirect
from django.contrib.auth.decorators import user_passes_test
from django.contrib import messages
from .utils import ServiceManager

# Solo administradores pueden ver esto
@user_passes_test(lambda u: u.is_superuser)
def admin_dashboard(request):
    manager = ServiceManager()
    is_running = manager.is_running()
    
    context = {
        'is_running': is_running,
        'service_name': 'TSM Prometheus Exporter'
    }
    return render(request, 'core_admin/dashboard.html', context)

@user_passes_test(lambda u: u.is_superuser)
def service_action(request, action):
    manager = ServiceManager()
    
    if action == 'start':
        success, msg = manager.start()
    elif action == 'stop':
        success, msg = manager.stop()
    elif action == 'restart':
        success, msg = manager.restart()
    else:
        success, msg = False, "Acción no válida"

    if success:
        messages.success(request, msg)
    else:
        messages.error(request, msg)
        
    return redirect('admin_dashboard')