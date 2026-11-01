"""
Desde Mi Orilla — sitio oficial del proyecto
Universidad Bolivariana del Ecuador (UBE) · Desafío Naranja 2026

Ejecutar en local:  streamlit run app.py
"""
from __future__ import annotations

import base64
import html
import io
import json
import threading
import zipfile
from datetime import datetime, timezone
from pathlib import Path

import qrcode
import qrcode.image.svg
import streamlit as st
import streamlit.components.v1 as components

from art import CLAY, DEEP, LAV, SAND, TEAL, leaf_branch, orillas_scene, wave_divider

# ---------------------------------------------------------------------------
# Configuración
# ---------------------------------------------------------------------------
ROOT = Path(__file__).parent
BRAND = ROOT / "assets" / "brand"
IMG = ROOT / "assets" / "img"
VIDEO = ROOT / "assets" / "video" / "desde_mi_orilla_promo.mp4"
DATA = ROOT / "data"

# Cambia esta URL cuando tengas el subdominio definitivo en Streamlit Cloud
try:
    APP_URL = st.secrets.get("APP_URL", "https://desdemiorilla.streamlit.app")
except Exception:
    APP_URL = "https://desdemiorilla.streamlit.app"

LINKS = {
    "ube_tv": "https://ube.edu.ec/UBE_Tv",
    "youtube": "https://www.youtube.com/@ube_ec/podcasts",
    "instagram": "https://www.instagram.com/miorilla.podcast",
    "desafio": "https://desafionaranja.com/sobre.php",
}

st.set_page_config(
    page_title="Desde Mi Orilla · Podcast intercultural de la UBE",
    page_icon=str(BRAND / "favicon.png"),
    layout="wide",
    initial_sidebar_state="collapsed",
)

_lock = threading.Lock()


# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
@st.cache_data
def svg(name: str) -> str:
    return (BRAND / name).read_text(encoding="utf-8")


def svg_uri(markup: str) -> str:
    if "xmlns=" not in markup[:200]:
        markup = markup.replace("<svg", '<svg xmlns="http://www.w3.org/2000/svg"', 1)
    return "data:image/svg+xml;base64," + base64.b64encode(markup.encode("utf-8")).decode()


def svg_img(markup: str, alt: str = "", cls: str = "", style: str = "") -> str:
    """st.html elimina el SVG en línea; lo insertamos como imagen vectorial (data URI)."""
    a = html.escape(alt, quote=True)
    role = "" if alt else ' aria-hidden="true"'
    return f'<img src="{svg_uri(markup)}" alt="{a}"{role} class="{cls}" style="display:block;width:100%;height:auto;{style}">'


def logo(name: str, alt: str = "", style: str = "") -> str:
    return svg_img(svg(name), alt, style=style)


def wave(top, bottom, flip=False):
    return svg_img(wave_divider(top, bottom, flip), "", cls="wave", style="height:90px")


@st.cache_data
def fonts_css() -> str:
    fd = ROOT / "assets" / "fonts"
    def ff(fam, file, style, wmin, wmax):
        b = base64.b64encode((fd / file).read_bytes()).decode()
        return (f"@font-face{{font-family:'{fam}';src:url(data:font/woff2;base64,{b}) format('woff2');"
                f"font-style:{style};font-weight:{wmin} {wmax};font-display:swap}}")
    return "".join([
        ff("Playfair Display", "PlayfairDisplay.woff2", "normal", 400, 900),
        ff("Playfair Display", "PlayfairDisplay-Italic.woff2", "italic", 400, 900),
        ff("DM Sans", "DMSans.woff2", "normal", 100, 1000),
        ff("DM Sans", "DMSans-Italic.woff2", "italic", 100, 1000),
    ])


@st.cache_data
def img_b64(name: str) -> str:
    data = (IMG / name).read_bytes()
    return "data:image/webp;base64," + base64.b64encode(data).decode()


@st.cache_data
def qr_svg(url: str) -> str:
    factory = qrcode.image.svg.SvgPathImage
    q = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=2)
    q.add_data(url)
    q.make(fit=True)
    buf = io.BytesIO()
    q.make_image(image_factory=factory).save(buf)
    s = buf.getvalue().decode()
    s = s[s.find("<svg"):]
    return s.replace('fill="#000000"', f'fill="{TEAL}"')


@st.cache_data
def brand_zip() -> bytes:
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as z:
        for f in sorted(BRAND.glob("*.svg")):
            z.write(f, f"kit-marca-desde-mi-orilla/{f.name}")
    return buf.getvalue()


def seed() -> dict:
    return json.loads((DATA / "preguntas.json").read_text(encoding="utf-8"))


def visitor_questions() -> list[dict]:
    f = DATA / "preguntas_visitantes.json"
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except Exception:
        return []


def add_visitor_question(orilla: str, texto: str, autora: str) -> None:
    f = DATA / "preguntas_visitantes.json"
    with _lock:
        items = visitor_questions()
        items.append({
            "orilla": orilla,
            "tipo": "visitante",
            "texto": texto,
            "autora": autora,
            "fecha": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        })
        f.write_text(json.dumps(items[-300:], ensure_ascii=False, indent=1), encoding="utf-8")


def H(markup: str) -> None:
    """Inserta HTML en el documento principal (sin iframe)."""
    st.html(markup)


