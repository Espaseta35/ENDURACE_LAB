#!/usr/bin/env python3
"""Genera los reels de ENDURACE LAB con voz.

    python3 _build/reels/reels.py              # todos
    python3 _build/reels/reels.py 01 04        # solo algunos (por número)

Para cada reel: crea la voz con la voz del Mac, ajusta la duración de cada escena a la frase,
escribe el timeline y lo renderiza con render.swift (motor engine.html).
Salida en ~/Desktop/endurace_reels/ junto con textos.txt (texto de cada publicación).
"""
import json, os, subprocess, sys, re

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.expanduser("~/Desktop/endurace_reels")
WORK = os.path.join(HERE, "out")
VOZ, RATE = os.environ.get("VOZ", "Mónica"), os.environ.get("RATE", "185")
os.makedirs(OUT, exist_ok=True); os.makedirs(WORK, exist_ok=True)

O, W = "#ff6b2c", "#f4f4f1"
CTA_V = "Calcúlalo gratis en endurace lab punto com."

# Datos reales de la temporada (CSV de TrainingPeaks, mayo-noviembre 2026)
EF = [1.022, 1.036, 1.144, 1.18, 0.998, 1.175, 1.066, 1.146, 1.112, 1.052, 1.176, 1.101, 1.18, 1.095, 1.2, 1.26, 1.154, 1.205,
      1.222, 1.202, 1.185, 1.093, 1.153, 1.191, 1.142, 1.101, 1.181, 1.208, 1.199, 1.265, 1.24, 1.269, 1.28, 1.31, 1.264, 1.223]
n = len(EF); mx = (n - 1) / 2; my = sum(EF) / n
sl = sum((i - mx) * (y - my) for i, y in enumerate(EF)) / sum((i - mx) ** 2 for i in range(n)); ic = my - sl * mx

