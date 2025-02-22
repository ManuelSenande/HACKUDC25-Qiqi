import streamlit as st
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import ollama

# 1. Configuración inicial ==============================================
analyzer = SentimentIntensityAnalyzer()
st.set_page_config(page_title="Qiqi Chatbot Emocional", layout="wide")

# 2. Sistema de seguimiento contextual ===================================
def inicializar_historial():
    if 'historial' not in st.session_state:
        st.session_state.historial = []
    if 'contexto' not in st.session_state:
        st.session_state.contexto = {
            'nombre': None,
            'temas_importantes': set(),
            'ultima_emocion': None
        }

# 3. Analizador de contenido avanzado ====================================
def analizar_entrada(texto):
    sentimiento = analyzer.polarity_scores(texto)
    elementos = {
        'palabras_clave': detectar_palabras_clave(texto),
        'es_pregunta': texto.strip().endswith('?'),
        'intensidad_emocional': abs(sentimiento['compound'])
    }
    return sentimiento, elementos

def detectar_palabras_clave(texto):
    palabras_relevantes = {
        'trabajo', 'estudio', 'familia', 'amigos', 'salud',
        'dinero', 'tiempo', 'futuro', 'pasado'
    }
    return [palabra for palabra in palabras_relevantes if palabra in texto.lower()]

def analizar_sentimiento_diario(entradas):
    resultados = []
    for entrada in entradas:
        sentimiento = analyzer.polarity_scores(entrada)
        resultados.append({
            'texto': entrada,
            'sentimiento': sentimiento,
            'categoria': categorizar_sentimiento(sentimiento['compound'])
        })
    return resultados

def analisis_colectivo_diario(entradas):
    if not entradas:
        return "No hay entradas para analizar."

    # Inicializar variables para el análisis colectivo
    total_compound = 0
    palabras_clave_count = {}
    total_entradas = len(entradas)

    # Analizar cada entrada
    for entrada in entradas:
        sentimiento = analyzer.polarity_scores(entrada)
        total_compound += sentimiento['compound']

        # Contar palabras clave
        palabras_clave = detectar_palabras_clave(entrada)
        for palabra in palabras_clave:
            palabras_clave_count[palabra] = palabras_clave_count.get(palabra, 0) + 1

    # Calcular el sentimiento promedio
    sentimiento_promedio = total_compound / total_entradas
    categoria_promedio = categorizar_sentimiento(sentimiento_promedio)

    # Obtener las palabras clave más recurrentes
    palabras_clave_recurrentes = sorted(palabras_clave_count.items(), key=lambda x: x[1], reverse=True)[:3]
    palabras_clave_recurrentes = [palabra for palabra, count in palabras_clave_recurrentes]

    # Generar el resumen
    resumen = f"El sentimiento general es {categoria_promedio}. "
    if palabras_clave_recurrentes:
        resumen += f"Los temas más recurrentes son: {', '.join(palabras_clave_recurrentes)}. "
    resumen += "Este análisis se basa en las entradas del diario."

    return resumen

# 4. Generador de respuestas con Ollama ==================================
def generar_respuesta_ollama(user_input, sentimiento, elementos):
    compound = sentimiento['compound']

    # Determinar categoría emocional
    if compound >= 0.6:
        categoria = "muy positivo"
    elif compound >= 0.2:
        categoria = "positivo"
    elif compound <= -0.6:
        categoria = "muy negativo"
    elif compound <= -0.2:
        categoria = "negativo"
    else:
        categoria = "neutral"


    # Construir prompt contextualizado
    prompt = f"""Eres Qiqi, un chatbot emocionalmente inteligente. El usuario se siente {categoria}.
Contexto:
- Palabras clave: {', '.join(elementos['palabras_clave']) if elementos['palabras_clave'] else 'ninguna'}
- Es pregunta: {'sí' if elementos['es_pregunta'] else 'no'}
- Emoción previa: {st.session_state.contexto['ultima_emocion'] or 'N/A'}
- Temas importantes: {', '.join(st.session_state.contexto['temas_importantes'])}

Instrucciones:
1. Usa un tono {categoria}
2. {"Responde la pregunta directamente" if elementos['es_pregunta'] else "Haz una pregunta relevante"}
3. {"Menciona: " + ', '.join(elementos['palabras_clave']) if elementos['palabras_clave'] else ""}

Mensaje del usuario: "{user_input}"
Respuesta de Qiqi:"""

    try:
        response = ollama.generate(
            model='mistral',  # Cambia el modelo según tus necesidades
            prompt=prompt,
            options={'temperature': 0.5, 'max_tokens': 300}
        )
        return response['response'].strip()
    except Exception as e:
        return f"Error: {str(e)}"
    
