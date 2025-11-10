from django.test import TestCase, Client
from django.urls import reverse


class HomeTemplateTests(TestCase):
	def setUp(self):
		self.client = Client()

	def test_home_renders_ok(self):
		resp = self.client.get(reverse("home"))
		self.assertEqual(resp.status_code, 200)
		html = resp.content.decode("utf-8")
		# Chequear presencia de secciones clave
		self.assertIn("Operaciones disponibles", html)
		self.assertIn("Cómo funciona", html)
		# Chequear que carga logo
		self.assertIn("KiwiSolveLogo.png", html)
