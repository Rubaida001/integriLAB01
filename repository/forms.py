from django import forms
import re
from .models import DocRepositoryConnection, DocRepositoryProject, CodeRepositoryProject, CodeRepositoryConnection, \
    DataRepositoryConnection, DataRepositoryProject, BlockRepositoryConnection
from management.models import Project


class DocRepositoryConnectionForm(forms.ModelForm):
    class Meta:
        model = DocRepositoryConnection
        fields = ['doc_repo_id', 'repo_username', 'git_token']
        widgets = {
            'repo_username': forms.EmailInput(attrs={'placeholder': 'Repository Username'}),
            'git_token': forms.PasswordInput(attrs={'placeholder': 'Git Token'}),
        }


class DocRepositoryProjectForm(forms.ModelForm):
    class Meta:
        model = DocRepositoryProject
        fields = ['document_name','git_link']
        widgets = {
            'document_name': forms.TextInput(attrs={'placeholder': 'Document Name'}),
            'git_link': forms.TextInput(attrs={'placeholder': 'Git Link'}),
        }


class CodeRepositoryConnectionForm(forms.ModelForm):
    class Meta:
        model = CodeRepositoryConnection
        fields = ['code_repo_id', 'repo_username', 'repo_password']
        widgets = {
            'repo_username': forms.TextInput(attrs={'placeholder': 'Repository Username'}),
            'repo_password': forms.PasswordInput(attrs={'placeholder': 'Token'}),
        }

    def clean_repo_password(self):
        password = self.cleaned_data.get('repo_password')
        regex = r'^(gh[ps]_[a-zA-Z0-9]{36}|github_pat_[a-zA-Z0-9]{22}_[a-zA-Z0-9]{59})$'
        if not re.match(regex, password):
            raise forms.ValidationError(
                "The password must match the required format: "
                "'ghp_...' or 'ghs_...' (36 characters) or "
                "'github_pat_...' (22 + 59 characters)."
            )
        return password

    def clean_repo_username(self):
        repo_username = self.cleaned_data['repo_username']
        regex = r'^(?!-)[a-zA-Z0-9-]{1,39}(?<!-)$'
        if not re.match(regex, repo_username):
            raise forms.ValidationError("Invalid GitHub username. Usernames must be 1-39 characters, "
                                        "can contain alphanumeric characters and hyphens, "
                                        "but cannot start or end with a hyphen.")
        return repo_username


class CodeRepositoryProjectForm(forms.ModelForm):
    class Meta:
        model = CodeRepositoryProject
        fields = ['code_repo_name']
        widgets = {
            'code_repo_name': forms.TextInput(attrs={'placeholder': 'Repository Name'}),

        }


class DataRepositoryConnectionForm(forms.ModelForm):
    class Meta:
        model = DataRepositoryConnection
        fields = ['data_repo_id', 'repo_username', 'repo_password', 'data_server']
        widgets = {
            'repo_username': forms.TextInput(attrs={'placeholder': 'Username'}),
            'repo_password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'data_server': forms.PasswordInput(attrs={'placeholder': 'Hostname'}),
        }


class DataRepositoryProjectForm(forms.ModelForm):
    class Meta:
        model = DataRepositoryProject
        fields = ['data_repo_path']
        widgets = {'data_repo_path': forms.TextInput(attrs={'placeholder': 'Repository Path'})}


class BlockRepositoryConnectionForm(forms.ModelForm):
    class Meta:
        model = BlockRepositoryConnection
        fields = ['block_repo_id', 'block_username', 'block_password']
        widgets = {
            'block_username': forms.EmailInput(attrs={'placeholder': 'LabTrace Username'}),
            'block_password': forms.PasswordInput(attrs={'placeholder': 'Password'}),
        }
