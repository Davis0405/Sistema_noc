from django.db import models

class Especialista(models.Model):
    AREAS = [
        ('Soporte', 'Soporte'),
        ('Infra', 'Infraestructura'),
        ('BD', 'Base de Datos'),
        ('Seguridad', 'Seguridad'),
    ]
    nombre = models.CharField(max_length=100)
    area = models.CharField(max_length=50, choices=AREAS)
    color = models.CharField(max_length=7, default='#3788d8') # Color para el calendario

    def __str__(self):
        return f"{self.nombre} ({self.area})"

class Turno(models.Model):
    especialista = models.ForeignKey(Especialista, on_delete=models.CASCADE)
    fecha = models.DateField()
    horario_inicio = models.TimeField() # Ej: 07:00
    horario_fin = models.TimeField()    # Ej: 16:00
    
    class Meta:
        unique_together = ('especialista', 'fecha') # Un especialista solo un turno por día

    def __str__(self):
        return f"{self.especialista} - {self.fecha}"