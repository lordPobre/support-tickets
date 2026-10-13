from django.contrib import admin
from django import forms
from django.utils.html import format_html
from django.db.models import Sum, Count
from django.http import HttpResponse
from django.utils import timezone
from .models import Company, CompanyUser, Ticket, TicketStatus, TicketPriority, TicketAttachment, TicketComment, Equipment


def _generate_billing_pdf(tickets_qs, company_name):
    """Genera un PDF de cobro para los tickets dados. Devuelve bytes."""
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.units import cm
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_RIGHT, TA_LEFT
    import io

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm,
    )

    styles = getSampleStyleSheet()
    brand_color = colors.HexColor("#4F46E5")
    dark = colors.HexColor("#111827")
    muted = colors.HexColor("#6B7280")
    light_bg = colors.HexColor("#F9FAFB")
    border = colors.HexColor("#E5E7EB")

    style_title = ParagraphStyle("title", fontSize=22, textColor=brand_color,
                                  fontName="Helvetica-Bold", spaceAfter=2)
    style_sub = ParagraphStyle("sub", fontSize=11, textColor=dark,
                                fontName="Helvetica-Bold", spaceAfter=2)
    style_meta = ParagraphStyle("meta", fontSize=9, textColor=muted,
                                 fontName="Helvetica")
    style_center = ParagraphStyle("center", fontSize=9, alignment=TA_CENTER,
                                   fontName="Helvetica")
    style_right = ParagraphStyle("right", fontSize=9, alignment=TA_RIGHT,
                                  fontName="Helvetica")
    style_total_label = ParagraphStyle("tlabel", fontSize=12, textColor=dark,
                                        fontName="Helvetica-Bold", alignment=TA_RIGHT)
    style_total_val = ParagraphStyle("tval", fontSize=14, textColor=brand_color,
                                      fontName="Helvetica-Bold", alignment=TA_RIGHT)

    now = timezone.localtime(timezone.now())
    fecha_str = now.strftime("%-d de %B de %Y").replace(
        "January","enero").replace("February","febrero").replace("March","marzo").replace(
        "April","abril").replace("May","mayo").replace("June","junio").replace(
        "July","julio").replace("August","agosto").replace("September","septiembre").replace(
        "October","octubre").replace("November","noviembre").replace("December","diciembre")

    story = []

    # Encabezado
    story.append(Paragraph("Perseus Technology", style_title))
    story.append(Paragraph("Detalle de Cobro — Soporte TI", style_sub))
    story.append(Spacer(1, 0.1*cm))
    story.append(Paragraph(f"Empresa: <b>{company_name}</b>", style_meta))
    story.append(Paragraph(f"Fecha de emisión: {fecha_str}", style_meta))
    story.append(Spacer(1, 0.4*cm))
    story.append(HRFlowable(width="100%", thickness=1.5, color=brand_color))
    story.append(Spacer(1, 0.4*cm))

    # Tabla
    tickets = list(tickets_qs.select_related("status", "priority").order_by("created_at"))
    col_widths = [2.2*cm, 6.8*cm, 3.2*cm, 2.4*cm, 2.4*cm]
    header = [
        Paragraph("<b>Token</b>", style_center),
        Paragraph("<b>Asunto</b>", style_center),
        Paragraph("<b>Categoría</b>", style_center),
        Paragraph("<b>Estado</b>", style_center),
        Paragraph("<b>Valor (CLP)</b>", style_center),
    ]
    data = [header]

    total = 0
    for t in tickets:
        valor = t.assigned_value
        if valor is not None:
            total += valor
            valor_str = f"$ {int(valor):,}".replace(",", ".")
        else:
            valor_str = "—"

        cat_display = {
            "software": "Software",
            "hardware": "Hardware",
            "email": "Email",
        }.get(t.category, t.category)

        estado_str = t.status.name if t.status else "—"

        data.append([
            Paragraph(f'<font color="#4F46E5"><b>{t.token}</b></font>', style_center),
            Paragraph(t.subject, styles["Normal"]),
            Paragraph(cat_display, style_center),
            Paragraph(estado_str, style_center),
            Paragraph(f'<b>{valor_str}</b>', style_right),
        ])

    table = Table(data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle([
        # Header
        ("BACKGROUND", (0, 0), (-1, 0), brand_color),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE", (0, 0), (-1, 0), 9),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, light_bg]),
        ("GRID", (0, 0), (-1, -1), 0.5, border),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("FONTSIZE", (0, 1), (-1, -1), 8),
    ]))
    story.append(table)
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border))
    story.append(Spacer(1, 0.3*cm))

    # Total
    total_fmt = f"$ {int(total):,}".replace(",", ".")
    ticket_count = len(tickets)
    story.append(Paragraph(f"Total de tickets: {ticket_count}", style_meta))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("TOTAL A COBRAR", style_total_label))
    story.append(Paragraph(total_fmt, style_total_val))
    story.append(Spacer(1, 0.6*cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=border))
    story.append(Spacer(1, 0.3*cm))
    story.append(Paragraph(
        "Este documento es un detalle interno de servicios prestados. "
        "Perseus Technology — soporte@perseustechnology.dev",
        style_meta
    ))

    doc.build(story)
    buffer.seek(0)
    return buffer.read()


