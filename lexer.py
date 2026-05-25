# lexer.py
import ply.lex as lex

# Definición de fichas (Tokens)
tokens = (
    'VARIABLE',
    'NUMERO',
    'SUMA',
    'RESTA',
    'IGUAL',
    'MULTIPLICACION',
    'DIVISION'
)

# Reglas de expresiones regulares simples
t_SUMA  = r'\+'
t_RESTA = r'-'
t_IGUAL = r'='
t_ignore = ' \t\n'
t_MULTIPLICACION = r'\*'
t_DIVISION = r'/'

# Reglas con acciones asociadas
def t_VARIABLE(t):
    r'[a-zA-Z_][a-zA-Z0-9_]*'
    return t

def t_NUMERO(t):
    r'[0-9]+'
    t.value = int(t.value)
    return t

# Manejo de errores léxicos
def t_error(t):
    # Guardamos el error en el propio objeto lexer para que la app pueda leerlo
    if not hasattr(t.lexer, 'lista_errores'):
        t.lexer.lista_errores = []
    t.lexer.lista_errores.append(f"Carácter ilegal '{t.value[0]}' en la posición {t.lexpos}")
    t.lexer.skip(1)

# Función para construir el lexer
def obtener_analizador_lexico():
    lexer = lex.lex()
    lexer.lista_errores = [] # Inicializar lista limpia
    return lexer