# ---------------------------------------------------------------------------
# Estilos globales
# ---------------------------------------------------------------------------
H(f"<style>{fonts_css()}</style>")
H(f"""
<style>
:root{{--teal:{TEAL};--clay:{CLAY};--lav:{LAV};--sand:{SAND};--deep:{DEEP};--paper:#FBF7F0;--ink:#173A45;--muted:#4D6A73;
  --serif:"Playfair Display",Georgia,serif;--sans:"DM Sans",system-ui,-apple-system,sans-serif;--maxw:1180px}}
html,body,.stApp{{background:var(--sand)!important;color:var(--ink);font-family:var(--sans)}}
header[data-testid="stHeader"],[data-testid="stToolbar"],[data-testid="stDecoration"],footer,#MainMenu,[data-testid="stStatusWidget"]{{display:none!important}}
.block-container{{padding:0!important;max-width:100%!important}}
[data-testid="stMainBlockContainer"]{{padding:0!important;max-width:100%!important}}
[data-testid="stVerticalBlock"]{{gap:0!important}}
[data-testid="stElementContainer"]:has(> [data-testid="stHtml"]){{margin:0}}
.stHtml{{width:100%}}
a{{color:inherit}}
:focus-visible{{outline:3px solid var(--lav);outline-offset:3px}}
.wrap{{max-width:var(--maxw);margin:0 auto;padding:0 28px}}
section.s{{padding:96px 0;scroll-margin-top:72px}}
.serif{{font-family:var(--serif)}}
h1,h2,h3{{font-family:var(--serif);font-weight:600;letter-spacing:-.01em;color:inherit;margin:0}}
h2.t{{font-size:clamp(34px,4.6vw,58px);line-height:1.06;max-width:16ch}}
h2.t + p.lead{{margin-top:22px}}
p.lead{{font-size:clamp(18px,1.6vw,21px);line-height:1.6;max-width:60ch;color:var(--muted)}}
p{{line-height:1.65}}
.wave{{display:block;width:100%;height:90px!important}}
/* nav */
.nav{{position:sticky;top:0;z-index:50;background:rgba(243,236,223,.92);backdrop-filter:blur(8px);border-bottom:1px solid rgba(20,69,86,.1)}}
.nav .wrap{{display:flex;align-items:center;justify-content:space-between;height:68px;gap:24px}}
.nav .wm{{width:156px;display:block}}
.nav nav{{display:flex;gap:26px;font-size:15px}}
.nav nav a{{text-decoration:none;color:var(--ink)}}
.nav nav a:hover{{color:var(--clay)}}
.btn{{display:inline-flex;align-items:center;gap:10px;border-radius:999px;padding:14px 24px;font:500 16px var(--sans);text-decoration:none;transition:transform .15s}}
.btn:hover{{transform:translateY(-1px)}}
.btn.p{{background:var(--teal);color:var(--sand)!important}}
.btn.o{{border:1.5px solid var(--teal);color:var(--teal)!important}}
.btn.c{{background:var(--clay);color:#fff!important}}
.nav .btn{{padding:10px 18px;font-size:14px}}
@media (max-width:900px){{.nav nav{{display:none}}}}
/* hero */
.hero{{padding:64px 0 40px}}
.hero .grid{{display:grid;grid-template-columns:1.05fr .95fr;gap:56px;align-items:center}}
.hero h1{{font-size:clamp(42px,5.6vw,84px);line-height:1;letter-spacing:-.02em;color:var(--teal)}}
.hero h1 .promise{{display:block;margin-top:.25em;font-size:.68em;line-height:1.08;font-style:italic;font-weight:500;color:var(--clay)}}
.hero .sub{{font-size:clamp(18px,1.7vw,22px);line-height:1.55;color:var(--muted);max-width:44ch;margin:28px 0 34px}}
.hero .ctas{{display:flex;gap:14px;flex-wrap:wrap}}
.cover{{position:relative;aspect-ratio:1/1;border-radius:28px;overflow:hidden;box-shadow:0 30px 60px -30px rgba(14,51,64,.45)}}
.cover > svg{{position:absolute;inset:0;width:100%;height:100%}}
.cover .logo{{position:absolute;left:15%;right:15%;top:9%}}
.cover .logo img{{filter:drop-shadow(0 1px 0 rgba(243,236,223,.6))}}
.backing{{display:flex;align-items:center;gap:22px;margin-top:56px;padding-top:26px;border-top:1px solid rgba(20,69,86,.15);font-size:15px;color:var(--muted)}}
.backing .ube{{width:190px;flex:none}}
@media (max-width:900px){{.hero .grid{{grid-template-columns:1fr}} .backing{{flex-direction:column;align-items:flex-start}}}}
/* dark sections */
.dark{{background:var(--deep);color:var(--sand)}}
.dark p.lead{{color:rgba(243,236,223,.78)}}
.teal{{background:var(--teal);color:var(--sand)}}
.teal p.lead{{color:rgba(243,236,223,.8)}}
/* problem */
.stat{{display:grid;grid-template-columns:auto 1fr;gap:48px;align-items:end;margin-top:56px}}
.stat .n{{font-family:var(--serif);font-size:clamp(90px,14vw,200px);line-height:.85;color:var(--clay)}}
.stat .n small{{font-size:.45em}}
.facts{{display:grid;grid-template-columns:repeat(3,1fr);gap:40px;margin-top:64px;padding-top:36px;border-top:1px solid rgba(243,236,223,.18)}}
.facts p{{margin:0;font-size:16px;color:rgba(243,236,223,.82)}}
.facts strong{{display:block;font-family:var(--serif);font-weight:500;font-size:22px;color:var(--sand);margin-bottom:10px}}
.src{{font-size:13px;color:rgba(243,236,223,.55);margin-top:40px}}
@media (max-width:900px){{.stat{{grid-template-columns:1fr}} .facts{{grid-template-columns:1fr}}}}
/* idea */
.meet{{display:grid;grid-template-columns:1fr 1.1fr;gap:64px;align-items:center}}
.meet svg.dia{{width:100%;height:auto}}
.chain{{margin-top:30px;padding:26px 28px;border-left:4px solid var(--lav);background:rgba(165,125,183,.1);border-radius:0 16px 16px 0}}
.chain p{{margin:0}}
@media (max-width:900px){{.meet{{grid-template-columns:1fr}}}}
/* orillas */
.or-list{{margin-top:56px;display:grid;gap:0}}
.or{{display:grid;grid-template-columns:90px 1fr 1.4fr;gap:28px;align-items:baseline;padding:30px 0;border-top:1px solid rgba(20,69,86,.15)}}
.or:last-child{{border-bottom:1px solid rgba(20,69,86,.15)}}
.or .k{{font-family:var(--serif);font-size:44px;line-height:1;color:var(--c)}}
.or h3{{font-size:30px;color:var(--teal)}}
.or p{{margin:0;font-family:var(--serif);font-style:italic;font-size:22px;line-height:1.4;color:var(--ink)}}
@media (max-width:760px){{.or{{grid-template-columns:1fr;gap:8px}}}}
.covers{{display:grid;grid-template-columns:repeat(3,1fr);gap:22px;margin-top:56px}}
.covers figure{{margin:0}}
.covers img{{width:100%;border-radius:18px;display:block;box-shadow:0 20px 40px -24px rgba(14,51,64,.5)}}
.covers figcaption{{font-size:14px;color:var(--muted);margin-top:10px}}
@media (max-width:760px){{.covers{{grid-template-columns:1fr}}}}
/* episode bar */
.epbar{{display:flex;margin-top:52px;border-radius:16px;overflow:hidden;min-height:150px}}
.epbar > div{{padding:20px 18px;color:#fff;display:flex;flex-direction:column;justify-content:space-between;gap:10px;min-width:0}}
.epbar b{{font-family:var(--serif);font-weight:600;font-size:20px;line-height:1.2}}
.epbar span{{font-size:14px;opacity:.9;line-height:1.4}}
.epbar em{{font-style:normal;font-size:28px;font-family:var(--serif)}}
@media (max-width:760px){{.epbar{{flex-direction:column}} .epbar > div{{flex:auto!important}}}}
/* ecosystem */
.eco{{display:grid;grid-template-columns:repeat(3,1fr);gap:0;margin-top:56px;border-top:1px solid rgba(243,236,223,.2)}}
.eco a,.eco div.it{{display:block;text-decoration:none;padding:30px 28px 30px 0;border-bottom:1px solid rgba(243,236,223,.2)}}
.eco h3{{font-size:24px;margin-bottom:8px;color:var(--sand)}}
.eco p{{margin:0;font-size:15.5px;color:rgba(243,236,223,.78)}}
.eco a:hover h3{{color:#F4B394}}
.eco .tag{{display:inline-block;margin-top:14px;font-size:13px;padding:4px 10px;border-radius:999px;background:rgba(243,236,223,.12);color:var(--sand)}}
@media (max-width:900px){{.eco{{grid-template-columns:1fr}}}}
/* roadmap */
.road{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin-top:60px;position:relative}}
.road::before{{content:"";position:absolute;left:0;right:0;top:11px;height:3px;background:linear-gradient(90deg,var(--teal),var(--clay),var(--lav))}}
.road > div{{padding:42px 26px 0 0;position:relative}}
.road > div::before{{content:"";position:absolute;top:0;left:0;width:24px;height:24px;border-radius:50%;background:var(--sand);border:4px solid var(--c)}}
.road h3{{font-size:23px;color:var(--teal);margin-bottom:6px}}
.road .when{{font-size:14px;color:var(--clay);font-weight:500;margin-bottom:12px}}
.road p{{margin:0;font-size:15.5px;color:var(--muted)}}
@media (max-width:900px){{.road{{grid-template-columns:1fr 1fr;row-gap:40px}} .road::before{{display:none}}}}
.money{{display:grid;grid-template-columns:1fr 1.25fr;gap:64px;margin-top:80px;align-items:start}}
.bar{{margin:16px 0 0}}
.bar .row{{display:grid;grid-template-columns:1fr auto;font-size:15.5px;margin-bottom:6px}}
.bar .track{{height:14px;border-radius:99px;background:rgba(20,69,86,.1);overflow:hidden;margin-bottom:22px}}
.bar .fill{{height:100%;border-radius:99px}}
.total{{font-family:var(--serif);font-size:56px;color:var(--teal);line-height:1}}
.kpis{{display:grid;grid-template-columns:repeat(3,1fr);gap:30px 26px}}
.kpis div b{{display:block;font-family:var(--serif);font-weight:600;font-size:40px;color:var(--clay);line-height:1.05}}
.kpis div span{{font-size:15px;color:var(--muted)}}
@media (max-width:900px){{.money{{grid-template-columns:1fr}} .kpis{{grid-template-columns:1fr 1fr}}}}
/* allies */
.allies{{display:grid;grid-template-columns:repeat(4,1fr);gap:36px;margin-top:48px}}
.allies h3{{font-family:var(--sans);font-size:15px;font-weight:700;color:var(--teal);margin-bottom:12px}}
.allies ul{{list-style:none;padding:0;margin:0;font-size:15.5px;line-height:1.75;color:var(--ink)}}
@media (max-width:900px){{.allies{{grid-template-columns:1fr 1fr}}}}
/* ethics */
.ethics{{display:grid;grid-template-columns:repeat(4,1fr);gap:26px;margin-top:44px}}
.ethics div{{border-top:3px solid var(--c);padding-top:16px}}
.ethics b{{display:block;font-size:17px;margin-bottom:6px;color:var(--sand)}}
.ethics span{{font-size:15px;color:rgba(243,236,223,.78);line-height:1.55}}
@media (max-width:900px){{.ethics{{grid-template-columns:1fr 1fr}}}}
/* footer */
.foot{{background:var(--deep);color:var(--sand);padding:80px 0 40px}}
.foot .grid{{display:grid;grid-template-columns:1.3fr 1fr 180px;gap:48px;align-items:start}}
.foot .qr{{background:var(--sand);border-radius:16px;padding:12px}}
.foot .qr svg{{width:100%;height:auto;display:block}}
.foot small{{display:block;color:rgba(243,236,223,.55);font-size:13px;margin-top:44px;padding-top:22px;border-top:1px solid rgba(243,236,223,.15)}}
@media (max-width:900px){{.foot .grid{{grid-template-columns:1fr}}}}
/* streamlit widgets inside sections */
.stForm{{border:0!important;padding:0!important}}
[data-testid="stForm"]{{background:var(--paper);border:1px solid rgba(20,69,86,.12)!important;border-radius:22px!important;padding:30px 30px 22px!important}}
.stTextArea textarea,.stTextInput input{{font-family:var(--sans)!important;font-size:17px!important;background:#fff!important;border-radius:12px!important}}
label p{{font-size:15px!important;color:var(--ink)!important;font-weight:500!important}}
.stFormSubmitButton button,.stDownloadButton button{{background:var(--clay)!important;color:#fff!important;border:0!important;border-radius:999px!important;padding:12px 26px!important;font:500 16px var(--sans)!important}}
.stFormSubmitButton button:hover,.stDownloadButton button:hover{{filter:brightness(1.05)}}
[data-testid="stVideo"],video{{border-radius:22px;overflow:hidden;width:100%}}
.st-key-pad-form,.st-key-pad-video,.st-key-pad-kit{{max-width:var(--maxw);margin:0 auto;padding:0 28px}}
.st-key-pad-form [data-testid="stVerticalBlock"],.st-key-pad-kit [data-testid="stVerticalBlock"]{{gap:14px!important}}
.st-key-bg-video{{background:var(--deep)}}
.st-key-bg-arbol{{background:var(--deep)}}
.st-key-bg-form{{background:var(--sand);padding:0 0 96px}}
.st-key-bg-kit{{background:var(--deep);padding:0 0 10px}}
iframe{{display:block}}
@media (max-width:900px){{.kitg{{grid-template-columns:1fr!important}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
</style>
""")

