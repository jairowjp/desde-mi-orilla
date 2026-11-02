"""
Desde Mi Orilla — sitio oficial del proyecto
Infraestructura de innovación social transmedia · Desafío Naranja 2026

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
    "instagram": "https://www.instagram.com/miorilla.podcast",
    "desafio": "https://desafionaranja.com/sobre.php",
}

st.set_page_config(
    page_title="Desde Mi Orilla · Bienvenidos a la orilla del cambio",
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
def audio_uri(name: str) -> str:
    """Audio real de un dilema, incrustado para que suene dentro de la atarraya."""
    data = (ROOT / "assets" / "audio" / name).read_bytes()
    return "data:audio/mpeg;base64," + base64.b64encode(data).decode()


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
        for f in sorted(BRAND.glob("dmo_*.svg")):
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
section.s{{padding:96px 0;scroll-margin-top:76px}}
section.hero{{scroll-margin-top:76px}}
.serif{{font-family:var(--serif)}}
h1,h2,h3{{font-family:var(--serif);font-weight:600;letter-spacing:-.01em;color:inherit;margin:0}}
h2.t{{font-size:clamp(34px,4.6vw,58px);line-height:1.06;max-width:16ch}}
h2.t + p.lead{{margin-top:22px}}
p.lead{{font-size:clamp(18px,1.6vw,21px);line-height:1.6;max-width:60ch;color:var(--muted)}}
p{{line-height:1.65}}
.wave{{display:block;width:100%;height:90px!important}}
/* nav */
.nav{{position:fixed;top:0;left:0;right:0;z-index:999990;background:rgba(243,236,223,.92);backdrop-filter:blur(8px);border-bottom:1px solid rgba(20,69,86,.1)}}
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
.navspace{{height:68px}}
.nav nav a.on,.nav nav a:focus-visible{{color:var(--clay)}}
@media (max-width:900px){{
  .nav .wrap{{flex-wrap:wrap;height:auto;padding-top:10px;padding-bottom:0;row-gap:6px}}
  .nav nav{{order:3;width:100%;overflow-x:auto;white-space:nowrap;gap:20px;padding:6px 0 10px;scrollbar-width:none;-webkit-overflow-scrolling:touch}}
  .nav nav::-webkit-scrollbar{{display:none}}
  .navspace{{height:112px}}
  section.s,section.hero{{scroll-margin-top:118px}}
}}
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
.hero .kicker{{font-family:var(--serif);font-style:italic;font-size:clamp(20px,1.9vw,26px);color:var(--clay);margin:0 0 18px}}
.pillars{{display:grid;grid-template-columns:repeat(3,1fr);gap:36px;margin-top:56px;padding-top:28px;border-top:1px solid rgba(20,69,86,.15)}}
.pillars b{{display:block;font-family:var(--serif);font-size:26px;color:var(--teal);margin-bottom:6px}}
.pillars span{{font-size:16px;color:var(--muted);line-height:1.5}}
.reach{{display:grid;grid-template-columns:1fr 1.05fr;gap:64px;align-items:center}}
.tiers{{display:grid;gap:18px;margin-top:30px}}
.tiers div{{border-left:4px solid var(--c);padding:4px 0 4px 18px}}
.tiers b{{display:block;font-size:18px;color:var(--sand)}}
.tiers span{{font-size:15.5px;color:rgba(243,236,223,.78)}}
.flow{{display:grid;grid-template-columns:repeat(4,1fr);gap:0;margin-top:56px;position:relative}}
.flow > div{{position:relative;padding:28px 26px 0 0;border-top:6px solid var(--c)}}
.flow em{{position:absolute;top:-24px;left:0;width:42px;height:42px;border-radius:50%;background:var(--c);color:#fff;font-style:normal;font:600 20px var(--serif);display:flex;align-items:center;justify-content:center}}
.flow b{{display:block;font-family:var(--serif);font-size:24px;color:var(--teal);margin:14px 0 8px}}
.flow span{{font-size:15.5px;color:var(--muted);line-height:1.55}}
@media (max-width:900px){{.pillars,.reach{{grid-template-columns:1fr}} .flow{{grid-template-columns:1fr 1fr;row-gap:50px}}}}
@media (prefers-reduced-motion:reduce){{*{{animation:none!important;transition:none!important}}}}
</style>
""")

