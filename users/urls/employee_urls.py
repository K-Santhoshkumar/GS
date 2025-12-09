from django.urls import path
from users.views import employee_profile, employee_view
from config.decorators import employee_required
from users.views.unauthorized import unauthorized

app_name = "employee"

urlpatterns = [
    # PUBLIC
    path("login/", employee_view.employee_login, name="employee_login"),
    path("register/", employee_view.employee_register, name="employee_register"),
    path("send-otp/", employee_view.send_employee_otp, name="employee_send_otp"),
    # PROTECTED
    path("home/", employee_required(employee_view.employee_home), name="employee_home"),
    path(
        "profile/",
        employee_required(employee_profile.employee_profile),
        name="employee_profile",
    ),
    path(
        "logout/",
        employee_required(employee_view.employee_logout),
        name="employee_logout",
    ),
    path("unauthorized/", unauthorized, name="unauthorized"),
]
