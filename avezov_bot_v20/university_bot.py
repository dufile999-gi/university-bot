from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re
import os
import sqlite3
import datetime
import logging
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️  WEB SERVER (RENDER/HEROKU UCHUN)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass

threading.Thread(
    target=lambda: HTTPServer(('0.0.0.0', 8080), Handler).serve_forever(),
    daemon=True
).start()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️  SOZLAMALAR & LOGGING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"
ADMIN_PHONE = "+998996844483"
DB_PATH = "universitet.db"
ABOUT_PHOTO_URL = "https://storage.googleapis.com/createsite-uz-bucket/blog/1722071060_chirchiq-auezov.jpg"

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Konversiya holatlari (States)
TIL_TANLASH, TANLA = "til_tanlash", "tanla"
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = "hf1", "hf2", "hf3", "hf4"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "h1", "h2", "h3", "h4"
SOROV_ISM, SOROV_FAMILYA, SOROV_YOSH, SOROV_TELEFON = "si", "sf", "sy", "st"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON = "yi", "yf", "yy", "yt"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL LUG'ATI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANG_TEXTS = {
    'uz': {
        'welcome': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!\n\n👇 _Davom etish uchun quyidagi menyudan foydalaning:_",
        'menu_about': "🎓 Universitet haqida", 'menu_yonalish': "🗃️ Yo'nalishlar",
        'menu_hujjat': "📝 Hujjat topshirish", 'menu_manzil': "📍 Manzil",
        'menu_sorov': "🗂 So'rovnoma", 'menu_tanlash': "📋 Yo'nalish tanlash",
        'menu_admin': "👤 Admin bilan bog'lanish", 'back': "🔙 Menyuga qaytish", 'cancel': "❌ Bekor qilish",
        'about_text': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti Chirchiq filiali*\n\nChirchiq shahrida universitetning yangi zamonaviy filiali o'z ishini boshlamoqda!\n\n🔗 [Batafsil ma'lumot (Oliygoh.uz)](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
        'yonalish_text': "👑 *TA'LIM YO'NALISHLARI*\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'hujjat_intro': "📋 *KERAKLI HUJJATLAR RO'YXATI*\n\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ 0.86 Med-ma'lumotnoma\n4️⃣ 3x4 rasm (6 dona)\n\n🟢 *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm ko'rinishida", 'format_fayl': "📎 Fayl ko'rinishida",
        'sorov_allready': "✨ *Siz so'rovnomani to'ldirib bo'lgansiz!*", 
        'yonalish_allready': "✨ *Siz yo'nalishni tanlab bo'lgansiz!*",
        'enter_name': "✍️ *To'liq ismingizni kiriting:*", 'enter_surname': "✍️ *Familiyangizni kiriting:*",
        'enter_age': "✍️ *Yoshingizni kiriting (faqat raqamlarda):*", 
        'invalid_age': "⚠️ *Xatolik:* Noto'g'ri yosh! 14 va 60 yosh oralig'ida faqat raqam kiriting.",
        'send_phone': "📞 Telefon raqamni yuborish", 
        'phone_intro': "📞 *Telefon raqamingizni kiriting:*\n\nPastdagi tugmani bosing yoki qo'lda yozing.\n📝 *Namuna:* `+998901234567`",
        'invalid_phone': "⚠️ *Xatolik:* Raqam formati noto'g'ri! Qayta urinib ko'ring.",
        'success_received': "✨ Muvaffaqiyatli qabul qilindi!", 'all_docs_success': "🎉 Barcha hujjatlar topshirildi! Tez orada bog'lanamiz.",
        'select_yonalish_title': "🎓 *RO'YXATDAGI YO'NALISHLARDAN BIRINI TANLANG:*",
        'unknown': "❓ Noma'lum xabar yoki buyruq. Iltimos, pastdagi menyu tugmalaridan foydalaning.",
        'error_need_file': "⚠️ *Xatolik:* Siz fayl formatini tanlagansiz! Hujjatni fayl (Document) sifatida biriktirib yuboring.",
        'error_need_photo': "⚠️ *Xatolik:* Siz rasm formatini tanlagansiz! Hujjatni oddiy rasm (Photo) ko'rinishida yuboring.",
        'channel_caption': "📋 *Yangi Hujjat Keldi!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat turi: *{doc_name}*",
        'reg_cancelled': "❌ Jarayon bekor qilindi va bosh menyuga qaytildi.", 'reg_success': "🎉 Ro'yxatdan muvaffaqiyatli o'tdingiz!",
        'manzil_text': "📍 *Universitet manzili:*\nChirchiq shahri, Toshkent viloyati.\n🗺 [Google Maps Xaritasi](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Siz hozir ro'yxatdan o'tish jarayonidasiz!*\n\nIltimos, joriy so'ralgan ma'lumotni yuboring. Agar jarayonni to'xtatmoqchi bo'lsangiz, **❌ Bekor qilish** yoki **🔙 Menyuga qaytish** tugmasini bosing."
    },
    'ru': {
        'welcome': "🏛 Добро пожаловать в официальный бот приема Чирчикского филиала *Южно-Казахстанского университета имени М. Ауэзова*!",
        'menu_about': "🎓 Об университете", 'menu_yonalish': "🗃️ Направления",
        'menu_hujjat': "📝 Подача документов", 'menu_manzil': "📍 Адрес",
        'menu_sorov': "🗂 Анкета", 'menu_tanlash': "📋 Выбор направления",
        'menu_admin': "👤 Связь с админом", 'back': "🔙 Назад в меню", 'cancel': "❌ Отмена",
        'about_text': "🏛 *Чирчикский филиал Южно-Казахстанского университета имени М. Ауэзова*\n\n[Подробнее на сайте Oliygoh.uz](https://oliygoh.uz)",
        'yonalish_text': "👑 *НАПРАВЛЕНИЯ ОБУЧЕНИЯ*\n\n🔬 Биотехнология\n💻 Информационные системы\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект",
        'hujjat_intro': "📋 *СПИСОК ДОКУМЕНТОВ*\n\n🟢 *Этап 1: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ В виде фото", 'format_fayl': "📎 В виде файла",
        'sorov_allready': "✨ *Вы уже заполнили анкету!*", 'yonalish_allready': "✨ *Вы уже выбрали направление!*",
        'enter_name': "✍️ *Введите ваше имя:*", 'enter_surname': "✍️ *Введите вашу фамилию:*",
        'enter_age': "✍️ *Введите ваш возраст (цифрами):*", 
        'invalid_age': "⚠️ *Ошибка:* Введите корректный возраст цифрами (14-60).",
        'send_phone': "📞 Отправить номер", 'phone_intro': "📞 *Введите номер телефона:*",
        'invalid_phone': "⚠️ *Ошибка:* Неверный формат номера телефона.",
        'success_received': "✨ Успешно принято!", 'all_docs_success': "🎉 Все документы поданы!",
        'select_yonalish_title': "🎓 *ВЫБЕРИТЕ ОДНО ИЗ НАПРАВЛЕНИЙ:*",
        'unknown': "❓ Неизвестная команда. Используйте кнопки меню.",
        'error_need_file': "⚠️ *Ошибка:* Пожалуйста, прикрепите документ как файл (Document).",
        'error_need_photo': "⚠️ *Ошибка:* Пожалуйста, отправьте документ как фото (Photo).",
        'channel_caption': "📋 *Поступил документ:* {doc_name}\n👤 {user}",
        'reg_cancelled': "❌ Процесс отменен. Возврат в главное меню.", 'reg_success': "🎉 Вы успешно зарегистрировались!",
        'manzil_text': "📍 *Адрес университета:* г. Чирчик.\n🗺 [Google Maps](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Вы находитесь в процессе заполнения!*\n\nПожалуйста, введите запрашиваемые данные. Для отмены нажмите **❌ Отмена** или **🔙 Назад в меню**."
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан университеті* Шыршық филиалының ботына қош келдіңіз!",
        'menu_about': "🎓 Университет туралы", 'menu_yonalish': "🗃️ Мамандықтар",
        'menu_hujjat': "📝 Құжат тапсыру", 'menu_manzil': "📍 Мекен-жай",
        'menu_sorov': "🗂 Сауалнама", 'menu_tanlash': "📋 Мамандық таңдау",
        'menu_admin': "👤 Adminмен байланыс", 'back': "🔙 Mәзірге қайту", 'cancel': "❌ Бас тарту",
        'about_text': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан университеті Шыршық филиалы*",
        'yonalish_text': "👑 *БІЛІМ БЕРУ БАҒДАРЛАМАЛАРЫ*\n\n🔬 Биотехнология\n💻 Ақпараттық жүйелер",
        'hujjat_intro': "📋 *ҚАЖЕТТІ ҚҰЖАТТАР*\n\n🟢 *1-Кезең:* Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет түрінде", 'format_fayl': "📎 Файл түрінде",
        'sorov_allready': "✨ *Сіз сауалнаманы толтырғансыз!*", 'yonalish_allready': "✨ *Сіз мамандықты таңдағансыз!*",
        'enter_name': "✍️ *Атыңызды енгізіңіз:*", 'enter_surname': "✍️ *Тегіңізді енгізіңіз:*",
        'enter_age': "✍️ *Жасыңызды енгізіңіз:*", 'invalid_age': "⚠️ *Қате:* Жасыңызды дұрыс енгізіңіз (14-60).",
        'send_phone': "📞 Нөмірді жіберу", 'phone_intro': "📞 *Телефон нөміріңіз:*",
        'invalid_phone': "⚠️ *Қате:* Телефон форматы қате.",
        'success_received': "✨ Сәтті қабылданды!", 'all_docs_success': "🎉 Барлық құжаттар тапсырылды!",
        'select_yonalish_title': "🎓 *МАМАНДЫҚТЫ ТАҢДАҢЫЗ:*",
        'unknown': "❓ Белгісіз бұйрық. Мәзірді қолданыңыз.",
        'error_need_file': "⚠️ *Қате:* Құжатты файл (Document) ретінде жіберіңіз.",
        'error_need_photo': "⚠️ *Қате:* Құжатты сурет (Photo) ретінде жіберіңіз.",
        'channel_caption': "📋 *Жаңа құжат:* {doc_name}",
        'reg_cancelled': "❌ Бас тартылды. Бас мәзір.", 'reg_success': "🎉 Сіз sәтті тіркелдіңіз!",
        'manzil_text': "📍 *Мекен-жай:* Шыршық қаласы.",
        'warning_in_progress': "⚠️ *Сіз қазір тіркелу үстіндесіз!*\n\nСұралған мәліметті енгізіңіз немесе тоқтату үшін **❌ Бас тарту** немесе **🔙 Мәзірге қайту** батырмасын басыңыз."
    }
}

