# core/middleware.py
from django.shortcuts import redirect
from django.urls import reverse
from .models import UserOnboarding

from django.urls import resolve, reverse
from django.shortcuts import redirect


class OnboardingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated:
            onboarding, _ = UserOnboarding.objects.get_or_create(user=request.user)
            onboarding.update_step()

            allowed_names = [
                "repository:block_connect",
                "repository:code_connect",
                "repository:doc_connect",
                "repository:data_connect",
                "repository:add_code_repo",
                "repository:add_data_repo",
                "repository:add_doc_repo",
                "management:project_details",
                "management:request_access",
                "management:home",
                "management:login",
                "management:logout",
            ]

            match = resolve(request.path_info)
            if not onboarding.is_complete() and match.view_name not in allowed_names:
                return redirect("management:home")

        return self.get_response(request)
