import pytest
from django.contrib.auth import get_user_model
from graphene_django.utils.testing import graphql_query
from django.test import RequestFactory

User = get_user_model()


@pytest.fixture
def teacher_user():
    return User.objects.create_user(username="teacher", password="testpass")


@pytest.fixture
def student_user():
    return User.objects.create_user(username="student", password="testpass")


@pytest.fixture
def other_user():
    return User.objects.create_user(username="other", password="testpass")


@pytest.fixture
def client_teacher(client, teacher_user):
    client.force_login(teacher_user)
    return client


@pytest.fixture
def client_student(client, student_user):
    client.force_login(student_user)
    return client


@pytest.fixture
def client_query(request, client):
    def func(*args, **kwargs):
        return graphql_query(*args, **kwargs, client=client, graphql_url="/graphql/")

    return func


@pytest.fixture
def client_query_logged_in(client_teacher, teacher_user):
    def func(*args, **kwargs):
        factory = RequestFactory()
        request = factory.post("/graphql/")
        request.user = teacher_user
        response = graphql_query(
            *args, **kwargs, client=client_teacher, graphql_url="/graphql/"
        )
        return response

    return func
