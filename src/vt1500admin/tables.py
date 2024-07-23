import django_tables2 as tables
from django_tables2 import TemplateColumn
from django.utils.html import format_html


from .models import Election, Voter

class ElectionTable(tables.Table):

    # actions = tables.Column()#TemplateColumn(template_code='<a href="{% url "election" %}" class="btn btn-success">Details', orderable=False)
    class Meta:
        model = Election
        fields = ['name', 'question', "status", "id"]
        template_name = "django_tables2/bootstrap5-responsive.html"


    def render_id(self, value, record):
        print(value)
        return format_html('<a href="{}" class="btn btn-success">Details', record.id)
        # return ('<a href="{% url "election" record.id %}" class="btn btn-success">Details')


class VotersTable(tables.Table):

    # actions = tables.Column()#TemplateColumn(template_code='<a href="{% url "election" %}" class="btn btn-success">Details', orderable=False)
    class Meta:
        model = Voter
        fields = ['first_name', 'last_name', "email"]
        template_name = "django_tables2/bootstrap5-responsive.html"


    def render_id(self, value, record):
        return format_html('<a href="{}" class="btn btn-success">Details', record.id)