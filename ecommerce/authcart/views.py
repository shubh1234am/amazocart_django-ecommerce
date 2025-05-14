from django.shortcuts import render, redirect
from django.contrib.auth import logout, authenticate, login
from django.contrib.auth.models import User
from django.contrib import messages
from django.core.validators import validate_email
from django.core.exceptions import ValidationError
from django.contrib.auth.decorators import login_required
from authcart.models import UserProfile

# Home View
def home(request):
    return render(request, "base.html")

# Signup View
def signup(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email", "").strip()
        password1 = request.POST.get("password1")
        password2 = request.POST.get("password2")

        try:
            validate_email(email)
        except ValidationError:
            messages.warning(request, "⚠️ Please enter a valid email address.")
            return redirect("signup")

        if password1 != password2:
            messages.error(request, "❌ Passwords do not match!")
            return redirect("signup")

        if len(password1) < 6:
            messages.warning(request, "⚠️ Password must be at least 6 characters.")
            return redirect("signup")

        if User.objects.filter(username=username).exists():
            messages.error(request, "❌ Username already taken.")
            return redirect("signup")

        if User.objects.filter(email=email).exists():
            messages.error(request, "❌ Email already registered.")
            return redirect("signup")

        user = User.objects.create_user(username=username, email=email, password=password1)
        user.save()

        # Create UserProfile
        UserProfile.objects.create(user=user)

        messages.success(request, "✅ Account created! Please log in.")
        return redirect("handlelogin")

    return render(request, "signup.html")

# Login View
def handlelogin(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, "✅ Login successful!")
                return redirect("home")
            else:
                messages.error(request, "❌ Your account is inactive.")
        else:
            messages.error(request, "❌ Invalid credentials.")
        return redirect("handlelogin")

    return render(request, "login.html")

# Logout View
def handlelogout(request):
    logout(request)
    messages.success(request, "✅ Logged out successfully.")
    return redirect("handlelogin")

# Profile View
@login_required(login_url='handlelogin')  # redirect to your login view
def profile_view(request):
    # Get or create profile to avoid DoesNotExist error
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        gender = request.POST.get("gender")
        profile_pic = request.FILES.get("profile_picture")

        if gender:
            profile.gender = gender
        if profile_pic:
            profile.profile_picture = profile_pic

        profile.save()
        messages.success(request, "✅ Profile updated.")

    return render(request, 'profile.html', {
        'user': request.user,
        'profile': profile
    })
