#!/usr/bin/env python3
"""Genera las páginas SEO de ENDURACE LAB: una página por calculadora y el blog
(índice + una página por artículo). Ejecutar desde la raíz del proyecto:

    python3 _build/generar_paginas.py

La carpeta _build no se publica en GitHub Pages. Para añadir un artículo, añade un
diccionario a ARTICULOS y vuelve a ejecutar el script.
"""
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.endurace-lab.com/"
MAIL = "info@endurace-lab.com"
os.chdir(ROOT)


def ft(s):
    s = round(s)
    h, m, x = s // 3600, s % 3600 // 60, s % 60
    return (f"{h}:{m:02d}" if h else f"{m}") + f":{x:02d}"


def riegel(t, d1, d2):
    return t * (d2 / d1) ** 1.06


# ---------------------------------------------------------------- plantilla
def head(title, desc, path, pre="", jsonld=None, og_type="website"):
    ld = "".join(f'\n  <script type="application/ld+json">{json.dumps(j, ensure_ascii=False)}</script>' for j in (jsonld or []))
    return f"""<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{html.escape(title)}</title>
  <meta name="description" content="{html.escape(desc)}">
  <link rel="canonical" href="{SITE}{path}">
  <meta property="og:type" content="{og_type}">
  <meta property="og:site_name" content="ENDURACE LAB">
  <meta property="og:locale" content="es_ES">
  <meta property="og:title" content="{html.escape(title)}">
  <meta property="og:description" content="{html.escape(desc)}">
  <meta property="og:url" content="{SITE}{path}">
  <meta property="og:image" content="{SITE}og-image.jpg">
  <meta property="og:image:width" content="1200">
  <meta property="og:image:height" content="630">
  <meta name="twitter:card" content="summary_large_image">
  <meta name="theme-color" content="#090b0e">
  <link rel="icon" type="image/svg+xml" href="{pre}logo.svg">
  <link rel="manifest" href="{pre}manifest.webmanifest">
  <link rel="apple-touch-icon" href="{pre}icon-192.png">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@500;600;700;800&family=IBM+Plex+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{pre}style.css?v=5">
  <link rel="stylesheet" href="{pre}lab.css?v=6">{ld}
</head>
<body>
"""


def nav(pre="", current=""):
    items = [(f"{pre}index.html#planes", "Planes"), (f"{pre}laboratorio.html", "Laboratorio"), (f"{pre}blog.html", "Blog"), (f"{pre}index.html#sobre-mi", "Sobre mí")]
    links = "".join(f'<a href="{u}"' + (' aria-current="page"' if t == current else "") + f">{t}</a>" for u, t in items)
    return f"""  <header class="site-header">
    <div class="container nav">
      <a class="brand" href="{pre}index.html" aria-label="ENDURACE LAB, inicio">
        <img src="{pre}logo.svg" alt="" width="46" height="46">
        <span>ENDURACE<span class="orange">_LAB</span></span>
      </a>
      <button class="menu-toggle" aria-label="Abrir menú" aria-expanded="false">☰</button>
      <nav class="main-nav" aria-label="Navegación principal">
        {links}
        <a class="nav-cta" href="{pre}inscripcion.html">Empieza <span>↗</span></a>
      </nav>
    </div>
  </header>
"""


def footer(pre="", scripts=()):
    sc = "".join(f'\n  <script src="{pre}{s}"></script>' for s in scripts)
    return f"""  <footer class="footer">
    <div class="container footer-top">
      <a class="brand" href="{pre}index.html"><img src="{pre}logo.svg" alt="" width="40" height="40"><span>ENDURACE<span class="orange">_LAB</span></span></a>
      <div class="footer-links"><a href="{pre}index.html#planes">Planes</a><a href="{pre}running.html">Running</a><a href="{pre}laboratorio.html">Laboratorio</a><a href="{pre}blog.html">Blog</a><a href="{pre}inscripcion.html">Inscripción</a><a href="mailto:{MAIL}">Contacto</a></div>
    </div>
    <div class="container footer-bottom">
      <p>© <span id="year"></span> ENDURACE LAB. Todos los derechos reservados.</p>
      <p>El entrenamiento físico conlleva riesgos. La información de esta web no sustituye una valoración médica, fisioterapéutica ni nutricional. Consulta con profesionales sanitarios cuando corresponda.</p>
      <p><a href="{pre}privacidad.html">Privacidad</a> · <a href="{pre}aviso-legal.html">Aviso legal</a> · <a href="{pre}condiciones.html">Condiciones de contratación</a></p>
    </div>
  </footer>
  <script>
    document.getElementById("year").textContent = new Date().getFullYear();
    const tg = document.querySelector(".menu-toggle"), nv = document.querySelector(".main-nav");
    tg.addEventListener("click", () => {{ const o = tg.getAttribute("aria-expanded") === "true"; tg.setAttribute("aria-expanded", String(!o)); nv.classList.toggle("open", !o); }});
  </script>{sc}
  <script src="{pre}fx.js" defer></script>
</body>
</html>
"""


