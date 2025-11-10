from django.shortcuts import render
from django.http import HttpRequest
from core.steps import Steps
from core.number_mode import configurar_modo_numerico
from .services.matrix import multiplicar_matrices, determinante, sumar_matrices


def _obtener_bool(request: HttpRequest, nombre: str) -> bool:
	return request.POST.get(nombre) in ("1", "true", "True", "on")


def matmul(request: HttpRequest):
	"""Vista de multiplicación de matrices.

	GET: muestra formulario.
	POST: procesa matrices (texto en campos 'A' y 'B').
	Opcional: activar pasos marcando "registrar".
	"""
	contexto = {
		"titulo": "Multiplicación de matrices",
		"resultado": None,
		"error": None,
		"pasos": [],
		"A": request.POST.get("A", "[[1,2],[3,4]]"),
		"B": request.POST.get("B", "[[1,0],[0,1]]"),
		"registrar": False,
	}
	if request.method == "POST":
		registrar = _obtener_bool(request, "registrar")
		contexto["registrar"] = registrar
		steps = Steps() if registrar else None
		res = multiplicar_matrices(request.POST.get("A", ""), request.POST.get("B", ""), steps=steps)
		if res["ok"]:
			contexto["resultado"] = res["datos"]
		else:
			contexto["error"] = res["error"]
		contexto["pasos"] = res["pasos"]
	return render(request, "algebra/matmul.html", contexto)


def det(request: HttpRequest):
	"""Vista de determinante de matriz.

	GET: muestra formulario.
	POST: procesa matriz (texto en campo 'M').
	"""
	contexto = {
		"titulo": "Determinante",
		"resultado": None,
		"error": None,
		"pasos": [],
		"M": request.POST.get("M", "[[2,3],[1,4]]"),
		"registrar": False,
	}
	if request.method == "POST":
		registrar = _obtener_bool(request, "registrar")
		contexto["registrar"] = registrar
		steps = Steps() if registrar else None
		res = determinante(request.POST.get("M", ""), steps=steps)
		if res["ok"]:
			contexto["resultado"] = res["datos"]
		else:
			contexto["error"] = res["error"]
		contexto["pasos"] = res["pasos"]
	return render(request, "algebra/det.html", contexto)


def suma(request: HttpRequest):
	"""Vista de suma de matrices con tamaño dinámico y selección de formato.

	GET: muestra formulario con tamaño por defecto 2x2.
	POST: controla acciones: actualizar tamaño, limpiar, ejemplo, calcular.
	"""
	filas = int(request.POST.get("filas", 2))
	cols = int(request.POST.get("cols", 2))
	formato = request.POST.get("formato", "fraction")  # 'fraction' | 'float'

	# Normalizar límites razonables
	filas = max(1, min(filas, 8))
	cols = max(1, min(cols, 8))

	def _leer_matriz(prefix):
		M = []
		for i in range(filas):
			fila = []
			for j in range(cols):
				fila.append(request.POST.get(f"{prefix}_{i}_{j}", "0"))
			M.append(fila)
		return M

	# Construir por defecto A y B (2x2) si no hay POST
	A_vals = _leer_matriz("A") if request.method == "POST" else [["1", "2"], ["3", "4"]]
	B_vals = _leer_matriz("B") if request.method == "POST" else [["5", "6"], ["7", "8"]]

	accion = request.POST.get("accion")

	error = None
	resultado = None

	# Acciones secundarias
	if accion == "limpiar":
		A_vals = [["0" for _ in range(cols)] for _ in range(filas)]
		B_vals = [["0" for _ in range(cols)] for _ in range(filas)]
	elif accion == "ejemplo":
		import random

		rnd = lambda: str(random.randint(-9, 9))  # números enteros pequeños
		A_vals = [[rnd() for _ in range(cols)] for _ in range(filas)]
		B_vals = [[rnd() for _ in range(cols)] for _ in range(filas)]
	elif accion == "actualizar":
		# sólo ajusta tamaño; A_vals/B_vals ya leídos con nuevas dimensiones
		pass
	elif accion == "calcular":
		# Preparar textos en formato [[...],[...]]
		def a_texto(M):
			filas_txt = ["[" + ",".join(M[i]) + "]" for i in range(filas)]
			return "[" + ",".join(filas_txt) + "]"

		texto_A = a_texto(A_vals)
		texto_B = a_texto(B_vals)

		# Configurar modo numérico de cálculo según formato deseado
		if formato == "float":
			configurar_modo_numerico("float", decimales=6, tolerancia=1e-9)
			modo_salida = "float"
		else:
			configurar_modo_numerico("fraction")
			modo_salida = "fraction"

		res = sumar_matrices(texto_A, texto_B, modo_formato=modo_salida)
		if res["ok"]:
			resultado = res["datos"]
		else:
			error = res["error"]

	contexto = {
		"titulo": "Suma de matrices",
		"filas": filas,
		"cols": cols,
		"formato": formato,
		"A_vals": A_vals,
		"B_vals": B_vals,
		"resultado": resultado,
		"error": error,
	}
	return render(request, "algebra/suma.html", contexto)
