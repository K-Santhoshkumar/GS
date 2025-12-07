from django.shortcuts import render


def unauthorized(request):
    return render(request, "users/unauthorized.html", status=403)