def faq_html(faqs):
    return "".join(f"<details><summary>{q}</summary><p>{a}</p></details>" for q, a in faqs)


def faq_ld(faqs):
    strip = lambda s: re.sub(r"<[^>]+>", "", s)
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [
        {"@type": "Question", "name": strip(q), "acceptedAnswer": {"@type": "Answer", "text": strip(a)}} for q, a in faqs]}


def crumbs_ld(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE + u} for i, (n, u) in enumerate(items)]}


# ---------------------------------------------------------------- calculadoras
LAB = open("laboratorio.html", encoding="utf-8").read()


def panel(start, end):
    a = LAB.index(start)
    b = LAB.index(end, a)
    p = LAB[a:b].strip()
    p = re.sub(r'<div class="tool-head">.*?</div>\s*', "", p, count=1, flags=re.S)
    p = p.replace(' role="tabpanel"', "").replace(" hidden>", ">", 1)
    p = re.sub(r' aria-labelledby="t-[a-z]+"', "", p)
    return p


CALCS = [
    dict(
        file="calculadora-ritmo-maraton.html", key="predictor",
        title="Calculadora de tiempos y ritmos: 5K, 10K, media maratón y maratón | ENDURACE LAB",
        desc="Calcula gratis tu tiempo y tu ritmo por kilómetro en 5K, 10K, media maratón y maratón a partir de una marca reciente. Fórmula de Riegel, sin registro.",
        crumb="Calculadora de tiempos y ritmos",
        h1='CALCULADORA DE<br><span class="orange">TIEMPOS Y RITMOS.</span>',
        intro="Mete una marca reciente y descubre cuánto harías en 5K, 10K, media maratón y maratón, con tu ritmo por kilómetro. Gratis, al instante y sin registrarte.",
        panel=("<!-- 02 · PREDICTOR -->", "<!-- 03 · ZONAS -->"),
    ),
    dict(
        file="calculadora-zonas-entrenamiento.html", key="zonas",
        title="Calculadora de zonas de entrenamiento: pulso, ritmo y potencia (FTP) | ENDURACE LAB",
        desc="Calcula gratis tus zonas de frecuencia cardiaca (Karvonen), tus zonas de ritmo de carrera y tus zonas de potencia en bici a partir de tu FTP.",
        crumb="Calculadora de zonas de entrenamiento",
        h1='CALCULADORA DE<br><span class="orange">ZONAS DE ENTRENAMIENTO.</span>',
        intro="Tus zonas de pulso, de ritmo de carrera y de potencia en bici en segundos. Mueve las barras con tus valores y entrena cada sesión a la intensidad que toca.",
        panel=("<!-- 03 · ZONAS -->", "<!-- 04 · NUTRICIÓN -->"),
    ),
    dict(
        file="calculadora-nutricion-carrera.html", key="nutricion",
        title="¿Cuánto comer en un maratón o un triatlón? Calculadora de hidratos, agua y sodio | ENDURACE LAB",
        desc="Calcula cuántos gramos de hidratos, cuánto líquido y cuánto sodio tomar por hora en tu maratón, medio Ironman o Ironman según la duración y el calor.",
        crumb="Calculadora de nutrición en carrera",
        h1='¿CUÁNTO COMER<br><span class="orange">EN TU CARRERA?</span>',
        intro="Hidratos, líquido y sodio por hora y en total según la duración de tu prueba y el calor, con una pauta práctica cada 20 minutos.",
        panel=("<!-- 04 · NUTRICIÓN -->", "<!-- 05 · CUENTA ATRÁS -->"),
    ),
    dict(
        file="cuenta-atras-carrera.html", key="cuenta",
        title="Cuenta atrás para tu carrera: semanas que faltan y fase de entrenamiento | ENDURACE LAB",
        desc="¿Cuántas semanas faltan para tu maratón o tu triatlón? Cuenta atrás gratuita que te dice en qué fase de preparación deberías estar y qué toca entrenar ahora.",
        crumb="Cuenta atrás para tu carrera",
        h1='CUENTA ATRÁS<br><span class="orange">PARA TU CARRERA.</span>',
        intro="Pon la fecha de tu carrera y descubre cuántas semanas faltan, en qué fase deberías estar y qué toca entrenar ahora. Se guarda en tu navegador para cuando vuelvas.",
        panel=("<!-- 05 · CUENTA ATRÁS -->", "    </div></section>"),
    ),
]