stand_mode = st.query_params.get("stand") == "1"
data = seed()
orillas = data["orillas"]
orilla_by_id = {o["id"]: o for o in orillas}

# ---------------------------------------------------------------------------
# Modo stand: pantalla táctil con el Árbol a pantalla completa
# ---------------------------------------------------------------------------
def render_arbol(height: int) -> None:
    preguntas = data["preguntas"] + [
        {**q, "autora": f"Pregunta dejada por {q['autora']}" if q.get("autora") else "Pregunta dejada por una visitante"}
        for q in visitor_questions()[-40:]
    ]
    payload = json.dumps({"orillas": orillas, "preguntas": preguntas}, ensure_ascii=False).replace("</", "<\\/")
    tpl = (ROOT / "components" / "arbol.html").read_text(encoding="utf-8")
    page = tpl.replace("__FONTS__", fonts_css()).replace("__DATA__", payload).replace("__HEIGHT__", str(height))
    if hasattr(st, "iframe"):          # Streamlit >= 1.5x
        st.iframe(page, height=height)
    else:                               # compatibilidad con versiones anteriores
        components.html(page, height=height, scrolling=False)


def question_form(key: str) -> None:
    with st.form(key, clear_on_submit=True):
        texto = st.text_area(
            "Tu pregunta para la siguiente mujer que se siente frente al micrófono",
            max_chars=200, height=110, placeholder="Escribe una pregunta que te gustaría heredar a otra mujer…",
        )
        c1, c2 = st.columns([1, 1])
        with c1:
            ori = st.selectbox("¿Desde qué orilla preguntas?", [o["id"] for o in orillas],
                               format_func=lambda i: orilla_by_id[i]["name"])
        with c2:
            autora = st.text_input("Tu nombre o país (opcional)", max_chars=40, placeholder="Ej.: Ana, Santo Domingo")
        ok = st.form_submit_button("Dejar mi pregunta en el árbol")
    if ok:
        clean = " ".join(texto.split())
        if len(clean) < 8:
            st.warning("Escribe una pregunta de al menos 8 caracteres para que podamos sumarla al árbol.")
        else:
            if not clean.endswith("?"):
                clean = clean + "?"
            if not clean.startswith("¿"):
                clean = "¿" + clean
            add_visitor_question(ori, clean, " ".join(autora.split()) or "una visitante")
            st.success("Tu pregunta ya está en el árbol. Búscala como un punto claro en la rama de "
                       f"{orilla_by_id[ori]['name']}.")
            st.rerun()


