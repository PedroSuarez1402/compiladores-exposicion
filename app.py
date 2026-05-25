# app.py
import streamlit as st
from lexer import obtener_analizador_lexico
from parser import analizar_codigo
from pathlib import Path

st.set_page_config(layout="wide", page_title="Dashboard LEX & YACC")

st.title("🖥️ Compiladores en Acción: Visualizador LEX y YACC")
st.markdown("Una herramienta didáctica para comprender las fases del Frontend de un compilador en tiempo real.")

st.subheader("📝 Código de Entrada")
if "codigo_usuario" not in st.session_state:
    st.session_state["codigo_usuario"] = "x = 15 + 20 - 5"

col_e1, col_e2, col_e3, col_e4 = st.columns(4)
with col_e1:
    if st.button("Código Válido", use_container_width=True):
        st.session_state["codigo_usuario"] = "x = 10 + 5"
with col_e2:
    if st.button("Error Léxico", use_container_width=True):
        st.session_state["codigo_usuario"] = "x = 10 @ 5"
with col_e3:
    if st.button("Error Sintáctico", use_container_width=True):
        st.session_state["codigo_usuario"] = "x = + 10"
with col_e4:
    if st.button("Error Semántico", use_container_width=True):
        st.session_state["codigo_usuario"] = "y = z + 5"

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

if codigo_usuario:
    lexer_inf = obtener_analizador_lexico()
    lexer_inf.input(codigo_usuario)
    
    tokens_tabla = []
    while True:
        tok = lexer_inf.token()
        if not tok:
            break
        tokens_tabla.append({
            "Token (Clase)": tok.type,
            "Lexema (Texto)": tok.value,
            "Posición Inicial": tok.lexpos
        })
    
    lexer_para_parser = obtener_analizador_lexico()
    res, reducciones, errores, variables = analizar_codigo(codigo_usuario, lexer_para_parser)
    
    todos_los_errores = lexer_para_parser.lista_errores + errores

    st.markdown("---")
    
    if todos_los_errores:
        st.error(f"❌ El proceso falló con {len(todos_los_errores)} error(es):")
        for err in todos_los_errores:
            st.write(f"⚠️ {err}")
    else:
        st.success("▲ ¡Análisis completado con éxito! El código es completamente válido.")

    col_lex, col_yacc, col_env = st.columns([1.2, 1.5, 1])
    
    with col_lex:
        st.subheader("🔍 1. Fase Léxica (Tokens)")
        if tokens_tabla:
            st.dataframe(tokens_tabla, use_container_width=True)
        else:
            st.caption("No se encontraron tokens válidos.")
            
    with col_yacc:
        st.subheader("⚙️ 2. Fase Sintáctica (Reducciones)")
        if reducciones:
            for red in reducciones:
                st.info(red)
        else:
            st.caption("Esperando reducciones gramaticales...")
            
    with col_env:
        st.subheader("📦 3. Entorno (Variables)")
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
