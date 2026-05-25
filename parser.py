# parser.py
import ply.yacc as yacc
from lexer import tokens

# Configuración de precedencia
precedence = (
    ('left', 'SUMA', 'RESTA'),
    ('left', 'MULTIPLICACION', 'DIVISION'),
)

# Variables globales para capturar el estado del análisis para la interfaz
historial_reducciones = []
errores_sintacticos = []
tabla_simbolos = {}

# REGLAS GRAMATICALES
def p_instruccion_asignacion(p):
    '''instruccion : VARIABLE IGUAL expresion'''
    tabla_simbolos[p[1]] = p[3]
    # Mensaje didáctico
    historial_reducciones.append(f"🎯 PASO FINAL (Asignación): YACC toma la variable '{p[1]}' y le guarda el resultado total de la operación, que es {p[3]}.")
    p[0] = p[3]

def p_instruccion_expresion(p):
    '''instruccion : expresion'''
    historial_reducciones.append(f"🏁 RESULTADO: YACC terminó de evaluar la expresión aislada. El resultado es {p[1]}.")
    p[0] = p[1]

def p_expresion_operacion(p):
    '''expresion : expresion SUMA expresion
                 | expresion RESTA expresion
                 | expresion MULTIPLICACION expresion
                 | expresion DIVISION expresion'''
    if p[2] == '+':
        p[0] = p[1] + p[3]
        nombre_op = "SUMA"
    elif p[2] == '-':
        p[0] = p[1] - p[3]
        nombre_op = "RESTA"
    elif p[2] == '*':
        p[0] = p[1] * p[3]
        nombre_op = "MULTIPLICACIÓN"
    elif p[2] == '/':
        p[0] = p[1] / p[3] if p[3] != 0 else 0 # Previene división por cero
        nombre_op = "DIVISIÓN"
    
    # Mensaje didáctico
    historial_reducciones.append(f"⚙️ OPERACIÓN MATEMÁTICA: YACC detecta el símbolo '{p[2]}'. {nombre_op} los dos valores anteriores ({p[1]} y {p[3]}). El resultado temporal es {p[0]}.")

def p_expresion_numero(p):
    '''expresion : NUMERO'''
    p[0] = p[1]
    # Mensaje didáctico
    historial_reducciones.append(f"📦 LECTURA DE DATO: YACC recibe el número {p[1]} desde LEX y lo reconoce como un valor válido para operar.")

def p_expresion_variable(p):
    '''expresion : VARIABLE'''
    if p[1] in tabla_simbolos:
        p[0] = tabla_simbolos[p[1]]
        historial_reducciones.append(f"🔍 BÚSQUEDA EN MEMORIA: YACC lee la variable '{p[1]}' y busca su valor guardado, que es {p[0]}.")
    else:
        errores_sintacticos.append(f"❌ Error Semántico: Intentaste usar la variable '{p[1]}', pero no existe en la memoria.")
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