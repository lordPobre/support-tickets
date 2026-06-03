from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("tickets/export/excel/", views.ticket_export_excel, name="ticket_export_excel"),
    path("tickets/<str:token>/", views.ticket_detail, name="ticket_detail"),
    path("tickets/<str:token>/pdf/", views.ticket_pdf, name="ticket_pdf"),
    path("tickets/<str:token>/image/", views.ticket_image, name="ticket_image"),

    path("portal/<slug:company_slug>/", views.portal_home, name="portal_home"),
    path("portal/<slug:company_slug>/ticket/<str:token>/", views.portal_ticket, name="portal_ticket"),
    path("portal/<slug:company_slug>/ticket/<str:token>/pdf/", views.portal_ticket_pdf, name="portal_ticket_pdf"),
    path("portal/<slug:company_slug>/ticket/<str:token>/image/", views.portal_ticket_image, name="portal_ticket_image"),
]