from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.db.models import Q
from django.views.generic import TemplateView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from ...models import ActivityLog, Bug, Comment, Project
from ..serializers.tracker import (
    ActivityLogSerializer,
    BugSerializer,
    CommentSerializer,
    ProjectSerializer,
)


class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["name", "description"]
    ordering_fields = ["name", "created_at"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        return Project.objects.filter(Q(owner=user) | Q(members=user)).distinct()

    @action(detail=True, methods=["post"])
    def add_member(self, request, pk=None):
        project = self.get_object()
        username = request.data.get("username")

        try:
            from core.models import User

            user = User.objects.get(username=username)
            project.members.add(user)
            return Response({"message": f"Added {username} to project"})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )

    @action(detail=True, methods=["delete"])
    def remove_member(self, request, pk=None):
        project = self.get_object()
        username = request.data.get("username")

        try:
            from core.models import User

            user = User.objects.get(username=username)
            project.members.remove(user)
            return Response({"message": f"Removed {username} from project"})
        except User.DoesNotExist:
            return Response(
                {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
            )


class BugViewSet(viewsets.ModelViewSet):
    serializer_class = BugSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [
        DjangoFilterBackend,
        filters.SearchFilter,
        filters.OrderingFilter,
    ]
    filterset_fields = ["status", "priority", "project", "assigned_to"]
    search_fields = ["title", "description"]
    ordering_fields = ["created_at", "updated_at", "priority"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        return Bug.objects.filter(
            Q(project__owner=user) | Q(project__members=user) | Q(created_by=user)
        ).distinct()

    def perform_create(self, serializer):
        bug = serializer.save()
        self._log_activity(bug, "created", f'Bug "{bug.title}" was created')
        self._send_websocket_update(bug, "bug_created")

    def perform_update(self, serializer):
        old_bug = Bug.objects.get(pk=serializer.instance.pk)
        bug = serializer.save()

        # Log specific changes
        changes = []
        if old_bug.status != bug.status:
            changes.append(f"status changed from {old_bug.status} to {bug.status}")
        if old_bug.assigned_to != bug.assigned_to:
            old_assignee = (
                old_bug.assigned_to.username if old_bug.assigned_to else "Unassigned"
            )
            new_assignee = bug.assigned_to.username if bug.assigned_to else "Unassigned"
            changes.append(f"assigned from {old_assignee} to {new_assignee}")

        if changes:
            description = f'Bug "{bug.title}" - {", ".join(changes)}'
            self._log_activity(bug, "updated", description)
            self._send_websocket_update(bug, "bug_updated")

    @action(detail=False, methods=["get"])
    def my_bugs(self, request):
        bugs = self.get_queryset().filter(assigned_to=request.user)
        serializer = self.get_serializer(bugs, many=True)
        return Response(serializer.data)

    def _log_activity(self, bug, action, description):
        ActivityLog.objects.create(
            project=bug.project,
            bug=bug,
            user=self.request.user,
            action=action,
            description=description,
        )

    def _send_websocket_update(self, bug, event_type):
        channel_layer = get_channel_layer()
        group_name = f"project_{bug.project.id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "bug_update",
                "event_type": event_type,
                "bug_id": bug.id,
                "data": BugSerializer(bug).data,
            },
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        bug_id = self.request.query_params.get("bug_id")
        if bug_id:
            return Comment.objects.filter(bug_id=bug_id)

        user = self.request.user
        return Comment.objects.filter(
            Q(bug__project__owner=user) | Q(bug__project__members=user)
        ).distinct()

    def perform_create(self, serializer):
        bug_id = self.request.data.get("bug_id")
        if not bug_id:
            return Response(
                {"error": "bug_id is required"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            bug = Bug.objects.get(id=bug_id)
            comment = serializer.save(bug=bug)

            # Log activity
            ActivityLog.objects.create(
                project=bug.project,
                bug=bug,
                user=self.request.user,
                action="commented",
                description=f'Comment added to bug "{bug.title}"',
            )

            # Send WebSocket notification
            self._send_comment_notification(comment)

        except Bug.DoesNotExist:
            return Response(
                {"error": "Bug not found"}, status=status.HTTP_404_NOT_FOUND
            )

    def _send_comment_notification(self, comment):
        channel_layer = get_channel_layer()
        group_name = f"project_{comment.bug.project.id}"

        async_to_sync(channel_layer.group_send)(
            group_name,
            {
                "type": "comment_added",
                "bug_id": comment.bug.id,
                "data": CommentSerializer(comment).data,
            },
        )


class ActivityLogViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = ActivityLogSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ["project", "action"]
    ordering = ["-created_at"]

    def get_queryset(self):
        user = self.request.user
        return ActivityLog.objects.filter(
            Q(project__owner=user) | Q(project__members=user)
        ).distinct()


class ProjectsView(TemplateView):
    template_name = "tracker/projects.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["page_title"] = "Projects Dashboard"
        return context
