import json
import random
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters

# Тек екі админнің ID-лері
ADMINS = [7186196783, 7335365453]  # Мұнда өз админ ID-леріңізді қойыңыз

# Пайдаланушылар мәліметтері сақталатын файл
DATA_FILE = "data.json"

# Деректерді оқу/жазу функциялары
def load_data():
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Пайдаланушыны деректерге қосу
def add_user(user_id, username):
    data = load_data()
    if str(user_id) not in data:
        data[str(user_id)] = {
            "username": username,
            "balance": 500_000,
            "wins": 0,
            "losses": 0,
            "sent": 0,
            "received": 0,
            "clan": "None",
            "level": 1
        }
        save_data(data)

# /profile командасы
async def profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    # Егер ответ болса
    if update.message.reply_to_message:
        user = update.message.reply_to_message.from_user
    add_user(user.id, user.username or user.first_name)
    data = load_data()[str(user.id)]
    text = f"""👤Профиль: {data['username']} 
⚙️ID: {user.id}
 ├ Ақша💰: {data['balance']}
 ├ Ұтқандары✅: {data['wins']}
 ├ Женілгендері🛑: {data['losses']}
 ├ Жіберілген суммасы💸: {data['sent']}
 ├ Алынған суммасы💵: {data['received']}
 ├ Клан⚔️: {data['clan']}
 ├ Дәреже📈: {data['level']}"""
    await update.message.reply_text(text)

# /givemoney командасы (пайдаланушылар бір біріне ақша жібереді)
async def givemoney(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        sender = update.message.from_user
        add_user(sender.id, sender.username or sender.first_name)
        data = load_data()
        if len(context.args) < 2:
            await update.message.reply_text("Қолдану: /givemoney <user_id> <сома>")
            return
        target_id = str(context.args[0])
        amount = int(context.args[1])
        if target_id not in data:
            await update.message.reply_text("Пайдаланушы жоқ!")
            return
        if data[str(sender.id)]["balance"] < amount:
            await update.message.reply_text("Сізде жеткілікті ақша жоқ!")
            return
        data[str(sender.id)]["balance"] -= amount
        data[str(sender.id)]["sent"] += amount
        data[target_id]["balance"] += amount
        data[target_id]["received"] += amount
        save_data(data)
        await update.message.reply_text(f"{amount}тг {data[target_id]['username']} қолданушысына жіберілді.")
    except:
        await update.message.reply_text("Қате!")

# /gmoney командасы (тек админдер қолданады)
async def gmoney(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id not in ADMINS:
        await update.message.reply_text("Сіз админ емессіз!")
        return
    if len(context.args) < 2:
        await update.message.reply_text("Қолдану: /gmoney <user_id> <сома>")
        return
    data = load_data()
    target_id = str(context.args[0])
    amount = int(context.args[1])
    if target_id not in data:
        add_user(target_id, f"User{target_id}")
    data[target_id]["balance"] += amount
    save_data(data)
    await update.message.reply_text(f"{amount}тг {data[target_id]['username']} қолданушысына берілді.")

# /delmoney командасы (тек админдер)
async def delmoney(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    if user.id not in ADMINS:
        await update.message.reply_text("Сіз админ емессіз!")
        return
    if len(context.args) < 1:
        await update.message.reply_text("Қолдану: /delmoney <user_id>")
        return
    target_id = str(context.args[0])
    data = load_data()
    if target_id not in data:
        await update.message.reply_text("Пайдаланушы жоқ!")
        return
    data[target_id]["balance"] = 0
    save_data(data)
    await update.message.reply_text(f"{data[target_id]['username']} қолданушысының ақшасы жойылды.")

# /balance командасы
async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    add_user(user.id, user.username or user.first_name)
    data = load_data()[str(user.id)]
    await update.message.reply_text(f"Сіздің балансыңыз: {data['balance']}тг")

# Казино ойындары
async def play(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    add_user(user.id, user.username or user.first_name)
    data = load_data()
    if len(context.args) < 2:
        await update.message.reply_text("Қолдану: /play <баскетбол/футбол/рулетка/дартс/боулинг> <сома>")
        return
    game = context.args[0].lower()
    amount = int(context.args[1])
    if data[str(user.id)]["balance"] < amount:
        await update.message.reply_text("Сізде жеткілікті ақша жоқ!")
        return
    win = random.choice([True, False])
    if win:
        data[str(user.id)]["balance"] += amount
        data[str(user.id)]["wins"] += 1
        msg = f"Сіз {game} ойынында ұттыңыз! +{amount}тг"
    else:
        data[str(user.id)]["balance"] -= amount
        data[str(user.id)]["losses"] += 1
        msg = f"Сіз {game} ойынында жеңілдіңіз! -{amount}тг"
    save_data(data)
    await update.message.reply_text(msg)

# Эротикалық командалар
async def erotic_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    add_user(user.id, user.username or user.first_name)
    if not update.message.reply_to_message:
        await update.message.reply_text("Кімге қолданатыныңызды белгілеңіз (ответь)")
        return
    target = update.message.reply_to_message.from_user
    action = update.message.text.lower()
    text_map = {
        "трахнуть": f"b. жёско аттрахал(-а) {target.username} /// ME 🥰🥵",
        "выебать": f"b. трахнул(-а) {target.username} /// ME 🥰🥵",
        "секс": f"b. отьебал(-а) во все дырочки {target.username} /// ME🥰🥵",
        "пнуть": f"b. пнул(-а) {target.username} /// ME 🥵"
    }
    if action in text_map:
        await update.message.reply_text(text_map[action])

# /help командасы
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = """/profile - Профиль көрсету
/balance - Баланс тексеру
/givemoney <id> <сома> - Бір қолданушыға ақша жіберу
/gmoney <id> <сома> - Админ ақша беру
/delmoney <id> - Админ ақша жою
/play <ойын> <сома> - Казино ойнау
Эротикалық: трахнуть, выебать, секс, пнуть (ответь арқылы)"""
    await update.message.reply_text(text)

# Ботты іске қосу
app = ApplicationBuilder().token("ВАШ_BOT_TOKEN").build()  # Мұнда Replit/Render Secrets қолдансаңыз болады

# Командаларды тіркеу
app.add_handler(CommandHandler("profile", profile))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("givemoney", givemoney))
app.add_handler(CommandHandler("gmoney", gmoney))
app.add_handler(CommandHandler("delmoney", delmoney))
app.add_handler(CommandHandler("play", play))
app.add_handler(CommandHandler("help", help_command))
# Эротикалық командалар
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, erotic_action))

# Ботты іске қосу
app.run_polling()