# --- textos de cada calculadora
t10 = 50 * 60
EJ = {k: ft(riegel(t10, 10, d)) for k, d in [("5", 5), ("21", 21.0975), ("42", 42.195)]}
OBJ = [("Maratón en 4:00", 4 * 3600, 42.195), ("Maratón en 3:30", 3.5 * 3600, 42.195), ("Maratón en 3:00", 3 * 3600, 42.195),
       ("Media en 2:00", 2 * 3600, 21.0975), ("Media en 1:45", 6300, 21.0975), ("10K en 50:00", 3000, 10), ("10K en 45:00", 2700, 10)]
TABLA_OBJ = "".join(f"<tr><td>{n}</td><td>{ft(t / d)} /km</td></tr>" for n, t, d in OBJ)

TEXTOS = {
    "predictor": dict(
        body=f"""<h2>Cómo funciona la calculadora</h2>
<p>Usa la <strong>fórmula de Riegel</strong>, la referencia más utilizada para comparar marcas entre distancias: <em>T2 = T1 × (D2 / D1)<sup>1,06</sup></em>. El exponente 1,06 recoge que, cuanto más larga es la prueba, más se frena el ritmo.</p>
<p>Por ejemplo, con un 10K en 50:00 la estimación es de <strong>{EJ['5']}</strong> en 5K, <strong>{EJ['21']}</strong> en media maratón y <strong>{EJ['42']}</strong> en maratón.</p>
<h2>Cómo usarla bien</h2>
<ul><li><strong>Usa una marca reciente</strong>, de las últimas 6 a 8 semanas, hecha a tope y en condiciones normales (sin calor extremo ni mucho desnivel).</li>
<li><strong>Cuanto más cerca esté la distancia, mejor</strong>: para predecir un maratón, una media maratón reciente es mucho más fiable que un 5K.</li>
<li><strong>En maratón suele ser optimista</strong> si haces poco volumen semanal o no has entrenado tiradas largas: ahí manda la resistencia, no solo la velocidad.</li></ul>
<h2>Ritmos para objetivos habituales</h2>
<div class="scroll"><table><tr><th>Objetivo</th><th>Ritmo medio</th></tr>{TABLA_OBJ}</table></div>
<p>Si quieres comprobar si tu objetivo es realista, mete tu marca actual y compara la predicción con el tiempo que buscas.</p>""",
        faqs=[
            ("¿Es fiable la predicción para el maratón?", "Es una buena referencia si tienes una base de entrenamiento de maratón: tiradas largas de 28 a 32 km y un volumen semanal suficiente. Sin esa base, lo normal es tardar más de lo que indica la fórmula."),
            ("¿A qué ritmo tengo que ir para hacer un maratón en 4 horas?", f"Necesitas un ritmo medio de {ft(4 * 3600 / 42.195)} por kilómetro. Para 3:30 son {ft(3.5 * 3600 / 42.195)} por kilómetro y para 3:00, {ft(3 * 3600 / 42.195)}."),
            ("¿Sirve para trail o carreras con mucho desnivel?", "No. La fórmula está pensada para carreras en asfalto y terreno llano. En montaña el desnivel y el terreno cambian por completo el ritmo."),
            ("¿Qué marca uso si tengo varias?", "La más reciente y la de distancia más parecida a la que quieres predecir. Si dudas entre dos, quédate con la más conservadora."),
        ]),
    "zonas": dict(
        body="""<h2>Qué son las zonas de entrenamiento</h2>
<p>Las zonas dividen tu esfuerzo en franjas para que cada sesión tenga un propósito: rodajes suaves que construyen base, trabajo de umbral que sube tu ritmo sostenible y series intensas que mejoran tu techo. Entrenar «a sensaciones» suele acabar en hacer los días suaves demasiado rápidos y los duros demasiado lentos.</p>
<h2>Zonas de pulso: método de la reserva (Karvonen)</h2>
<p>Este método tiene en cuenta tu <strong>pulso en reposo</strong> además del máximo, así que se ajusta mejor a tu forma física que un simple porcentaje del máximo: <em>pulso objetivo = reposo + % × (máximo − reposo)</em>.</p>
<ul><li><strong>Pulso máximo:</strong> la fórmula «220 − edad» puede fallar en más de 10 pulsaciones. Es mejor el valor más alto que hayas visto en una carrera o en series cuesta arriba muy duras.</li>
<li><strong>Pulso en reposo:</strong> mídelo al despertar, aún tumbado, varios días seguidos, y quédate con la media.</li></ul>
<h2>Zonas de ritmo de carrera</h2>
<p>Parten de tu <strong>ritmo umbral</strong>: el que podrías mantener alrededor de una hora. Una forma sencilla de estimarlo es correr 30 minutos a tope en llano y tomar el ritmo medio de los últimos 20.</p>
<h2>Zonas de potencia en bici</h2>
<p>Se calculan sobre tu <strong>FTP</strong>, la potencia que podrías sostener una hora. El test más común es rodar 20 minutos al máximo después de un buen calentamiento y multiplicar la potencia media por 0,95.</p>
<h2>¿Cuánto tiempo en cada zona?</h2>
<p>En deportes de resistencia funciona muy bien la regla del <strong>80/20</strong>: alrededor del 80 % del tiempo suave (zonas 1 y 2) y el 20 % restante a intensidad media o alta. Si quieres saber cómo lo estás haciendo tú, sube tus entrenamientos al <a href="laboratorio.html">informe del laboratorio</a> y verás tu distribución real.</p>""",
        faqs=[
            ("¿Sirve la fórmula 220 menos la edad?", "Como punto de partida, pero tiene mucho margen de error entre personas. Si puedes, usa el pulso más alto que hayas registrado en un esfuerzo máximo reciente."),
            ("¿Por qué mis zonas no coinciden con las de mi reloj?", "Cada marca usa sus propios métodos y porcentajes, y muchos relojes parten de un pulso máximo estimado. Lo importante es usar siempre el mismo sistema y basarlo en tus valores reales."),
            ("¿Cada cuánto tengo que actualizar mis zonas?", "Cada 6 a 8 semanas o cuando notes un cambio claro de forma. Repite el test de umbral o de FTP en condiciones parecidas para poder comparar."),
            ("¿Qué zonas uso: pulso, ritmo o potencia?", "En carrera, el ritmo es muy útil en llano y el pulso en días de calor o con desnivel. En bici, la potencia es la medida más precisa. Lo ideal es combinarlos."),
        ]),
    "nutricion": dict(
        body="""<h2>Hidratos de carbono: cuánto por hora</h2>
<p>Tus reservas de glucógeno dan para un esfuerzo intenso de entre 60 y 90 minutos. A partir de ahí, comer durante la carrera marca la diferencia entre mantener el ritmo y «pegarte con el muro».</p>
<ul><li><strong>Menos de 1 hora:</strong> no suele hacer falta comer; basta con llegar bien desayunado.</li>
<li><strong>De 1 a 2,5 horas:</strong> entre 30 y 60 g de hidratos por hora.</li>
<li><strong>Más de 2,5 horas:</strong> entre 60 y 90 g por hora. Para pasar de 60 g conviene combinar glucosa y fructosa (lo indican muchos geles y bebidas) y haberlo entrenado antes.</li></ul>
<p>Como referencia práctica, un gel normal aporta entre 20 y 25 g de hidratos.</p>
<h2>Líquido y sodio</h2>
<p>Lo habitual es beber entre 400 y 800 ml por hora según el calor y cuánto sudes, y tomar entre 300 y 600 mg de sodio por hora en pruebas largas o con calor. Beber de más también es un riesgo: guíate por la sed y por tu experiencia en entrenamientos.</p>
<h2>Entrena tu estómago</h2>
<p>El intestino también se entrena. Prueba exactamente lo que vas a tomar —marca, cantidad y frecuencia— en tus tiradas largas. Y la regla de oro: <strong>nada nuevo el día de la carrera</strong>.</p>""",
        faqs=[
            ("¿Cuántos geles necesito para un maratón?", "Depende de tu tiempo y de cuántos hidratos tomes por hora. Por ejemplo, en 3 h 30 min a 60 g por hora necesitarías unos 210 g: entre 8 y 10 geles de 20 a 25 g, o menos si combinas con bebida isotónica."),
            ("¿Cuándo tomo el primer gel?", "Lo habitual es empezar entre los minutos 30 y 45 y seguir cada 20 o 30 minutos. Esperar a tener hambre o sensación de cansancio suele ser tarde."),
            ("¿Agua o bebida isotónica?", "La isotónica aporta hidratos y sodio a la vez, lo que es útil en pruebas largas y con calor. Puedes combinarla con agua para tomar los geles."),
            ("¿Esto sustituye a un nutricionista?", "No. Son pautas generales para deportistas sanos. Si tienes alguna condición médica o problemas digestivos, consulta con un dietista-nutricionista."),
        ]),
    "cuenta": dict(
        body="""<h2>Las fases de una buena preparación</h2>
<ul><li><strong>Base:</strong> mucho trabajo suave y fuerza para construir el motor aeróbico.</li>
<li><strong>Desarrollo:</strong> la carga sube de forma progresiva y aparece el trabajo de umbral.</li>
<li><strong>Específico:</strong> entrenas a ritmo de carrera y pruebas nutrición y material.</li>
<li><strong>Puesta a punto (tapering):</strong> bajas el volumen para llegar fresco, manteniendo algo de intensidad.</li></ul>
<h2>¿Cuántas semanas necesito?</h2>
<p>Con una base previa de entrenamiento, como referencia: entre 8 y 12 semanas para un 10K, entre 10 y 14 para una media maratón, entre 12 y 20 para un maratón, y entre 16 y 24 para un medio Ironman o un Ironman. Si partes de cero, suma unas semanas de base.</p>
<h2>La puesta a punto</h2>
<p>Suele durar 1 semana en 5K y 10K, unas 2 en media maratón y medio Ironman, y alrededor de 3 en maratón e Ironman. Se reduce el volumen entre un 30 y un 50 %, pero no la frecuencia ni del todo la intensidad: así llegas descansado sin perder chispa.</p>""",
        faqs=[
            ("¿Cuántas semanas hacen falta para preparar un maratón?", "Con una base de rodajes regulares, entre 12 y 20 semanas de preparación específica. Si es tu primer maratón o partes de poco volumen, mejor apurar hacia la parte alta."),
            ("¿Qué es el tapering?", "Es la reducción de carga de las últimas semanas antes de la carrera para eliminar fatiga y llegar en tu mejor forma. Se baja sobre todo el volumen, manteniendo algo de intensidad."),
            ("¿Qué hago la semana de la carrera?", "Sesiones cortas con algún cambio de ritmo, dormir bien, cuidar la hidratación y no probar nada nuevo. Ten tu plan de ritmos y de nutrición claro."),
            ("¿Dónde se guarda mi carrera?", "Solo en tu navegador, en este dispositivo. No se envía a ningún servidor."),
        ]),
}

