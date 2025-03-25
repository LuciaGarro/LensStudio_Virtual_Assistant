# 🤖 LS_Virtual_Assistant

Asistente virtual para responder preguntas sobre Lens Studio usando inteligencia artificial (OpenAI) y Telegram.

Desarrollado en Python, este bot permite a usuarios enviar preguntas a través de Telegram y recibir respuestas estructuradas en base a documentación previamente extraída.

---

## 📦 Requisitos

- Python 3.9 o superior
- Una cuenta de Telegram y un bot creado con [@BotFather](https://t.me/BotFather)
- Una API key de OpenAI

Instalá las dependencias con:

```bash
pip install -r requirements.txt
🚀 Cómo usar el bot
Cloná el repositorio:
bash
Copy
Edit
git clone https://github.com/LuciaGarro/LS_Virtual_Assistant.git
cd LS_Virtual_Assistant
Agregá tus claves en un archivo .env:
env
Copy
Edit
TELEGRAM_BOT_TOKEN=tu_token_de_telegram
OPENAI_API_KEY=tu_clave_de_openai
Ejecutá el bot:
bash
Copy
Edit
python bot.py
🧠 Sobre el conocimiento
El bot utiliza un archivo knowledge.json ubicado en la carpeta data/, que contiene información obtenida previamente mediante scraping o curación manual.

📁 Estructura del proyecto
plaintext
Copy
Edit
LS_Virtual_Assistant/
├── bot.py
├── .env (ignorado por Git)
├── .gitignore
├── requirements.txt
├── README.md
├── data/
│   └── knowledge.json
💡 Ideas futuras
Agregar scraping automatizado desde Lens Studio Docs
Mejorar la búsqueda de contexto con embeddings
Añadir más comandos personalizados
Soporte multilenguaje mejorado


