from django.db import transaction


class ReadReplicaRouter:
    def db_for_read(self, model, **hints):
        # Fuerza sesiones y auth a ir al primary
        if model._meta.app_label in [
            "sessions",
            "auth",
            "admin",
            "contenttypes",
            "account",  # <- Django Allauth
            "socialaccount",  # <- Django Allauth social login
        ]:
            # print("Se leyo en default por que es una sesion, auth, admin o contenttypes")
            return "default"

        # Si hay una transacción activa, usar la base de datos primaria
        # para evitar inconsistencias entre lecturas y escrituras
        if transaction.get_connection().in_atomic_block:
            # print("Se leyo en default por que hay una transaccion activa")
            return "default"

        # print("Se leyo en replica")

        return "replica"

    def db_for_write(self, model, **hints):
        # print("Se escribio en default")
        return "default"

    def allow_relation(self, obj1, obj2, **hints):
        return True

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        return db == "default"


def test_db_router():
    from core.models import Feedback

    print("Testeando write only: ")

    feedback = Feedback.objects.create(message="Test de escritura")
    print(f"Feedback created: {feedback.id}")
    print("Testeando read only: ")
    feedback = Feedback.objects.get(id=feedback.id)
    print(f"Feedback read: {feedback.message}")
    feedback.delete()

    print("Testeando read only en transaccion: ")
    with transaction.atomic():
        feedback = Feedback.objects.create(message="Test de escritura en transaccion")
        print(f"Feedback created: {feedback.id}")
        feedback = Feedback.objects.get(id=feedback.id)
        print(f"Feedback read: {feedback.message}")
        feedback.delete()
