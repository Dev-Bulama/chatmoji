from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required

def landing_page(request):
    """Landing page view"""
    if request.user.is_authenticated:
        return redirect('chat:dashboard')
    
    return render(request, 'core/landing.html')

@login_required
def dashboard_redirect(request):
    """Redirect to chat dashboard"""
    return redirect('chat:dashboard')