if stand_mode:
    H(f"""<div style="background:{DEEP};padding:22px 28px;display:flex;align-items:center;justify-content:space-between;gap:20px">
      <div style="width:220px">{logo('dmo_wordmark_blanco.svg', "Desde Mi Orilla")}</div>
      <div style="color:{SAND};font:500 18px var(--sans)">Toca una pregunta. Escúchala. Deja la tuya.</div>
      <div style="width:150px">{logo('ube_horizontal_blanco.svg', "Universidad Bolivariana del Ecuador")}</div></div>""")
    with st.container(key="bg-arbol"):
        render_arbol(640)
    with st.container(key="bg-form"):
        H('<div class="wrap" style="padding-top:40px"><h2 class="t" style="color:var(--teal);font-size:40px;max-width:none">Deja una pregunta en la orilla</h2></div>')
        with st.container(key="pad-form"):
            question_form("stand_form")
    st.stop()

# ---------------------------------------------------------------------------
# Navegación + Hero
# ---------------------------------------------------------------------------
H(f"""
<div class="nav"><div class="wrap">
  <a href="#inicio" class="wm" aria-label="Desde Mi Orilla, inicio">{logo('dmo_wordmark.svg', "Desde Mi Orilla")}</a>
  <nav aria-label="Secciones">
    <a href="#problema">Por qué</a><a href="#idea">La idea</a><a href="#orillas">Las orillas</a>
    <a href="#arbol">Árbol de Preguntas</a><a href="#plataforma">Plataforma UBE</a><a href="#vision">Si ganamos</a>
  </nav>
  <a class="btn p" href="#video">Ver el video</a>
</div></div>

<section class="hero" id="inicio"><div class="wrap">
  <div class="grid">
    <div>
      <h1>Nadie conoce sus nombres. <span class="promise">Muy pronto, el mundo entero los va a pronunciar.</span></h1>
      <p class="sub">Son médicas, maestras, ingenieras, artesanas, parteras y lideresas que sostienen al Ecuador en silencio. Desde Mi Orilla, el podcast intercultural de la UBE, les entrega el micrófono para que su voz cruce fronteras.</p>
      <div class="ctas">
        <a class="btn p" href="#video">Ver el video</a>
        <a class="btn o" href="#arbol">Explorar el Árbol de Preguntas</a>
      </div>
    </div>
    <div class="cover">
      {svg_img(orillas_scene(idp="hero", leaf_left=False), "", cls="scene", style="position:absolute;inset:0;height:100%")}
      <div class="logo">{logo('dmo_logo.svg', "Desde Mi Orilla")}</div>
    </div>
  </div>
  <div class="backing">
    <div class="ube">{logo('ube_horizontal.svg', "Universidad Bolivariana del Ecuador")}</div>
    <div>Una iniciativa de estudiantes de la UBE, dirigida por la Coordinación de Innovación y Transferencia del Conocimiento (CITC), Vicerrectorado de Investigación y Vinculación Social. Postulada al Desafío Naranja 2026, vertical Industrias Culturales: podcast y audio.</div>
  </div>
</div></section>
{wave(SAND, DEEP)}
""")

