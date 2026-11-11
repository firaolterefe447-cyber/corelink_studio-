from functools import wraps
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect


def crm_login_required(view_func):
    """Custom login requirement that redirects to CRM login instead of admin login."""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect('crm:login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def crm_manager_required(view_func):
    """Require user to be in CRM Manager group."""
    @wraps(view_func)
    @crm_login_required
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.groups.filter(name='CRM Manager').exists():
            raise PermissionDenied("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def marketing_or_manager_required(view_func):
    """Require user to be in Marketing or CRM Manager group."""
    @wraps(view_func)
    @crm_login_required
    def _wrapped_view(request, *args, **kwargs):
        if not (request.user.groups.filter(name='Marketing').exists() or 
                request.user.groups.filter(name='CRM Manager').exists()):
            raise PermissionDenied("You don't have permission to access this page.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def is_crm_manager(user):
    """Check if user is a CRM Manager."""
    return user.is_authenticated and user.groups.filter(name='CRM Manager').exists()


def is_marketing_user(user):
    """Check if user is in Marketing group."""
    return user.is_authenticated and user.groups.filter(name='Marketing').exists()
