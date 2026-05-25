# parser.py
import ply.yacc as yacc
from lexer import tokens

# Configuración de precedencia
precedence = (
    ('left', 'SUMA', 'RESTA'),
)

# Variables globales para capturar el estado del análisis para la interfaz
historial_reducciones = []
errores_sintacticos = []
tabla_simbolos = {}

# REGLAS GRAMATICALES
def p_instruccion_asignacion(p):
    '''instruccion : VARIABLE IGUAL expresion'''
    tabla_simbolos[p[1]] = p[3]
    historial_reducciones.append(f"REDUCCIÓN: instruccion -> {p[1]} = expresion (Valor: {p[3]})")
    p[0] = p[3]

def p_instruccion_expresion(p):
    '''instruccion : expresion'''
    historial_reducciones.append(f"REDUCCIÓN: instruccion -> expresion (Valor: {p[1]})")
    p[0] = p[1]

def p_expresion_operacion(p):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
    else:
        p[0] = p[1] - p[3]
    historial_reducciones.append(f"REDUCCIÓN: expresion -> expresion {p[2]} expresion (Resultado parcial: {p[0]})")

def p_expresion_numero(p):
    '''expresion : NUMERO'''
    p[0] = p[1]
    historial_reducciones.append(f"REDUCCIÓN: expresion -> NUMERO ({p[1]})")

def p_expresion_variable(p):
    '''expresion : VARIABLE'''
    if p[1] in tabla_simbolos:
        p[0] = tabla_simbolos[p[1]]
        historial_reducciones.append(f"REDUCCIÓN: expresion -> VARIABLE ({p[1]} = {p[0]})")
    else:
        errores_sintacticos.append(f"Error Semántico: Variable '{p[1]}' no definida.")
        p[0] = 0

# Manejo de errores de sintaxis
def p_error(p):
    if p:
        errores_sintacticos.append(f"Error de Sintaxis: Token inesperado '{p.value}' (Tipo: {p.type})")
    else:
        errores_sintacticos.append("Error de Sintaxis: Estructura incompleta al final de la línea.")

# Función para reiniciar el estado y analizar el código
def analizar_codigo(codigo, lexer_objeto):
    global historial_reducciones, errores_sintacticos
    historial_reducciones = []
    errores_sintacticos = []
    
    # Construir el parser de YACC
    parser = yacc.yacc(debug=False, write_tables=False)
    
    # Ejecutar el análisis sintáctico usando nuestro lexer configurado
    resultado = parser.parse(codigo, lexer=lexer_objeto)
    
    return resultado, historial_reducciones, errores_sintacticos, tabla_simbolos