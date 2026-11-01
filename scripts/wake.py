"""
Mantiene despierta la app de Streamlit Community Cloud.

Abre la app con un navegador real (cuenta como tráfico) y, si la encuentra
dormida, pulsa el botón «Yes, get this app back up!». Lo ejecuta GitHub
Actions cada 4 horas (ver .github/workflows/keep-alive.yml).
"""
import os
import sys

from playwright.sync_api import sync_playwright

URL = os.environ.get("APP_URL", "").strip()
if not URL:
    sys.exit("Falta la variable APP_URL (configúrala como secreto o variable del repositorio).")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    page.goto(URL, wait_until="domcontentloaded", timeout=90_000)
    page.wait_for_timeout(8_000)

    wake = page.get_by_role("button", name="Yes, get this app back up!")
    if wake.count() > 0:
        print("La app estaba dormida: despertándola…")
        wake.first.click()
        page.wait_for_timeout(60_000)  # tiempo para que el contenedor arranque
    else:
        print("La app está activa.")

    # Espera a que Streamlit cargue para que la visita cuente como sesión real
    page.wait_for_timeout(15_000)
    print("Título:", page.title())
    browser.close()
