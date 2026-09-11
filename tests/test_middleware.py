import pytest

from tests.app.models import Author, Book


@pytest.fixture
def books(db):
    for i in range(10):
        author = Author.objects.create(name=f"Author {i}")
        Book.objects.create(title=f"Book {i}", author=author)


def test_flags_n_plus_one_and_points_at_the_view(client, books, caplog):
    response = client.get("/n-plus-one/")

    report = response.wsgi_request.queryscope
    assert len(report.queries) == 11
    [repeated] = report.repeated
    assert repeated.count == 10
    assert "views.py" in repeated.origin and "n_plus_one" in repeated.origin
    assert "N+1: 10x" in caplog.text


def test_select_related_is_clean(client, books, caplog):
    response = client.get("/select-related/")

    report = response.wsgi_request.queryscope
    assert len(report.queries) == 1
    assert not report.has_problems
    assert caplog.text == ""


def test_can_be_disabled(client, books, settings):
    settings.QUERYSCOPE = {"ENABLED": False}
    response = client.get("/n-plus-one/")
    assert not hasattr(response.wsgi_request, "queryscope")
