# account/urls.py   (or whatever your app is called)

from django.urls import path
from .views import (
    CreateFirm,
    DeleteFirm,
    GetMemberFirms,
    GetSingleFirm,
    GetMembers,
    AssignTask,
    GetAllTaskMember,
    EditTask,
    DeleteTask,
)

urlpatterns = [
    path("firms/create/", CreateFirm.as_view(), name="create-firm"),
    path("firms/<int:firm_id>/delete/", DeleteFirm.as_view(), name="delete-firm"),
    path("firms/by-user/", GetMemberFirms.as_view(), name="get-member-firms"),
    path("firms/single/", GetSingleFirm.as_view(), name="get-single-firm"),
    path("firms/members/", GetMembers.as_view(), name="get-members"),

    path("tasks/assign/", AssignTask.as_view(), name="assign-task"),
    path("tasks/by-name/", GetAllTaskMember.as_view(), name="get-tasks-by-name"),
    path("tasks/<int:pk>/edit/", EditTask.as_view(), name="edit-task"),
    path("tasks/<int:pk>/delete/", DeleteTask.as_view(), name="delete-task"),
]
