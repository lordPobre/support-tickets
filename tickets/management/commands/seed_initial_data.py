from django.core.management.base import BaseCommand
from tickets.models import TicketStatus, TicketPriority


class Command(BaseCommand):
    help = "Crea los estados y prioridades iniciales del sistema"

    def handle(self, *args, **kwargs):
        # Statuses
        statuses = [
            {"name": "Abierto", "slug": "open", "color": "#3B82F6", "order": 1, "is_closed_state": False},
            {"name": "En Progreso", "slug": "in-progress", "color": "#F59E0B", "order": 2, "is_closed_state": False},
            {"name": "Esperando Cliente", "slug": "waiting-client", "color": "#8B5CF6", "order": 3, "is_closed_state": False},
            {"name": "Resuelto", "slug": "resolved", "color": "#10B981", "order": 4, "is_closed_state": True},
            {"name": "Cerrado", "slug": "closed", "color": "#6B7280", "order": 5, "is_closed_state": True},
        ]

        for data in statuses:
            obj, created = TicketStatus.objects.get_or_create(slug=data["slug"], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Estado creado: {obj.name}"))
            else:
                self.stdout.write(f"  · Estado ya existe: {obj.name}")

        # Priorities
        priorities = [
            {"name": "Baja", "slug": "low", "color": "#10B981", "order": 1, "sla_hours": 72},
            {"name": "Media", "slug": "medium", "color": "#F59E0B", "order": 2, "sla_hours": 24},
            {"name": "Alta", "slug": "high", "color": "#EF4444", "order": 3, "sla_hours": 8},
            {"name": "Crítica", "slug": "critical", "color": "#7C3AED", "order": 4, "sla_hours": 2},
        ]

        for data in priorities:
            obj, created = TicketPriority.objects.get_or_create(slug=data["slug"], defaults=data)
            if created:
                self.stdout.write(self.style.SUCCESS(f"  ✓ Prioridad creada: {obj.name}"))
            else:
                self.stdout.write(f"  · Prioridad ya existe: {obj.name}")

        self.stdout.write(self.style.SUCCESS("\n¡Datos iniciales cargados correctamente!"))