HUJJAT_NOMLAR = {
    'uz': {1: "📗 Diplom / Attestat", 2: "🪪 Pasport nusxasi", 3: "🗂 0.86 Med-ma'lumotnoma", 4: "📸 3×4 rasm (6 dona)"},
    'ru': {1: "📗 Диплом / Аттестат", 2: "🪪 Копия паспорта", 3: "🗂 Мед. справка 0.86", 4: "📸 Фото 3×4 (6 шт)"},
    'kk': {1: "📗 Диплом / Аттестат", 2: "🪪 Төлқұжат көшірмесі", 3: "🗂 0.86 Мед. анықтама", 4: "📸 3×4 photo"}
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗄️  MA'LUMOTLAR BAZASI BILAN ISHLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def db_connect(): return sqlite3.connect(DB_PATH)

def init_db():
    con = db_connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, lang TEXT, birinchi_vaqt TEXT);
        CREATE TABLE IF NOT EXISTS sorovnama (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT);
        CREATE TABLE IF NOT EXISTS yonalish_royxat (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT, yonalish TEXT);
    """)
    con.commit()
    con.close()

def check_already_registered(user_id, table_name):
    con = db_connect()
    cur = con.cursor()
    cur.execute(f"SELECT id FROM {table_name} WHERE id=?", (user_id,))
    res = cur.fetchone()
    con.close()
    return bool(res)

def get_lang(context, update=None):
    if context and 'lang' in context.user_data: return context.user_data['lang']
    if update and update.message:
        uid = update.message.from_user.id
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT lang FROM foydalanuvchilar WHERE id=?", (uid,))
        res = cur.fetchone()
        con.close()
        if res and res[0]:
            context.user_data['lang'] = res[0]
            return res[0]
    return 'uz'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎛️  KLAVIATURA INTERFEYSLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_menu_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([
        [t['menu_about'], t['menu_yonalish']],
        [t['menu_hujjat'], t['menu_manzil']],
        [t['menu_sorov'], t['menu_tanlash']],
        [t['menu_admin']],
    ], resize_keyboard=True)

def cancel_back_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([[t['back'], t['cancel']]], resize_keyboard=True)

def format_tanlash_keyboard(lang, step_num):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t['format_rasm'], callback_data=f"format_rasm_{step_num}"),
            InlineKeyboardButton(t['format_fayl'], callback_data=f"format_fayl_{step_num}"),
        ]
    ])

def is_any_menu_button(text_to_check):
    if not text_to_check: return False
    for lang in LANG_TEXTS:
        for key, value in LANG_TEXTS[lang].items():
            if key.startswith('menu_'):
                if text_to_check == value: return True
    return False

def is_cancel_or_back(text_to_check):
    if not text_to_check: return False
    for lang in LANG_TEXTS:
        if text_to_check in [LANG_TEXTS[lang]['cancel'], LANG_TEXTS[lang]['back']]: return True
    return False

def validate_phone(phone_str):
    clean_phone = re.sub(r'[\s\-()]+', '', phone_str)
    if re.match(r'^\+?[1-9]\d{6,14}$', clean_phone): return clean_phone
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛡️  BOSQICHMA-BOSQICH FILTRLASH (GUARD PIPELINE)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def process_step_guard(update, context):
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]
    msg_text = update.message.text if update.message else None
    
    if msg_text:
        if is_cancel_or_back(msg_text):
            await update.message.reply_text(t['reg_cancelled'], reply_markup=main_menu_markup(lang))
            return "FORCE_CAN_MENU"
            
        if is_any_menu_button(msg_text):
            await update.message.reply_text(t['warning_in_progress'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
            return "FORCE_STAY"
            
    return "PROCEED"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀  BOSHLACH / START
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update, context):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton("🇰🇿 Қазақша", callback_data="set_lang_kk")
        ]
    ])
    await update.message.reply_text("🌐 Bot tilini tanlang / Выберите язык бота / Тілді таңдаңыз:", reply_markup=keyboard)
    return TIL_TANLASH

async def select_lang_callback(update, context):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[2]
    context.user_data['lang'] = lang
    user = query.from_user

    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT id FROM foydalanuvchilar WHERE id=?", (user.id,))
    if not cur.fetchone():
        cur.execute("INSERT INTO foydalanuvchilar VALUES (?,?,?,?,?,?)", (user.id, user.first_name, user.last_name, user.username, lang, str(datetime.datetime.now())))
    else:
        cur.execute("UPDATE foydalanuvchilar SET lang=? WHERE id=?", (lang, user.id))
    con.commit()
    con.close()

    await query.message.delete()
    await context.bot.send_message(chat_id=query.message.chat_id, text=LANG_TEXTS[lang]['welcome'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  ASOSIY MENYU DISPATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def main_menu_dispatcher(update, context):
    msg = update.message.text if update.message else None
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]
    uid = update.message.from_user.id if update.message else None

    if not msg:
        await update.message.reply_text(t['unknown'], reply_markup=main_menu_markup(lang))
        return TANLA

    if msg == t['menu_about']:
        try:
            await update.message.reply_photo(photo=ABOUT_PHOTO_URL, caption=t['about_text'], parse_mode="Markdown")
        except Exception:
            await update.message.reply_text(t['about_text'], parse_mode="Markdown")
        return TANLA

    elif msg == t['menu_yonalish']:
        await update.message.reply_text(t['yonalish_text'], parse_mode="Markdown")
        return TANLA

    elif msg == t['menu_hujjat']:
        await update.message.reply_text(t['hujjat_intro'], parse_mode="Markdown", reply_markup=format_tanlash_keyboard(lang, 1))
        return HUJJAT_FORMAT_1

    elif msg == t['menu_manzil']:
        await update.message.reply_text(t['manzil_text'], parse_mode="Markdown")
        return TANLA

    elif msg == t['menu_sorov']:
        if check_already_registered(uid, "sorovnama"):
            await update.message.reply_text(t['sorov_allready'])
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return SOROV_ISM

    elif msg == t['menu_tanlash']:
        if check_already_registered(uid, "yonalish_royxat"):
            await update.message.reply_text(t['yonalish_allready'])
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return YONALISH_ISM

    elif msg == t['menu_admin']:
        await update.message.reply_text(f"💬 *Telegram:* {ADMIN_USERNAME}\n📞 *Phone:* `{ADMIN_PHONE}`", parse_mode="Markdown")
        return TANLA
        
    else:
        await update.message.reply_text(t['unknown'], reply_markup=main_menu_markup(lang))
        return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📤  HUJJAT TOPSHIRISH (TUG'RI TIZIMDA)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def format_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)
    parts = data.split("_")
    format_turi, step = parts[1], int(parts[2])
    context.user_data[f'hujjat_format_{step}'] = format_turi
    await query.edit_message_text(f"📥 {HUJJAT_NOMLAR[lang][step]} ({format_turi.upper()})\n\n👇 Iltimos, fayl yoki rasmni yuboring:", reply_markup=cancel_back_markup(lang))
    return HUJJAT_STATES[step]

async def hujjat_handler(update, context, step):
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return HUJJAT_STATES[step]

    tanlangan_format = context.user_data.get(f'hujjat_format_{step}', 'rasm')
    if tanlangan_format == 'fayl' and not update.message.document:
        await update.message.reply_text(t['error_need_file'], parse_mode="Markdown")
        return HUJJAT_STATES[step]
    if tanlangan_format == 'rasm' and not update.message.photo:
        await update.message.reply_text(t['error_need_photo'], parse_mode="Markdown")
        return HUJJAT_STATES[step]

    user = update.message.from_user
    username = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
    caption_txt = t['channel_caption'].format(user=username, uid=user.id, doc_name=HUJJAT_NOMLAR[lang][step])

    try:
         if update.message.document:
              await context.bot.send_document(chat_id=CHANNEL_USERNAME, document=update.message.document.file_id, caption=caption_txt, parse_mode="Markdown")
         elif update.message.photo:
              await context.bot.send_photo(chat_id=CHANNEL_USERNAME, photo=update.message.photo[-1].file_id, caption=caption_txt, parse_mode="Markdown")
    except Exception as e:
         logger.error(f"Kanalga yuborishda xato: {e}")

    if step < 4:
        next_step = step + 1
        await update.message.reply_text(f"{t['success_received']}\n\n🟢 *{next_step}-Bosqich: {HUJJAT_NOMLAR[lang][next_step]}*\n❓ Formatni tanlang:", parse_mode="Markdown", reply_markup=format_tanlash_keyboard(lang, next_step))
        return HUJJAT_FORMAT_STATES[next_step]
    else:
        await update.message.reply_text(t['all_docs_success'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA

async def hujjat_1(update, context): return await hujjat_handler(update, context, 1)
async def hujjat_2(update, context): return await hujjat_handler(update, context, 2)
async def hujjat_3(update, context): return await hujjat_handler(update, context, 3)
async def hujjat_4(update, context): return await hujjat_handler(update, context, 4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📝  SO'ROVNOMA OQIMI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def sorov_ism(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_ISM
    
    if not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_name'])
        return SOROV_ISM

    context.user_data['sorov_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return SOROV_FAMILYA

async def sorov_familya(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_FAMILYA
    
    if not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'])
        return SOROV_FAMILYA

    context.user_data['sorov_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return SOROV_YOSH

async def sorov_yosh(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_YOSH
    
    yosh = update.message.text.strip() if update.message.text else ""
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return SOROV_YOSH
        
    context.user_data['sorov_yosh'] = yosh
    k = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['back']), KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True))
    return SOROV_TELEFON

async def sorov_telefon(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_TELEFON

    telefon = None
    if update.message.contact: telefon = update.message.contact.phone_number
    elif update.message.text:
        telefon = validate_phone(update.message.text.strip())
        if not telefon:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return SOROV_TELEFON
    else:
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
        return SOROV_TELEFON
        
    user = update.message.from_user
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO sorovnama VALUES (?,?,?,?,?,?,?,?,?)", (user.id, user.first_name, user.last_name, user.username, str(datetime.datetime.now()), context.user_data.get('sorov_ism'), context.user_data.get('sorov_familya'), context.user_data.get('sorov_yosh'), telefon))
    con.commit()
    con.close()

    await update.message.reply_text(LANG_TEXTS[lang]['reg_success'], reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  YO'NALISH TANLASH OQIMI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_ISM
    
    if not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_name'])
        return YONALISH_ISM

    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_FAMILYA
    
    if not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'])
        return YONALISH_FAMILYA

    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_YOSH
    
    yosh = update.message.text.strip() if update.message.text else ""
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return YONALISH_YOSH
        
    context.user_data['yonalish_yosh'] = yosh
    k = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['back']), KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True))
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    lang = get_lang(context, update)
    guard = await process_step_guard(update, context)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_TELEFON

    telefon = None
    if update.message.contact: telefon = update.message.contact.phone_number
    elif update.message.text:
        telefon = validate_phone(update.message.text.strip())
        if not telefon:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return YONALISH_TELEFON
    else:
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
        return YONALISH_TELEFON

    context.user_data['yonalish_telefon'] = telefon
    
    yonalishlar = [
        ("🔬 Biotexnologiya", "Biotexnologiya"), ("🌍 Ekologiya", "Ekologiya"),
        ("💻 Axborot tizimlar", "Axborot_tizimlar"), ("⚙️ Avtomatizatsiya", "Avtomatizatsiya"),
        ("🚚 Transport", "Transport"), ("⚡ Elektroenergetika", "Elektroenergetika"),
        ("🧑‍🏫 Pedagogika", "Pedagogika"), ("🧠 Sun'iy intellekt", "Suniy_intellekt"),
        ("💼 Hisob va audit", "Hisob_audit"), ("✈️ Turizm", "Turizm"),
    ]
    
    keyboard = []
    for i in range(0, len(yonalishlar), 2):
        row = [InlineKeyboardButton(yonalishlar[i][0], callback_data=yonalishlar[i][1])]
        if i + 1 < len(yonalishlar): row.append(InlineKeyboardButton(yonalishlar[i+1][0], callback_data=yonalishlar[i+1][1]))
        keyboard.append(row)
        
    await update.message.reply_text(LANG_TEXTS[lang]['select_yonalish_title'], parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
    return TANLA

YONALISH_MAP = {
    "Biotexnologiya": "🔬 Biotexnologiya", "Ekologiya": "🌍 Ekologiya", "Axborot_tizimlar": "💻 Axborot tizimlar",
    "Avtomatizatsiya": "⚙️ Avtomatizatsiya", "Transport": "🚚 Transport", "Elektroenergetika": "⚡ Elektroenergetika",
    "Pedagogika": "🧑‍🏫 Pedagogika", "Suniy_intellekt": "🧠 Sun'iy intellekt", "Hisob_audit": "💼 Hisob va audit", "Turizm": "✈️ Turizm",
}

async def callback_data(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)
    user_id = query.message.chat_id

    if data.startswith("format_") or data.startswith("set_lang_") or data == "bekor": return 

    if check_already_registered(user_id, "yonalish_royxat"):
        await query.edit_message_text(LANG_TEXTS[lang]['yonalish_allready'], parse_mode="Markdown")
        return TANLA

    yonalish = YONALISH_MAP.get(data)
    context.user_data['yonalish'] = yonalish

    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO yonalish_royxat VALUES (?,?,?,?,?,?,?,?,?,?)", (user_id, "", "", "", str(datetime.datetime.now()), context.user_data.get('yonalish_ism'), context.user_data.get('yonalish_familya'), context.user_data.get('yonalish_yosh'), context.user_data.get('yonalish_telefon'), yonalish))
    con.commit()
    con.close()

    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(chat_id=user_id, text="🏠 Bosh menyuga qaytdingiz.", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👤  ADMIN COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def admin_statistika(update, context):
    if update.effective_user.username != "Saman2611":
        await update.message.reply_text("❌ Bu buyruq faqat admin uchun!")
        return
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT ism, familya, telefon FROM sorovnama")
    sorov_rows = cur.fetchall()
    cur.execute("SELECT ism, familya, telefon, yonalish FROM yonalish_royxat")
    yonalish_rows = cur.fetchall()
    con.close()

    matn = "📊 *STATISTIKA MA'LUMOTLARI*\n\n"
    matn += f"📝 *So'rovnoma to'ldirganlar ({len(sorov_rows)} ta):*\n"
    for i, row in enumerate(sorov_rows, 1): matn += f"{i}. {row[0]} {row[1]} -> `{row[2]}`\n"
    matn += "\n" + "━" * 15 + "\n\n"
    matn += f"🎓 *Yo'nalish tanlaganlar ({len(yonalish_rows)} ta):*\n"
    for i, row in enumerate(yonalish_rows, 1): matn += f"{i}. {row[0]} {row[1]} | *{row[3]}* -> `{row[2]}`\n"
    await update.message.reply_text(matn, parse_mode="Markdown")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖  MAIN RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    if not BOT_TOKEN: raise ValueError("❌ BOT_TOKEN xatoligi!")
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("users", admin_statistika))

    conv = ConversationHandler(
        entry_points=[
            CommandHandler('start', start), 
            MessageHandler(filters.ALL, main_menu_dispatcher)
        ],
        states={
            TIL_TANLASH: [CallbackQueryHandler(select_lang_callback, pattern="^set_lang_")],
            TANLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher), 
                CallbackQueryHandler(callback_data)
            ],
            
            HUJJAT_FORMAT_1: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_2: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_3: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_4: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            
            HUJJAT_1: [MessageHandler(filters.ALL, hujjat_1)],
            HUJJAT_2: [MessageHandler(filters.ALL, hujjat_2)],
            HUJJAT_3: [MessageHandler(filters.ALL, hujjat_3)],
            HUJJAT_4: [MessageHandler(filters.ALL, hujjat_4)],
            
            SOROV_ISM:     [MessageHandler(filters.ALL, sorov_ism)],
            SOROV_FAMILYA: [MessageHandler(filters.ALL, sorov_familya)],
            SOROV_YOSH:    [MessageHandler(filters.ALL, sorov_yosh)],
            SOROV_TELEFON: [MessageHandler(filters.ALL, sorov_telefon)],
            
            YONALISH_ISM:     [MessageHandler(filters.ALL, yonalish_ism)],
            YONALISH_FAMILYA: [MessageHandler(filters.ALL, yonalish_familya)],
            YONALISH_YOSH:    [MessageHandler(filters.ALL, yonalish_yosh)],
            YONALISH_TELEFON: [MessageHandler(filters.ALL, yonalish_telefon)],
        },
        fallbacks=[CommandHandler('start', start), MessageHandler(filters.ALL, main_menu_dispatcher)],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == '__main__':
    main()
