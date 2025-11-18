from datetime import timedelta
from itertools import chain

from django.contrib.auth.tokens import default_token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.db.models import Prefetch, Q
from django.dispatch import receiver
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect, resolve_url
from django.contrib import messages
from django.template.loader import render_to_string
from django.template.response import TemplateResponse
from django.urls import reverse
from django.utils import timezone
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode

from Notebook import settings
from repository.forms import DocRepositoryConnectionForm, DataRepositoryConnectionForm, CodeRepositoryConnectionForm, \
    BlockRepositoryConnectionForm
from repository.models import DataRepositoryDetail, CodeRepositoryDetail, DocRepositoryDetail, DocRepositoryConnection, \
    DataRepositoryConnection, CodeRepositoryConnection, BlockRepositoryConnection
from .backends import AuthBackend
from .forms import UserRegistrationForm, MemberForm, PasswordResetForm, SetPasswordForm
from django.contrib.auth.decorators import login_required
from .forms import ProjectForm, UserProfileUpdateForm
from .models import User, ProjectMember, Project, Notification
from django.contrib.auth import logout, login, authenticate, signals, get_user_model
from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from django.shortcuts import redirect
from .tables import ProjectMemberTable
from sendgrid import SendGridAPIClient, Email, Personalization
from sendgrid.helpers.mail import Mail

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        print(request.method)
        if form.is_valid():
            form.save()
            first_name = form.cleaned_data.get('first_name')
            last_name = form.cleaned_data.get('last_name')
            selected = True
            print(first_name, last_name, selected)

            #Notify all PIs
            staff_users = User.objects.filter(is_pi=True)
            for user in staff_users:
                create_notification(user, 'new_member', f"{first_name} {last_name} has joined.")
            messages.success(request, f'Account created for {first_name} {last_name}!')
            return redirect('management:registration')
        else:
            messages.warning(request,'Try again!')
            return render(request, 'management/register.html', {'form': form})
    else:
        form = UserRegistrationForm()
        return render(request, 'management/register.html', {'form': form})

def loginView(request):
    print(request.method)
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        print('email:', email, password)
        is_pi = 'False' #User.objects.get(email=email).is_pi
        remember_me = request.POST.get('remember_me')
        user = AuthBackend.authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30)  
            else:
                request.session.set_expiry(0)  

            return redirect('management:home')  .
        elif user is not None and not is_pi:
            login(request, user)
            if remember_me:
                request.session.set_expiry(60 * 60 * 24 * 30) 
            else:
                request.session.set_expiry(0) 
            return redirect('management:home')  
        else:
            messages.warning(request, 'Invalid username or password.')
            return redirect('management:login')
    return render(request, 'management/login.html')




@login_required
def update_profile(request):
    try:
        if request.method == 'POST':
            form = UserProfileUpdateForm(request.POST, instance=request.user)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your profile was updated successfully.')
                return redirect('management:update_profile')
            else:
                messages.warning(request, 'Please correct the errors below.')

        else:
            form = UserProfileUpdateForm(instance=request.user)

    except Exception as e:
        #logger.error(f"Error updating profile: {str(e)}", exc_info=True)
        messages.error(request, "An error occurred while updating your profile. Please try again.")

    return render(request, 'management/profile.html', {'form': form})

@login_required
def update_repository(request):
    return render(request, 'management/update_repository.html')

