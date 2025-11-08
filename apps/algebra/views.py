from django.http import JsonResponse


def matmul(request):
	"""Placeholder para multiplicación de matrices.
	Próxima fase: validar dimensiones y delegar en services/matrix.py
	"""
	return JsonResponse({"endpoint": "matmul", "status": "placeholder", "detail": "Implementar lógica en services/"})


def det(request):
	"""Placeholder para cálculo de determinante.
	Próxima fase: usar función optimizada en services/matrix.py
	"""
	return JsonResponse({"endpoint": "det", "status": "placeholder", "detail": "Implementar lógica en services/"})
