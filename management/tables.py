import django_tables2 as tables
from .models import User
from django.utils.html import format_html


class ProjectMemberTable(tables.Table):
    # Custom column to combine 'firstname' and 'lastname'
    full_name = tables.LinkColumn("management:add_member", args=[tables.A("pk")], attrs={"a": {
                "style": "color: #36454F; text-decoration: none; font-size: medium"  # Change color and remove underline
            }}, orderable=False)
    date_joined = tables.DateColumn(verbose_name="Date", format="Y-m-d", orderable=False)
    actions = tables.TemplateColumn(
        template_code='<a href="{% url "review_detail" record.id %}" class="btn btn-success">Ver</a>',orderable=False)

    class Meta:
        model = User
        template_name = "django_tables2/bootstrap.html"
        fields = ("date_joined", "full_name")  # Only include fields from the model (not custom ones)
        sequence = ("date_joined", "full_name", "actions")

    def render_actions(self, record):
        return format_html(
            '<a href="{}" class="btn btn-sm btn-success"><i class="fas fa-check"></i></a>  '
            ' <a href="{}" class="btn btn-sm btn-danger"><i class="fas fa-remove"></i></a>',
            f"/edit/{record.id}/",  # Edit button link
            f"/delete/{record.id}/"  # Delete button link
        )
