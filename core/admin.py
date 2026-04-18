from django.contrib import admin
from django.contrib import messages
from .models import Skill, Artifact, Vote


@admin.register(Artifact)
class ArtifactAdmin(admin.ModelAdmin):
    list_display = ('title', 'contributor', 'skill', 'status', 'submitted_at')
    list_filter = ('status', 'skill')
    actions = ['approve_artifacts', 'reject_artifacts']

    @admin.action(description='Approve selected artifacts')
    def approve_artifacts(self, request, queryset):
        queryset.update(status='approved')
        self.message_user(request,
            f"{queryset.count()} artifact(s) approved.", messages.SUCCESS)

    @admin.action(description='Reject selected artifacts')
    def reject_artifacts(self, request, queryset):
        queryset.update(status='rejected')
        self.message_user(request,
            f"{queryset.count()} artifact(s) rejected.", messages.WARNING)


admin.site.register(Skill)
admin.site.register(Vote)