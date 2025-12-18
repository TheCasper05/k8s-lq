# core/middleware.py
import os
import json
import time
import logging
import psutil
from contextlib import ExitStack
from django.db import connections
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed


log = logging.getLogger("django.request")


class DBTimer:
    def __init__(self, alias):
        self.alias = alias
        self.count = 0
        self.time = 0.0

    def __call__(self, execute, sql, params, many, context):
        t0 = time.perf_counter()
        try:
            return execute(sql, params, many, context)
        finally:
            self.count += 1
            self.time += time.perf_counter() - t0


try:
    # Para medir CPU por request con precisión
    import resource

    def _proc_cpu_seconds():
        r = resource.getrusage(resource.RUSAGE_SELF)
        return r.ru_utime + r.ru_stime
except Exception:

    def _proc_cpu_seconds():
        # Fallback si no hay resource (Windows)
        p = psutil.Process(os.getpid())
        t = p.cpu_times()
        return (t.user or 0) + (t.system or 0)


def _graphql_info(request):
    """Extrae info útil sin romper el body."""
    # Verificar si es una petición GraphQL (con o sin barra final)
    if "/graphql" not in request.path or "/graphql/" not in request.path:
        return {}

    q = ""
    op = None
    is_intro = False
    depth = None
    try:
        if request.method == "GET":
            q = request.GET.get("query") or ""
            op = request.GET.get("operationName")
        else:
            # request.body en Django es seguro: cachea el body
            data = json.loads(request.body.decode("utf-8") or "{}")
            q = data.get("query") or ""
            op = data.get("operationName")
        is_intro = ("__schema" in q) or ("__type" in q)

        # Estimación ligera de profundidad (sin dependencias raras)
        # cuenta llaves anidadas como proxy de profundidad
        d = m = 0
        for ch in q:
            if ch == "{":
                d += 1
                m = max(m, d)
            elif ch == "}":
                d -= 1 if d > 0 else 0
        depth = m
    except Exception as e:
        # Debug: imprimir el error para ver qué está pasando
        print(f"Error en _graphql_info: {e}")
        pass
    return {
        "gql_len": len(q),
        "gql_op": op,
        "gql_intro": is_intro,
        "gql_depth": depth,
    }


class PerformanceLoggingMiddleware(MiddlewareMixin):
    def __init__(self, get_response):
        super().__init__(get_response)
        self.process = psutil.Process(os.getpid())
        self.cpu_count = psutil.cpu_count(logical=True) or 1

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)
        else:
            # --- Métricas antes ---
            t0 = time.perf_counter()
            cpu0 = _proc_cpu_seconds()
            rss0 = self.process.memory_info().rss

            gql = _graphql_info(request)

            # Medición de DB (todas las conexiones) sin DEBUG=True
            timers = []
            with ExitStack() as stack:
                for conn in connections.all():
                    timer = DBTimer(conn.alias)
                    timers.append(timer)
                    stack.enter_context(conn.execute_wrapper(timer))
                response = self.get_response(request)

            # --- Métricas después ---
            dt_wall = time.perf_counter() - t0
            cpu1 = _proc_cpu_seconds()
            rss1 = self.process.memory_info().rss

            # CPU por request (sum(user+sys) / wall) * 100; puede ser >100% si multi-core
            cpu_sec = max(cpu1 - cpu0, 0.0)
            cpu_pct = (cpu_sec / dt_wall * 100.0) if dt_wall > 0 else 0.0

            # DB agregada
            db_count = sum(t.count for t in timers)
            db_time = sum(t.time for t in timers)

            # Tamaños
            req_len = int(request.META.get("CONTENT_LENGTH") or 0)
            try:
                resp_len = int(response.get("Content-Length") or 0)
            except Exception:
                resp_len = 0

            # Resultado
            log.info(
                (
                    "%s %s %s | %.1fms wall | %.3fs CPU (%.0f%%) | RSS %+d MB (now %.1f MB)"
                    " | DB %d in %.1fms | req %dB -> resp %dB%s%s"
                ),
                request.method,
                request.path,
                response.status_code,
                dt_wall * 1000,
                cpu_sec,
                cpu_pct,
                int((rss1 - rss0) / (1024**2)),
                rss1 / (1024**2),
                db_count,
                db_time * 1000,
                req_len,
                resp_len,
                f" | GQL op={gql.get('gql_op')} depth={gql.get('gql_depth')} len={gql.get('gql_len')}"
                if gql
                else "",
                " | INTROSPECTION" if gql.get("gql_intro") else "",
            )

            return response


class GraphQLJWTMiddleware:
    """Middleware to authenticate GraphQL requests using JWT tokens."""

    def resolve(self, next, root, info, **kwargs):
        request = info.context

        # Skip if already authenticated
        if hasattr(request, "user") and request.user.is_authenticated:
            return next(root, info, **kwargs)

        # Try to authenticate with JWT
        jwt_auth = JWTAuthentication()
        try:
            auth_result = jwt_auth.authenticate(request)
            if auth_result is not None:
                user, token = auth_result
                request.user = user
        except (AuthenticationFailed, Exception):
            # If JWT auth fails, leave user as AnonymousUser
            pass

        return next(root, info, **kwargs)
