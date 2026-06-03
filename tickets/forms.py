from django import forms
from .models import Ticket, TicketComment, CompanyUser

class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = [single_file_clean(d, initial) for d in data]
        else:
            result = [single_file_clean(data, initial)]
        return result

INPUT_CLASS = (
    "w-full px-4 py-3 rounded-xl border border-slate-200 "
    "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
    "outline-none transition bg-white text-slate-800 placeholder-slate-400"
)

SELECT_CLASS = INPUT_CLASS + " cursor-pointer"

class TicketPublicForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        label="Archivos adjuntos",
        widget=MultipleFileInput(attrs={
            "class": "hidden",
            "accept": ".pdf,.png,.jpg,.jpeg,.gif,.txt,.doc,.docx,.xls,.xlsx,.zip",
            "id": "file-upload",
            "multiple": True,
        })
    )

    class Meta:
        model = Ticket
        fields = [
            "company_user", "requester_name", "requester_email",
            "category", "priority", "subject", "description",
        ]
        widgets = {
            "company_user": forms.Select(attrs={"class": SELECT_CLASS}),
            "requester_name": forms.TextInput(attrs={
                "placeholder": "Tu nombre completo",
                "class": INPUT_CLASS,
            }),
            "requester_email": forms.EmailInput(attrs={
                "placeholder": "tu@email.com",
                "class": INPUT_CLASS,
            }),
            # category is rendered manually as card buttons in template
            "category": forms.HiddenInput(),
            "priority": forms.Select(attrs={"class": SELECT_CLASS}),
            "subject": forms.TextInput(attrs={
                "placeholder": "Resumen breve del problema",
                "class": INPUT_CLASS,
            }),
            "description": forms.Textarea(attrs={
                "placeholder": "Describe el problema con el mayor detalle posible...",
                "rows": 5,
                "class": INPUT_CLASS + " resize-none",
            }),
        }
        labels = {
            "company_user": "¿Quién eres?",
            "requester_name": "Tu nombre",
            "requester_email": "Tu email",
            "category": "Tipo de soporte",
            "priority": "Prioridad",
            "subject": "Asunto",
            "description": "Descripción del problema",
        }

    def __init__(self, company=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if company:
            users_qs = CompanyUser.objects.filter(company=company, is_active=True)
            self.fields["company_user"].queryset = users_qs
            if users_qs.exists():
                self.fields["company_user"].empty_label = "— Selecciona tu nombre —"
            else:
                self.fields["company_user"].widget = forms.HiddenInput()
                self.fields["company_user"].required = False
        else:
            self.fields["company_user"].widget = forms.HiddenInput()
            self.fields["company_user"].required = False

        self.fields["requester_name"].required = False
        self.fields["requester_email"].required = False
        self.fields["priority"].required = False

    def clean(self):
        cleaned = super().clean()
        company_user = cleaned.get("company_user")
        name = cleaned.get("requester_name", "").strip()
        email = cleaned.get("requester_email", "").strip()

        if company_user:
            cleaned["requester_name"] = company_user.name
            cleaned["requester_email"] = company_user.email
        else:
            if not name:
                self.add_error("requester_name", "Este campo es obligatorio.")
            if not email:
                self.add_error("requester_email", "Este campo es obligatorio.")

        if not cleaned.get("category"):
            self.add_error("category", "Selecciona el tipo de soporte.")

        return cleaned


class TicketCommentForm(forms.ModelForm):
    class Meta:
        model = TicketComment
        fields = ["message"]
        widgets = {
            "message": forms.Textarea(attrs={
                "placeholder": "Escribe tu respuesta...",
                "rows": 4,
                "class": INPUT_CLASS + " resize-none",
            })
        }
        labels = {"message": "Tu mensaje"}


class TicketSearchForm(forms.Form):
    token = forms.CharField(
        max_length=12,
        label="",
        widget=forms.TextInput(attrs={
            "placeholder": "Ingresa tu código de ticket (ej: A1B2C3D4E5F6)",
            "class": (
                "w-full px-4 py-3 rounded-xl border border-slate-200 "
                "focus:ring-2 focus:ring-indigo-500 focus:border-transparent "
                "outline-none transition bg-white text-slate-800 "
                "placeholder-slate-400 uppercase tracking-widest text-center font-mono"
            ),
        })
    )