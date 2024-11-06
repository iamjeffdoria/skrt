from django.urls import path
from django.conf import settings  
from django.conf.urls.static import static 
from . import views
from .views import search_records
from django.contrib.auth import views as auth_views
from .views import approve_request, reject_request
from .views import registration_data
from .views import get_attendance_data
from .views import student_details
from .views import all_logs, download_logs_pdf
from .views import activate_account

urlpatterns = [
    path('all-logs/', all_logs, name='all-logs'),
    path('download-logs-pdf/', download_logs_pdf, name='download-logs-pdf'),
    path('update-profile/', views.update_profile, name='update-profile'),
    path('', views.home, name="index"),
    path('search/', search_records, name='search-records'),
 
    path('unified-login/',views.unified_login, name='unified-login'),
    path('head-dashboard/',views.head_dashboard, name='head-dashboard'),
   
    path('stud-logout/', views.student_logout, name="stud-logout"),
    path('head-logout/', views.head_logout, name="head-logout"),
    path('logout/', views.logout, name="logout"),
  
    path('stud-dash/',views.student_dashboard, name='stud-dash'),

    path('create-report/',views.create_report, name='create-report'),
    # CRUD
    path('dashboard/', views.dashboard, name="dashboard"),
    path('dashboard-real/', views.dashboard_real, name="dashboard-real"),
    path('create-record/', views.create_record, name="create-record"),
    path('student-register/', views.student_register, name="student-register"),
    path('student-request/', views.student_request, name="student-request"),

    path('update-record/<int:pk>/', views.update_record, name="update-record"),
    path('record/<int:pk>/', views.view_record, name="record"),    
    path('delete-record/<int:pk>/', views.delete_record, name="delete-record"),
    path('admin-record/', views.view_admin, name="admin-record"), 
    path('create-record-admin/', views.create_admin, name="create-record-admin"), 
    path('prompt/', views.prompt, name='prompt'),
    path('process-rfid/', views.process_rfid, name='process-rfid'),
    path('student-logs/<str:student_id>/', views.view_student_logs, name='student-logs'),  # URL pattern with student_id
    path('block-student/<int:pk>/', views.block_student, name="block-student"),
    path('unblock-student/<int:pk>/', views.unblock_student, name="unblock-student"),
    path('create-report/', views.create_report, name='create-report'),
    path('student-reports/', views.student_reports, name='student-reports'),
    path('sidebar/', views.sidebar_view, name='sidebar-view'),
    path('own-logs/', views.view_own_logs, name="own-logs"),

    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='webapp/registration/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='webapp/registration/password_reset_done.html'), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='webapp/registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='webapp/registration/password_reset_complete.html'), name='password_reset_complete'),
    path('approve-request/<int:request_id>/', approve_request, name='approve-request'),
    path('reject/<int:request_id>/', reject_request, name='reject-request'),
    path('registration-data/', registration_data, name='registration_data'),
    path('get-attendance-data/', get_attendance_data, name='get_attendance_data'),
    path('all-logs', views.all_logs, name='all-logs'),
    path('student-details/<int:student_id>/', student_details, name='student-details'),
 
    path('activate-account/<int:student_id>/', activate_account, name='activate-account'),
    
    path('check-username-availability/', views.check_username_availability, name='check_username_availability'),
    path('check-student-id-availability/', views.check_student_id_availability, name='check_student_id_availability'),
    path('check_email_availability/', views.check_email_availability, name='check_email_availability'),
] 

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
