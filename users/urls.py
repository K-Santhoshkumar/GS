"""from django.urls import path
from django.contrib.auth import views as auth_views
from .views import employee_view, customer_view, broker_view
from users.views.unauthorized import unauthorized


app_name = "users"

urlpatterns = [
    # Employee URLs
    path("employee/login/", employee_view.employee_login, name="employee_login"),
    # path("employee/register/", employee_view.employee_register, name="employee_register"),
    path("employee/profile/", employee_view.employee_profile, name="employee_profile"),
    path("employee/home/", employee_view.employee_home, name="employee_home"),
    path(
        "employee/send-otp/", employee_view.send_employee_otp, name="send_employee_otp"
    ),
    # Customer URLs
    path("customer/login/", customer_view.customer_login, name="customer_login"),
    path(
        "customer/register/", customer_view.customer_register, name="customer_register"
    ),
    path("customer/profile/", customer_view.customer_profile, name="customer_profile"),
    path("customer/home/", customer_view.customer_home, name="customer_home"),
    path(
        "customer/send-otp/", customer_view.send_customer_otp, name="send_customer_otp"
    ),
    # Broker URLs
    path("broker/login/", broker_view.broker_login, name="broker_login"),
    path("broker/register/", broker_view.broker_register, name="broker_register"),
    path("broker/profile/", broker_view.broker_profile, name="broker_profile"),
    path("broker/home/", broker_view.broker_home, name="broker_home"),
    path("broker/send-otp/", broker_view.send_broker_otp, name="send_broker_otp"),
    path("customer/logout/", customer_view.customer_logout, name="customer_logout"),
    path("broker/logout/", broker_view.broker_logout, name="broker_logout"),
    path("employee/logout/", employee_view.employee_logout, name="employee_logout"),
    path("unauthorized/", unauthorized, name="unauthorized"),
    # Legacy URLs (keeping for backward compatibility)
    # path("create-employee/", views.create_employee, name="create_employee"),
    # path("create-broker/", views.create_broker, name="create_broker"),
    # path("create-customer/", views.create_customer, name="create_customer"),
]
"""
