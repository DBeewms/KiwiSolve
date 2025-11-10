from django.test import TestCase, Client
from django.urls import reverse


class AlgebraViewsTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_matmul_get(self):
		resp = self.client.get(reverse("algebra-matmul"))
		self.assertEqual(resp.status_code, 200)
		self.assertIn("Multiplicación de matrices", resp.content.decode("utf-8"))

	def test_det_get(self):
		resp = self.client.get(reverse("algebra-det"))
		self.assertEqual(resp.status_code, 200)
		self.assertIn("Determinante", resp.content.decode("utf-8"))

	def test_matmul_happy_path(self):
		url = reverse("algebra-matmul")
		resp = self.client.post(url, {
			"A": "[[1,2],[3,4]]",
			"B": "[[2,0],[0,2]]",
		})
		self.assertEqual(resp.status_code, 200)
		html = resp.content.decode("utf-8")
		self.assertIn("Resultado", html)
		# Resultado esperado C = [[2,4],[6,8]] con factores 2
		self.assertIn("2", html)
		self.assertIn("8", html)

	def test_matmul_dim_error(self):
		url = reverse("algebra-matmul")
		resp = self.client.post(url, {
			"A": "[[1,2,3]]",
			"B": "[[1,2],[3,4]]",
		})
		self.assertEqual(resp.status_code, 200)
		html = resp.content.decode("utf-8")
		self.assertIn("Error", html)

	def test_det_happy_path(self):
		url = reverse("algebra-det")
		resp = self.client.post(url, {
			"M": "[[2,3],[1,4]]",
		})
		self.assertEqual(resp.status_code, 200)
		html = resp.content.decode("utf-8")
		# determinante = 2*4 - 3*1 = 5
		self.assertIn("5", html)

	def test_det_error_no_cuadrada(self):
		url = reverse("algebra-det")
		resp = self.client.post(url, {
			"M": "[[1,2,3],[4,5,6]]",
		})
		self.assertEqual(resp.status_code, 200)
		html = resp.content.decode("utf-8")
		self.assertIn("Error", html)

	def test_suma_get(self):
		resp = self.client.get(reverse("algebra-suma"))
		self.assertEqual(resp.status_code, 200)
		html = resp.content.decode("utf-8")
		self.assertIn("Suma de matrices", html)

	def test_suma_happy_path(self):
		url = reverse("algebra-suma")
		# Simular formulario 2x2 con acción calcular
		resp = self.client.post(url, {
			"filas": "2",
			"cols": "2",
			"formato": "fraction",
			"accion": "calcular",
			"A_0_0": "1", "A_0_1": "2", "A_1_0": "3", "A_1_1": "4",
			"B_0_0": "5", "B_0_1": "6", "B_1_0": "7", "B_1_1": "8",
		})
		self.assertEqual(resp.status_code, 200)
		html = resp.content.decode("utf-8")
		# Resultado esperado [[6,8],[10,12]]
		self.assertIn("12", html)

    # Nota: La UI de suma fuerza dimensiones coincidentes, por lo que no se prueba error de dimensiones aquí.