def categorizar_sentimiento(compound):
    if compound >= 0.6:
        return "muy positivo"
    elif compound >= 0.2:
        return "positivo"
    elif compound <= -0.6:
        return "muy negativo"
    elif compound <= -0.2:
        return "negativo"
    else:
        return "neutral"

# 5. Interfaz de usuario principal ======================================
def main():
    st.title("💬 Qiqi, tu chat personal con IA")

    # Inicializar estados de sesión
    inicializar_historial()
    for key in ["entrada", "diario", "nueva_con"]:
        if key not in st.session_state:
            st.session_state[key] = [] if key != "nueva_con" else False

    # Barra lateral
    with st.sidebar:
        seccion = st.radio("Selecciona una sección", ["Chatbot", "Diario"])

    if seccion == "Chatbot":
        # Historial de chat
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Entrada de usuario
        if user_input := st.chat_input("Escribe tu mensaje aquí..."):
            sentimiento, elementos = analizar_entrada(user_input)
            respuesta = generar_respuesta_ollama(user_input, sentimiento, elementos)

            # Actualizar contexto
            st.session_state.contexto.update({
                'ultima_emocion': sentimiento['compound'],
                'temas_importantes': st.session_state.contexto['temas_importantes'].union(elementos['palabras_clave'])
            })

            # Añadir mensajes al historial
            st.session_state.messages.append({"role": "user", "content": user_input})
            st.session_state.messages.append({"role": "assistant", "content": respuesta})

        # Mostrar mensajes
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"]):
                st.write(msg["content"])

        # Panel de análisis
        with st.sidebar:
            if st.session_state.messages:
                st.subheader("Análisis Emocional")
                ultimo_mensaje = st.session_state.messages[-2]["content"] if len(st.session_state.messages) >=2 else ""
                if ultimo_mensaje:
                    sentimiento = analyzer.polarity_scores(ultimo_mensaje)
                    st.metric("Intensidad Emocional", f"{sentimiento['compound']:.2f}")
                    st.progress((sentimiento['compound'] + 1) / 2)

                    st.write("**Distribución Emocional:**")
                    col1, col2, col3 = st.columns(3)
                    col1.metric("Positivo", f"{sentimiento['pos']:.2%}")
                    col2.metric("Neutral", f"{sentimiento['neu']:.2%}")
                    col3.metric("Negativo", f"{sentimiento['neg']:.2%}")

    elif seccion == "Diario":
        st.header("📔 Diario Personal")
        entrada_diario = st.text_area("Escribe tus pensamientos aquí...", height=200)

        if st.button("Guardar entrada"):
            st.session_state.diario.append(entrada_diario)
            st.success("Entrada guardada exitosamente!")

        if st.session_state.diario:
            st.subheader("Entradas anteriores")
            for i, entrada in enumerate(st.session_state.diario, 1):
                with st.expander(f"Entrada #{i}"):
                    st.write(entrada)

        with st.sidebar: 
            if st.button("Realizar Analisis"):
                st.subheader("Análisis Colectivo")
                resumen_colectivo = analisis_colectivo_diario(st.session_state.diario)
                st.write(resumen_colectivo)

if __name__ == "__main__":
    main()