LINKS = [("calculadora-ritmo-maraton.html", "Tiempos y ritmos", "5K · 10K · MEDIA · MARATÓN"),
         ("calculadora-zonas-entrenamiento.html", "Zonas de entrenamiento", "PULSO · RITMO · POTENCIA"),
         ("calculadora-nutricion-carrera.html", "Nutrición en carrera", "HIDRATOS · LÍQUIDO · SODIO"),
         ("cuenta-atras-carrera.html", "Cuenta atrás", "FECHA · FASE · QUÉ TOCA"),
         ("laboratorio.html", "Informe de tus datos", "SUBE TU CSV DE TRAININGPEAKS")]


def more_tools(current):
    return "".join(f'<a class="more-tool" href="{u}"><span class="tile-k">{k}</span><b>{t}</b><span class="tile-go" aria-hidden="true">↗</span></a>' for u, t, k in LINKS if u != current)


for c in CALCS:
    T = TEXTOS[c["key"]]
    ld = [faq_ld(T["faqs"]), crumbs_ld([("Inicio", ""), ("Laboratorio", "laboratorio.html"), (c["crumb"], c["file"])]),
          {"@context": "https://schema.org", "@type": "WebApplication", "name": c["crumb"], "url": SITE + c["file"], "applicationCategory": "HealthApplication",
           "operatingSystem": "Web", "inLanguage": "es", "offers": {"@type": "Offer", "price": "0", "priceCurrency": "EUR"}}]
    page = head(c["title"], c["desc"], c["file"], jsonld=ld) + nav(current="Laboratorio") + f"""
  <main class="lab-page calc-page">
    <section class="section section-dark lab-top"><div class="container">
      <nav class="crumbs" aria-label="Migas de pan"><a href="index.html">Inicio</a> / <a href="laboratorio.html">Laboratorio</a> / <span>{c['crumb']}</span></nav>
      <div class="section-heading">
        <p class="eyebrow"><span class="dot"></span> CALCULADORA GRATIS</p>
        <h1>{c['h1']}</h1>
        <p class="section-intro">{c['intro']}</p>
      </div>
      {panel(*c['panel'])}
    </div></section>

    <section class="section section-dark seo-sec"><div class="container seo-grid">
      <article class="seo-text">{T['body']}</article>
      <aside class="seo-aside">
        <p class="eyebrow">MÁS HERRAMIENTAS</p>
        {more_tools(c['file'])}
        <a class="quiz-mini" href="test.html"><b>¿Qué plan es para ti?</b><span>5 preguntas · 60 segundos ↗</span></a>
      </aside>
    </div></section>

    <section class="section section-dark section-line faq-dark"><div class="container faq-wrap">
      <div class="section-heading"><p class="eyebrow">PREGUNTAS FRECUENTES</p><h2>LO QUE MÁS<br><span class="orange">SE PREGUNTA.</span></h2></div>
      <div class="faq-list">{faq_html(T['faqs'])}</div>
    </div></section>

    <section class="final-cta"><div class="container final-cta-inner"><p class="eyebrow">DEL DATO AL PLAN</p><h2>¿QUIERES UN PLAN<br>QUE USE <span>TODO ESTO?</span></h2><p>Lo llevamos a tu calendario de TrainingPeaks, semana a semana, con tus zonas y tu objetivo.</p><div class="hero-actions" style="justify-content:center"><a class="button button-orange" href="index.html#planes">Ver planes ↗</a><a class="text-link" href="test.html">Haz el test de 60 s <span>↗</span></a></div></div></section>
  </main>
""" + footer(scripts=["calc.js?v=1"])
    open(c["file"], "w", encoding="utf-8").write(page)
    print("ok", c["file"])

