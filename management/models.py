from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth.base_user import BaseUserManager, AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models

from django.utils import timezone


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.date_joined = timezone.now()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    institution = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    designation = models.CharField(max_length=255)
    date_joined = models.DateTimeField(default=timezone.now)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_pi = models.BooleanField(default=False)
    selected = models.BooleanField(default=False)
    first_login = models.BooleanField(default=True)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = UserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return '{0} {1}'.format(self.first_name, self.last_name)


class Project(models.Model):
    project_id = models.AutoField(primary_key=True)
    project_name = models.CharField(max_length=255)
    project_description = models.CharField(max_length=255)
    block_project_id = models.CharField(max_length=255)
    start_date = models.DateField()
    end_date = models.DateField()
    pi = models.ForeignKey(User, on_delete=models.CASCADE, related_name='projects')
    is_critical = models.BooleanField(default=False) #critical project or not

    def __str__(self):
        return self.project_name

class ProjectMember(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True,related_name="member_name")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='project_name_for_member')
    is_approved = models.BooleanField(default=False)

    def __int__(self):
        return self.user.id
        #return f"{self.user.id} in {self.project.project_name}"


class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('new_doc', 'New Document'),
        ('new_data', 'New Data'),
        ('new_code', 'New Code'),
        ('new_member', 'New Member'),
        ('add_member', 'Add Member'),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="notifications")
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.full_name} - {self.notification_type}"

