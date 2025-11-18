from django.urls import path, re_path
from .views import loginView, logoutView, register, home, add_project, add_member, home_member, new_member_list, \
    confirm_or_delete_member, password_reset, password_reset_done, password_reset_confirm, password_reset_complete, \
    delete_member, update_profile, mark_notification_as_read, terms_and_conditions, project_repository_feed, \
    update_repository, update_code_repository, update_doc_repository, update_data_repository, update_cert_repository
from django.contrib.auth import views as auth_views

app_name = 'management'
urlpatterns = [
    path('registration/', register, name='registration'),
    path('', loginView, name='login'),
    path('logout/', logoutView, name='logout'),
    path('home/<int:project_id>', project_repository_feed, name='feed'),
    path('home/', home, name='home'),
    path('add-project/', add_project, name='add_project'),
    path('add-member/<int:pk>/', add_member, name='add_member'),
    path('confirm-member/<int:pk>/', confirm_or_delete_member, name='confirm_member'),
    path('delete-member/<int:pk>/', delete_member, name='delete_member'),
    path('new-member/', new_member_list, name='new_member'),
    path('update-profile/', update_profile, name='update_profile'),
    path('update-repository/', update_repository, name='update_repo'),
    path('update-code-repository/', update_code_repository, name='update_code_repo'),
    path('update-doc-repository/', update_doc_repository, name='update_doc_repo'),
    path('update-data-repository/', update_data_repository, name='update_data_repo'),
    path('update-certificate-repository/', update_cert_repository, name='update_cert_repo'),

    path('password-reset/', password_reset, name='password_reset'),
    path('password-reset/done/', password_reset_done, name='password_reset_done'),
    path('reset/<str:uidb64>/<str:token>/',password_reset_confirm, name='password_reset_confirm'),
    path('reset/done/', password_reset_complete, name='password_reset_complete'),

    path('notifications/read/<int:notification_id>/', mark_notification_as_read, name='mark_notification_as_read'),
    path('terms/and/conditions', terms_and_conditions, name='terms_and_conditions'),

]