# ---------------------------------------------------------------- blog
ARTICULOS = [
    dict(slug="forma-fatiga-frescura-ctl-atl-tsb", date="2026-11-27",
         title="Forma, fatiga y frescura: qué son el CTL, el ATL y el TSB de TrainingPeaks",
         summary="Las tres líneas del gráfico más famoso de TrainingPeaks, explicadas fácil: qué miden, cómo leerlas y qué valores vigilar.",
         body="""<p>Si usas TrainingPeaks habrás visto el gráfico de rendimiento, con una línea azul, una rosa y unas barras amarillas. Son la forma (CTL), la fatiga (ATL) y la frescura (TSB). Bien entendidas, te dicen si estás cargando, si te estás pasando o si llegas fresco a tu carrera.</p>
<h2>Todo parte del TSS</h2>
<p>El <strong>TSS</strong> (Training Stress Score) resume en un número cuánto te ha cargado una sesión, combinando duración e intensidad. Una hora a tu ritmo umbral equivale a 100 TSS. Para que sea fiable, tus umbrales (FTP, ritmo umbral o pulso umbral) tienen que estar bien configurados.</p>
<h2>Forma (CTL): lo que has construido</h2>
<p>Es la media de tu TSS diario de las últimas 6 semanas, aproximadamente. Sube despacio y representa tu capacidad para aguantar carga: tu forma de fondo.</p>
<h2>Fatiga (ATL): lo que llevas encima</h2>
<p>Es lo mismo, pero con la última semana. Sube y baja rápido: un par de días duros la disparan y un par de días suaves la bajan.</p>
<h2>Frescura (TSB): la diferencia</h2>
<p>Es la forma menos la fatiga. Como referencia orientativa:</p>
<ul><li><strong>Por debajo de −30:</strong> fatiga muy alta; riesgo de pasarte.</li>
<li><strong>Entre −30 y −10:</strong> fase productiva de carga.</li>
<li><strong>Entre −10 y +5:</strong> equilibrio.</li>
<li><strong>Entre +5 y +25:</strong> fresco; buen momento para competir.</li></ul>
<h2>Dos avisos importantes</h2>
<p><strong>Vigila lo rápido que sube la forma:</strong> subirla más de 5 a 8 puntos por semana durante varias semanas suele ser demasiado. Y <strong>revisa tus umbrales</strong>: si están desactualizados, el TSS sale inflado y todos estos números pierden sentido. Me pasó a mí: mis rodajes suaves marcaban un IF imposible porque mi ritmo umbral estaba mal.</p>
<p>Puedes ver tus tres líneas gratis subiendo tu exportación de TrainingPeaks al <a href="../laboratorio.html">informe del laboratorio</a>: te avisa si detecta umbrales mal configurados.</p>"""),
    dict(slug="como-calcular-zonas-entrenamiento", date="2026-11-27",
         title="Cómo calcular tus zonas de entrenamiento (y por qué las de tu reloj pueden fallar)",
         summary="Pulso máximo, pulso en reposo, ritmo umbral y FTP: cómo medirlos bien para que tus zonas sirvan de verdad.",
         body="""<p>Entrenar por zonas solo funciona si las zonas son tuyas. Muchos relojes parten de un pulso máximo estimado con la edad y el resultado puede estar desviado más de 10 pulsaciones. Así se calculan bien.</p>
<h2>1. Tu pulso máximo real</h2>
<p>La fórmula «220 − edad» es una media de población con mucho error individual. Mejor usa el pulso más alto que hayas registrado en un esfuerzo máximo reciente: el final de una carrera de 5K o unas series cuesta arriba muy duras, bien calentado.</p>
<h2>2. Tu pulso en reposo</h2>
<p>Mídelo al despertar, aún tumbado, durante varios días, y haz la media. Con el máximo y el reposo puedes usar el método de la reserva (Karvonen), que se adapta mejor a tu forma física.</p>
<h2>3. Tu ritmo umbral (carrera)</h2>
<p>Corre 30 minutos a tope en llano después de calentar y toma el ritmo medio de los últimos 20 minutos. Es una buena aproximación al ritmo que podrías sostener una hora.</p>
<h2>4. Tu FTP (bici)</h2>
<p>Tras un buen calentamiento, rueda 20 minutos lo más fuerte que puedas de forma constante y multiplica la potencia media por 0,95.</p>
<h2>5. Repite cada 6 a 8 semanas</h2>
<p>Tus zonas cambian con tu forma. Repite los tests en condiciones parecidas (mismo recorrido, hora y descanso previo) para poder comparar.</p>
<p>Con esos valores, calcula tus zonas de pulso, ritmo y potencia en la <a href="../calculadora-zonas-entrenamiento.html">calculadora de zonas</a>.</p>"""),
    dict(slug="calculadoras-del-laboratorio", date="2026-11-26",
         title="Calculadoras gratis en el laboratorio",
         summary="Predictor de tiempos, zonas de entrenamiento, nutrición en carrera y cuenta atrás, gratis y sin registrarte.",
         body="""<p>El laboratorio tiene herramientas que puedes usar ahora mismo desde tu navegador, sin crear cuenta y sin que se guarde ningún dato:</p>
<ul><li><a href="../calculadora-ritmo-maraton.html"><strong>Calculadora de tiempos y ritmos</strong></a>: parte de una marca reciente y estima tus tiempos en 5K, 10K, media maratón y maratón.</li>
<li><a href="../calculadora-zonas-entrenamiento.html"><strong>Zonas de entrenamiento</strong></a>: pulso, ritmo de carrera y potencia en bici a partir de tus valores.</li>
<li><a href="../calculadora-nutricion-carrera.html"><strong>Nutrición en carrera</strong></a>: hidratos, líquido y sodio orientativos según la duración de la prueba y el calor.</li>
<li><a href="../cuenta-atras-carrera.html"><strong>Cuenta atrás</strong></a>: cuántas semanas faltan para tu carrera y en qué fase deberías estar.</li></ul>
<p>Recuerda que son estimaciones. Úsalas como punto de partida, contrástalas con tus sensaciones y pruébalas en entrenamientos antes de aplicarlas el día de la carrera.</p>"""),
    dict(slug="bienvenida-al-laboratorio", date="2026-11-26",
         title="Bienvenida al laboratorio",
         summary="Qué es ENDURACE LAB y qué vas a encontrar aquí cada semana.",
         body="""<p>ENDURACE LAB nace con una idea sencilla: entrenar mejor empieza por mirar tus datos con calma y tomar decisiones a partir de ellos, no de modas.</p>
<p>Cada semana publicaré aquí una entrada corta con una de estas cosas:</p>
<ul><li>un experimento propio, con sus números;</li><li>una pregunta frecuente sobre entrenamiento o nutrición, respondida con claridad;</li><li>un resultado o un aprendizaje de mi propia preparación.</li></ul>
<p>Si quieres ver cómo está repartida tu carga ahora mismo, prueba el <a href="../laboratorio.html">informe del laboratorio</a>: lo analiza todo en tu navegador y no guardamos nada.</p>"""),
]

