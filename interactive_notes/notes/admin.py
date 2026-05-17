from django.contrib import admin
from .models import Notebook, Section, ContentBlock, Collaborator

admin.site.register(Notebook)
admin.site.register(Section)
admin.site.register(ContentBlock)
admin.site.register(Collaborator)
