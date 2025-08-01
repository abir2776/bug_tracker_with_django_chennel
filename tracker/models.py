from django.db import models

from .choices import ACTION_CHOICES, PRIORITY_CHOICES, STATUS_CHOICES


class Project(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    owner = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="owned_projects"
    )
    members = models.ManyToManyField("core.User", related_name="projects", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name


class Bug(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="Open")
    priority = models.CharField(
        max_length=20, choices=PRIORITY_CHOICES, default="Medium"
    )
    assigned_to = models.ForeignKey(
        "core.User",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="assigned_bugs",
    )
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="bugs")
    created_by = models.ForeignKey(
        "core.User", on_delete=models.CASCADE, related_name="created_bugs"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.project.name}"


class Comment(models.Model):
    bug = models.ForeignKey(Bug, on_delete=models.CASCADE, related_name="comments")
    commenter = models.ForeignKey("core.User", on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Comment on {self.bug.title} by {self.commenter.email}"


class ActivityLog(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="activities"
    )
    bug = models.ForeignKey(
        Bug, on_delete=models.CASCADE, related_name="activities", null=True, blank=True
    )
    user = models.ForeignKey("core.User", on_delete=models.CASCADE)
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.email} {self.action} - {self.description}"
