"""Ilustraciones vectoriales originales de Desde Mi Orilla (SVG puro)."""
TEAL = "#144556"; CLAY = "#CF764E"; LAV = "#A57DB7"; SAND = "#F3ECDF"; DEEP = "#0E3340"

def leaf_branch(x, y, s=1.0, rot=0, color=TEAL, n=5):
    """Rama de hojas alargadas (motivo de las portadas)."""
    leaves = []
    for i in range(n):
        t = i / (n - 1) if n > 1 else 0
        cy = -t * 230
        side = -1 if i % 2 == 0 else 1
        ang = side * (38 - t * 14)
        L = 120 - t * 40
        leaves.append(
            f'<path transform="translate(0 {cy:.1f}) rotate({ang:.1f})" '
            f'd="M0 0 C {L*0.18:.1f} {-L*0.35:.1f} {L*0.16:.1f} {-L*0.8:.1f} 0 {-L:.1f} '
            f'C {-L*0.16:.1f} {-L*0.8:.1f} {-L*0.18:.1f} {-L*0.35:.1f} 0 0Z" fill="{color}"/>')
    stem = f'<path d="M0 40 C 4 -60 -4 -160 0 -260" stroke="{color}" stroke-width="5" fill="none" stroke-linecap="round"/>'
    return f'<g transform="translate({x} {y}) rotate({rot}) scale({s})">{stem}{"".join(leaves)}</g>'

def orillas_scene(w=800, h=800, sun=True, leaves=True, idp="o", leaf_left=True):
    """Dos orillas (verde azulado y arcilla) separadas por un río de arena."""
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 800" width="{w}" height="{h}" role="img" aria-label="Ilustración: dos orillas separadas por un río">
<defs><clipPath id="{idp}c"><rect width="800" height="800" rx="0"/></clipPath></defs>
<g clip-path="url(#{idp}c)">
<rect width="800" height="800" fill="{SAND}"/>
{f'<circle cx="690" cy="70" r="150" fill="{LAV}"/>' if sun else ''}
<path d="M0 470 C 90 430 190 470 250 520 C 320 580 330 650 420 690 C 480 718 520 760 540 800 L0 800Z" fill="{TEAL}"/>
<path d="M0 520 C 80 500 170 520 230 565 C 290 612 300 680 380 720" stroke="{SAND}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".85"/>
<path d="M0 640 C 60 640 110 690 140 760 C 150 785 150 800 150 800 L0 800Z" fill="{LAV}"/>
<path d="M800 300 C 720 330 650 420 640 500 C 630 580 560 620 500 650 C 440 680 420 740 430 800 L800 800Z" fill="{CLAY}"/>
<path d="M800 380 C 740 410 690 470 680 540 C 672 600 620 650 560 680" stroke="{SAND}" stroke-width="3" fill="none" stroke-linecap="round" opacity=".85"/>
<path d="M800 520 C 740 540 720 600 740 660 C 755 705 800 720 800 720Z" fill="{LAV}"/>
{leaf_branch(40, 560, 0.75, 35) if (leaves and leaf_left) else ''}
{leaf_branch(760, 820, 0.95, -18) if leaves else ''}
</g></svg>'''

def wave_divider(top=SAND, bottom=TEAL, flip=False, h=90):
    tr = ' transform="scale(-1 1) translate(-1440 0)"' if flip else ''
    return (f'<svg class="wave" viewBox="0 0 1440 {h}" preserveAspectRatio="none" aria-hidden="true">'
            f'<rect width="1440" height="{h}" fill="{top}"/>'
            f'<path{tr} d="M0 {h*0.55} C 240 {h*0.05} 480 {h*0.05} 720 {h*0.45} C 960 {h*0.85} 1200 {h*0.9} 1440 {h*0.35} L1440 {h} L0 {h}Z" fill="{bottom}"/></svg>')