stand_mode = st.query_params.get("stand") == "1"
data = seed()
orillas = data["orillas"]
orilla_by_id = {o["id"]: o for o in orillas}

# ---------------------------------------------------------------------------
# Atarraya de Saberes (componente) y formulario
# ---------------------------------------------------------------------------
def render_atarraya(height: int) -> None:
    preguntas = data["preguntas"] + [
        {**q, "autora": f"Dejado por {q['autora']}" if q.get("autora") else "Dejado por una visitante"}
        for q in visitor_questions()[-60:]
    ]
    preguntas = [{**q, "audio": audio_uri(q["audio_file"])} if q.get("audio_file") else q for q in preguntas]
    payload = json.dumps({"orillas": orillas, "preguntas": preguntas}, ensure_ascii=False).replace("</", "<\\/")
    tpl = (ROOT / "components" / "atarraya.html").read_text(encoding="utf-8")
    page = tpl.replace("__FONTS__", fonts_css()).replace("__DATA__", payload).replace("__HEIGHT__", str(height))
    if hasattr(st, "iframe"):
        st.iframe(page, height=height)
    else:
        components.html(page, height=height, scrolling=False)


def question_form(key: str) -> None:
    with st.form(key, clear_on_submit=True):
        texto = st.text_area(
            "Tu dilema o pregunta para la siguiente mujer que se siente frente al micrófono",
            max_chars=200, height=110, placeholder="Escribe la pregunta que te gustaría heredar a otra mujer…",
        )
        c1, c2 = st.columns([1, 1])
        with c1:
            ori = st.selectbox("¿Desde qué orilla preguntas?", [o["id"] for o in orillas],
                               format_func=lambda i: orilla_by_id[i]["name"])
        with c2:
            autora = st.text_input("Tu nombre o país (opcional)", max_chars=40, placeholder="Ej.: Ana, Santo Domingo")
        ok = st.form_submit_button("Tejer mi dilema en la atarraya")
    if ok:
        clean = " ".join(texto.split())
        if len(clean) < 8:
            st.warning("Escribe al menos 8 caracteres para que podamos tejerlo en la atarraya.")
        else:
            if not clean.endswith("?"):
                clean += "?"
            if not clean.startswith("¿"):
                clean = "¿" + clean
            add_visitor_question(ori, clean, " ".join(autora.split()) or "una visitante")
            st.success(f"Tu dilema ya está tejido en la atarraya. Búscalo como un nudo claro en la orilla {orilla_by_id[ori]['name']}.")
            st.rerun()


# ---------------------------------------------------------------------------
# Modo stand: pantalla táctil con la atarraya a pantalla completa
# ---------------------------------------------------------------------------
if stand_mode:
    H(f"""<div style="background:{DEEP};padding:22px 28px;display:flex;align-items:center;justify-content:space-between;gap:20px">
      <div style="width:220px">{logo('dmo_wordmark_blanco.svg', "Desde Mi Orilla")}</div>
      <div style="color:{SAND};font:500 19px var(--sans)">Toca un nudo. Escucha su voz. Teje tu propio dilema.</div>
      <div style="width:56px">{logo('dmo_isotipo_blanco.svg', "")}</div></div>""")
    with st.container(key="bg-arbol"):
        render_atarraya(660)
    with st.container(key="bg-form"):
        H('<div class="wrap" style="padding-top:40px"><h2 class="t" style="color:var(--teal);font-size:40px;max-width:none">Teje tu dilema en la atarraya</h2></div>')
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
    <a href="#problema">Por qué</a><a href="#idea">La propuesta</a><a href="#atarraya">Atarraya</a>
    <a href="#alcance">Alcance</a><a href="#economia">Economía creativa</a><a href="#vision">Si ganamos</a>
  </nav>
  <a class="btn p" href="#video">Ver el video</a>
