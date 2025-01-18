from django.urls import path,include
from . import views
from django.conf import settings
from django.conf.urls.static import static
from .views import *
from django.contrib.auth import views as auth_views


urlpatterns = [

 path('dashboard/',dashboard, name='dashboard'),
 path('password_reset/', auth_views.PasswordResetView.as_view(template_name='registration/password_reset.html'), name='password_reset'),
 path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
 path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
 path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),


    path('',views.index,name='index'),
    path('index',views.index,name='index'),
    path('about',views.about,name='about'),
    path('service',views.service,name='service'),
    path('contact',views.contact,name='contact'),
    path('category_list', category_list, name='category_list'),
    path('locations/', location_list, name='location_list'),
    


    path('home/',views.home,name='home'),
    path("login/",views.login_form,name="login"),
    path('create/', views.create_ticket, name='create_ticket'),
    path('list/', views.ticket_list, name='ticket_list'),
    path('create_ticket/', views.create_ticket, name='create_ticket'),
    path('tickets/', views.ticket_list, name='ticket_list'),
    path('tickets/<int:ticket_id>/details/', ticket_details, name='ticket_details'),
    path('assign/<int:ticket_id>/', views.assign_ticket, name='assign_ticket'),
    path('resolve/<int:ticket_id>/', views.resolve_ticket, name='resolve_ticket'),
    path('approve/<int:ticket_id>/', views.approve_ticket, name='approve_ticket'),
    path('tickets/<int:ticket_id>/validate/', views.validate_ticket, name='validate_ticket'),
    path('tickets/<int:ticket_id>/close/', views.close_ticket, name='close_ticket'),
    path('closed-tickets/', views.closed_tickets_list, name='closed_tickets_list'),
    path('closed-tickets/<int:ticket_id>/details/', views.closedticket_details, name='closedticket_details'),
    path('closed-tickets/<int:ticket_id>/delete/', delete_closed_ticket, name='delete_closed_ticket'),
    path('tickets/<int:ticket_id>/return-to-unaffected/', views.return_to_unaffected, name='return_to_unaffected'),

    path('UserRoter/',views.UserRoter,name='user_roter'),
    path('add_agent/',views.CreateAgent,name='create_agent'),

    path('agent/',views.AgentPage,name='agent_page'),

    path('technician/',views.TechnicianPage,name='technician_page'),
    path('supervisor/',views.SupervisorPage,name='supervisor_page'),
    path('station_de_base/',views.StationDeBase,name='station_de_base'),

    path('admin/', views.admin_page, name='admin'),
    path('add_technician/', views.CreateTechnician, name='create_technician'),
    path('add_supervisor/', views.CreateSupervisor, name='create_supervisor'),
    path('add_station_base/', views.CreationAdminSationBase, name='create_station_base'),

    path('add_superuser/',views.CreateSuperUser,name='create_superuser'),

    path('DeleteUser/',views.DeleteUser,name='delete_user'),
path("DesactivateAcount/",views.DesactivateAcount,name='DesactivateAcount'),
    path("ActivateAcount/",views.ActivateAcount,name='ActivateAcount'),
    path('delete/<int:ticket_id>/', views.delete_ticket, name='delete_ticket'),
    path('UpdateUser/<int:user_id>',views.UpdateUser,name='update_user'),
    path('UpdateAdmin/<int:admin_id>',views.UpdateAdminSationBase,name='update_admin'),
    path('DeleteAdmin/<int:admin_id>', views.DeleteAdminSationBase, name='delete_admin'),

    path('search_engine/',views.search_general,name='search_engine'),
    path('DataDisplay',views.DataDisplay,name='DataDisplay'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)