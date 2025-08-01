from django.contrib import admin

from .models import ActivityLog, Bug, Comment, Project


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ["name", "owner", "created_at"]
    list_filter = ["created_at"]
    search_fields = ["name", "description"]
    filter_horizontal = ["members"]


@admin.register(Bug)
class BugAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "project",
        "status",
        "priority",
        "assigned_to",
        "created_by",
        "created_at",
    ]
    list_filter = ["status", "priority", "project", "created_at"]
    search_fields = ["title", "description"]
    raw_id_fields = ["assigned_to", "created_by", "project"]


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ["bug", "commenter", "created_at"]
    list_filter = ["created_at"]
    raw_id_fields = ["bug", "commenter"]


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ["user", "action", "project", "bug", "created_at"]
    list_filter = ["action", "created_at"]
    raw_id_fields = ["user", "project", "bug"]
