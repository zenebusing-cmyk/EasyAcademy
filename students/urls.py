from django.urls import path
from . import views


urlpatterns = [

    path(
    "dashboard/admin/",
    views.admin_dashboard,
    name="admin_dashboard"
    ),

    path(
    "dashboard/admin/students/",
    views.admin_student_list,
    name="admin_student_list"
    ),

    path(
        "login/",
        views.login_choice,
        name="login_choice"
    ),

    path(
        "",
        views.student_list,
        name="student_list"
    ),

    path(
        "add/",
        views.add_student,
        name="add_student"
    ),

    path(
        "success/",
        views.student_success,
        name="student_success"
    ),

    path(
        "<int:student_id>/fees/add/",
        views.add_fee,
        name="add_fee"
    ),

    path(
        "<int:student_id>/",
        views.student_detail,
        name="student_detail"
    ),

    path(
        "fees/success/<int:payment_id>/",
        views.fee_success,
        name="fee_success"
    ),
    
    path(
    "fee-reminders/",
    views.fee_reminders,
    name="fee_reminders"
    ),

    path(
    "login/<str:role>/",
    views.role_login,
    name="role_login"
    ),
]