MESES = ["enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre", "noviembre", "diciembre"]
fecha = lambda d: f"{int(d[8:])} de {MESES[int(d[5:7]) - 1]} de {d[:4]}"
os.makedirs("blog", exist_ok=True)
ARTICULOS.sort(key=lambda a: a["date"], reverse=True)

for i, a in enumerate(ARTICULOS):
    path = f"blog/{a['slug']}.html"
    ld = [{"@context": "https://schema.org", "@type": "BlogPosting", "headline": a["title"], "description": a["summary"], "datePublished": a["date"],
           "inLanguage": "es", "mainEntityOfPage": SITE + path, "image": SITE + "og-image.jpg",
           "author": {"@type": "Person", "name": "Joan Espasa"}, "publisher": {"@type": "Organization", "name": "ENDURACE LAB", "logo": {"@type": "ImageObject", "url": SITE + "logo.svg"}}},
          crumbs_ld([("Inicio", ""), ("Blog", "blog.html"), (a["title"], path)])]
    otros = [x for x in ARTICULOS if x is not a][:3]
    more = "".join(f'<a class="post" href="{x["slug"]}.html"><div class="date">{fecha(x["date"])}</div><h3>{html.escape(x["title"])}</h3></a>' for x in otros)
    page = head(f"{a['title']} | ENDURACE LAB", a["summary"], path, pre="../", jsonld=ld, og_type="article") + nav("../", "Blog") + f"""
  <main>
    <section class="section section-dark"><div class="container blog-post">
      <nav class="crumbs" aria-label="Migas de pan"><a href="../index.html">Inicio</a> / <a href="../blog.html">Blog</a></nav>
      <p class="eyebrow">CUADERNO DE LABORATORIO · {fecha(a['date']).upper()}</p>
      <h1>{html.escape(a['title'])}</h1>
      <p class="post-lead">{html.escape(a['summary'])}</p>
      <article class="seo-text">{a['body']}</article>
      <div class="lab-cta"><div><p class="eyebrow">PRUÉBALO GRATIS</p><h2>TUS DATOS, TRADUCIDOS.</h2><p>Sube tus entrenamientos de TrainingPeaks y descubre tu forma, tu intensidad y si tu motor mejora.</p></div><div class="lab-cta-actions"><a class="button button-orange" href="../laboratorio.html">Abrir el laboratorio <span>↗</span></a><a class="text-link" href="../test.html">¿Qué plan es para ti? <span>↗</span></a></div></div>
      <div class="more-posts"><p class="eyebrow">SIGUE LEYENDO</p>{more}</div>
    </div></section>
  </main>
""" + footer("../")
    open(path, "w", encoding="utf-8").write(page)
    print("ok", path)

