from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count
from .models import Company, CompanyUser, Ticket, TicketStatus, TicketPriority, TicketAttachment, TicketComment


class CompanyUserInline(admin.TabularInline):
    model = CompanyUser
    extra = 1
    fields = ("name", "email", "position", "is_active")
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


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ("name", "company", "email", "position", "tickets_count", "is_active")
    list_filter = ("company", "is_active")
    search_fields = ("name", "email", "company__name")
    readonly_fields = ("created_at",)

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