class CompanyUserInline(admin.TabularInline):
    model = CompanyUser
    extra = 1
    fields = ("name", "email", "position", "is_active", "is_manager")
    verbose_name = "Usuario de empresa"
    verbose_name_plural = "Usuarios de la empresa"


@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ("name", "contact_email", "phone", "users_count", "open_tickets_badge", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "contact_email")
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "portal_url")
    inlines = [CompanyUserInline]

    fieldsets = (
        ("Información de la empresa", {
            "fields": ("name", "slug", "portal_url", "contact_email", "phone", "address", "logo")
        }),
        ("Estado", {
            "fields": ("is_active", "created_at")
        }),
    )

    @admin.display(description="URL del portal")
    def portal_url(self, obj):
        if obj.slug:
            url = f"/portal/{obj.slug}/"
            return format_html('<a href="{}" target="_blank">{}</a>', url, url)
        return "—"

    @admin.display(description="Usuarios")
    def users_count(self, obj):
        count = obj.users.filter(is_active=True).count()
        return format_html(
            '<span style="background:#E0E7FF;color:#4338CA;padding:2px 8px;'
            'border-radius:12px;font-size:12px;font-weight:600;">{}</span>',
            count
        )

    @admin.display(description="Tickets abiertos")
    def open_tickets_badge(self, obj):
        count = obj.open_tickets_count()
        color = "#EF4444" if count > 0 else "#10B981"
        return format_html(
            '<span style="background:{};color:white;padding:2px 8px;'
            'border-radius:12px;font-size:12px;">{}</span>',
            color, count
        )


class CompanyUserForm(forms.ModelForm):
    raw_password = forms.CharField(
        label="Nueva contraseña del portal",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Escribe una nueva contraseña para cambiarla. Deja en blanco para mantener la actual."
    )

    class Meta:
        model = CompanyUser
        fields = "__all__"

    def save(self, commit=True):
        user = super().save(commit=False)
        raw = self.cleaned_data.get("raw_password", "").strip()
        if raw:
            user.set_portal_password(raw)
        if commit:
            user.save()
        return user


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    form = CompanyUserForm
    list_display  = ("name", "company", "email", "position", "is_manager", "has_password", "tickets_count", "is_active")
    list_filter   = ("company", "is_active", "is_manager")
    search_fields = ("name", "email", "company__name")
    readonly_fields = ("created_at",)
    fieldsets = (
        ("Información", {"fields": ("company", "name", "email", "position")}),
        ("Acceso al Portal", {
            "fields": ("is_active", "is_manager", "raw_password"),
            "description": "Configura el acceso al inventario del portal público.",
        }),
        ("Fechas", {"fields": ("created_at",), "classes": ("collapse",)}),
    )

    @admin.display(description="🔑 Clave", boolean=True)
    def has_password(self, obj):
        return bool(obj.password)

    @admin.display(description="Tickets")
    def tickets_count(self, obj):
        return obj.tickets.count()


