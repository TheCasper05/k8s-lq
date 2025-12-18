from django.http import HttpResponse
from django.db import connections, OperationalError


def is_app_ready():
    """Verifica si la app está lista para responder"""
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1;")
        return True
    except OperationalError:
        return False


def home(request):
    return HttpResponse("Django is running", status=200)


def health_check(request):
    if not is_app_ready():
        return HttpResponse("starting", status=200)
    return HttpResponse("ok", status=200)


def db_health_check(request):
    try:
        with connections["default"].cursor() as cursor:
            cursor.execute("SELECT 1;")
        return HttpResponse("db ok", status=200)
    except OperationalError:
        return HttpResponse("db error", status=503)