</div></div>
<div class="navspace"></div>

<section class="hero" id="inicio"><div class="wrap">
  <div class="grid">
    <div>
      <p class="kicker">Bienvenidos a la orilla del cambio.</p>
      <h1>Nadie conoce sus nombres. <span class="promise">Muy pronto, el mundo entero los va a pronunciar.</span></h1>
      <p class="sub">En Ecuador, las mujeres sostienen la cultura y el territorio, pero sus voces están fragmentadas en los medios. Desde Mi Orilla es una infraestructura de innovación social transmedia diseñada para registrar, interconectar y potenciar la memoria de las comunidades, sin intermediarios.</p>
      <div class="ctas">
        <a class="btn p" href="#video">Ver el video</a>
        <a class="btn o" href="#atarraya">Explorar la Atarraya de Saberes</a>
      </div>
    </div>
    <div class="cover">
      {svg_img(orillas_scene(idp="hero", leaf_left=False), "", cls="scene", style="position:absolute;inset:0;height:100%")}
      <div class="logo">{logo('dmo_logo.svg', "Desde Mi Orilla")}</div>
    </div>
  </div>
  <div class="pillars">
    <div><b>Registrar</b><span>la memoria oral de mujeres de todas las culturas del país</span></div>
    <div><b>Interconectar</b><span>orillas distintas en una misma atarraya de saberes</span></div>
    <div><b>Potenciar</b><span>sus voces, sus oficios y sus economías en nuevos mercados</span></div>
  </div>
</div></section>
{wave(SAND, DEEP)}
""")

# ---------------------------------------------------------------------------
# Video
# ---------------------------------------------------------------------------
with st.container(key="bg-video"):
    H("""<section class="s" id="video" style="padding-bottom:40px;color:var(--sand)"><div class="wrap">
      <h2 class="t">Escúchalas desde su orilla</h2>
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
  <h2 class="t">Sostienen la cultura y el territorio. Sus voces siguen fragmentadas.</h2>
  <div class="stat">
    <div class="n">51,3<small>%</small></div>
    <p class="lead" style="margin:0">de la población del Ecuador son mujeres. Sin embargo, su presencia como fuentes, protagonistas y productoras de conocimiento en los medios sigue siendo escasa, y las mujeres indígenas suelen aparecer en papeles secundarios.</p>
  </div>
  <div class="facts">
    <p><strong>Voces fragmentadas</strong>Las historias de mujeres afroecuatorianas, indígenas, montubias, rurales y urbanas se cuentan por separado, o desde una sola mirada.</p>
    <p><strong>Memoria que se pierde</strong>Sin espacios de encuentro, se rompen los puentes entre generaciones y culturas, y con ellos los saberes de las comunidades.</p>
    <p><strong>Territorios desconectados</strong>En muchas zonas rurales y aisladas no hay internet ni cobertura celular: esas voces no llegan, y la información tampoco.</p>
  </div>
  <p class="src">Fuentes: INEC (2023); Consejo de Comunicación (2019); Coronado-Otavalo et al. (2025), Historia y Comunicación Social, 30(2).</p>
</div></section>
{wave(DEEP, SAND, flip=True)}
""")

# ---------------------------------------------------------------------------
# La propuesta
# ---------------------------------------------------------------------------
H(f"""
<section class="s" id="idea"><div class="wrap meet">
  <div>{svg_img((IMG / "encuentro.svg").read_text(encoding="utf-8"), "Dos mujeres desde orillas distintas se encuentran en un mismo dilema")}</div>
  <div>
    <h2 class="t" style="color:var(--teal)">Dos mujeres. Dos orillas. Un mismo dilema.</h2>
    <p class="lead">Cada episodio reúne a dos mujeres que normalmente no se encontrarían —distintas por cultura, generación o territorio— y las une una pregunta. La diferencia no se suaviza: es el motor de la conversación. Sin intermediarios: ellas narran su propia realidad.</p>
    <div class="chain"><p><strong class="serif" style="font-size:21px;color:var(--teal)">El dilema que heredamos.</strong><br>Cada participante cierra su episodio dejando un dilema a la siguiente. Así, voz tras voz, se teje la Atarraya de Saberes: un archivo vivo de la memoria de las comunidades.</p></div>
  </div>
