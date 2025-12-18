from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def profile(request):
    """
    Simple profile view so that `/accounts/profile/` resolves and shows
    the current user plus a logout link.
    """
    return render(request, "authentication/profile.html", {"user": request.user})
