# HACKUDC25-Qiqi
CHATBOT Qiqi - Proyecto HACKUDC 2025 - KELEA

Para ejecutarlo son requeridos : Python 3.8 o posterior; OLLAMA instalado y corriendo; Modelo LLM Mistral

Ejecucion:
instala python
  #sudo apt update && sudo apt install -y python3-pip python3-venv
instala ollama
  #curl -fsSL https://ollama.ai/install.sh | sh
instala mistral
  #ollama pull mistral
pon en funcionamiento el servidor, si ya está corriendo puedes seguir con la ejecucion
  #ollama serve
prepara el espacio virtual
  #python -m venv qiqi-env
ejecuta el espacio virtual
  #source qiqi-env/bin/activate
instala los requerimientos
  #pip install streamlit ollama vaderSentiment
Asegurate de que situarte en el fichero contenedor de Qiqi.py
  #streamlit run Qiqi.py 
