import json
import os
import openai
from openai.error import OpenAIError
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)
from dotenv import load_dotenv
load_dotenv()

# === Enviroment ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# === Track if users were greeted ===
user_greeted = set()

# === Load knowledge.json ===
def load_knowledge():
    knowledge_path = os.path.join("data", "knowledge.json")
    if os.path.exists(knowledge_path):
        with open(knowledge_path, "r") as f:
            return json.load(f)
    return {}

# === Search for relevant info  ===
def find_relevant_text(question, knowledge):
    matches = []
    for url, content in knowledge.items():
        if any(word.lower() in content.lower() for word in question.lower().split()):
            matches.append(content)
    return "\n\n".join(matches)[:4000] if matches else "No matching information found."

# === Detect language===
def detect_language(text):
    spanish_keywords = ["qué", "como", "por qué", "dónde", "cuál", "cuando", "hola"]
    english_keywords = ["what", "how", "why", "where", "which", "when", "hello"]

    text_lower = text.lower()
    if any(word in text_lower for word in spanish_keywords):
        return "es"
    elif any(word in text_lower for word in english_keywords):
        return "en"
    else:
        return "en"

# === Call OpenAI ===
def ask_openai(question, context_text, lang="en"):
    if lang == "es":
        prompt = f"""
Recibirás información y una pregunta del usuario.

- NO saludes.
- Respondé como un asistente robótico, profesional y estructurado.
- Usá viñetas o pasos (nada de párrafos largos).
- Sé claro y directo.

Información:
{context_text}

Pregunta del usuario:
{question}
"""
        system_msg = "Sos un asistente robótico. Respondé sin saludo, en viñetas, claro y profesionalmente."
    else:
        prompt = f"""
You will receive background info and a user question.

- DO NOT greet.
- Respond as a robotic, helpful assistant.
- Use bullet points or numbered steps (no long paragraphs).
- Be clear, structured, and professional.

Background:
{context_text}

User question:
{question}
"""
        system_msg = "You are a robotic assistant. Respond clearly, professionally, and in bullet-point format. Do not greet the user."

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            temperature=0.5,
            messages=[
                {"role": "system", "content": system_msg},
                {"role": "user", "content": prompt}
            ]
        )
        return response.choices[0].message["content"]
    except OpenAIError as e:
        print("❌ OpenAI API Error:", e)
        return "⚠️ Sorry, I couldn't contact OpenAI. Please try again later."

# === /start ===
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hi! I'm your Lens Studio bot. Ask me anything!")

# === hangle messages ===
async def handle_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text.strip()
    lang = detect_language(message)
    knowledge = load_knowledge()

    if not knowledge:
        warning = "⚠️ No hay conocimiento cargado. Ejecutá el scraper primero." if lang == "es" else "⚠️ No knowledge found. Please run the scraper first."
        await update.message.reply_text(warning)
        return

    # Detect greeting
    greeting_words = ["hola", "buenas", "hello", "hi"]
    is_greeting = any(word in message.lower() for word in greeting_words)

    # Search for relevant info
    relevant_text = find_relevant_text(message, knowledge)
    has_match = relevant_text != "No matching information found."

    # if greeting without relevant info
    if is_greeting and not has_match:
        greeting = "👋 ¡Hola! ¿En qué puedo ayudarte?" if lang == "es" else "👋 Hello! How can I help you?"
        await update.message.reply_text(greeting)
        return

    # first time the user greets
    if user_id not in user_greeted:
        user_greeted.add(user_id)
        if has_match:
            greeting = "👋 ¡Hola! Te respondo a continuación:" if lang == "es" else "👋 Hello! Here's your answer:"
            await update.message.reply_text(greeting)
        else:
            greeting = "👋 ¡Hola! ¿En qué puedo ayudarte?" if lang == "es" else "👋 Hello! What can I help you with?"
            await update.message.reply_text(greeting)
            return

    # if found knowledge answers
    if has_match:
        reply = ask_openai(message, relevant_text, lang)
        await update.message.reply_text(reply)
    else:
        fallback = "🤖 No encontré información para eso. ¿Podés reformular tu consulta?" if lang == "es" else "🤖 I couldn't find relevant information. Could you rephrase your question?"
        await update.message.reply_text(fallback)

# === Bot App ===
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_question))
    print("🤖 Bot is running... Ask your questions on Telegram!")
    await app.run_polling()

# === Entry point  ===
if __name__ == "__main__":
    import asyncio
    async def safe_start():
        try:
            await main()
        except KeyboardInterrupt:
            print("👋 Bot stopped by user")

    try:
        import nest_asyncio
        nest_asyncio.apply()
        loop = asyncio.get_event_loop()
        if loop.is_running():
            loop.create_task(safe_start())
        else:
            loop.run_until_complete(safe_start())
    except RuntimeError as e:
        print(f"❌ Runtime error: {e}")