REELS = [
  dict(id="01", name="zonas-rodajes-suaves", tag="ZONAS", scenes=[
    dict(type="hook", size=150, lines=[["¿TUS RODAJES"], ["SUAVES SON"], ["SUAVES DE VERDAD?", "o"]], v="¿Tus rodajes suaves son suaves de verdad?"),
    dict(type="zones", k="PULSO MÁX. 190 · REPOSO 52", hl=1, rows=[["Z1 · Recuperación", "121–135", 60], ["Z2 · Aeróbica", "135–149", 70], ["Z3 · Tempo", "149–162", 80], ["Z4 · Umbral", "162–176", 90], ["Z5 · Máxima", "176–190", 100]],
         v="Con un pulso máximo de ciento noventa y cincuenta y dos en reposo, estas son tus zonas.", min=4),
    dict(type="big", k="TU RODAJE SUAVE", fmt="str", to="135–149", unit="PULSACIONES", sub="Si vas por encima, estás en zona 3: demasiado rápido para recuperar.",
         v="Tu rodaje suave va entre ciento treinta y cinco y ciento cuarenta y nueve pulsaciones. Por encima, ya es zona tres."),
    dict(type="cta", k="CALCULA LAS TUYAS GRATIS", v="Calcula tus zonas gratis en endurace lab punto com.")],
    caption="¿Tus rodajes suaves son suaves de verdad? 🫀\nLa mayoría los corre en zona 3: demasiado rápido para recuperar y demasiado lento para mejorar.\nCalcula tus zonas de pulso, ritmo y potencia gratis (enlace en la bio).",
    pin="Dime tu pulso máximo y tu pulso en reposo y te digo tu zona 2 👇", tags="#running #triatlon #zona2 #entrenamiento #frecuenciacardiaca #corredores"),

  dict(id="02", name="geles-maraton", tag="NUTRICIÓN", scenes=[
    dict(type="hook", size=150, lines=[["¿CUÁNTOS GELES"], ["NECESITAS PARA"], ["TU MARATÓN?", "o"]], v="¿Cuántos geles necesitas para tu maratón?"),
    dict(type="cards", k="MARATÓN EN 3:30", cards=[dict(k="HIDRATOS POR HORA", v="60–90 g"), dict(k="TOTAL A 60 g/h", v="210 g", on=True)],
         v="Si lo corres en tres horas y media, necesitas entre sesenta y noventa gramos de hidratos por hora. A sesenta, son doscientos diez gramos.", min=4),
    dict(type="big", fmt="str", to="8–10", unit="GELES", sub="De 20–25 g cada uno. Empieza en el minuto 30–45 y toma uno cada 20–30 minutos.",
         v="Unos ocho a diez geles. Empieza en el minuto treinta y toma uno cada veinte o treinta minutos."),
    dict(type="cta", k="CALCULA TU ESTRATEGIA", v=CTA_V)],
    caption="¿Cuántos geles necesitas para tu maratón? 🍯\nEn 3:30 y a 60 g de hidratos por hora: unos 8–10 geles.\nY lo más importante: pruébalo antes en tus tiradas largas.\nCalcula tu estrategia gratis (enlace en la bio).",
    pin="¿En cuánto vas a correr tu maratón? Te digo cuántos geles 👇", tags="#maraton #nutriciondeportiva #running #geles #corredores #maratonvalencia"),

  dict(id="03", name="cuenta-atras", tag="CUENTA ATRÁS", scenes=[
    dict(type="hook", lines=[["¿CUÁNTAS"], ["SEMANAS"], ["TE QUEDAN?", "o"]], v="¿Cuántas semanas te quedan para tu maratón?"),
    dict(type="phases", k="SI TU MARATÓN ES DENTRO DE", big="12 SEMANAS", on=1, pos=42.9, ph=[["BASE", 4], ["DESARROLLO", 8], ["ESPECÍFICO", 6], ["PUESTA A PUNTO", 3]],
         sub="Ahora toca: subir la carga poco a poco y meter trabajo de umbral.", v="Si faltan doce semanas, estás en desarrollo: sube la carga poco a poco y mete trabajo de umbral.", min=4),
    dict(type="list", title='<span class="o">Y DESPUÉS</span>', items=["A 9 semanas: bloque específico a ritmo de carrera", "A 3 semanas: puesta a punto, baja el volumen", "Última semana: nada nuevo"],
         v="A nueve semanas, bloque específico. A tres, puesta a punto. Y la última, nada nuevo."),
    dict(type="cta", k="PON LA FECHA DE TU CARRERA", v="Pon tu fecha gratis en endurace lab punto com.")],
    caption="¿Cuántas semanas te quedan para tu carrera? ⏳\nCada fase de la preparación tiene su trabajo: base, desarrollo, específico y puesta a punto.\nPon tu fecha y mira en qué fase estás (enlace en la bio).",
    pin="¿Cuál es tu próxima carrera y cuándo es? 👇", tags="#maraton #triatlon #running #planentrenamiento #corredores #tapering"),

  dict(id="04", name="mi-temporada", tag="MIS DATOS", scenes=[
    dict(type="hook", k="MAYO — NOVIEMBRE 2026", lines=[["MI"], ["TEMPORADA", "ol"], ["EN DATOS", "o"]], v="Mi temporada, en datos."),
    dict(type="big", k="HE ENTRENADO", fmt="int", to=286, unit="HORAS", sub="En <b>244 entrenos</b>. Sin contar paseos.", v="Doscientas ochenta y seis horas de entrenamiento."),
    dict(type="big", k="HE RECORRIDO", fmt="int", to=4351, unit="KILÓMETROS", sub="Como hacer <b>5,6 veces</b> el Camino de Santiago francés.", v="Cuatro mil trescientos cincuenta y un kilómetros. Más de cinco veces el Camino de Santiago."),
    dict(type="bars", k="MI MES MÁS FUERTE", title="JULIO", hl=2, hlLabel="53 h", items=[["M", 36.4], ["J", 44.2], ["J", 53.3], ["A", 28.0], ["S", 43.6], ["O", 49.1], ["N", 31.0]], v="Mi mes más fuerte, julio, con cincuenta y tres horas.", min=3.6),
    dict(type="big", k="MI MOTOR · CARRERA", fmt="dec1", to=17.3, pre="+", small="%", unit="DE EFICIENCIA", sub="Corro más rápido con el mismo pulso.", v="Y mi eficiencia en carrera ha mejorado un diecisiete por ciento."),
    dict(type="big", k="MI TIPO DE ATLETA", fmt="str", to="MODO SERIES", sub="Lo mío es apretar. Me toca más volumen suave.", v="Mi tipo de atleta: modo series."),
    dict(type="cta", k="TU TEMPORADA, GRATIS", title='HAZ LA<br><span class="o">TUYA</span>', v="Haz la tuya gratis en endurace lab punto com.")],
    caption="Mi temporada en datos 📊\n286 horas · 4351 km · +17 % de eficiencia en carrera.\nSube tu CSV de TrainingPeaks y descubre la tuya, con imagen para compartir (enlace en la bio).",
    pin="¿Cuál ha sido tu mes más fuerte este año? 👇", tags="#triatlon #running #trainingpeaks #datos #temporada #endurance"),

  dict(id="05", name="mi-motor-17", tag="MIS DATOS", scenes=[
    dict(type="hook", lines=[["MI MOTOR"], ["HA MEJORADO"], ["UN 17 %", "o"]], v="Mi motor ha mejorado un diecisiete por ciento."),
    dict(type="line", k="EFICIENCIA EN RODAJES SUAVES", pts=EF, trend=[ic, ic + sl * (n - 1)], **{"from": "MAYO", "to": "NOVIEMBRE"},
         sub="Cada punto es un rodaje. La línea, la tendencia.", v="Cada punto es uno de mis rodajes suaves. Y la tendencia no para de subir.", min=4.4),
    dict(type="big", k="MISMO PULSO, MÁS RÁPIDO", fmt="dec1", to=17.3, pre="+", small="%", unit="DE EFICIENCIA", sub="Metros por minuto que corro por cada pulsación.",
         v="Corro más rápido con el mismo pulso. Eso es base aeróbica."),
    dict(type="cta", k="MIDE EL TUYO GRATIS", title='SUBE TU<br><span class="o">CSV</span>', v="Mide el tuyo gratis en endurace lab punto com.")],
    caption="Mi motor ha mejorado un 17 % 📈\nNo es que corra más rápido: es que corro más rápido con el mismo pulso. Eso es base aeróbica.\nMide el tuyo con tus datos de TrainingPeaks (enlace en la bio).",
    pin="¿Sabes si tu eficiencia está subiendo o bajando? 👇", tags="#running #zona2 #baseaerobica #trainingpeaks #corredores #triatlon"),

  dict(id="06", name="error-umbral", tag="MIS DATOS", scenes=[
    dict(type="hook", lines=[["EL ERROR"], ["QUE INFLABA"], ["MIS DATOS", "o"]], v="El error que inflaba todos mis datos."),
    dict(type="cards", k="FACTOR DE INTENSIDAD (IF)", cards=[dict(k="NORMAL EN UN RODAJE SUAVE", v="0,65–0,85"), dict(k="EL MÍO CORRIENDO SUAVE", v="1,34", on=True)],
         v="En un rodaje suave, lo normal es un IF de cero sesenta y cinco a cero ochenta y cinco. El mío marcaba uno treinta y cuatro.", min=4.2),
    dict(type="big", k="RESULTADO", fmt="int", to=828, unit="TSS EN UN 26K", sub="Imposible. Mi <b>ritmo umbral</b> en TrainingPeaks estaba mal.", v="Ochocientos veintiocho de TSS en un veintiséis kilómetros. Imposible: mi umbral estaba mal."),
    dict(type="list", title='<span class="o">LA SOLUCIÓN</span>', items=["Actualiza tu ritmo umbral", "Repite el test cada 6–8 semanas", "Comprueba que tu IF tenga sentido"], v="Actualiza tu umbral y repite el test cada seis u ocho semanas."),
    dict(type="cta", k="EL LABORATORIO LO DETECTA SOLO", v="Compruébalo gratis en endurace lab punto com.")],
    caption="El error que inflaba todos mis datos 😅\nMis rodajes suaves marcaban un IF de 1,34 y un 26K, 828 de TSS. Mi ritmo umbral en TrainingPeaks estaba desactualizado.\nEl laboratorio te avisa si te pasa lo mismo (enlace en la bio).",
    pin="¿Cuándo actualizaste tu umbral por última vez? 👇", tags="#trainingpeaks #running #triatlon #tss #entrenamiento #datos"),

  dict(id="07", name="aprendi-312", tag="MIS DATOS", scenes=[
    dict(type="hook", lines=[["3 COSAS"], ["QUE APRENDÍ"], ["BAJANDO A 3:12", "o"]], v="Tres cosas que aprendí bajando a tres doce en maratón."),
    dict(type="list", items=["El calor lo cambia todo: ese día, manda el pulso", "Valida tu ritmo objetivo con un test", "Los rodajes suaves, suaves de verdad"], at=.4, gap=1.1,
         v="Uno: el calor lo cambia todo. Dos: valida tu ritmo con un test. Tres: los rodajes suaves, suaves de verdad.", min=5),
    dict(type="big", k="MI MARATÓN", fmt="str", to="3:12", unit="Y A POR MÁS", v="Tres horas doce. Y a por más."),
    dict(type="cta", k="CALCULA TU RITMO DE MARATÓN", v=CTA_V)],
    caption="3 cosas que aprendí bajando a 3:12 en maratón 🏃\n1. El calor lo cambia todo: ese día, manda el pulso.\n2. Valida tu ritmo objetivo con un test.\n3. Los rodajes suaves, suaves de verdad.\nCalcula tu ritmo de maratón gratis (enlace en la bio).",
    pin="¿Cuál ha sido tu mayor aprendizaje preparando un maratón? 👇", tags="#maraton #running #corredores #sub315 #entrenamiento #maratonvalencia"),

  dict(id="08", name="mito-220-edad", tag="MITOS", scenes=[
    dict(type="hook", lines=[["220 − EDAD"], ["NO ES TU"], ["PULSO MÁXIMO", "o"]], v="Doscientos veinte menos tu edad no es tu pulso máximo."),
    dict(type="big", k="CON 30 AÑOS, LA FÓRMULA DICE", fmt="int", to=190, unit="PULSACIONES", v="Con treinta años, la fórmula dice ciento noventa."),
    dict(type="cards", k="PERO TU MÁXIMO REAL PUEDE SER", cards=[dict(k="POR DEBAJO", v="178"), dict(k="O POR ENCIMA", v="202", on=True)],
         v="Pero puede fallar en más de diez pulsaciones, por arriba o por abajo. Y todas tus zonas saldrían mal.", min=4),
    dict(type="list", title='<span class="o">CÓMO MEDIRLO</span>', items=["Calienta bien", "Series cuesta arriba muy duras o el final de un 5K", "Usa el pulso más alto que veas"], v="Mídelo en un esfuerzo máximo real, bien calentado."),
    dict(type="cta", k="CALCULA TUS ZONAS", v="Calcula tus zonas gratis en endurace lab punto com.")],
    caption="220 menos tu edad NO es tu pulso máximo ❌\nPuede fallar en más de 10 pulsaciones, y con él todas tus zonas.\nMídelo en un esfuerzo máximo real y calcula tus zonas gratis (enlace en la bio).",
    pin="¿Cuál es tu pulso máximo real y cuántos años tienes? 👇", tags="#running #ciclismo #triatlon #frecuenciacardiaca #mitos #entrenamiento"),

  dict(id="09", name="regla-80-20", tag="MITOS", scenes=[
    dict(type="hook", lines=[["ENTRENAR MÁS"], ["NO ES"], ["ENTRENAR MEJOR", "o"]], v="Entrenar más no es entrenar mejor."),
    dict(type="split", title='LA REGLA<br><span class="o">80/20</span>', parts=[["Suave", 80, W], ["Media o alta", 20, O]], sub="80 % del tiempo suave. 20 % a intensidad media o alta.",
         v="La regla del ochenta veinte: ochenta por ciento del tiempo suave, y solo un veinte por ciento intenso.", min=4.2),
    dict(type="hook", lines=[["¿Y TÚ,"], ["CÓMO"], ["REPARTES?", "o"]], sub="Mira tu reparto real con tus datos de TrainingPeaks.", v="¿Y tú? ¿Cómo repartes tu intensidad?"),
    dict(type="cta", k="MIRA TU REPARTO GRATIS", v="Descúbrelo gratis en endurace lab punto com.")],
    caption="Entrenar más no es entrenar mejor 🧠\nLa regla 80/20: el 80 % del tiempo suave y el 20 % intenso. La mayoría hace justo lo contrario.\nMira tu reparto real con tus datos de TrainingPeaks (enlace en la bio).",
    pin="Sé sincero: ¿tus rodajes suaves son suaves? 👇", tags="#running #triatlon #8020 #zona2 #entrenamiento #ciclismo"),

  dict(id="10", name="nada-nuevo", tag="CONSEJOS", scenes=[
    dict(type="hook", lines=[["NADA NUEVO"], ["EL DÍA DE"], ["LA CARRERA", "o"]], v="Nada nuevo el día de la carrera."),
    dict(type="list", title='<span class="o">PRUEBA ANTES</span>', size=110, items=["Los geles: marca, cantidad y cada cuánto", "Las zapatillas: al menos una tirada larga", "El desayuno: igual que en tus tiradas", "El ritmo: valídalo con un test"], at=.4, gap=.9,
         v="Los geles, las zapatillas, el desayuno y el ritmo. Todo, probado antes.", min=5),
    dict(type="cta", k="PLANIFICA TU NUTRICIÓN", v=CTA_V)],
    caption="Nada nuevo el día de la carrera ⚠️\nGeles, zapatillas, desayuno y ritmo: todo probado antes en tus tiradas largas.\nCalcula tu estrategia de nutrición gratis (enlace en la bio).",
    pin="¿Qué fue lo nuevo que probaste y salió mal? 👇", tags="#maraton #triatlon #running #consejos #corredores #nutriciondeportiva"),
]


