from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from .models import User, Project, ProjectMember
from django.contrib.auth.password_validation import validate_password


class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'institution', 'department', 'designation', 'password1', 'password2','selected']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'institution': forms.TextInput(attrs={'placeholder': 'Institution'}),
            'department': forms.TextInput(attrs={'placeholder': 'Department'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Designation'}),
            'password1': forms.PasswordInput(attrs={'placeholder': 'Password'}),
            'password2': forms.PasswordInput(attrs={'placeholder': 'Confirm Password'}),
        }

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')

        if password1 and password2 and password1 != password2:
            self.add_error('password2', 'Passwords do not match.')

        return cleaned_data

User = get_user_model()
class UserProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'institution', 'department', 'designation', 'selected']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'institution': forms.TextInput(attrs={'placeholder': 'Institution'}),
            'department': forms.TextInput(attrs={'placeholder': 'Department'}),
            'designation': forms.TextInput(attrs={'placeholder': 'Designation'}),
        }
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('A user with that email already exists.')
        return email

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['project_name', 'project_description','start_date', 'end_date', 'block_project_id', 'is_critical']
        widgets = {
            'project_name': forms.TextInput(attrs={'placeholder': 'Name'}),
            'project_description': forms.TextInput(attrs={'placeholder': 'Description'}),
            'block_project_id' : forms.TextInput(attrs={'placeholder': 'LabTrace Project ID'}),
            'start_date': forms.TextInput(attrs={'placeholder': 'Start Date (DD-MM-YYYY)',
                                                 'class': 'datepicker start-date'}),
            'end_date': forms.DateInput(attrs={'placeholder': 'End Date (DD-MM-YYYY)',
                                               'class': 'datepicker end-date'}),
            'is_critical': forms.CheckboxInput(attrs={'label': 'Automated Certification'}),
        }


class MemberForm(forms.ModelForm):
    class Meta:
        model = ProjectMember
        fields = [ 'project']

class PasswordResetForm(forms.Form):
    email = forms.EmailField(label=("Email"), max_length=254)


class SetPasswordForm(forms.Form):
    error_messages = {
        'password_mismatch': ("The two password fields didn't match."),
    }
    new_password1 = forms.CharField(label=("New password"), validators=[validate_password,],
                                    widget=forms.PasswordInput, help_text='Use at least 8 characters with a mix of letters, numbers & symbols')
    new_password2 = forms.CharField(label=("New password confirmation"),validators=[validate_password,],
                                    widget=forms.PasswordInput,help_text='Required')

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(SetPasswordForm, self).__init__(*args, **kwargs)

    def clean_new_password2(self):
        password1 = self.cleaned_data.get('new_password1')
        password2 = self.cleaned_data.get('new_password2')
        if password1 and password2:
            if password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
        return password2

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password1'])
        if commit:
            self.user.save()
        return self.user