# ---------------------------------------------------------------------------
# Video
# ---------------------------------------------------------------------------
with st.container(key="bg-video"):
    H("""<section class="s" id="video" style="padding-bottom:40px;color:var(--sand)"><div class="wrap">
      <h2 class="t">Ochenta segundos para conocerlas</h2>
      <p class="lead" style="color:rgba(243,236,223,.78)">El video oficial del proyecto, preparado para el Desafío Naranja 2026 en Santo Domingo.</p>
    </div></section>""")
    with st.container(key="pad-video"):
        if VIDEO.exists():
            st.video(str(VIDEO), loop=False)
        else:
            st.info("Sube el archivo assets/video/desde_mi_orilla_promo.mp4 para mostrar el video aquí.")

# ---------------------------------------------------------------------------
# Problema
# ---------------------------------------------------------------------------
H(f"""
<section class="s dark" id="problema"><div class="wrap">
  <h2 class="t">Existen. Trabajan. Transforman. Y casi nadie las escucha.</h2>
  <div class="stat">
    <div class="n">51,3<small>%</small></div>
    <p class="lead" style="margin:0">de la población del Ecuador son mujeres. Sin embargo, su presencia como fuentes, protagonistas y productoras de conocimiento en los medios sigue siendo escasa, y las mujeres indígenas suelen aparecer en papeles secundarios.</p>
  </div>
  <div class="facts">
    <p><strong>Voces fragmentadas</strong>Cuando aparecen, las historias de mujeres afroecuatorianas, indígenas, montubias, rurales y urbanas se cuentan por separado, o desde una sola mirada.</p>
    <p><strong>Saberes que se pierden</strong>Sin espacios de encuentro, se rompen los puentes entre generaciones y culturas que podrían generar comprensión mutua.</p>
    <p><strong>Jóvenes sin referentes</strong>Las personas de 16 a 30 años crecen con pocos relatos que reflejen la diversidad real de ser mujer en el país.</p>
  </div>
  <p class="src">Fuentes: INEC (2023); Consejo de Comunicación (2019); Coronado-Otavalo et al. (2025), Historia y Comunicación Social, 30(2).</p>
</div></section>
{wave(DEEP, SAND, flip=True)}
""")

