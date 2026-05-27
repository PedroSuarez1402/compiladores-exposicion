# app.py
import streamlit as st
from lexer import obtener_analizador_lexico
from parser import analizar_codigo
from pathlib import Path
import re

st.set_page_config(layout="wide", page_title="Dashboard LEX & YACC")

st.title("🖥️ Compiladores en Acción: Visualizador LEX y YACC")
st.markdown("Una herramienta didáctica para comprender las fases del Frontend de un compilador en tiempo real.")

st.subheader("📝 Código de Entrada")
if "codigo_usuario" not in st.session_state:
    st.session_state["codigo_usuario"] = "x = 15 + 20 - 5"

col_e1, col_e2, col_e3 = st.columns(3)
with col_e1:
    if st.button("Código Válido", use_container_width=True):
        st.session_state["codigo_usuario"] = "x = 10 + 5"
with col_e2:
    if st.button("Error Léxico", use_container_width=True):
        st.session_state["codigo_usuario"] = "x = 10 @ 5"
with col_e3:
    if st.button("Error Sintáctico", use_container_width=True):
        st.session_state["codigo_usuario"] = "x = + 10"

codigo_usuario = st.text_area("Escribe instrucciones matemáticas o asignaciones aquí:", key="codigo_usuario", height=100)

def _extraer_fragmento(texto, marca_inicio, marca_fin):
    lineas = texto.splitlines()
    idx_inicio = next((i for i, l in enumerate(lineas) if marca_inicio in l), None)
    idx_fin = next((i for i, l in enumerate(lineas) if marca_fin in l), None)
    if idx_inicio is None:
        return texto
    if idx_fin is None or idx_fin <= idx_inicio:
        return "\n".join(lineas[idx_inicio:])
    return "\n".join(lineas[idx_inicio:idx_fin])

def _leer_archivo_como_texto(ruta):
    try:
        return ruta.read_text(encoding="utf-8")
    except Exception:
        try:
            return ruta.read_text()
        except Exception:
            return None

def _pos_a_linea_columna(texto, pos):
    if pos is None or pos < 0:
        return 1, 1
    hasta = texto[:pos]
    linea = hasta.count("\n") + 1
    col = len(hasta.split("\n")[-1]) + 1
    return linea, col

