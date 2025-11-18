import csv
from datetime import datetime

import boto3
from django.contrib import messages
from django.db import IntegrityError
from django.db.models import Q
from django.http import JsonResponse, FileResponse, HttpResponse
from django.shortcuts import render, redirect

from Notebook import settings
from management.models import Project, ProjectMember, User
from management.views import create_notification
from .forms import DocRepositoryConnectionForm, DocRepositoryProjectForm, CodeRepositoryConnectionForm, \
    CodeRepositoryProjectForm, DataRepositoryConnectionForm, DataRepositoryProjectForm, BlockRepositoryConnectionForm
from django.contrib.auth.decorators import login_required

from .getCertificate import getCertificate, check_block_repo_connection 
from .getCodeRepoDetails import get_code_repo_details, check_code_repo_connection
from .getDataDetailsFromS3 import delete_folder_from_s3, extract_git_log_from_s3
from .getDataRepoDetails import get_data_repo_details
from .getDocRepoDetails import get_doc_repo_details, clone_repo, checkout_commit_and_zip, \
    cleanup_temp_files  # , check_doc_repo_connection
from .models import DocRepositoryDetail, CodeRepositoryDetail, CodeRepositoryProject, DocRepositoryProject, \
    DataRepositoryDetail, DataRepositoryProject, BlockRepositoryDetail, BlockRepositoryConnection, \
    DocRepositoryConnection, CodeRepositoryConnection, DataRepositoryConnection

from datetime import datetime
import paramiko
from django.http import FileResponse

from Notebook.settings import base
from labTrace_sdk.labtrace.client import Client
import os, time
import tempfile

# =========================Document Repository=========================
@login_required
def doc_repository_connection(request):
    print('doc_repository_connection', request.method)
    if request.method == 'POST':
        form = DocRepositoryConnectionForm(request.POST)
        if form.is_valid():
            doc_repo = form.save(commit=False)
            doc_repo.notebook_user_id = request.user
            doc_repo.repo_username = form.cleaned_data.get('repo_username')
            doc_repo.git_token = form.cleaned_data.get('git_token')
            if not DocRepositoryConnection.objects.filter(repo_username=doc_repo.repo_username).exists():
                response = 200  # check_doc_repo_connection(doc_repo.repo_username, doc_repo.repo_password)
                if response == 200:
                    doc_repo.save()
                    messages.success(request, 'Account has been successfully set up!')
                else:
                    messages.info(request, 'Enter valid username and password!')
            else:
                messages.warning(request, 'User already exists!')
        else:
            messages.info(request, 'Enter valid username and password!')
        return redirect('repository:doc_connect')
    else:
        form = DocRepositoryConnectionForm()
    return render(request, 'repository/doc_connect.html', {'form': form})


@login_required
def add_doc_repo(request):
    if request.method == 'POST':
        form = DocRepositoryProjectForm(request.POST)  
        for obj in DocRepositoryConnection.objects.all():
        if form.is_valid():
            try:
                doc_conn = DocRepositoryConnection.objects.filter(notebook_user_id=request.user).first()
                if not doc_conn:
                    messages.warning(request, 'Please set up your Overleaf account to continue.')
                    return redirect('repository:home_doc_repo')

                if not DocRepositoryProject.objects.filter(
                        document_name=form.cleaned_data.get('document_name')).exists():
                    new_doc_in_repo = form.save(commit=False)
                    new_doc_in_repo.document_name = form.cleaned_data.get('document_name')
                    new_doc_in_repo.notebook_user_id = doc_conn
                    new_doc_in_repo.project_id = Project.objects.get(project_id=request.POST.get('project'))
                    new_doc_in_repo.save()
                    messages.success(request, 'The document has been successfully added!')
                else:
                    messages.warning(request, 'Document already exists')
                return redirect('repository:add_doc_repo')  # Redirect to the project list or detail page
            except Exception as e:
                messages.warning(request, f"An unexpected error occurred: {e}")

    else:
        form = DocRepositoryProjectForm()  # user=request.user
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    repo_connection_username = DocRepositoryConnection.objects.filter(notebook_user_id=request.user)
    return render(request, 'repository/doc_add.html',
                  {'form': form, 'project_details': project_details, 'user': repo_connection_username})