# ---------------------------------------------------------------------------
# La idea
# ---------------------------------------------------------------------------


H(f"""
<section class="s" id="idea"><div class="wrap meet">
  <div>{svg_img((IMG / "encuentro.svg").read_text(encoding="utf-8"), "Dos mujeres desde orillas distintas se encuentran en una misma pregunta")}</div>
  <div>
    <h2 class="t" style="color:var(--teal)">Dos mujeres. Dos orillas. Una misma pregunta.</h2>
    <p class="lead">No es un podcast de entrevistas. Cada episodio reúne a dos mujeres que normalmente no se encontrarían —distintas por cultura, generación o territorio— y las une una pregunta. La diferencia no se suaviza: es el motor de la conversación.</p>
    <div class="chain"><p><strong class="serif" style="font-size:21px;color:var(--teal)">La pregunta que heredamos.</strong><br>Cada invitada cierra su episodio dejando una pregunta para la siguiente. Así nace una cadena de voces que atraviesa toda la temporada y se convierte en el Árbol de Preguntas Heredadas.</p></div>
  </div>
</div></section>
""")

# ---------------------------------------------------------------------------
# Las cinco orillas
# ---------------------------------------------------------------------------
rows = "".join(
    f'<div class="or" style="--c:{o["color"] if o["id"] not in ("identidad",) else TEAL}"><div class="k">{o["ep"]}</div>'
    f'<h3>{o["name"]}</h3><p>{html.escape(next(q["texto"] for q in data["preguntas"] if q["orilla"]==o["id"] and q["tipo"]=="central"))}</p></div>'
    for o in orillas
)
H(f"""
<section class="s" id="orillas" style="padding-top:20px"><div class="wrap">
  <h2 class="t" style="color:var(--teal)">Una temporada piloto, cinco orillas</h2>
  <p class="lead">Cinco episodios principales y un especial de cierre. Quincenales, de 35 a 45 minutos, con cápsulas en kichwa y shuar para radios comunitarias.</p>
  <div class="or-list">{rows}</div>
  <div class="covers">
    <figure><img src="{img_b64('portada_general.webp')}" alt="Portada general del podcast Desde Mi Orilla" loading="lazy"><figcaption>Portada general del podcast</figcaption></figure>
    <figure><img src="{img_b64('portada_ep01_identidad.webp')}" alt="Portada del episodio 01, Identidad" loading="lazy"><figcaption>Episodio 01: Identidad</figcaption></figure>
    <figure><img src="{img_b64('portada_ep02_oportunidades.webp')}" alt="Portada del episodio sobre Oportunidades" loading="lazy"><figcaption>Episodio: Oportunidades</figcaption></figure>
  </div>
  <h3 style="font-size:30px;color:var(--teal);margin-top:90px">Así suena un episodio</h3>
  <div class="epbar" role="list" aria-label="Estructura de un episodio de 40 minutos">
    <div role="listitem" style="flex:10;background:{TEAL}"><em>10′</em><b>El Encuentro</b><span>Cada invitada expone su orilla frente a la pregunta central.</span></div>
    <div role="listitem" style="flex:20;background:#2E6E7E"><em>20′</em><b>La Marea</b><span>Diálogo horizontal: de las historias personales a lo que tienen en común.</span></div>
    <div role="listitem" style="flex:8;background:{CLAY}"><em>8′</em><b>La pregunta que heredamos</b><span>Responden la pregunta anterior y dejan una nueva.</span></div>
    <div role="listitem" style="flex:4;background:{LAV}"><em>2′</em><b>Eco</b><span>Invitación al Árbol.</span></div>
  </div>
</div></section>
{wave(SAND, DEEP)}
""")

# ---------------------------------------------------------------------------
# Árbol de Preguntas Heredadas
# ---------------------------------------------------------------------------
with st.container(key="bg-arbol"):
    H("""<section class="s dark" id="arbol" style="padding-bottom:36px"><div class="wrap">
      <h2 class="t">El Árbol de Preguntas Heredadas</h2>
      <p class="lead">Nuestra pieza de tecnología y arte. Cada pregunta que una invitada deja al cierre de su episodio se convierte en un punto del árbol; al tocarlo se escucha su voz. Temporada tras temporada, el árbol crece y se vuelve un archivo vivo de memoria oral de mujeres del Ecuador.</p>
    </div></section>""")
    render_arbol(600)
    H(f"<div style='height:30px;background:{DEEP}'></div>{wave(DEEP, SAND, flip=True)}")

