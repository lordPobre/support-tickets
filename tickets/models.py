import uuid
from django.db import models
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings


class Company(models.Model):
    name = models.CharField(max_length=200, verbose_name="Nombre")
    slug = models.SlugField(unique=True, help_text="Identificador único para la URL del portal público")
    contact_email = models.EmailField(verbose_name="Email de contacto")
    logo = models.FileField(upload_to="companies/logos/", blank=True, null=True)
    phone = models.CharField(max_length=30, blank=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, verbose_name="Activa")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    def open_tickets_count(self):
        return self.tickets.exclude(status__is_closed_state=True).count()

    class Meta:
        verbose_name = "Empresa"
        verbose_name_plural = "Empresas"
        ordering = ["name"]


class CompanyUser(models.Model):
    """A contact/user belonging to a company. Created by admin."""
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE,
        related_name="users", verbose_name="Empresa"
    )
    name = models.CharField(max_length=200, verbose_name="Nombre completo")
    email = models.EmailField(verbose_name="Email")
    position = models.CharField(max_length=100, blank=True, verbose_name="Cargo")
    is_active = models.BooleanField(default=True, verbose_name="Activo")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.company.name})"

    class Meta:
        verbose_name = "Usuario de empresa"
        verbose_name_plural = "Usuarios de empresa"
        ordering = ["company", "name"]
        unique_together = [("company", "email")]


class TicketStatus(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default="#6B7280", help_text="Color hex, ej: #EF4444")
    order = models.PositiveIntegerField(default=0)
    is_closed_state = models.BooleanField(default=False, help_text="¿Este estado cierra el ticket?")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Estado"
        verbose_name_plural = "Estados"
        ordering = ["order"]


class TicketPriority(models.Model):
    name = models.CharField(max_length=100, verbose_name="Nombre")
    slug = models.SlugField(unique=True)
    color = models.CharField(max_length=7, default="#6B7280", help_text="Color hex")
    icon = models.CharField(max_length=50, default="circle", help_text="Nombre del ícono Heroicon")
    order = models.PositiveIntegerField(default=0)
    sla_hours = models.PositiveIntegerField(default=24, help_text="Horas de SLA para esta prioridad")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Prioridad"
        verbose_name_plural = "Prioridades"
        ordering = ["order"]


def ticket_token():
    return uuid.uuid4().hex[:12].upper()


class Ticket(models.Model):
    CATEGORY_SOFTWARE = "software"
    CATEGORY_HARDWARE = "hardware"
    CATEGORY_EMAIL = "email"
    CATEGORY_CHOICES = [
        (CATEGORY_SOFTWARE, "Software"),
        (CATEGORY_HARDWARE, "Hardware"),
        (CATEGORY_EMAIL, "Email / Correo"),
    ]
    CATEGORY_COLORS = {
        CATEGORY_SOFTWARE: "#6366F1",
        CATEGORY_HARDWARE: "#F59E0B",
        CATEGORY_EMAIL:    "#10B981",
    }
    CATEGORY_ICONS = {
        CATEGORY_SOFTWARE: "💻",
        CATEGORY_HARDWARE: "🖥️",
        CATEGORY_EMAIL:    "✉️",
    }

    token = models.CharField(max_length=12, unique=True, default=ticket_token, editable=False)
    company = models.ForeignKey(
        Company, on_delete=models.CASCADE, related_name="tickets", verbose_name="Empresa"
    )
    company_user = models.ForeignKey(
        CompanyUser, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets", verbose_name="Usuario solicitante"
    )
    subject = models.CharField(max_length=300, verbose_name="Asunto")
    description = models.TextField(verbose_name="Descripción")

    # Category
    category = models.CharField(
        max_length=20, choices=CATEGORY_CHOICES,
        default=CATEGORY_SOFTWARE, verbose_name="Categoría de soporte"
    )

    # Contact info (kept for fallback / non-registered users)
    requester_name = models.CharField(max_length=200, verbose_name="Nombre del solicitante")
    requester_email = models.EmailField(verbose_name="Email del solicitante")

    # Classification
    status = models.ForeignKey(
        TicketStatus, on_delete=models.SET_NULL, null=True,
        related_name="tickets", verbose_name="Estado"
    )
    priority = models.ForeignKey(
        TicketPriority, on_delete=models.SET_NULL, null=True, blank=True,
        related_name="tickets", verbose_name="Prioridad"
    )

    # Billing
    assigned_value = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True,
        verbose_name="Valor asignado (CLP)",
        help_text="Valor cobrable por este ticket de soporte"
    )
    is_billed = models.BooleanField(default=False, verbose_name="Facturado")

    # Dates
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    # Internal notes
    internal_notes = models.TextField(blank=True, verbose_name="Notas internas")

    def __str__(self):
        return f"[{self.token}] {self.subject}"

    def get_category_color(self):
        return self.CATEGORY_COLORS.get(self.category, "#6B7280")

    def get_category_icon(self):
        return self.CATEGORY_ICONS.get(self.category, "")

    def close(self):
        self.closed_at = timezone.now()
        self.save()

    def send_confirmation_email(self):
        subject_line = f"Ticket #{self.token} recibido — {self.subject}"
        message = (
            f"Hola {self.requester_name},\n\n"
            f"Hemos recibido tu solicitud de soporte.\n\n"
            f"Ticket: #{self.token}\n"
            f"Categoría: {self.get_category_display()}\n"
            f"Asunto: {self.subject}\n"
            f"Empresa: {self.company.name}\n\n"
            f"Puedes seguir el estado de tu ticket en:\n"
            f"{settings.SITE_URL}/portal/{self.company.slug}/ticket/{self.token}/\n\n"
            f"Gracias,\nEquipo de Soporte"
        )
        send_mail(subject_line, message, settings.DEFAULT_FROM_EMAIL, [self.requester_email], fail_silently=True)

    def send_status_update_email(self, new_status_name):
        subject_line = f"Actualización ticket #{self.token} — {new_status_name}"
        message = (
            f"Hola {self.requester_name},\n\n"
            f"El estado de tu ticket ha cambiado a: {new_status_name}\n\n"
            f"Ticket: #{self.token}\n"
            f"Asunto: {self.subject}\n\n"
            f"Puedes ver los detalles en:\n"
            f"{settings.SITE_URL}/portal/{self.company.slug}/ticket/{self.token}/\n\n"
            f"Gracias,\nEquipo de Soporte"
        )
        send_mail(subject_line, message, settings.DEFAULT_FROM_EMAIL, [self.requester_email], fail_silently=True)

    class Meta:
        verbose_name = "Ticket"
        verbose_name_plural = "Tickets"
        ordering = ["-created_at"]


class TicketAttachment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="attachments")
    file = models.FileField(upload_to="attachments/%Y/%m/")
    original_name = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.original_name

    class Meta:
        verbose_name = "Adjunto"
        verbose_name_plural = "Adjuntos"


class TicketComment(models.Model):
    ticket = models.ForeignKey(Ticket, on_delete=models.CASCADE, related_name="comments")
    author_name = models.CharField(max_length=200)
    author_email = models.EmailField()
    is_staff = models.BooleanField(default=False)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_internal = models.BooleanField(default=False, help_text="Nota interna (no visible al cliente)")

    def __str__(self):
        return f"Comentario de {self.author_name} en {self.ticket.token}"

    class Meta:
        verbose_name = "Comentario"
        verbose_name_plural = "Comentarios"
        ordering = ["created_at"]