</div></section>
""")

# ---------------------------------------------------------------------------
# Las cinco orillas
# ---------------------------------------------------------------------------
rows = "".join(
    f'<div class="or" style="--c:{o["color"] if o["id"] != "identidad" else TEAL}"><div class="k">{o["ep"]}</div>'
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
    <div role="listitem" style="flex:10;background:{TEAL}"><em>10′</em><b>El Encuentro</b><span>Cada participante expone su orilla frente a la pregunta central.</span></div>
    <div role="listitem" style="flex:20;background:#2E6E7E"><em>20′</em><b>La Marea</b><span>Diálogo horizontal: de las historias personales a lo que tienen en común.</span></div>
    <div role="listitem" style="flex:8;background:{CLAY}"><em>8′</em><b>El dilema que heredamos</b><span>Responden el dilema anterior y tejen uno nuevo.</span></div>
    <div role="listitem" style="flex:4;background:{LAV}"><em>2′</em><b>Eco</b><span>Invitación a la atarraya.</span></div>
  </div>
</div></section>
{wave(SAND, DEEP)}
""")

# ---------------------------------------------------------------------------
# Atarraya de Saberes
# ---------------------------------------------------------------------------
with st.container(key="bg-arbol"):
    H("""<section class="s dark" id="atarraya" style="padding-bottom:36px"><div class="wrap">
      <h2 class="t">La Atarraya de Saberes</h2>
      <p class="lead">Nuestra metodología es un ecosistema vivo donde las participantes heredan dilemas tejiendo esta atarraya interactiva de saberes. Cada nudo es una voz; cada hilo, una herencia. Temporada tras temporada, la red se amplía y se convierte en la memoria viva de las comunidades.</p>
    </div></section>""")
    render_atarraya(640)
    H(f"<div style='height:30px;background:{DEEP}'></div>{wave(DEEP, SAND, flip=True)}")

with st.container(key="bg-form"):
    H("""<div class="wrap" style="padding:30px 28px 26px"><h2 class="t" style="color:var(--teal);font-size:clamp(30px,3.6vw,44px);max-width:22ch">Teje tu dilema en la atarraya</h2>
    <p class="lead">Escribe la pregunta que le harías a una mujer de otra cultura u otra generación. Aparecerá como un nudo claro en la red.</p></div>""")
    with st.container(key="pad-form"):
        question_form("main_form")

# ---------------------------------------------------------------------------
# Alcance: incluso donde no hay internet
# ---------------------------------------------------------------------------
H(f"""
{wave(SAND, DEEP)}
<section class="s dark" id="alcance"><div class="wrap reach">
  <div>{svg_img((IMG / "alcance.svg").read_text(encoding="utf-8"), "Una antena de radio lleva la señal desde la ciudad hasta comunidades aisladas entre montañas y ríos")}</div>
  <div>
    <h2 class="t">Llegaremos incluso donde no hay internet</h2>
    <p class="lead">Nos proponemos llegar a zonas sin conectividad, desplegando la información a través de redes de radioaficionados en zonas aisladas. Ninguna orilla queda fuera.</p>
    <div class="tiers">
      <div style="--c:{LAV}"><b>Digital</b><span>Videopodcast, plataformas de streaming y redes sociales.</span></div>
      <div style="--c:{CLAY}"><b>Radio comunitaria</b><span>Cápsulas de 5 minutos en kichwa y shuar para emisoras locales.</span></div>
      <div style="--c:#8DB97C"><b>Radioaficionados</b><span>Con Radio Club Guayaquil, transmisión en zonas sin cobertura celular.</span></div>
    </div>
  </div>
</div></section>
{wave(DEEP, TEAL, flip=True)}
""")

