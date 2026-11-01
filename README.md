# Desde Mi Orilla · Sitio oficial

Podcast intercultural de la **Universidad Bolivariana del Ecuador (UBE)**, postulado al **Desafío Naranja 2026** (Industrias Culturales: podcast y audio).

Sitio construido en Streamlit, con identidad 100 % vectorial, Árbol de Preguntas Heredadas interactivo, video promocional y modo stand para pantalla táctil.

---

## 1. Estructura del repositorio

```
desde-mi-orilla/
├── app.py                         # Sitio completo
├── art.py                         # Ilustraciones vectoriales (orillas, olas, ramas)
├── requirements.txt
├── .streamlit/config.toml         # Tema y opciones del servidor
├── components/arbol.html          # Árbol de Preguntas Heredadas (interactivo)
├── data/
│   ├── preguntas.json             # Orillas y preguntas semilla (editable)
│   └── preguntas_visitantes.json  # Preguntas que deja el público
├── assets/
│   ├── brand/                     # Kit de marca en SVG (logos DMO y UBE)
│   ├── fonts/                     # Playfair Display y DM Sans (woff2, licencia OFL)
│   ├── img/                       # Portadas y diagrama
│   └── video/desde_mi_orilla_promo.mp4
├── scripts/wake.py                # Despertador de la app
└── .github/workflows/keep-alive.yml
```

---

## 2. Publicar en GitHub

**Opción A, desde el navegador (sin instalar nada):**

1. Entra a https://github.com/new
2. Nombre del repositorio: `desde-mi-orilla`. Visibilidad: **Public** (Streamlit Community Cloud gratuito lo requiere para apps públicas).
3. No marques README ni .gitignore (ya vienen en el ZIP). Pulsa **Create repository**.
4. En la página del repo vacío pulsa **uploading an existing file**.
5. Descomprime el ZIP en tu computadora, abre la carpeta `desde-mi-orilla` y **arrastra todo su contenido** (no la carpeta, su contenido) a la ventana de GitHub.
   - Las carpetas ocultas `.streamlit` y `.github` no siempre se ven en Windows/Mac. En Windows: Explorador → Vista → Mostrar → Elementos ocultos. En Mac: `Cmd + Shift + .`
   - Si el navegador no sube las carpetas ocultas, usa la opción B.
6. Mensaje de commit: `Versión inicial del sitio`. Pulsa **Commit changes**.

**Opción B, con Git (recomendado):**

```bash
cd desde-mi-orilla
git init
git add .
git commit -m "Versión inicial del sitio"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/desde-mi-orilla.git
git push -u origin main
```

---

## 3. Desplegar en Streamlit Community Cloud

1. Entra a https://share.streamlit.io e inicia sesión **con la misma cuenta de GitHub**.
2. Pulsa **Create app** → **Deploy a public app from GitHub**.
3. Repository: `TU_USUARIO/desde-mi-orilla` · Branch: `main` · Main file path: `app.py`.
4. **App URL**: escribe `desdemiorilla` para obtener `https://desdemiorilla.streamlit.app` (si está tomado, elige otro y actualiza el paso 5).
5. Abre **Advanced settings**:
   - Python version: **3.12**
   - Secrets: pega esta línea (es la URL que va dentro del código QR):
     ```toml
     APP_URL = "https://desdemiorilla.streamlit.app"
     ```
6. Pulsa **Deploy**. El primer arranque tarda de 2 a 4 minutos.

---

## 4. Que la página nunca se duerma

Streamlit Community Cloud pone a dormir las apps que pasan **12 horas sin visitas**. El repositorio incluye un flujo de GitHub Actions que abre la app con un navegador real cada 4 horas y, si la encuentra dormida, pulsa automáticamente **«Yes, get this app back up!»**.

Actívalo así:

1. En GitHub: **Settings → Secrets and variables → Actions → pestaña Variables → New repository variable**.
   - Name: `APP_URL`
   - Value: `https://desdemiorilla.streamlit.app`
2. Ve a la pestaña **Actions**. Si GitHub pregunta, pulsa **I understand my workflows, go ahead and enable them**.
3. Abre **Mantener activa la app (Streamlit)** → **Run workflow** para probarlo. Debe terminar en verde y mostrar «La app está activa».

**Por qué una visita y no commits vacíos:** cada commit reinicia la app y borraría las preguntas que el público deja en el árbol durante el stand. Una visita con navegador no reinicia nada.

**Dos cuidados:**
- GitHub pausa los flujos programados si el repositorio pasa **60 días sin actividad**. Si recibes el correo de aviso, entra a Actions y pulsa **Enable workflow** (o haz cualquier commit).
- Los cron de GitHub pueden retrasarse algunos minutos; con un ciclo de 4 horas sobra margen frente al umbral de 12 horas.
- **La mañana de cada presentación**, abre la app tú mismo 15 minutos antes como respaldo.

---

## 5. Modo stand (pantalla táctil)

Abre: `https://desdemiorilla.streamlit.app/?stand=1`

Muestra solo el Árbol de Preguntas a pantalla completa y el formulario «Deja una pregunta en la orilla». Pon el navegador en pantalla completa (F11).

> Las preguntas del público se guardan en el servidor mientras la app esté en marcha. Si la app se reinicia (por ejemplo, al subir un cambio a GitHub), vuelven a cero. **No subas cambios durante los días del concurso.**

---

## 6. Editar contenido

| Qué cambiar | Dónde |
|---|---|
| Preguntas y colores de las orillas | `data/preguntas.json` |
| Textos de las secciones | `app.py` (cada sección está marcada con un comentario) |
| Enlaces a UBE TV, YouTube, Instagram | diccionario `LINKS` al inicio de `app.py` |
| Video | reemplaza `assets/video/desde_mi_orilla_promo.mp4` (mismo nombre) |
| Logos | `assets/brand/*.svg` |

Cuando existan los audios reales de cada episodio, el Árbol puede reproducir el fragmento exacto: basta con añadir a cada pregunta un campo `"audio"` con la URL del fragmento (se deja preparado para la temporada piloto).

---

## 7. Probar en tu computadora

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

Coordinación de Innovación y Transferencia del Conocimiento (CITC) · Vicerrectorado de Investigación y Vinculación Social · UBE
