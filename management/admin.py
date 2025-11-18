from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from management.models import User, Project, ProjectMember, Notification


# Register your models here.
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('email', 'first_name', 'last_name', 'institution', 'department', 'designation', 'is_active', 'is_pi', 'is_staff', 'selected','date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)


    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'is_pi','selected')}),
        #('Important dates', {'fields': ('last_login')}),  #, 'date_joined'
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'institution', 'department', 'designation', 'is_active', 'is_pi', 'is_staff', 'password1','password2'),
        }),
    )
    def has_add_permission(self, request):
        return True
    def has_change_permission(self, request, obj=None):
        return True
    def has_delete_permission(self, request, obj=None):
        return True


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('project_name', 'project_description', 'block_project_id', 'start_date', 'end_date', 'pi', 'is_critical')
    def has_add_permission(self, request):
        return True
    def has_change_permission(self, request, obj=None):
        return True

    def has_delete_permission(self, request, obj=None):
        return True


class ProjectMemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'project', 'is_approved')
    def has_add_permission(self, request):
        return True

class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user','notification_type','message','created_at', 'is_read')
    def has_add_permission(self, request):
        return False
    def has_delete_permission(self, request, obj=None):
        return True

admin.site.register(Project, ProjectAdmin)
admin.site.register(User, UserAdmin)
admin.site.register(ProjectMember, ProjectMemberAdmin)
admin.site.register(Notification, NotificationAdmin)