class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ("original_name", "uploaded_at")


class TicketCommentInline(admin.TabularInline):
    model = TicketComment
    extra = 1
    readonly_fields = ("created_at",)
    fields = ("author_name", "author_email", "is_staff", "is_internal", "message", "created_at")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "token_badge", "company", "subject", "requester_name",
        "category_badge", "status_badge", "priority_badge",
        "value_display", "is_billed", "created_at"
    )
    list_filter = ("category", "status", "priority", "company", "is_billed", "created_at")
    search_fields = ("token", "subject", "requester_name", "requester_email")
    readonly_fields = ("token", "created_at", "updated_at", "closed_at")
    date_hierarchy = "created_at"
    inlines = [TicketAttachmentInline, TicketCommentInline]
    save_on_top = True
    actions = ["generar_cobro_pdf"]

    @admin.action(description="📄 Generar PDF de cobro para los tickets seleccionados")
    def generar_cobro_pdf(self, request, queryset):
        # Detectar empresa(s) en la selección
        companies = queryset.values_list("company__name", flat=True).distinct()
        if companies.count() > 1:
            company_name = "Varias empresas"
            filename_slug = "cobro_multiple"
        else:
            company_name = companies.first() or "Sin empresa"
            filename_slug = company_name.lower().replace(" ", "_")

        pdf_bytes = _generate_billing_pdf(queryset, company_name)

        now = timezone.localtime(timezone.now())
        fecha = now.strftime("%Y%m%d")
        filename = f"cobro_{filename_slug}_{fecha}.pdf"

        response = HttpResponse(pdf_bytes, content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="{filename}"'
        return response

    fieldsets = (
        ("Información del Ticket", {
            "fields": ("token", "company", "company_user", "subject", "description")
        }),
        ("Solicitante", {
            "fields": ("requester_name", "requester_email")
        }),
        ("Clasificación", {
            "fields": ("category", "status", "priority")
        }),
        ("Facturación", {
            "fields": ("assigned_value", "is_billed"),
            "classes": ("collapse",),
        }),
        ("Notas internas", {
            "fields": ("internal_notes",),
            "classes": ("collapse",),
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at", "closed_at"),
            "classes": ("collapse",),
        }),
    )

    @admin.display(description="Token")
    def token_badge(self, obj):
        return format_html(
            '<code style="font-weight:bold;color:#4F46E5;">{}</code>',
            obj.token
        )

    CATEGORY_STYLES = {
        "software": ("#6366F1", "💻 Software"),
        "hardware": ("#F59E0B", "🖥️ Hardware"),
        "email":    ("#10B981", "✉️ Email"),
    }

    @admin.display(description="Categoría")
    def category_badge(self, obj):
        color, label = self.CATEGORY_STYLES.get(obj.category, ("#6B7280", obj.category))
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;'
            'border-radius:12px;font-size:12px;white-space:nowrap;">{}</span>',
            color, label
        )

    @admin.display(description="Estado")
    def status_badge(self, obj):
        if obj.status:
            return format_html(
                '<span style="background:{};color:white;padding:2px 10px;'
                'border-radius:12px;font-size:12px;">{}</span>',
                obj.status.color, obj.status.name
            )
        return "—"

    @admin.display(description="Prioridad")
    def priority_badge(self, obj):
        if obj.priority:
            return format_html(
                '<span style="background:{};color:white;padding:2px 10px;'
                'border-radius:12px;font-size:12px;">{}</span>',
                obj.priority.color, obj.priority.name
            )
        return "—"

    @admin.display(description="Valor (CLP)")
    def value_display(self, obj):
        if obj.assigned_value is not None:
            return format_html(
                '<span style="font-weight:bold;color:#059669;">${}</span>',
                f"{int(obj.assigned_value):,}".replace(",", ".")
            )
        return format_html('<span style="color:#9CA3AF;">Sin asignar</span>')

    def save_model(self, request, obj, form, change):
        old_status = None
        if change:
            try:
                old_obj = Ticket.objects.get(pk=obj.pk)
                old_status = old_obj.status
            except Ticket.DoesNotExist:
                pass
        super().save_model(request, obj, form, change)
        if not change:
            obj.send_confirmation_email()
        elif old_status != obj.status and obj.status:
            obj.send_status_update_email(obj.status.name)