# ---------------------------------------------------------------------------
# No empezamos desde cero: respaldo y red de aliados
# ---------------------------------------------------------------------------
H(f"""
<section class="s teal" id="aliados"><div class="wrap">
  <h2 class="t">No empezamos desde cero</h2>
  <p class="lead">Esta iniciativa de economía creativa cuenta con el respaldo técnico y la infraestructura de la Universidad Bolivariana del Ecuador, y articula una red de aliados que ya está en marcha.</p>
  <div class="eco">
    <div class="it"><h3>Minedec · SEIBE</h3><p>Secretaría de Educación Intercultural Bilingüe y Etnoeducación: validación metodológica y divulgación en unidades educativas.</p><span class="tag">Aval metodológico</span></div>
    <div class="it"><h3>Consejo de Comunicación</h3><p>Capacitación, entrenamiento y certificación de competencias de las mujeres que se sumen a los nodos de comunicación.</p><span class="tag">Certificación</span></div>
    <div class="it"><h3>Radio Club Guayaquil</h3><p>Red de radioaficionados para transmitir en zonas sin conectividad celular.</p><span class="tag">Zonas aisladas</span></div>
    <div class="it"><h3>Colectivos y redes de mujeres</h3><p>Comunicación comunitaria, redes de mujeres y organizaciones sociales que ya trabajan en el territorio.</p><span class="tag">Territorio</span></div>
    <div class="it"><h3>Nodos de comunicación</h3><p>Mujeres capacitadas y certificadas que registran y difunden la memoria de su propia comunidad.</p><span class="tag">Formación</span></div>
    <div class="it"><h3>Empresa y cultura</h3><p>Empresas aliadas, moda intercultural, modistas y artistas que amplifican y compran lo que crean.</p><span class="tag">Mercados</span></div>
  </div>
  <div class="ethics">
    <div style="--c:{SAND}"><b>Sin intermediarios</b><span>Ellas narran su propia realidad, en primera persona.</span></div>
    <div style="--c:{CLAY}"><b>Consentimiento informado</b><span>Alineado con el Convenio 169 de la OIT, con revisión del corte final y derecho a réplica.</span></div>
    <div style="--c:{LAV}"><b>Reciprocidad</b><span>Becas de conectividad, insumos y coautoría en investigaciones para sus colectivos.</span></div>
    <div style="--c:#8DB97C"><b>Accesibilidad</b><span>Transcripciones, subtítulos y una web que apunta a WCAG 2.2 AA.</span></div>
  </div>
</div></section>
{wave(TEAL, SAND, flip=True)}
""")