def _marcar_posicion(texto, pos, ancho=90):
    if pos is None or pos < 0:
        return texto
    inicio = max(0, pos - ancho // 2)
    fin = min(len(texto), inicio + ancho)
    recorte = texto[inicio:fin]
    caret = " " * (pos - inicio) + "^"
    return f"{recorte}\n{caret}"

def _fragmento_token_lexer(texto_lex, tipo_token):
    marca_def = f"def t_{tipo_token}("
    marca_asig = f"t_{tipo_token}"
    lineas = texto_lex.splitlines()

    for i, l in enumerate(lineas):
        if marca_def in l:
            fin = i + 1
            while fin < len(lineas) and lineas[fin].strip() != "":
                fin += 1
            return "\n".join(lineas[i:fin]).strip()

    for i, l in enumerate(lineas):
        if l.strip().startswith(marca_asig):
            return l.strip()

    return None

def _lhs_desde_reduccion(mensaje):
    prefijo = "REDUCCIÓN:"
    if prefijo not in mensaje:
        return None
    cuerpo = mensaje.split(prefijo, 1)[1].strip()
    if "->" not in cuerpo:
        return None
    return cuerpo.split("->", 1)[0].strip()

def _fragmento_regla_parser(texto_yacc, mensaje_reduccion):
    mensaje = mensaje_reduccion.lower()
    if "instruccion ->" in mensaje and "=" in mensaje:
        marca_inicio = "def p_instruccion_asignacion"
    elif "instruccion ->" in mensaje:
        marca_inicio = "def p_instruccion_expresion"
    elif "expresion -> numero" in mensaje:
        marca_inicio = "def p_expresion_numero"
    elif "expresion -> variable" in mensaje:
        marca_inicio = "def p_expresion_variable"
    elif "expresion -> expresion" in mensaje:
        marca_inicio = "def p_expresion_operacion"
    else:
        marca_inicio = "def p_"

    lineas = texto_yacc.splitlines()
    idx_inicio = next((i for i, l in enumerate(lineas) if marca_inicio in l), None)
    if idx_inicio is None:
        return None
    fin = idx_inicio + 1
    while fin < len(lineas) and lineas[fin].strip() != "":
        fin += 1
    return "\n".join(lineas[idx_inicio:fin]).strip()

def _terminal_en_pila(tok):
    tipo = tok.get("type")
    valor = tok.get("value")
    if valor is None:
        return f"{tipo}"
    return f"{tipo}({valor})"

def _pila_como_texto(pila):
    if not pila:
        return "(vacía)"
    lineas = []
    for i, sym in enumerate(pila):
        lineas.append(f"{i:02d} | {sym}")
    lineas.append("TOP")
    return "\n".join(lineas)

def _produccion_desde_mensaje_reduccion(mensaje):
    m = re.search(r"REDUCCI[ÓO]N:\s*(.*)", mensaje)
    if not m:
        return None
    cuerpo = m.group(1).strip()
    prod = cuerpo.split("(", 1)[0].strip()
    if "->" not in prod:
        return None
    lhs, rhs = [p.strip() for p in prod.split("->", 1)]
    rhs_raw = rhs.split()

    rhs_mapped = []
    for sym in rhs_raw:
        if sym == "+":
            rhs_mapped.append("SUMA")
        elif sym == "-":
            rhs_mapped.append("RESTA")
        elif sym == "=":
            rhs_mapped.append("IGUAL")
        elif sym in {"NUMERO", "VARIABLE", "expresion", "instruccion"}:
            rhs_mapped.append(sym)
        elif re.fullmatch(r"[A-Za-z_]\w*", sym):
            rhs_mapped.append("VARIABLE")
        else:
            rhs_mapped.append(sym)

    return {"lhs": lhs, "rhs": rhs_mapped, "rhs_raw": rhs_raw}

def _simular_reducciones_con_pila(tokens_detalle, reducciones):
    pila = [_terminal_en_pila(t) for t in tokens_detalle]
    pasos = []
    for red in reducciones:
        prod = _produccion_desde_mensaje_reduccion(red)
        if not prod:
            pasos.append({
                "mensaje": red,
                "error": "No se pudo inferir la producción desde el texto de la reducción.",
                "antes": list(pila),
                "popped": [],
                "despues": list(pila)
            })
            continue
        antes = list(pila)
        n = len(prod["rhs"])
        popped = pila[-n:] if n <= len(pila) else list(pila)
        pila = pila[:-n] if n <= len(pila) else []
        pila.append(prod["lhs"])
        despues = list(pila)
        pasos.append({
            "mensaje": red,
            "lhs": prod["lhs"],
            "rhs": prod["rhs"],
            "rhs_raw": prod["rhs_raw"],
            "antes": antes,
            "popped": popped,
            "despues": despues
        })
    return pasos

if codigo_usuario:
    if "analisis_listo" not in st.session_state:
        st.session_state["analisis_listo"] = False
    if "paso_actual" not in st.session_state:
        st.session_state["paso_actual"] = 0
    if "codigo_analizado" not in st.session_state:
        st.session_state["codigo_analizado"] = ""

    if st.session_state["codigo_analizado"] != codigo_usuario:
        st.session_state["analisis_listo"] = False
        st.session_state["paso_actual"] = 0

    col_a1, col_a2 = st.columns([1, 3])
    with col_a1:
        analizar = st.button("Analizar", type="primary", use_container_width=True)
    with col_a2:
        st.caption("Ejecuta el análisis una vez y luego navega paso a paso por tokens y reducciones.")

    if analizar:
        lexer_inf = obtener_analizador_lexico()
        lexer_inf.input(codigo_usuario)

        tokens_detalle = []
        tokens_tabla = []
        while True:
            tok = lexer_inf.token()
            if not tok:
                break
            tokens_detalle.append({
                "type": tok.type,
                "value": tok.value,
                "lexpos": tok.lexpos
            })
            tokens_tabla.append({
                "Token (Clase)": tok.type,
                "Lexema (Texto)": tok.value,
                "Posición Inicial": tok.lexpos
            })

        lexer_para_parser = obtener_analizador_lexico()
        res, reducciones, errores, variables = analizar_codigo(codigo_usuario, lexer_para_parser)
        todos_los_errores = lexer_para_parser.lista_errores + errores

        st.session_state["tokens_detalle"] = tokens_detalle
        st.session_state["tokens_tabla"] = tokens_tabla
        st.session_state["reducciones"] = reducciones
        st.session_state["errores"] = todos_los_errores
        st.session_state["variables"] = variables
        st.session_state["resultado"] = res
        st.session_state["reducciones_simuladas"] = _simular_reducciones_con_pila(tokens_detalle, reducciones)
        st.session_state["codigo_analizado"] = codigo_usuario
        st.session_state["paso_actual"] = 0
        st.session_state["analisis_listo"] = True

    if not st.session_state.get("analisis_listo"):
        st.info("Presiona Analizar para iniciar el modo Depurador Paso a Paso.")
    else:
        tokens_detalle = st.session_state.get("tokens_detalle", [])
        tokens_tabla = st.session_state.get("tokens_tabla", [])
        reducciones = st.session_state.get("reducciones", [])
        reducciones_simuladas = st.session_state.get("reducciones_simuladas", [])
        todos_los_errores = st.session_state.get("errores", [])
        variables = st.session_state.get("variables", {})

        total_pasos = len(tokens_detalle) + len(reducciones)
        if total_pasos <= 0:
            st.warning("No hay pasos para mostrar. Revisa el código y vuelve a analizar.")
        else:
            max_paso = total_pasos - 1
            st.session_state["paso_actual"] = max(0, min(st.session_state["paso_actual"], max_paso))

            st.markdown("---")
            st.progress((st.session_state["paso_actual"] + 1) / total_pasos)

            m1, m2, m3 = st.columns(3)
            m1.metric("Paso", f"{st.session_state['paso_actual'] + 1} / {total_pasos}")
            m2.metric("Tokens", len(tokens_detalle))
            m3.metric("Reducciones", len(reducciones))

            nav1, nav2, nav3 = st.columns(3)
            with nav1:
                if st.button("⬅️ Anterior", use_container_width=True, disabled=st.session_state["paso_actual"] <= 0):
                    st.session_state["paso_actual"] -= 1
                    st.rerun()
            with nav2:
                if st.button("Paso a Paso ➡️", use_container_width=True, disabled=st.session_state["paso_actual"] >= max_paso):
                    st.session_state["paso_actual"] += 1
                    st.rerun()
            with nav3:
                if st.button("⏭️ Ejecutar Todo", use_container_width=True):
                    st.session_state["paso_actual"] = max_paso
                    st.rerun()

            if todos_los_errores:
                st.error(f"❌ El análisis tiene {len(todos_los_errores)} error(es).")
                with st.expander("Ver lista de errores", expanded=False):
                    for err in todos_los_errores:
                        st.write(f"⚠️ {err}")
            else:
                st.success("▲ Análisis completado: sin errores.")

            base_dir_step = Path(__file__).resolve().parent
            texto_lex_step = _leer_archivo_como_texto(base_dir_step / "lexer.py") or ""
            texto_yacc_step = _leer_archivo_como_texto(base_dir_step / "parser.py") or ""

            paso = st.session_state["paso_actual"]
            if paso < len(tokens_detalle):
                tok = tokens_detalle[paso]
                linea, col = _pos_a_linea_columna(codigo_usuario, tok.get("lexpos"))

                st.subheader("🔍 Depurador: Fase Léxica (LEX)")
                st.info(f"Acción: SHIFT | Token: {tok.get('type')} | Lexema: {tok.get('value')} | Línea {linea}, Columna {col}")

                c1, c2, c3 = st.columns([1.2, 1, 1])
                with c1:
                    st.code(_marcar_posicion(codigo_usuario, tok.get("lexpos")), language="text")
                with c2:
                    frag = _fragmento_token_lexer(texto_lex_step, tok.get("type"))
                    if frag:
                        st.code(frag, language="python")
                    else:
                        st.caption("No se encontró el fragmento exacto de la regla para este token.")
                with c3:
                    st.subheader("🧱 Pila")
                    pila_shift = [_terminal_en_pila(t) for t in tokens_detalle[: paso + 1]]
                    st.code(_pila_como_texto(pila_shift), language="text")
            else:
                idx_red = paso - len(tokens_detalle)
                reduccion_actual = reducciones[idx_red] if 0 <= idx_red < len(reducciones) else ""

                st.subheader("⚙️ Depurador: Fase Sintáctica (YACC)")
                st.info(f"Acción: REDUCE | {reduccion_actual}")

                sim = reducciones_simuladas[idx_red] if 0 <= idx_red < len(reducciones_simuladas) else None

                c1, c2, c3 = st.columns([1.2, 1, 1])
                with c1:
                    st.subheader("🧱 Pila (antes / después)")
                    if sim:
                        tab_b, tab_a = st.tabs(["Antes", "Después"])
                        with tab_b:
                            st.code(_pila_como_texto(sim.get("antes", [])), language="text")
                        with tab_a:
                            st.code(_pila_como_texto(sim.get("despues", [])), language="text")
                        rhs = sim.get("rhs_raw", [])
                        lhs = sim.get("lhs", "")
                        if sim.get("error"):
                            st.caption(sim.get("error"))
                        else:
                            st.caption(f"Pop ({len(rhs)}): {' '.join(rhs)} | Push: {lhs}")
                    else:
                        st.caption("No hay simulación de pila disponible para esta reducción.")
                with c2:
                    st.subheader("📦 Variables")
                    if variables:
                        st.json(variables)
                    else:
                        st.caption("La memoria de variables está vacía.")
                with c3:
                    st.subheader("📜 Regla activada")
                    frag = _fragmento_regla_parser(texto_yacc_step, reduccion_actual)
                    if frag:
                        st.code(frag, language="python")
                    else:
                        st.caption("No se encontró el fragmento exacto de la regla para esta reducción.")

            with st.expander("Vista completa (tokens y reducciones)", expanded=False):
                col_lex, col_yacc, col_env = st.columns([1.2, 1.5, 1])

                with col_lex:
                    st.subheader("🔍 Tokens")
                    if tokens_tabla:
                        st.dataframe(tokens_tabla, use_container_width=True)
                    else:
                        st.caption("No se encontraron tokens válidos.")

                with col_yacc:
                    st.subheader("⚙️ Reducciones")
                    if reducciones:
                        for red in reducciones:
                            st.info(red)
                    else:
                        st.caption("No se registraron reducciones gramaticales.")

                with col_env:
                    st.subheader("📦 Entorno")
                    if variables:
                        st.json(variables)
                    else:
                        st.caption("La memoria de variables está vacía.")

    st.markdown("---")
    st.subheader("📚 Fragmentos de código (LEX / YACC)")

    base_dir = Path(__file__).resolve().parent
    ruta_lex = base_dir / "lexer.py"
    ruta_yacc = base_dir / "parser.py"

    texto_lex = _leer_archivo_como_texto(ruta_lex)
    texto_yacc = _leer_archivo_como_texto(ruta_yacc)

    tab_lex, tab_yacc = st.tabs(["LEX (lexer.py)", "YACC (parser.py)"])
    with tab_lex:
        if texto_lex is None:
            st.warning("No fue posible leer lexer.py desde el disco.")
        else:
            fragmento = _extraer_fragmento(texto_lex, "tokens", "def obtener_analizador_lexico")
            st.code(fragmento.strip(), language="python")
    with tab_yacc:
        if texto_yacc is None:
            st.warning("No fue posible leer parser.py desde el disco.")
        else:
            fragmento = _extraer_fragmento(texto_yacc, "# REGLAS GRAMATICALES", "def analizar_codigo")
            st.code(fragmento.strip(), language="python")
