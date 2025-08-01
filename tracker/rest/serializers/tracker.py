from django.contrib.auth.models import User
from rest_framework import serializers

from ...models import ActivityLog, Bug, Comment, Project


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "username", "email", "first_name", "last_name"]


class ProjectSerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    members = UserSerializer(many=True, read_only=True)
    bug_count = serializers.SerializerMethodField()

    class Meta:
        model = Project
        fields = [
            "id",
            "name",
            "description",
            "owner",
            "members",
            "bug_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_bug_count(self, obj):
        return obj.bugs.count()

    def create(self, validated_data):
        validated_data["owner"] = self.context["request"].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    commenter = UserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ["id", "message", "commenter", "created_at", "updated_at"]
        read_only_fields = ["created_at", "updated_at"]

    def create(self, validated_data):
        validated_data["commenter"] = self.context["request"].user
        return super().create(validated_data)


class BugSerializer(serializers.ModelSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    project_name = serializers.CharField(source="project.name", read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Bug
        fields = [
            "id",
            "title",
            "description",
            "status",
            "priority",
            "assigned_to",
            "project",
            "project_name",
            "created_by",
            "comments",
            "comment_count",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_comment_count(self, obj):
        return obj.comments.count()

    def create(self, validated_data):
        validated_data["created_by"] = self.context["request"].user
        return super().create(validated_data)


class ActivityLogSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = ActivityLog
        fields = ["id", "user", "action", "description", "created_at"]