with st.container(key="bg-form"):
    H("""<div class="wrap" style="padding:30px 28px 26px"><h2 class="t" style="color:var(--teal);font-size:clamp(30px,3.6vw,44px);max-width:22ch">Deja tu pregunta en la orilla</h2>
    <p class="lead">Escribe la pregunta que le harías a una mujer de otra cultura u otra generación. Aparecerá en el árbol como un punto claro.</p></div>""")
    with st.container(key="pad-form"):
        question_form("main_form")

# ---------------------------------------------------------------------------
# Plataforma UBE: no empezamos desde cero
# ---------------------------------------------------------------------------
H(f"""
{wave(SAND, TEAL)}
<section class="s teal" id="plataforma"><div class="wrap">
  <h2 class="t">No empezamos desde cero</h2>
  <p class="lead">Desde Mi Orilla arranca con una plataforma tecnológica y de medios que ya funciona. La UBE pone su infraestructura al servicio de estas voces desde el primer episodio, con costo fijo cero en estudio y personal base.</p>
  <div class="eco">
    <div class="it"><h3>Sala de podcast UBE</h3><p>Estudio y equipos de grabación de la universidad, operativos desde el día uno.</p><span class="tag">Disponible</span></div>
    <a href="{LINKS['ube_tv']}" target="_blank" rel="noopener"><h3>UBE TV</h3><p>El canal de la universidad donde se desarrollarán los programas piloto.</p><span class="tag">Canal de televisión</span></a>
    <a href="{LINKS['youtube']}" target="_blank" rel="noopener"><h3>YouTube UBE Podcasts</h3><p>Videopodcast completo y clips para la audiencia de 16 a 30 años.</p><span class="tag">@ube_ec</span></a>
    <a href="{LINKS['instagram']}" target="_blank" rel="noopener"><h3>Instagram del podcast</h3><p>Clips verticales subtitulados, adelantos y comunidad entre episodios.</p><span class="tag">@miorilla.podcast</span></a>
    <div class="it"><h3>Radio y territorio</h3><p>Cápsulas de 5 minutos en kichwa y shuar para radios comunitarias, con La Batucada y su frecuencia radial.</p><span class="tag">Aliado radial</span></div>
    <div class="it"><h3>Spotify y redes UBE</h3><p>Audio en plataformas de streaming, y difusión por las redes y canales de mensajería de la universidad.</p><span class="tag">Transmedia</span></div>
  </div>
  <div class="ethics">
    <div style="--c:{SAND}"><b>Voces en primera persona</b><span>Ellas narran su propia realidad, sin intermediarios.</span></div>
    <div style="--c:{CLAY}"><b>Consentimiento informado</b><span>Alineado con el Convenio 169 de la OIT, con revisión del corte final y derecho a réplica.</span></div>
    <div style="--c:{LAV}"><b>Reciprocidad</b><span>Becas de conectividad, insumos y coautoría en investigaciones para sus colectivos.</span></div>
    <div style="--c:#8DB97C"><b>Accesibilidad</b><span>Transcripciones, subtítulos y una web que apunta a WCAG 2.2 AA.</span></div>
  </div>
</div></section>
{wave(TEAL, SAND, flip=True)}
""")

# ---------------------------------------------------------------------------
# Visión: si ganamos
# ---------------------------------------------------------------------------
def bar(label, amount, total, color):
    pct = amount / total * 100
    return (f'<div class="row"><span>{label}</span><b>US$ {amount:,.2f}</b></div>'
            f'<div class="track"><div class="fill" style="width:{pct:.1f}%;background:{color}"></div></div>')

TOTAL = 4125.50
H(f"""
<section class="s" id="vision"><div class="wrap">
  <h2 class="t" style="color:var(--teal);max-width:20ch">Si ganamos, estas voces tendrán su propia casa</h2>
  <p class="lead">Hoy tenemos la plataforma de la UBE. Con el Desafío Naranja damos el salto: equipos para grabar en cualquier territorio, un equipo profesional que dirija el proyecto y una plataforma propia para la comunidad de mujeres que lo dan todo.</p>
  <div class="road">
    <div style="--c:{TEAL}"><div class="when">Hoy</div><h3>Plataforma UBE</h3><p>Sala de podcast, UBE TV, YouTube y redes. Marca, portadas, metodología y prototipo del Árbol listos.</p></div>
    <div style="--c:#2E6E7E"><div class="when">Abril a julio 2027</div><h3>Temporada piloto</h3><p>Seis episodios, doce voces, cápsulas en kichwa y shuar e informe de impacto.</p></div>
    <div style="--c:{CLAY}"><div class="when">Agosto 2027 a enero 2028</div><h3>Expansión nacional</h3><p>Grabaciones en la Sierra Centro y la Amazonía Sur con equipo portátil 4K.</p></div>
    <div style="--c:{LAV}"><div class="when">Visión</div><h3>Plataforma propia</h3><p>Estudio, equipo profesional y temporadas hermanas con universidades de la red iberoamericana.</p></div>
  </div>
  <div class="money">
    <div>
      <p style="margin:0;color:var(--muted)">Inversión total estimada</p>
      <div class="total">US$ 4.125,50</div>
      <div class="bar" style="margin-top:28px">
        {bar('Fase 1: temporada piloto (4 meses)', 1000, TOTAL, TEAL)}
        {bar('Fase 2: expansión nacional (6 meses)', 1500, TOTAL, CLAY)}
        {bar('Equipamiento portátil reutilizable', 1625.50, TOTAL, LAV)}
      </div>
      <p style="font-size:14px;color:var(--muted)">Estudio y personal base: US$ 0, cubiertos por la UBE. Montos referenciales sujetos a cotización.</p>
    </div>
    <div>
      <p style="margin:0 0 22px;color:var(--muted)">Metas de la temporada piloto</p>
      <div class="kpis">
        <div><b>12</b><span>voces de mujeres visibilizadas</span></div>
        <div><b>≥ 5</b><span>provincias o territorios de origen</span></div>
        <div><b>4</b><span>identidades: indígena, afro, montubia y mestiza</span></div>
        <div><b>100 %</b><span>de episodios con cápsula en kichwa o shuar</span></div>
        <div><b>≥ 500</b><span>reproducciones por episodio a 30 días</span></div>
        <div><b>≥ 6</b><span>colectivos apoyados con reciprocidad</span></div>
      </div>
    </div>
  </div>
</div></section>
""")