@login_required
def update_code_repository(request):
    try:
        # Try to get the DocRepositoryConnection instance for the current user
        code_repo_instance = CodeRepositoryConnection.objects.filter(notebook_user_id=request.user).first()
        #print('data_repo_instance', code_repo_instance)

        if request.method == 'POST':
            form = CodeRepositoryConnectionForm(request.POST, instance=code_repo_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your repository connection was updated successfully.')
                return redirect('management:update_code_repo')
            else:
                messages.warning(request, 'No available data to update.')
        else:
            form = CodeRepositoryConnectionForm(instance=code_repo_instance)

    except Exception as e:
        messages.info(request, "No repository found.")
        form = CodeRepositoryConnectionForm()  # Return an empty form if something goes wrong

    return render(request, 'management/update_code_repo.html', {'form': form})

@login_required
def update_doc_repository(request):
    try:
        # Try to get the DocRepositoryConnection instance for the current user
        doc_repo_instance = DocRepositoryConnection.objects.filter(notebook_user_id=request.user).first()

        if request.method == 'POST':
            form = DocRepositoryConnectionForm(request.POST, instance=doc_repo_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your repository connection was updated successfully.')
                return redirect('management:update_doc_repo')
            else:
                messages.warning(request, 'No available data to update.')
        else:
            form = DocRepositoryConnectionForm(instance=doc_repo_instance)

    except Exception as e:
        messages.info(request, "No repository found.")
        form = DocRepositoryConnectionForm()  # Return an empty form if something goes wrong

    return render(request, 'management/update_doc_repo.html', {'form': form})

@login_required
def update_data_repository(request):
    try:
        # Try to get the DocRepositoryConnection instance for the current user
        data_repo_instance = DataRepositoryConnection.objects.filter(notebook_user_id=request.user).first()
        print('data_repo_instance',data_repo_instance)

        if request.method == 'POST':
            form = DataRepositoryConnectionForm(request.POST, instance=data_repo_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your repository connection was updated successfully.')
                return redirect('management:update_data_repo')
            else:
                messages.warning(request, 'No available data to update.')
        else:
            form = DataRepositoryConnectionForm(instance=data_repo_instance)

    except Exception as e:
        messages.info(request, "No repository found.")
        form = DataRepositoryConnectionForm()  # Return an empty form if something goes wrong

    return render(request, 'management/update_data_repo.html', {'form': form})

@login_required
def update_cert_repository(request):
    try:
        # Try to get the DocRepositoryConnection instance for the current user
        block_repo_instance = BlockRepositoryConnection.objects.filter(notebook_user_id=request.user).first()
        #print('block_repo_instance', block_repo_instance)

        if request.method == 'POST':
            form = BlockRepositoryConnectionForm(request.POST, instance=block_repo_instance)
            if form.is_valid():
                form.save()
                messages.success(request, 'Your repository connection has updated successfully.')
                return redirect('management:update_cert_repo')
            else:
                messages.warning(request, 'No available data to update.')
                return redirect('management:update_cert_repo')
        else:
            form = BlockRepositoryConnectionForm(instance=block_repo_instance)

    except Exception as e:
        messages.info(request, "No repository found.")
        form = BlockRepositoryConnectionForm()  # Return an empty form if something goes wrong

    return render(request, 'management/update_cert_repo.html', {'form': form})

def logoutView(request):
    logout(request)
    return redirect('management:login')
    #template_name = 'management/logout.html'


@login_required
def project_repository_feed(request, project_id):
    project_name = Project.objects.get(project_id=project_id).project_name
    print('project repo feed', Project.objects.filter(pi=request.user,project_id=project_id).exists(), ProjectMember.objects.filter(user=request.user,project_id=project_id).exists(), ProjectMember.objects.filter(is_approved=True).exists())
    if Project.objects.filter(pi=request.user,project_id=project_id).exists() or (ProjectMember.objects.filter(user=request.user,project_id=project_id).exists() and ProjectMember.objects.filter(is_approved=True).exists()):
        data = DataRepositoryDetail.objects.filter(data_details_id__DataRepository__project_id=project_id)
        doc = DocRepositoryDetail.objects.filter(doc_details_id__DocRepository__project_id=project_id)
        code = CodeRepositoryDetail.objects.filter(code_details_id__CodeRepository__project_id=project_id)
        for d in data:
            d.object_type = 'data'
        for d in doc:
            d.object_type = 'doc'
        for d in code:
            d.object_type = 'code'
        combined_results = list(chain(data, doc, code))
        return render(request, 'management/home.html', {'combined_results': combined_results,'project_name': project_name})
    else:
        return render(request, 'management/home.html', {'combined_results': [],'project_name': project_name})


@login_required
def home(request):
    project_list = Project.objects.all()
    return render(request, 'management/home_project_list.html',{'projects': project_list})


@login_required
def home_member(request):
    return render(request, 'management/home_member.html')



@login_required
def new_member_list(request):
    # Get all users who are not PIs and not superuser
    users_not_pis = User.objects.exclude(id__in=Project.objects.values('pi')).exclude(is_superuser=True)
    # Get the users who are not in ProjectMember
    newly_registered_users = users_not_pis.exclude(id__in=ProjectMember.objects.values('user'))
    print('newly_registered_users', newly_registered_users)
    return render(request, "management/newMemberList.html", {"new_members": newly_registered_users})
    #return render(request, '', {'newly_registered_users':newly_registered_users})




@login_required
def add_project(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            #print(form.cleaned_data.get('project_name'))
            #print(form.cleaned_data.get('project_description'))
            project = form.save(commit=False)
            project.pi = request.user
            project.is_critical = form.cleaned_data.get('is_critical')
            project.save()
            messages.success(request, "A new project has been added!")
            return redirect('management:home')  # Redirect to the home page or project list after saving
    else:
        form = ProjectForm()
    return render(request, 'management/add_project.html', {'form': form})



@login_required
def add_member(request,pk):
    pi_projects = Project.objects.filter(pi=request.user)
    member_projects = Project.objects.filter(
        project_id__in=ProjectMember.objects.filter(
            user=request.user, is_approved=True
        ).values_list('project', flat=True)
    )

    project_details = (pi_projects | member_projects).distinct()
    member_details = User.objects.get(id=pk)
    return render(request, 'management/add_member.html', {'member_details': member_details, 'project_details':project_details})

@login_required
def confirm_or_delete_member(request, pk):
    data = User.objects.get(id=pk)
    #print('data', data)
    if request.method == 'POST':
        selected_project_id = request.POST.get('project')
        print(data, request.POST.get('project'))
        project_member = ProjectMember()
        project_member.user = data
        project_member.project_id = Project.objects.get(project_id=selected_project_id).pk
        print(project_member.project_id)
        project_member.is_approved = True
        User.objects.filter(id=pk).update(is_staff=True)
        project_member.save()
        # Notify new member
        #staff_users = User.objects.filter(is_pi=True)
        #for user in staff_users:
        create_notification(project_member.user, 'add_member', f"You are added to project {Project.objects.get(project_id=selected_project_id).project_name}.")
        messages.success(request, 'A new member has been added!')
        return redirect('management:new_member')

@login_required
def delete_member(request, pk):
    data = User.objects.get(id=pk)
    print('data', data)
    return redirect('management:new_member')


# notifications.py
@staticmethod
def create_notification(user, notification_type, message):
    Notification.objects.create(
        user=user,
        notification_type=notification_type,
        message=message
    )



def mark_notification_as_read(request, notification_id):
    notification = Notification.objects.get(id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('management:home')

def password_reset(request):
    if request.method == "POST":
        password_reset_form = PasswordResetForm(request.POST)
        if password_reset_form.is_valid():
            data = password_reset_form.cleaned_data['email']
            associated_users = User.objects.filter(Q(email=data))
            if associated_users.exists():
                for user in associated_users:
                    subject_template = "management/password_reset_subject.txt"
                    email_template_name = "management/password_reset_email.html"
                    c = {
                        "first_name": user.first_name,
                        "email": user.email,
                        'domain': get_current_site(request).domain,
                        #'site_name': 'Website',
                        "uid": urlsafe_base64_encode(force_bytes(user.pk)),
                        'token': default_token_generator.make_token(user),
                        'protocol': 'http',
                    }
                    html_message = render_to_string(email_template_name, c)
                    subject = render_to_string(subject_template)
                    print(user.email)
                    message = Mail(
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        to_emails= '', 
                        subject=subject,
                        html_content=html_message)
                    try:
                        sg = SendGridAPIClient('')
                        sg.send(message)
                        print('sg',sg)
                        return redirect('management:password_reset_done')
                    except Exception as e:
                        print('Failed to send password reset email. {}'.format(e))
                        #logger.error('Failed to send password reset email. {}'.format(e))
                        messages.warning(request,'Sending of message failed. Please try again.',extra_tags='password_reset_msg')
                        return redirect('management:password_reset')
            else:
                messages.warning(request, 'Please enter a valid email.',extra_tags='password_reset_msg')
                return redirect('management:password_reset')

    password_reset_form = PasswordResetForm()
    return render(request=request, template_name="management/password_reset.html",
                  context={"password_reset_form": password_reset_form})

def password_reset_done(request,
                        template_name='management/password_reset_done.html',
                        current_app=None, extra_context=None):
    context = {
        'title': ('Password reset successful'),
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)
                            #current_app=current_app)



def password_reset_confirm(request, uidb64=None, token=None,
                           template_name='management/password_reset_confirm.html',
                           token_generator=default_token_generator,
                           set_password_form=SetPasswordForm,
                           post_reset_redirect=None,
                           current_app=None, extra_context=None):
    UserModel = get_user_model()
    assert uidb64 is not None and token is not None  # checked by URLconf
    if post_reset_redirect is None:
        post_reset_redirect = reverse('management:password_reset_complete')
    else:
        post_reset_redirect = resolve_url(post_reset_redirect)
    try:
        uid = urlsafe_base64_decode(uidb64)
        user = UserModel._default_manager.get(pk=uid)
    except (TypeError, ValueError, OverflowError, UserModel.DoesNotExist):
        user = None

    if user is not None and token_generator.check_token(user, token):
        validlink = True
        title = ('Enter new password')
        if request.method == 'POST':
            form = set_password_form(user, request.POST)
            if form.is_valid():
                form.save()
                return HttpResponseRedirect(post_reset_redirect)
        else:
            form = set_password_form(user)
    else:
        validlink = False
        form = None
        title = ('Password reset unsuccessful')
    context = {
        'form': form,
        'title': title,
        'validlink': validlink,
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)
                            #current_app=current_app)


def password_reset_complete(request,
                            template_name='management/password_reset_complete.html',
                            current_app=None, extra_context=None):
    context = {
        'login_url': resolve_url(settings.base.LOGIN_URL),
        'title': ('Password reset complete'),
    }
    if extra_context is not None:
        context.update(extra_context)
    return TemplateResponse(request, template_name, context)

def terms_and_conditions(request):
    return render(request,'management/terms_and_conditions.html')