from django.urls import include, path
from rest_framework.routers import DefaultRouter

from ..views import tracker

router = DefaultRouter()
router.register(r"projects", tracker.ProjectViewSet, basename="project")
router.register(r"bugs", tracker.BugViewSet, basename="bug")
router.register(r"comments", tracker.CommentViewSet, basename="comment")
router.register(r"activities", tracker.ActivityLogViewSet, basename="activity")

urlpatterns = [
    path("", include(router.urls)),
]