# ---------------------------------------------------------------------------
# Aliados
# ---------------------------------------------------------------------------
H(f"""
<section class="s" id="aliados" style="padding-top:0"><div class="wrap">
  <h2 class="t" style="color:var(--teal);font-size:clamp(30px,3.6vw,44px)">Una red que ya está en marcha</h2>
  <p class="lead">Alianzas en gestión desde septiembre de 2026 y en proceso de formalización.</p>
  <div class="allies">
    <div><h3>Universidad</h3><ul><li>UBE, socio ancla</li><li>CITC y sus programas RAÍCES, UBE Violeta y Maker Women STEM</li><li>CRAI de la UBE</li></ul></div>
    <div><h3>Organizaciones de mujeres</h3><ul><li>Mujeres de Asfalto</li><li>Afroamérica XXI</li><li>FEMUAFRO</li><li>Palenque Libre por Derecho</li><li>Fundación Mintaimi</li><li>Warmi Imbabura</li><li>Red de Mujeres Rurales del Ecuador</li></ul></div>
    <div><h3>Comunicación y radio</h3><ul><li>Consejo de Comunicación</li><li>La Batucada, frecuencia radial ganada en concurso de la Casa de la Cultura</li></ul></div>
    <div><h3>Empresa y cultura</h3><ul><li>Clorox León, empresa aliada</li><li>Moda intercultural, modistas y artistas aliados</li></ul></div>
  </div>
</div></section>
""")

# ---------------------------------------------------------------------------
# Kit de marca + Footer
# ---------------------------------------------------------------------------
with st.container(key="bg-kit"):
    H(f"""<div class="wrap" style="padding:80px 28px 24px;color:var(--sand)">
      <div style="display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:48px;align-items:center" class="kitg">
        <div style="max-width:440px">{logo('dmo_logo_blanco.svg', "Desde Mi Orilla")}</div>
        <div><h2 class="t" style="font-size:clamp(30px,3.4vw,42px)">Sus historias merecen ser escuchadas</h2>
        <p class="lead" style="color:rgba(243,236,223,.78)">Desde mi orilla, hacia el mundo. Descarga el kit de marca vectorial para prensa, jurado y aliados.</p></div>
      </div></div>""")
    with st.container(key="pad-kit"):
        st.download_button("Descargar kit de marca (SVG)", brand_zip(), "kit-marca-desde-mi-orilla.zip", "application/zip")

H(f"""
<div class="foot" role="contentinfo"><div class="wrap">
  <div class="grid">
    <div>
      <div style="width:230px">{logo('ube_horizontal_blanco.svg', "Universidad Bolivariana del Ecuador")}</div>
      <p style="color:rgba(243,236,223,.75);max-width:46ch;margin-top:22px">Coordinación de Innovación y Transferencia del Conocimiento (CITC)<br>Vicerrectorado de Investigación y Vinculación Social<br>Universidad Bolivariana del Ecuador · Durán, Guayas</p>
    </div>
    <div>
      <p style="margin:0 0 10px;font-weight:500">Síguenos</p>
      <p style="margin:0;line-height:2"><a href="{LINKS['instagram']}" target="_blank" rel="noopener">Instagram @miorilla.podcast</a><br>
      <a href="{LINKS['youtube']}" target="_blank" rel="noopener">YouTube UBE Podcasts</a><br>
      <a href="{LINKS['ube_tv']}" target="_blank" rel="noopener">UBE TV</a><br>
      <a href="{LINKS['desafio']}" target="_blank" rel="noopener">Desafío Naranja</a></p>
    </div>
    <div><div class="qr">{svg_img(qr_svg(APP_URL), "Código QR del sitio")}</div>
      <p style="font-size:13px;color:rgba(243,236,223,.65);margin-top:10px">Escanea para abrir el sitio</p></div>
  </div>
  <small>© 2026 Desde Mi Orilla. Universidad Bolivariana del Ecuador. Preguntas de muestra en el Árbol: ilustrativas hasta la grabación de la temporada piloto.</small>
</div></div>
""")
