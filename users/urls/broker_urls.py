from django.urls import path
from users.views import broker_view
from config.decorators import broker_required
from users.views import broker_profile
from users.views.unauthorized import unauthorized

app_name = "broker"

urlpatterns = [
    # PUBLIC
    path("login/", broker_view.broker_login, name="broker_login"),
    path("register/", broker_view.broker_register, name="broker_register"),
    path(
        "send-otp/",
        broker_view.send_broker_otp,
        name="broker_send_otp",
    ),
    # PROTECTED
    path("home/", broker_required(broker_view.broker_home), name="broker_home"),
    path(
        "profile/",
        broker_required(broker_profile.broker_profile),
        name="broker_profile",
    ),
    path("logout/", broker_required(broker_view.broker_logout), name="broker_logout"),
    path("unauthorized/", unauthorized, name="unauthorized"),
]