# ---------------------------------------------------------------------------
# Economía creativa
# ---------------------------------------------------------------------------
H(f"""
<section class="s" id="economia"><div class="wrap">
  <h2 class="t" style="color:var(--teal);max-width:20ch">Cultura que se convierte en desarrollo</h2>
  <p class="lead">Seremos un motor de fomento de servicios culturales: difundiremos y conectaremos los productos y servicios de mujeres y organizaciones sociales con nuevos mercados, para convertir la cultura en desarrollo laboral y económico de los territorios.</p>
  <div class="flow">
    <div style="--c:{TEAL}"><em>1</em><b>Voces y oficios</b><span>Mujeres y organizaciones sociales con productos, servicios y saberes.</span></div>
    <div style="--c:{CLAY}"><em>2</em><b>Vitrina transmedia</b><span>Episodios, cápsulas y la atarraya muestran quiénes son y qué crean.</span></div>
    <div style="--c:{LAV}"><em>3</em><b>Nuevos mercados</b><span>Empresas aliadas, ferias, compradores y audiencias de otros países.</span></div>
    <div style="--c:#5E8F4E"><em>4</em><b>Desarrollo territorial</b><span>Empleo, ingresos y orgullo que se quedan en la comunidad.</span></div>
  </div>
</div></section>
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
<section class="s" id="vision" style="padding-top:0"><div class="wrap">
  <h2 class="t" style="color:var(--teal);max-width:20ch">Si ganamos, estas voces tendrán su propia casa</h2>
  <p class="lead">Hoy contamos con estudio, metodología, marca y el prototipo de la atarraya. Con el Desafío Naranja damos el salto: equipos para grabar en cualquier territorio, nodos de comunicación certificados y una plataforma propia para la comunidad de mujeres que lo dan todo.</p>
  <div class="road">
    <div style="--c:{TEAL}"><div class="when">Hoy</div><h3>Base lista</h3><p>Estudio, equipo base, metodología, marca, portadas y prototipo funcional de la Atarraya de Saberes.</p></div>
    <div style="--c:#2E6E7E"><div class="when">Abril a julio 2027</div><h3>Temporada piloto</h3><p>Seis episodios, doce voces, cápsulas en kichwa y shuar e informe de impacto.</p></div>
    <div style="--c:{CLAY}"><div class="when">Agosto 2027 a enero 2028</div><h3>Expansión nacional</h3><p>Sierra Centro y Amazonía Sur, radioaficionados en zonas aisladas y primeros nodos certificados.</p></div>
    <div style="--c:{LAV}"><div class="when">Visión</div><h3>Plataforma propia</h3><p>Equipo profesional, red de nodos en todo el país y vitrina de economía creativa con alcance internacional.</p></div>
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
      <p style="font-size:14px;color:var(--muted)">Estudio y personal base: US$ 0, aportados por el socio ancla. Montos referenciales sujetos a cotización.</p>
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
# Red de aliados
# ---------------------------------------------------------------------------
H("""
<section class="s" id="red" style="padding-top:0"><div class="wrap">
  <h2 class="t" style="color:var(--teal);font-size:clamp(30px,3.6vw,44px)">Una red que ya está en marcha</h2>
  <p class="lead">Alianzas en gestión desde septiembre de 2026 y en proceso de formalización.</p>
  <div class="allies">
    <div><h3>Universidad y entidades públicas</h3><ul><li>UBE, socio ancla</li><li>CITC y sus programas RAÍCES, UBE Violeta y Maker Women STEM</li><li>Incubadora de emprendimientos y CRAI de la UBE</li><li>Minedec, SEIBE y Consejo de Comunicación</li></ul></div>
    <div><h3>Organizaciones de mujeres y colectivos sociales</h3><ul><li>Mujeres de Asfalto</li><li>Afroamérica XXI</li><li>FEMUAFRO</li><li>Palenque Libre por Derecho</li><li>Fundación Minkayni</li><li>Warmi Imbabura</li><li>Red de Mujeres Rurales del Ecuador</li></ul></div>
    <div><h3>Comunicación y radio</h3><ul><li>Radio Club Guayaquil</li><li>Sin Paro, frecuencia radial ganadora del concurso de la Casa de la Cultura</li></ul></div>
    <div><h3>Empresa y cultura</h3><ul><li>Clorox León, empresa aliada</li><li>Empresas de moda intercultural, modistas y artistas aliados</li></ul></div>
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
      <div style="width:260px">{logo('dmo_wordmark_blanco.svg', "Desde Mi Orilla")}</div>
      <p style="color:rgba(243,236,223,.75);max-width:46ch;margin-top:22px">Infraestructura de innovación social transmedia.<br>Miradas distintas, historias compartidas.<br>Ecuador · 2026</p>
    </div>
    <div>
      <p style="margin:0 0 10px;font-weight:500">Síguenos</p>
      <p style="margin:0;line-height:2"><a href="{LINKS['instagram']}" target="_blank" rel="noopener">Instagram @miorilla.podcast</a><br>
      <a href="{LINKS['desafio']}" target="_blank" rel="noopener">Desafío Naranja 2026</a></p>
    </div>
    <div><div class="qr">{svg_img(qr_svg(APP_URL), "Código QR del sitio")}</div>
      <p style="font-size:13px;color:rgba(243,236,223,.65);margin-top:10px">Escanea para abrir el sitio</p></div>
  </div>
  <small>© 2026 Desde Mi Orilla. Dilemas de muestra en la atarraya: ilustrativos hasta la grabación de la temporada piloto.</small>
</div></div>
""")
