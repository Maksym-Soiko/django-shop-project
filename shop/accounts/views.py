from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required
from main.models import Category

def register_view(request):
	if request.user.is_authenticated:
		return redirect("main:product_list")

	categories = Category.objects.all()
	form = UserCreationForm(request.POST or None)

	if request.method == 'POST' and form.is_valid():
		user = form.save()
		login(request, user)
		return redirect("main:product_list")

	return render(request, 'accounts/register.html', {'form': form, 'categories': categories})


def login_view(request):
	if request.user.is_authenticated:
		return redirect("main:product_list")

	categories = Category.objects.all()
	form = AuthenticationForm(request, data=request.POST or None)

	if request.method == 'POST' and form.is_valid():
		login(request, form.get_user())
		return redirect("main:product_list")
	
	return render(request, 'accounts/login.html', {'form': form, 'categories': categories})


def logout_view(request):
	logout(request)
	return redirect("main:product_list")


@login_required
def profile_view(request):
	categories = Category.objects.all()
	return render(request, 'accounts/profile.html', {'categories': categories})


class AdminAccessRedirectMiddleware:
	def __init__(self, get_response):
		self.get_response = get_response

	def __call__(self, request):
		if request.path.startswith('/admin/'):
			user = request.user

			if not user.is_authenticated or not user.is_staff:
				return redirect('main:product_list')
			
		return self.get_response(request)