def dur(path):
    o = subprocess.run(["afinfo", path], capture_output=True, text=True).stdout
    return float(re.search(r"estimated duration: ([\d.]+)", o).group(1))


def build(r):
    t, voice = 0.0, []
    for i, s in enumerate(r["scenes"]):
        f = os.path.join(WORK, f"{r['id']}_{i}.aiff")
        subprocess.run(["say", "-v", VOZ, "-r", RATE, "-o", f, s["v"]], check=True)
        d = dur(f)
        length = max(s.get("min", 2.4), d + (0.9 if i < len(r["scenes"]) - 1 else 1.0))
        s["start"], s["end"] = round(t, 3), round(t + length, 3)
        voice.append({"file": f, "at": round(t + 0.25, 3)})
        t += length
    tl = {"duration": round(t, 3), "tag": r["tag"], "scenes": r["scenes"], "voice": voice}
    p = os.path.join(WORK, f"{r['id']}.json")
    json.dump(tl, open(p, "w"), ensure_ascii=False)
    return p, t


def tool(name):
    """Compila una vez cada script Swift (encode, voz) para no recompilar en cada reel."""
    src, binp = os.path.join(HERE, name + ".swift"), os.path.join(WORK, name + "_bin")
    if not os.path.exists(binp) or os.path.getmtime(binp) < os.path.getmtime(src):
        subprocess.run(["swiftc", "-O", src, "-o", binp], check=True, capture_output=True)
    return binp