@login_required
def home_doc_repo(request):
    project_id_from_projectmember = ProjectMember.objects.filter(user=request.user).values(
        'project__project_id').first()
    if project_id_from_projectmember:
        project_id = project_id_from_projectmember.get('project__project_id')
        repo_details = DocRepositoryDetail.objects.filter(doc_details_id__project_id=project_id).order_by('-committed_date')
    else:
        project_id_from_project = Project.objects.filter(pi=request.user).values_list('project_id', flat=True).first()
        repo_details = DocRepositoryDetail.objects.filter(doc_details_id__project_id=project_id_from_project).order_by('-committed_date')
    projects = Project.objects.all()  # Assuming each Project has related documents
    # print('projects', repo_details)
    return render(request, 'repository/doc_home.html',
                  {'repo_details': repo_details, 'projects': projects})


@login_required
def add_new_commit_in_doc(request, document_id):
    email = DocRepositoryConnection.objects.get(notebook_user_id=request.user).repo_username.strip()
    full_name = request.user.first_name + ' ' + request.user.last_name
    git_token = DocRepositoryConnection.objects.get(notebook_user_id=request.user).git_token.strip()
    document_name_obj = DocRepositoryProject.objects.get(doc_project_id=document_id)
    repo_details = get_doc_repo_details(email, git_token, document_name_obj.git_link,
                                        full_name)  # get_doc_repo_details(email= "rubaida.easmin@kcl.ac.uk",password= "Jacknief!23", project_name='Bitbox_paper')
    new_commit_count = 0
    if isinstance(repo_details[0], dict):
        for repo in repo_details:
            doc_repo_db = DocRepositoryDetail()
            doc_repo_db.doc_details_id = document_name_obj
            doc_repo_db.committed_hash = repo['hash']
            doc_repo_db.committed_by = repo['author_name']
            doc_repo_db.committed_msg = repo['message']
            doc_repo_db.committed_date = repo[
                'commit_time']  
            if not DocRepositoryDetail.objects.filter(committed_hash=repo['hash']).exists():
                doc_repo_db.save()
                new_commit_count = new_commit_count + 1

        if new_commit_count == 0:
            messages.warning(request, "No updates detected in the repository.")
        else:
            project = Project.objects.get(project_id=document_name_obj.project_id.pk)
            users_in_project = User.objects.filter(
                Q(projects=project) | Q(member_name__project=project, member_name__is_approved=True)
            ).distinct()
            print('users_in_project', users_in_project)
            for user in users_in_project.exclude(email=request.user.email):
                create_notification(user, 'new_doc',
                                    f"A new commit has been made in the {document_name_obj} repository by {request.user}.")
            messages.success(request, "Updates have been successfully added!")
    else:
        messages.warning(request, repo_details[0])
    return redirect('repository:home_doc_repo')


def download_repo(request, hash):
    project = DocRepositoryDetail.objects.get(committed_hash=hash)
    print(project.doc_details_id.git_link)
    print(project.doc_details_id.notebook_user_id.git_token)
    try:
        # Clone the repository or update if it exists
        repo_path = clone_repo(project.doc_details_id.git_link, project.doc_details_id.notebook_user_id.git_token)
        print('repo_path', repo_path)

        # Checkout the specified commit and create a zip archive
        zip_path = checkout_commit_and_zip(repo_path, hash)
        print('zip_path', zip_path)
        # Serve the zip file for download
        response = FileResponse(open(zip_path, 'rb'), as_attachment=True)
        response['Content-Disposition'] = f'attachment; filename=overleaf_{hash}.zip'
        return response
    except Exception as e:
        messages.warning(request, str(e))
        return redirect('repository:home_doc_repo')  # render(request, "repository/doc_home.html", {"message": str(e)})
    finally:
        cleanup_temp_files('repo_path')
    #return render(request, 'repository/doc_home.html')


