from django.urls import path, include

app_name = "users"  # ✔ REQUIRED

urlpatterns = [
    path("customer/", include("users.urls.customer_urls")),
    path("broker/", include("users.urls.broker_urls")),
    path("employee/", include("users.urls.employee_urls")),
]
