from django.shortcuts import render


def home(request):
	"""Vista simple que renderiza la plantilla principal de inicio."""
	return render(request, "home.html")
