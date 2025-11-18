from django.urls import path
from .views import doc_repository_connection, add_doc_repo, home_doc_repo, add_new_commit_in_doc, \
    code_repository_connection, add_code_repo, home_code_repo, \
    add_new_commit_in_code, process_doc_selection, get_documents, get_coderepo, process_code_repo_selection, \
    data_repository_connection, home_data_repo, add_data_repo, get_datarepo, process_data_repo_selection, \
    block_repository_connection, home_block_repo, \
    process_block_repo_selection, download_certificate, get_project_for_commit, commit_coderepo, commit_docrepo, \
    commit_datarepo, load_subcategories, user_guide, user_guide_overleaf_details, user_guide_data_details, \
    user_guide_code_details, user_guide_cert_details, download_repo, upload_datarepo, download_datadetails


app_name = 'repository'
urlpatterns = [
    path('connect-doc/', doc_repository_connection, name='doc_connect'),
    path('add-doc/', add_doc_repo, name='add_doc_repo'),
    path('home-doc/', home_doc_repo, name='home_doc_repo'),
    path('commit-docrepo/', commit_docrepo, name='commit_docrepo'),
    path('commit-doc/<int:document_id>/', add_new_commit_in_doc, name='commit_doc_repo'),
    path('download/<str:hash>/', download_repo, name='download_repo'),
    path('get-documents/',get_documents, name='get_documents'),
    path('process-doc-selection/',process_doc_selection, name='process_doc_selection'),

    path('connect-code/', code_repository_connection, name='code_connect'),
    path('add-code/', add_code_repo, name='add_code_repo'),
    path('home-code/', home_code_repo, name='home_code_repo'),
    path('commit-coderepo/',commit_coderepo, name='commit_coderepo'),
    path('commit-code/<int:coderepo_id>/', add_new_commit_in_code, name='commit_code_repo'),
    path('get-coderepo/', get_coderepo, name='get_coderepo'),
    path('process-code-selection/', process_code_repo_selection, name='process_code_selection'),

    path('connect-data/', data_repository_connection, name='data_connect'),
    path('add-data/', add_data_repo, name='add_data_repo'),
    path('home-data/', home_data_repo, name='home_data_repo'),
    path('commit-datarepo/', commit_datarepo, name='commit_datarepo'),
    path('upload-datarepo/', upload_datarepo, name='upload_datarepo'),
    path('download-datadetails/<str:project>/<str:data_hash>',download_datadetails, name='download_datadetails'),
    path('get-datarepo/', get_datarepo, name='get_datarepo'),
    path('process-data-selection/', process_data_repo_selection, name='process_data_selection'),

    path('connect-block/', block_repository_connection, name='block_connect'),
    path('home-block/', home_block_repo, name='home_block_repo'),
    path('download/<str:project>/<str:block_hash>', download_certificate, name='download_certificate'), #
    path('get-projects/', get_project_for_commit, name='get_projects'),
    path('process-block-selection/', process_block_repo_selection, name='process_block_selection'),
    path('load-subcategories/', load_subcategories, name='load_subcategories'),

    path('user-guide/', user_guide, name='user_guide'),
    path('user-guide-doc/', user_guide_overleaf_details, name='user_guide_doc'),
    path('user-guide-data/', user_guide_data_details, name='user_guide_data'),
    path('user-guide-code/', user_guide_code_details, name='user_guide_code'),
    path('user-guide-cert/', user_guide_cert_details, name='user_guide_cert'),

]