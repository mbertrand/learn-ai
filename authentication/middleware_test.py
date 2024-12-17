"""Tests for auth middleware"""

from urllib.parse import quote

import pytest
from django.contrib.sessions.middleware import SessionMiddleware
from django.shortcuts import reverse
from rest_framework import status
from social_core.exceptions import AuthAlreadyAssociated
from social_django.utils import load_backend, load_strategy

from authentication.middleware import (
    SocialAuthExceptionRedirectMiddleware,
)


def test_process_exception_no_strategy(mocker, rf, settings):
    """Tests that if the request has no strategy it does nothing"""
    settings.DEBUG = False
    request = rf.get(reverse("social:complete", args=("email",)))
    middleware = SocialAuthExceptionRedirectMiddleware(mocker.Mock())
    assert middleware.process_exception(request, None) is None


@pytest.mark.skip("No auths for now")
def test_process_exception(mocker, rf, settings):
    """Tests that a process_exception handles auth exceptions correctly"""
    settings.DEBUG = False
    msg = "error message"
    request = rf.get(reverse("social:complete", args=("email",)))
    # social_django depends on request.sesssion, so use the middleware to set that
    SessionMiddleware(mocker.Mock()).process_request(request)
    strategy = load_strategy(request)
    backend = load_backend(strategy, "email", None)
    exc = AuthAlreadyAssociated(backend, msg)
    request.social_strategy = strategy
    request.backend = backend

    middleware = SocialAuthExceptionRedirectMiddleware(mocker.Mock())
    result = middleware.process_exception(request, exc)
    assert result.status_code == status.HTTP_302_FOUND
    assert result.url == "{}?message={}&backend={}".format(
        reverse("login"), quote(str(exc)), backend.name
    )


@pytest.mark.skip("No auths for now")
def test_process_exception_non_auth_error(mocker, rf, settings):
    """Tests that a process_exception handles non-auth exceptions correctly"""
    settings.DEBUG = False
    request = rf.get(reverse("social:complete", args=("email",)))
    # social_django depends on request.sesssion, so use the middleware to set that
    SessionMiddleware(mocker.Mock()).process_request(request)
    strategy = load_strategy(request)
    backend = load_backend(strategy, "email", None)
    request.social_strategy = strategy
    request.backend = backend

    middleware = SocialAuthExceptionRedirectMiddleware(mocker.Mock())
    assert (
        middleware.process_exception(request, Exception("something bad happened"))
        is None
    )