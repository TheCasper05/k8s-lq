# def test_admin_authorized(admin_client: Client) -> None:
#     response = admin_client.get("/admin/", follow=True)

#     if settings.SECURE_SSL_REDIRECT:
#         assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
#     else:
#         assert response.status_code == HTTPStatus.OK
#         assert response.redirect_chain == [] or any(
#             "/admin/" in url for url, _ in response.redirect_chain
#         )

#     response = admin_client.get("/admin/", follow=True)

#     assert len(response.redirect_chain) > 0
#     last_url, last_status = response.redirect_chain[-1]
#     assert "/admin/" in last_url

#     if settings.SECURE_SSL_REDIRECT:
#         assert response.status_code == HTTPStatus.MOVED_PERMANENTLY
#     else:
#         assert response.status_code == HTTPStatus.OK


# def test_admin_unauthorized(client: Client) -> None:
#     """This test ensures that admin panel requires auth."""
#     response = client.get("/admin/")

#     assert response.status_code == HTTPStatus.FOUND


# def test_admin_authorized(admin_client: Client) -> None:
#     """This test ensures that admin panel is accessible."""
#     response = admin_client.get("/admin/")

#     assert response.status_code == HTTPStatus.OK
