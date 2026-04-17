from django.contrib import admin
from .models import Skill, Artifact, Vote

admin.site.register(Skill)
admin.site.register(Artifact)
admin.site.register(Vote)