lista = "".join(f'<a class="post" href="blog/{a["slug"]}.html"><div class="date">{fecha(a["date"])}</div><h2>{html.escape(a["title"])}</h2><p>{html.escape(a["summary"])}</p></a>' for a in ARTICULOS)
idx = head("Blog: entrenamiento con datos para triatlón y running | ENDURACE LAB",
           "Artículos sobre entrenamiento, zonas, carga y nutrición en triatlón, running y ciclismo, explicados con datos reales.", "blog.html") + nav(current="Blog") + f"""
  <main>
    <section class="section section-dark"><div class="container blog-index">
      <div class="section-heading"><p class="eyebrow"><span class="dot"></span> CUADERNO DE LABORATORIO</p><h1>ENTRENA<br><span class="orange">CON DATOS.</span></h1>
      <p class="section-intro">Un experimento, una idea o un resultado cada semana sobre entrenamiento y nutrición en triatlón, running y ciclismo.</p></div>
      <div class="post-list">{lista}</div>
    </div></section>
  </main>
""" + footer()
open("blog.html", "w", encoding="utf-8").write(idx)
json.dump([{k: a[k] for k in ("slug", "date", "title", "summary")} | {"url": f"blog/{a['slug']}.html"} for a in ARTICULOS],
          open("posts.json", "w", encoding="utf-8"), ensure_ascii=False, indent=2)
print("ok blog.html + posts.json")

# ---------------------------------------------------------------- sitemap
urls = ["", "running.html", "laboratorio.html"] + [c["file"] for c in CALCS] + ["test.html", "blog.html"] + [f"blog/{a['slug']}.html" for a in ARTICULOS] + ["inscripcion.html", "condiciones.html"]
lastmod = {f"blog/{a['slug']}.html": a["date"] for a in ARTICULOS}
sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join(
    f"  <url><loc>{SITE}{u}</loc><lastmod>{lastmod.get(u, '2026-11-27')}</lastmod></url>\n" for u in urls) + "</urlset>\n"
open("sitemap.xml", "w", encoding="utf-8").write(sm)
print("ok sitemap.xml")