@admin.register(TicketStatus)
class TicketStatusAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color_preview", "order", "is_closed_state")
    list_editable = ("order", "is_closed_state")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Color")
    def color_preview(self, obj):
        return format_html(
            '<span style="background:{};width:20px;height:20px;display:inline-block;'
            'border-radius:4px;vertical-align:middle;margin-right:6px;"></span>{}',
            obj.color, obj.color
        )


@admin.register(TicketPriority)
class TicketPriorityAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "color_preview", "sla_hours", "order")
    list_editable = ("order", "sla_hours")
    prepopulated_fields = {"slug": ("name",)}

    @admin.display(description="Color")
    def color_preview(self, obj):
        return format_html(
            '<span style="background:{};width:20px;height:20px;display:inline-block;'
            'border-radius:4px;vertical-align:middle;margin-right:6px;"></span>{}',
            obj.color, obj.color
        )


admin.site.site_header = "Soporte — Panel de Control"
admin.site.site_title = "Support Admin"
admin.site.index_title = "Gestión de Tickets"


@admin.register(Equipment)
class EquipmentAdmin(admin.ModelAdmin):
    list_display  = ("device_type_badge", "brand_model", "serial_number", "company",
                     "assigned_to", "year", "status_badge", "updated_at")
    list_filter   = ("status", "device_type", "company", "year")
    search_fields = ("brand", "model", "serial_number", "assigned_to__name")
    readonly_fields = ("created_at", "updated_at")
    list_per_page = 25

    fieldsets = (
        ("Identificación", {
            "fields": ("company", "device_type", "brand", "model", "serial_number", "year", "image")
        }),
        ("Asignación y Estado", {
            "fields": ("assigned_to", "status")
        }),
        ("Detalles técnicos", {
            "fields": ("specs", "notes"),
            "classes": ("collapse",),
        }),
        ("Fechas", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )

    DEVICE_ICONS = {
        "desktop":  "🖥️", "laptop": "💻", "server": "🗄️",
        "printer":  "🖨️", "monitor": "🖵", "switch": "🔀", "other": "📦",
    }
    STATUS_COLORS = {
        "active": "#10B981", "maintenance": "#F59E0B",
        "retired": "#EF4444", "storage": "#6B7280",
    }

    @admin.display(description="Tipo")
    def device_type_badge(self, obj):
        icon = self.DEVICE_ICONS.get(obj.device_type, "📦")
        return format_html(
            '<span title="{}">{}</span>',
            obj.get_device_type_display(), icon
        )

    @admin.display(description="Marca / Modelo")
    def brand_model(self, obj):
        return format_html("<b>{}</b> {}", obj.brand, obj.model)

    @admin.display(description="Estado")
    def status_badge(self, obj):
        color = self.STATUS_COLORS.get(obj.status, "#6B7280")
        return format_html(
            '<span style="background:{};color:white;padding:2px 10px;'
            'border-radius:12px;font-size:12px;">{}</span>',
            color, obj.get_status_display()
        )
