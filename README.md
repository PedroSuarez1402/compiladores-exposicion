# Simulador Educativo LEX & YACC (PLY + Streamlit)

Simulador interactivo para demostrar, en tiempo real, cómo un código fuente pasa por:

1) **Análisis Léxico (LEX/PLY)** → generación de tokens  
2) **Análisis Sintáctico + Semántico Bottom-Up (YACC/PLY)** → reducciones y tabla de símbolos  

## Requisitos

- Windows (proyecto pensado para ejecutarse dentro de Laragon)
- Python 3 instalado
- (Recomendado) Un entorno virtual `venv`

## Instalación (primera vez)

Abre una terminal en la carpeta del proyecto (`C:\laragon\www\compiladores`) y ejecuta:

### Opción A: Usar `venv` (recomendada)

**CMD (típico en Laragon):**

```bat
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

**PowerShell:**

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Opción B: Sin `venv` (no recomendado)

```bat
pip install -r requirements.txt
```

## Ejecución

Con el entorno activo (si usas `venv`), ejecuta:

```bat
streamlit run app.py
```

Streamlit mostrará una URL local (por ejemplo `http://localhost:8501`) para abrirla en el navegador.

## Uso en la interfaz

- Escribe una asignación o expresión (ej. `x = 15 + 20 - 5`) y observa:
  - **Tokens** generados por el lexer
  - **Reducciones** del parser (bottom-up)
  - **Tabla de símbolos** (variables en memoria)
- Usa los botones superiores para inyectar ejemplos:
  - **Código Válido**
  - **Error Léxico**
  - **Error Sintáctico**
  - **Error Semántico**
- Abajo verás pestañas con fragmentos clave del código de `lexer.py` y `parser.py`.

## Estructura del proyecto

- `lexer.py`: tokens y reglas léxicas (PLY `lex`)
- `parser.py`: gramática y acciones (PLY `yacc`)
- `app.py`: UI en Streamlit (dashboard)

## Subir a GitHub (pasos sugeridos)

1) Crea un repositorio vacío en GitHub.
2) Desde la carpeta del proyecto, inicializa Git y sube:

```bat
git init
git add .
git commit -m "Proyecto: simulador LEX & YACC"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/TU_REPO.git
git push -u origin main
```

> Nota: `.gitignore` ya excluye `venv/`, cachés de Python y otros artefactos locales.

