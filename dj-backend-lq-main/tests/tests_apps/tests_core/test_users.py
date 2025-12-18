import pytest
import json

QUERY_READ_STUDENT = """
query readUser($where: FilterUserInput!) {
  readUser(where: $where) {
    id
    username
  }
}
"""


@pytest.mark.django_db
def test_read_user(client_query_logged_in, teacher_user):
    """Un teacher puede ver el perfil de uno de sus students."""
    variables = {"where": {"id": {"exact": str(teacher_user.id)}}}
    response = client_query_logged_in(QUERY_READ_STUDENT, variables=variables)
    content = json.loads(response.content)

    assert "errors" not in content
    user_data = content["data"]["readUser"]
    assert user_data is not None
    assert user_data["id"] == str(teacher_user.id)
    assert user_data["username"] == teacher_user.username
