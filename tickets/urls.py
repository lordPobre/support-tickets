from django.urls import path
from . import views

urlpatterns = [
    # Internal Dashboard
    path("", views.dashboard, name="dashboard"),
    path("tickets/", views.ticket_list, name="ticket_list"),
    path("inventario/", views.inventory_list, name="inventory_list"),
    path("inventario/agregar/", views.inventory_add, name="inventory_add"),
    path("inventario/<int:pk>/", views.inventory_detail, name="inventory_detail"),
    path("inventario/<int:pk>/editar/", views.inventory_edit, name="inventory_edit"),
    path("inventario/<int:pk>/eliminar/", views.inventory_delete, name="inventory_delete"),
    path("tickets/export/excel/", views.ticket_export_excel, name="ticket_export_excel"),
    path("tickets/<str:token>/", views.ticket_detail, name="ticket_detail"),
    path("tickets/<str:token>/pdf/", views.ticket_pdf, name="ticket_pdf"),
    path("tickets/<str:token>/image/", views.ticket_image, name="ticket_image"),

    # Public Portal
    path("portal/<slug:company_slug>/", views.portal_home, name="portal_home"),
    path("portal/<slug:company_slug>/login/", views.portal_login, name="portal_login"),
    path("portal/<slug:company_slug>/logout/", views.portal_logout, name="portal_logout"),
    path("portal/<slug:company_slug>/inventario/", views.portal_inventory, name="portal_inventory"),
    path("portal/<slug:company_slug>/ticket/<str:token>/", views.portal_ticket, name="portal_ticket"),
    path("portal/<slug:company_slug>/ticket/<str:token>/pdf/", views.portal_ticket_pdf, name="portal_ticket_pdf"),
    path("portal/<slug:company_slug>/ticket/<str:token>/image/", views.portal_ticket_image, name="portal_ticket_image"),
]
