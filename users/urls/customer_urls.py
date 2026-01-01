from django.urls import path
from users.views import customer_view
from config.decorators import customer_required
from users.views.customer_profile import customer_profile
from users.views.unauthorized import unauthorized

app_name = "customer"

urlpatterns = [
    # PUBLIC
    path("login/", customer_view.customer_login, name="customer_login"),
    path("register/", customer_view.customer_register, name="customer_register"),
    path("send-otp/", customer_view.send_customer_otp, name="customer_send_otp"),
    # PROTECTED
    path("home/", customer_required(customer_view.customer_home), name="customer_home"),
    path(
        "profile/",
        customer_required(customer_profile),
        name="customer_profile",
    ),
    path(
    "dashboard/",
    customer_required(customer_view.customer_dashboard),
    name="customer_dashboard",
    ),
    path(
        "investments/",
        customer_required(customer_view.customer_investments),
        name="customer_investments",
    ),
    path(
        "logout/",
        customer_required(customer_view.customer_logout),
        name="customer_logout",
    ),
    path("unauthorized/", unauthorized, name="unauthorized"),
]