if __name__ == "__main__":
    import shutil, time
    sys.path.insert(0, HERE)
    import cdp_render
    want = set(sys.argv[1:])
    enc, voz = tool("encode"), tool("voz")
    textos = []
    for r in REELS:
        textos.append(f"===== {r['id']} · {r['name']}.mp4 =====\n{r['caption']}\n\n{r['tags']}\n\nComentario fijado: {r['pin']}\n")
    open(os.path.join(OUT, "textos.txt"), "w").write("\n".join(textos))
    for r in REELS:
        if want and r["id"] not in want:
            continue
        t0 = time.time()
        p, t = build(r)
        frames = os.path.join(WORK, "frames_" + r["id"])
        if os.path.isdir(frames):
            shutil.rmtree(frames)
        cdp_render.render(os.path.join(HERE, "engine.html"), p, frames, 9600 + int(r["id"]))
        silent = os.path.join(WORK, r["id"] + "_mudo.mp4")
        subprocess.run([enc, frames, silent, "30"], check=True, capture_output=True)
        tl = json.load(open(p))
        out = os.path.join(OUT, f"{r['id']}-{r['name']}.mp4")
        subprocess.run([voz, silent, out] + [f"{v['file']}@{v['at']}" for v in tl["voice"]], check=True, capture_output=True)
        shutil.rmtree(frames)
        os.remove(silent)
        print(f"OK {r['id']} · {t:.1f} s de vídeo · {time.time() - t0:.0f} s de proceso → {os.path.basename(out)}", flush=True)
    print("textos.txt listo")