@login_required
def process_doc_selection(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        document_id = request.POST.get('document')
        return redirect('repository:commit_doc_repo', document_id=document_id)
    else:
        return redirect('repository:home_doc_repo')  


@login_required
def get_documents(request):
    project_id = request.GET.get('project_id')
    documents = DocRepositoryProject.objects.filter(project_id=project_id).values('doc_project_id', 'document_name')
    print('documents', documents)
    return JsonResponse({'documents': list(documents)})


@login_required
def commit_docrepo(request):
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    project_id = request.GET.get('project_id')
    documents = DocRepositoryProject.objects.filter(project_id=project_id).values('doc_project_id', 'document_name')
    print('documents', documents)
    return render(request, 'repository/doc_projects.html', {'projects': project_details})


# ==========================Code Repository============================
@login_required
def code_repository_connection(request):
    print('doc_repository_connection', request.method)
    if request.method == 'POST':
        form = CodeRepositoryConnectionForm(request.POST)
        if form.is_valid():
            code_repo = form.save(commit=False)
            code_repo.notebook_user_id = request.user
            code_repo.repo_username = form.cleaned_data.get('repo_username')
            code_repo.repo_password = form.cleaned_data.get('repo_password')
            if not CodeRepositoryConnection.objects.filter(repo_username=code_repo.repo_username).exists():
                response = check_code_repo_connection(code_repo.repo_username, code_repo.repo_password)
                if response == 200:
                    code_repo.save()
                    messages.success(request, 'Account has been successfully set up!')
                else:
                    messages.info(request, 'Enter valid username and token!')
            else:
                messages.warning(request, 'User already exists!')
        else:
            messages.info(request, 'Enter valid username and token!')
        return redirect('repository:code_connect')
    else:
        form = CodeRepositoryConnectionForm()
    return render(request, 'repository/code_connect.html', {'form': form})


@login_required
def add_code_repo(request):
    if request.method == 'POST':
        form = CodeRepositoryProjectForm(request.POST)  # , user=request.user
        if form.is_valid():
            new_code_in_repo = form.save(commit=False)
            new_code_in_repo.code_repo_name = request.POST.get('code_repo_name')
            new_code_in_repo.repo_username_for_connection = CodeRepositoryConnection.objects.get(
                code_repo_id=request.POST.get('repo_username'))
            new_code_in_repo.project_id = Project.objects.get(project_id=request.POST.get('project'))
            print('new_doc_in_repo', new_code_in_repo.project_id, new_code_in_repo.code_repo_name,
                  new_code_in_repo.repo_username_for_connection)
            if not CodeRepositoryProject.objects.filter(code_repo_name=new_code_in_repo.code_repo_name).exists():
                new_code_in_repo.save()
                messages.success(request, 'The repository has been successfully added!')
            else:
                messages.warning(request, 'Repository already exists!')
            return redirect('repository:add_code_repo')
    else:
        form = CodeRepositoryProjectForm()  # user=request.user
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    repo_connection_username = CodeRepositoryConnection.objects.filter(notebook_user_id=request.user)
    return render(request, 'repository/code_add.html',
                  {'form': form, 'project_details': project_details, 'users': repo_connection_username})


@login_required
def home_code_repo(request):
    project_id_from_projectmember = ProjectMember.objects.filter(user=request.user).values(
        'project__project_id').first()
    if project_id_from_projectmember:
        project_id = project_id_from_projectmember.get('project__project_id')
        repo_details = CodeRepositoryDetail.objects.filter(code_details_id__project_id=project_id).order_by('-committed_date')
    else:
        project_id_from_project = Project.objects.filter(pi=request.user).values_list('project_id', flat=True).first()
        repo_details = CodeRepositoryDetail.objects.filter(code_details_id__project_id=project_id_from_project).order_by('-committed_date')
    projects = Project.objects.all()  # Assuming each Project has related documents
    return render(request, 'repository/code_home.html',
                  {'repo_details': repo_details, 'projects': projects})


@login_required
def add_new_commit_in_code(request, coderepo_id):
    new_commit_count = 0
    email = CodeRepositoryConnection.objects.get(notebook_user_id=request.user).repo_username
    password = CodeRepositoryConnection.objects.get(notebook_user_id=request.user).repo_password
    repo_name_obj = CodeRepositoryProject.objects.get(code_project_id=coderepo_id)
    repo_details = get_code_repo_details(email, password, repo_name_obj.code_repo_name)
    if isinstance(repo_details[0], dict):
        for repo in repo_details:
            code_repo_db = CodeRepositoryDetail()
            code_repo_db.code_details_id = repo_name_obj
            code_repo_db.committed_hash = repo['commit_sha']
            code_repo_db.committed_by = repo['author']
            code_repo_db.committed_msg = repo['commit_message']
            code_repo_db.committed_date = datetime.strptime(repo['last_commit_date'], '%Y-%m-%d %H:%M:%S').date()
            code_repo_db.committed_url = repo['url']
            if not CodeRepositoryDetail.objects.filter(committed_hash=repo['commit_sha']).exists():
                print('code repo save')
                code_repo_db.save()
                new_commit_count = new_commit_count + 1
        if new_commit_count == 0:
            messages.warning(request, "No updates detected in the repository.")
        else:
            # Notify only staff users about the new member
            project = Project.objects.get(project_id=repo_name_obj.project_id.pk)
            users_in_project = User.objects.filter(
                Q(projects=project) | Q(member_name__project=project, member_name__is_approved=True)
            ).distinct()
            for user in users_in_project.exclude(email=request.user.email):
                create_notification(user, 'new_code',
                                    f"A new commit has been made in the {repo_name_obj} repository by {request.user}.")
            messages.success(request, "Updates have been successfully added!")
    else:
        messages.warning(request,repo_details[0])
    return redirect('repository:home_code_repo')


@login_required
def process_code_repo_selection(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        coderepo_id = request.POST.get('coderepo')
        return redirect('repository:commit_code_repo', coderepo_id=coderepo_id)
    else:
        return redirect('repository:home_code_repo')  # Redirect to home or another view if the request is not POST


@login_required
def get_coderepo(request):
    project_id = request.GET.get('project_id')
    print(project_id)
    coderepo = CodeRepositoryProject.objects.filter(project_id=project_id).values('code_project_id', 'code_repo_name')
    return JsonResponse({'coderepo': list(coderepo)})


@login_required
def commit_coderepo(request):
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    return render(request, 'repository/code_projects.html', {'projects': project_details})


# ==========================Data Repository============================
@login_required
def data_repository_connection(request):
    if request.method == 'POST':
        form = DataRepositoryConnectionForm(request.POST)
        if form.is_valid():
            data_repo = form.save(commit=False)
            data_repo.notebook_user_id = request.user
            data_repo.repo_username = form.cleaned_data.get('repo_username')
            data_repo.repo_password = form.cleaned_data.get('repo_password')
            data_repo.data_server = form.cleaned_data.get('data_server')
            if not DataRepositoryConnection.objects.filter(repo_username=data_repo.repo_username).exists():
                data_repo.save()
                messages.success(request, 'Account has been successfully set up!')
            else:
                messages.warning(request, 'User already exists!')
        else:
            messages.info(request, 'Enter valid username/password/server!')
        return redirect('repository:data_connect')
    else:
        form = DataRepositoryConnectionForm()
    return render(request, 'repository/data_connect.html', {'form': form})


@login_required
def add_data_repo(request):
    if request.method == 'POST':
        form = DataRepositoryProjectForm(request.POST)  # , user=request.user
        if form.is_valid():
            new_data_in_repo = form.save(commit=False)
            new_data_in_repo.data_repo_path = request.POST.get('data_repo_path')
            new_data_in_repo.repo_username_for_connection = DataRepositoryConnection.objects.get(
                data_repo_id=request.POST.get('repo_username'))
            new_data_in_repo.project_id = Project.objects.get(project_id=request.POST.get('project'))
            if not DataRepositoryProject.objects.filter(data_repo_path=new_data_in_repo.data_repo_path).exists():
                new_data_in_repo.save()
                messages.success(request, 'The dataset has been successfully added!')
            else:
                messages.warning(request, 'Dataset already exists!')
            return redirect('repository:add_data_repo')  # Redirect to the project list or detail page

    else:
        form = DataRepositoryProjectForm()  # user=request.user
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    repo_connection_username = DataRepositoryConnection.objects.filter(notebook_user_id=request.user)
    return render(request, 'repository/data_add.html',
                  {'form': form, 'project_details': project_details, 'users': repo_connection_username})


@login_required
def home_data_repo(request):
    project_id_from_projectmember = ProjectMember.objects.filter(user=request.user).values(
        'project__project_id').first()
    if project_id_from_projectmember:
        project_id = project_id_from_projectmember.get('project__project_id')
        repo_details = DataRepositoryDetail.objects.filter(data_details_id__project_id=project_id).order_by('-committed_date')
    else:
        project_id_from_project = Project.objects.filter(pi=request.user).values_list('project_id', flat=True).first()
        repo_details = DataRepositoryDetail.objects.filter(data_details_id__project_id=project_id_from_project).order_by('-committed_date')
    projects = Project.objects.all()  # Assuming each Project has related documents
    return render(request, 'repository/data_home.html',
                  {'repo_details': repo_details, 'projects': projects})


def download_datadetails(request, project, data_hash):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="data_repository_details.csv"'

    # Create CSV writer
    writer = csv.writer(response)
    writer.writerow(['ID', 'Project', 'Committed Hash', 'Committed By', 'Commit Message', 'Commit Date'])

    # Fetch and write model data
    data_details = DataRepositoryDetail.objects.filter(committed_hash=data_hash)
    print('data_details', data_details)
    for detail in data_details:
        writer.writerow([
            detail.data_details_id.data_project_id,  # Assuming data_details_id is a ForeignKey
            project,
            detail.committed_hash,
            detail.committed_by,
            detail.committed_msg,
            detail.committed_date
        ])

    return response


@login_required
def process_data_repo_selection(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        datarepo_id = request.POST.get('datarepo')
        files = request.FILES.getlist("folder")
        s3_client = boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        )

        folder_name = f"uploads/data01/"  
        print('s3_client', s3_client)
        # Upload files to S3
        for file in files:
            print('file', file.name)
            file_path = folder_name + file.name
            s3_client.upload_fileobj(file, AWS_STORAGE_BUCKET_NAME, file_path)

        # Process Git log file from S3
        git_log_file_path = folder_name + "HEAD"  
        commit_history = extract_git_log_from_s3(s3_client, git_log_file_path)
        # Check if there is problem getting git history from s3
        if len(commit_history) == 0:
            messages.warning(request, "Error fetching git log!")
            return redirect('repository:home_data_repo')
        else:
            new_commit_count = 0
            for commit in commit_history:
                data_repo_db = DataRepositoryDetail()
                data_repo_db.data_details_id = DataRepositoryProject.objects.get(data_project_id=datarepo_id)
                data_repo_db.committed_hash = commit["hash"]
                data_repo_db.committed_by = commit["author"]
                data_repo_db.committed_msg = commit["message"]
                data_repo_db.committed_date = commit["date"].date()
                if not DataRepositoryDetail.objects.filter(committed_hash=commit["hash"]).exists():
                    data_repo_db.save()
                    new_commit_count = new_commit_count + 1

            delete_folder_from_s3(s3_client, folder_name)
            if new_commit_count == 0:  # 0
                messages.warning(request, "No updates detected in the dataset.")
            else:
                # Notify only staff users about the new member
                project = Project.objects.get(project_id=project_id)
                users_in_project = User.objects.filter(
                    Q(projects=project) | Q(member_name__project=project, member_name__is_approved=True)
                ).distinct()
                # print('project_mm', users_in_project.exclude(email=request.user.email))
                for member in users_in_project.exclude(email=request.user.email):
                    create_notification(member, 'new_data',
                                        f"A new commit has been made in the data repository by {request.user}.")
                messages.success(request, "Updates have been successfully added!")
            return redirect('repository:home_data_repo')


@login_required
def get_datarepo(request):
    project_id = request.GET.get('project_id')
    datarepo = DataRepositoryProject.objects.filter(project_id=project_id).values('data_project_id', 'data_repo_path')
    return JsonResponse({'datarepo': list(datarepo)})


@login_required
def commit_datarepo(request):
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    return render(request, 'repository/data_projects.html', {'projects': project_details})  # , 'active_page':'block'


def upload_datarepo(request):
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    return render(request, 'repository/data_file_upload.html', {'projects': project_details})  # , 'active_page':'block'




# ===========================Block Repository==========================
@login_required
def block_repository_connection(request):
    if request.method == 'POST':
        form = BlockRepositoryConnectionForm(request.POST)
        if form.is_valid():
            block_repo = form.save(commit=False)
            block_repo.notebook_user_id = request.user
            block_repo.block_username = form.cleaned_data.get('block_username')
            block_repo.block_password = form.cleaned_data.get('block_password')
            if not BlockRepositoryConnection.objects.filter(block_username=block_repo.block_username).exists():
                response = check_block_repo_connection(block_repo.block_username, block_repo.block_password)
                if response == 200:
                    block_repo.save()
                    messages.success(request, 'Account has been successfully set up!')
                else:
                    messages.info(request, 'Enter valid username and password!')
            else:
                messages.warning(request, 'User already exists!')
        else:
            messages.info(request, 'Enter valid username and password!')
        return redirect('repository:block_connect')
    else:
        form = BlockRepositoryConnectionForm()
    return render(request, 'repository/block_connect.html', {'form': form})


'''
def add_block_repo(request):
    if request.method == 'POST':
        form = DataRepositoryProjectForm(request.POST) 
        if form.is_valid():
            new_block_in_repo = form.save(commit=False)
            new_block_in_repo.block_repo_name = form.cleaned_data.get('block_repo_path')
            new_block_in_repo.notebook_user_id = request.user
            new_block_in_repo.project_id = Project.objects.get(project_id=request.POST.get('project'))
            new_block_in_repo.save()
            return redirect('repository:home_block_repo')  # Redirect to the project list or detail page
    else:
        form = DataRepositoryProjectForm()#user=request.user
    project_details = Project.objects.all()
    return render(request, 'repository/block_add.html', {'form': form,'project_details': project_details})
'''


@login_required
def home_block_repo(request):

    project_id_from_projectmember = ProjectMember.objects.filter(user=request.user).values(
        'project__project_id').first()
    if project_id_from_projectmember:
        project_id = project_id_from_projectmember.get('project__project_id')
        repo_details = BlockRepositoryDetail.objects.filter(project=project_id).order_by('-committed_date')
    else:
        project_id_from_project = Project.objects.filter(pi=request.user).values_list('project_id', flat=True).first()
        repo_details = BlockRepositoryDetail.objects.filter(project=project_id_from_project).order_by('-committed_date')
    projects = Project.objects.all()  # Assuming each Project has related documents
    return render(request, 'repository/block_home.html',
                  {'repo_details': repo_details, 'projects': projects})


@login_required
def process_block_repo_selection(request):
    if request.method == 'POST':
        project_id = request.POST.get('project')
        data_repo_id = request.POST.get('datacategory')
        doc_repo_id = request.POST.get('doccategory')
        code_repo_id = request.POST.get('codecategory')
        comment = request.POST.get('comment')
        try:
            # Get LabTrace credentials, handle missing BlockRepositoryConnection
            block_conn = BlockRepositoryConnection.objects.filter(notebook_user_id=request.user).first()
            if not block_conn:
                messages.warning(request, 'Please set up your LabTrace account to continue.')
                return redirect('repository:home_block_repo')

            username = block_conn.block_username
            password = block_conn.block_password

            # Get LabTrace project ID, handle missing project
            project = Project.objects.filter(project_id=project_id).first()
            if not project:
                messages.warning(request, 'Invalid project ID.')
                return redirect('repository:home_block_repo')

            labtrace_project_id = project.block_project_id

            # Initialize BlockRepositoryDetail
            block_repo_db = BlockRepositoryDetail()

            # Get the latest commit hashes, handling cases where no commits exist
            block_repo_db.data_hash = (
                DataRepositoryDetail.objects.filter(data_details_id=data_repo_id)
                .order_by('committed_date', 'id')
                .last()
            )
            block_repo_db.code_hash = (
                CodeRepositoryDetail.objects.filter(code_details_id=code_repo_id)
                .order_by('committed_date')
                .last()
            )
            block_repo_db.doc_hash = (
                DocRepositoryDetail.objects.filter(doc_details_id=doc_repo_id)
                .order_by('committed_date')
                .last()
            )

            # Extract hashes safely (handle None cases)
            block_repo_db.data_hash = block_repo_db.data_hash.committed_hash if block_repo_db.data_hash else None
            block_repo_db.code_hash = block_repo_db.code_hash.committed_hash if block_repo_db.code_hash else None
            block_repo_db.doc_hash = block_repo_db.doc_hash.committed_hash if block_repo_db.doc_hash else None

            # Ensure all required hashes exist before proceeding
            if not all([block_repo_db.data_hash, block_repo_db.code_hash, block_repo_db.doc_hash]):
                messages.warning(request, "Some repository details are missing. Ensure all repositories have commits.")
                return redirect('repository:home_block_repo')

            # Check if this combination already exists in BlockRepositoryDetail
            if not BlockRepositoryDetail.objects.filter(
                    data_hash=block_repo_db.data_hash,
                    code_hash=block_repo_db.code_hash,
                    doc_hash=block_repo_db.doc_hash
            ).exists():
                # Get repositories, handle missing cases
                block_repo_db.data_repo = DataRepositoryProject.objects.filter(data_project_id=data_repo_id).first()
                block_repo_db.code_repo = CodeRepositoryProject.objects.filter(code_project_id=code_repo_id).first()
                block_repo_db.doc_repo = DocRepositoryProject.objects.filter(doc_project_id=doc_repo_id).first()

                if not all([block_repo_db.data_repo, block_repo_db.code_repo, block_repo_db.doc_repo]):
                    messages.warning(request, "One or more repositories are missing.")
                    return redirect('repository:home_block_repo')

                block_repo_db.block_details_id = block_conn
                block_repo_db.project = project
                block_repo_db.committed_date = datetime.now().date()
                block_repo_db.comment = comment

                # Generate certificate (handle failure case)
                block_repo_db.block_hash = getCertificate(
                    username, password, labtrace_project_id,
                    block_repo_db.data_hash, block_repo_db.code_hash, block_repo_db.doc_hash
                )

                if block_repo_db.block_hash:
                    block_repo_db.save()
                    messages.success(request, "Certificate generated successfully!")
                else:
                    messages.warning(request, "Failed to create certificate!")

            else:
                messages.warning(request, "No updates detected in the project.")

        except Exception as e:
            messages.warning(request, f"An unexpected error occurred: {e}")

        return redirect('repository:home_block_repo')
    else:
        return redirect('repository:home_block_repo')  



@login_required
def get_project_for_commit(request):
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    return render(request, 'repository/block_projects.html', {'projects': project_details})  # , 'active_page':'block'


@login_required
def load_subcategories(request):
    project_id = request.GET.get('project_id')
    codecategory = list(
        CodeRepositoryProject.objects.filter(project_id=project_id).values('code_project_id', 'code_repo_name'))
    doccategory = list(
        DocRepositoryProject.objects.filter(project_id=project_id).values('doc_project_id', 'document_name'))
    datacategory = list(
        DataRepositoryProject.objects.filter(project_id=project_id).values('data_project_id', 'data_repo_path'))

    return JsonResponse({
        'datacategory': datacategory,
        'doccategory': doccategory,
        'codecategory': codecategory,
    })


@login_required
def download_certificate(request, project, block_hash):
    username = BlockRepositoryConnection.objects.get(notebook_user_id=request.user).block_username
    password = BlockRepositoryConnection.objects.get(notebook_user_id=request.user).block_password
    labtrace_project_id = Project.objects.get(project_name=project).block_project_id
    labtrace_client = Client(username, password)
    save_path = tempfile.mkdtemp()  
    certificate_name = labtrace_client.get_private_file_certificate(labtrace_project_id, block_hash, save_path)
    response = FileResponse(open(os.path.join(save_path, certificate_name), 'rb'), as_attachment=True)
    return response
    
@login_required
def user_guide(request):
    return render(request, 'repository/user_guide.html')


@login_required
def user_guide_overleaf_details(request):
    return render(request, 'repository/user_guide_doc.html')


@login_required
def user_guide_data_details(request):
    return render(request, 'repository/user_guide_data.html')


@login_required
def user_guide_code_details(request):
    return render(request, 'repository/user_guide_code.html')


@login_required
def user_guide_cert_details(request):
    return render(request, 'repository/user_guide_cert.html')


