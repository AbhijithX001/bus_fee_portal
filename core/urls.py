from django.urls import path
from .views import (
    landing_view,
    login_view,
    logout_view,
    student_dashboard,
    admin_dashboard,
    admin_bus_list,
    admin_bus_students,
    admin_add_student,
    admin_edit_student,
    admin_delete_student,
    admin_view_student_fees,
    admin_fee_update,
    create_razorpay_order,
    verify_payment,
    razorpay_webhook
)

urlpatterns = [
    path("", landing_view, name="landing"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    path("student/dashboard/", student_dashboard, name="student_dashboard"),

    path("admin/dashboard/", admin_dashboard, name="admin_dashboard"),

    path("admin/buses/", admin_bus_list, name="admin_bus_list"),
    path("admin/buses/<int:bus_number>/", admin_bus_students, name="admin_bus_students"),
    path("admin/buses/<int:bus_number>/add/", admin_add_student, name="admin_add_student"),

    path("admin/student/<int:student_id>/edit/", admin_edit_student, name="admin_edit_student"),
    path("admin/student/<int:student_id>/delete/", admin_delete_student, name="admin_delete_student"),

    path("admin/student/<int:student_id>/fees/", admin_view_student_fees, name="admin_view_student_fees"),
    path("admin/student/<int:student_id>/fees/<int:record_id>/update/", admin_fee_update, name="admin_fee_update"),

    path("payment/create-order/", create_razorpay_order, name="create_razorpay_order"),
    path("payment/verify/", verify_payment, name="verify_payment"),
    path("payment/webhook/", razorpay_webhook, name="razorpay_webhook"),
]
