from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

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

import os
import sqlite3
import datetime
import logging
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, BotCommand,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️  SOZLAMALAR & DIZAYN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"
ADMIN_PHONE = "+998996844483"
DB_PATH = "universitet.db"

MAX_REGISTRATIONS = 5

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

SEP = "━" * 22
SUCCESS = "✨"

# Conversation states
TIL_TANLASH, TANLA = "til_tanlash", "tanla"
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = (
    "hujjat_format_1", "hujjat_format_2", "hujjat_format_3", "hujjat_format_4"
)
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "hujjat_1", "hujjat_2", "hujjat_3", "hujjat_4"
SOROV_ISM, SOROV_FAMILYA, SOROV_YOSH, SOROV_TELEFON = (
    "sorov_ism", "sorov_familya", "sorov_yosh", "sorov_telefon"
)
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON = (
    "yonalish_ism", "yonalish_familya", "yonalish_yosh", "yonalish_telefon"
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL LUG'ATI (UZ, RU, KK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANG_TEXTS = {
    'uz': {
        'welcome': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!\n\n👇 _Davom etish uchun quyidagi menyudan foydalaning:_",
        'menu_about': "🎓 Universitet haqida", 'menu_yonalish': "🗃️ Yo'nalishlar",
        'menu_hujjat': "📝 Hujjat topshirish", 'menu_manzil': "📍 Manzil",
        'menu_sorov': "🗂 So'rovnoma", 'menu_tanlash': "📋 Yo'nalish tanlash",
        'menu_admin': "👤 Admin bilan bog'lanish", 'back': "🔙 Menyuga qaytish",
        'about_text': " Chirchiq shahrida universitetning yangi zamonaviy filiali o'z ishini boshlamoqda! [Batafsil...](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
        'yonalish_text': f"👑 *TA'LIM YO'NALISHLARI*\n*{SEP}*\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'hujjat_intro': f"📋 *KERAKLI HUJJATLAR RO'YXATI*\n*{SEP}*\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ 0.86 Med-ma'lumotnoma\n4️⃣ 3x4 rasm (6 dona)\n\n🟢 *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm ko'rinishida", 'format_fayl': "📎 Fayl ko'rinishida",
        'sorov_allready': "✨ *Siz so'rovnomani to'ldirib bo'lgansiz!*", 'yonalish_allready': "✨ *Siz yo'nalishni tanlab bo'lgansiz!*",
        'enter_name': "✍️ *To'liq ismingizni kiriting:*\n\n_(Bekor qilish uchun tugmani bosing)_",
        'enter_surname': "✍️ *Familiyangizni kiriting:*\n\n_(Bekor qilish uchun tugmani bosing)_",
        'enter_age': "✍️ *Yoshingizni kiriting (raqamlarda):*\n\n_(Bekor qilish uchun tugmani bosing)_",
        'invalid_age': "⚠️ Noto'g'ri yosh kiriting (14-60)!",
        'send_phone': "📞 Telefon raqamni yuborish", 'phone_intro': "📞 Pastdagi tugma orqali telefon raqamingizni jo'nating:",
        'success_received': "✨ Muvaffaqiyatli qabul qilindi!", 'all_docs_success': "🎉 Barcha hujjatlar topshirildi! Tez orada bog'lanamiz.",
        'select_yonalish_title': "🎓 *RO'YXATDAGI YO'NALISHLARDAN BIRINI TANLANG:*", 'cancel': "❌ Bekor qilish",
        'ariza_success': "🎉 Arizangiz muvaffaqiyatli ro'yxatga olindi!", 'unknown': "❓ Noma'lum buyruq.",
        'error_need_file': "⚠️ Siz fayl ko'rinishida yuborishni tanladingiz! Iltimos, hujjatni fayl (document) sifatida yuboring.",
        'error_need_photo': "⚠️ Siz rasm ko'rinishida yuborishni tanladingiz! Iltimos, hujjatni rasm (photo) sifatida yuboring.",
        'channel_caption': "📋 *Yangi Hujjat Keldi!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat turi: *{doc_name}*",
        'cancelled': "❌ *Bekor qilindi.* Asosiy menyuga qaytdingiz.",
        'limit_sorov': f"⛔ *Siz allaqachon {MAX_REGISTRATIONS} marta so'rovnoma to'ldirdingiz!*\nMaksimal chegara ({MAX_REGISTRATIONS} ta) ga yetgansiz.",
        'limit_yonalish': f"⛔ *Siz allaqachon {MAX_REGISTRATIONS} marta yo'nalish tanladingiz!*\nMaksimal chegara ({MAX_REGISTRATIONS} ta) ga yetgansiz.",
    },
    'ru': {
        'welcome': "🏛 Добро пожаловать в официальный бот приема Чирчикского филиала *Южно-Казахстанского университета имени М. Ауэзова*!\n\n👇 _Используйте меню ниже для продолжения:_ ",
        'menu_about': "🎓 Об университете", 'menu_yonalish': "🗃️ Направления",
        'menu_hujjat': "📝 Подача документов", 'menu_manzil': "📍 Адрес",
        'menu_sorov': "🗂 Анкета", 'menu_tanlash': "📋 Выбор направления",
        'menu_admin': "👤 Связь с админом", 'back': "🔙 Назад в меню",
        'about_text': " В городе Чирчик начинает работу новый современный филиал университета! [Подробнее...](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
        'yonalish_text': f"👑 *НАПРАВЛЕНИЯ ОБУЧЕНИЯ*\n*{SEP}*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Transport\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект\n💼 Учет и аудит\n✈️ Туризм",
        'hujjat_intro': f"📋 *СПИСОК НЕОБХОДИМЫХ ДОКУМЕНТОВ*\n*{SEP}*\n1️⃣ Диплом/Аттестат\n2️⃣ Копия паспорта\n3️⃣ Мед. справка 0.86\n4️⃣ Фото 3х4 (6 шт)\n\n🟢 *Этап 1: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ В виде фото", 'format_fayl': "📎 В виде файла",
        'sorov_allready': "✨ *Вы уже заполнили анкету!*", 'yonalish_allready': "✨ *Вы уже выбрали направление!*",
        'enter_name': "✍️ *Введите ваше имя:*\n\n_(Для отмены нажмите кнопку)_",
        'enter_surname': "✍️ *Введите вашу фамилию:*\n\n_(Для отмены нажмите кнопку)_",
        'enter_age': "✍️ *Введите ваш возраст (цифрами):*\n\n_(Для отмены нажмите кнопку)_",
        'invalid_age': "⚠️ Некорректный возраст (14-60)!",
        'send_phone': "📞 Отправить номер телефона", 'phone_intro': "📞 Отправьте свой номер телефона с помощью кнопки ниже:",
        'success_received': "✨ Успешно принято!", 'all_docs_success': "🎉 Все документы поданы! Скоро мы с вами свяжемся.",
        'select_yonalish_title': "🎓 *ВЫБЕРИТЕ ОДНО ИЗ НАПРАВЛЕНИЙ:*", 'cancel': "❌ Отмена",
        'ariza_success': "🎉 Ваша заявка успешно зарегистрирована!", 'unknown': "❓ Неизвестная команда.",
        'error_need_file': "⚠️ Вы выбрали отправку в виде файла! Пожалуйста, отправьте документ как файл (document).",
        'error_need_photo': "⚠️ Вы выбрали отправку в виде фото! Пожалуйста, отправьте документ как фото (photo).",
        'channel_caption': "📋 *Поступил новый документ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📂 Тип документа: *{doc_name}*",
        'cancelled': "❌ *Отменено.* Вы вернулись в главное меню.",
        'limit_sorov': f"⛔ *Вы уже заполнили анкету {MAX_REGISTRATIONS} раз!*\nДостигнут максимальный лимит ({MAX_REGISTRATIONS}).",
        'limit_yonalish': f"⛔ *Вы уже выбирали направление {MAX_REGISTRATIONS} раз!*\nДостигнут максимальный лимит ({MAX_REGISTRATIONS}).",
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан университеті* Шыршық филиалының ресми қабылдау ботына қош келдіңіз!\n\n👇 _Жалғастыру үшін төмендегі мәзірді пайдаланыңыз:_ ",
        'menu_about': "🎓 Университет туралы", 'menu_yonalish': "🗃️ Мамандықтар",
        'menu_hujjat': "📝 Құжат тапсыру", 'menu_manzil': "📍 Мекен-жай",
        'menu_sorov': "🗂 Сауалнама", 'menu_tanlash': "📋 Мамандық таңдау",
        'menu_admin': "👤 Админмен байланыс", 'back': "🔙 Мәзірге қайту",
        'about_text': " Шыршық қаласында университеттің жаңа заманауи филиалы өз жұмысын бастауда! [Толығырақ...](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
        'yonalish_text': f"👑 *БІЛІМ БЕРУ БАҒДАРЛАМАЛАРЫ*\n*{SEP}*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматизация\n🚚 Көлік техникасы\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм",
        'hujjat_intro': f"📋 *ҚАЖЕТТІ ҚҰЖАТТАР ТІЗІМІ*\n*{SEP}*\n1️⃣ Диплом/Аттестат\n2️⃣ Төлқұжат көшірмесі\n3️⃣ 0.86 Мед. анықтама\n4️⃣ 3x4 photo (6 дана)\n\n🟢 *1-Кезең: Диплом немесе Аттестат*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет түрінде", 'format_fayl': "📎 Файл түрінде",
        'sorov_allready': "✨ *Сіз сауалнаманы толтырып қойғансыз!*", 'yonalish_allready': "✨ *Сіз мамандықты таңдап қойғансыз!*",
        'enter_name': "✍️ *Толық атыңызды енгізіңіз:*\n\n_(Бас тарту үшін батырманы басыңыз)_",
        'enter_surname': "✍️ *Тегіңізді енгізіңіз:*\n\n_(Бас тарту үшін батырманы басыңыз)_",
        'enter_age': "✍️ *Жасыңызды енгізіңіз (санмен):*\n\n_(Бас тарту үшін батырманы басыңыз)_",
        'invalid_age': "⚠️ Жас қате енгізілді (14-60)!",
        'send_phone': "📞 Телефон нөмірін жіберу", 'phone_intro': "📞 Төмендегі арнайы батырма арқылы телефон нөміріңізді жіберіңіз:",
        'success_received': "✨ Сәтті қабылданды!", 'all_docs_success': "🎉 Барлық құжаттар тапсырылды! Тез арада хабарласамыз.",
        'select_yonalish_title': "🎓 *ТІЗІМДЕГІ МАМАНДЫҚТАРДЫҢ БІРІН ТАҢДАҢЫЗ:*", 'cancel': "❌ Бас тарту",
        'ariza_success': "🎉 Өтінішіңіз сәтті тіркелді!", 'unknown': "❓ Белгісіз бұйрық.",
        'error_need_file': "⚠️ Сіз файл түрінде жіберуді таңдадыңыз! Құжатты файл (document) ретінде жіберіңіз.",
        'error_need_photo': "⚠️ Сіз сурет түрінде жіберуді таңдадыңыз! Құжатты сурет (photo) ретінде жіберіңіз.",
        'channel_caption': "📋 *Жаңа құжат түсті!*\n\n👤 Пайдаланушы: {user}\n🆔 ID: `{uid}`\n📂 Құжат түрі: *{doc_name}*",
        'cancelled': "❌ *Бас тартылды.* Басты мәзірге оралдыңыз.",
        'limit_sorov': f"⛔ *Сіз сауалнаманы {MAX_REGISTRATIONS} рет толтырып қойдыңыз!*\nМаксималды шек ({MAX_REGISTRATIONS}) жетті.",
        'limit_yonalish': f"⛔ *Сіз {MAX_REGISTRATIONS} рет мамандық таңдадыңыз!*\nМаксималды шек ({MAX_REGISTRATIONS}) жетті.",
    }
}

HUJJAT_NOMLAR = {
    'uz': {1: "📗 Diplom / Attestat", 2: "🪪 Pasport nusxasi", 3: "🗂 0.86 Meditsina ma'lumotnomasi", 4: "📸 3×4 oq-qora rasm (6 dona)"},
    'ru': {1: "📗 Диплом / Аттестат", 2: "🪪 Копия паспорта", 3: "🗂 Мед. справка 0.86", 4: "📸 Фото 3×4 (6 шт)"},
    'kk': {1: "📗 Диплом / Аттестат", 2: "🪪 Төлқұжат көшірмесі", 3: "🗂 0.86 Мед. анықтама", 4: "📸 3×4 фото (6 дана)"}
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗄️  MA'LUMOTLAR BAZASI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def db_connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = db_connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id            INTEGER PRIMARY KEY,
            first_name    TEXT,
            last_name     TEXT,
            user_name     TEXT,
            lang          TEXT,
            birinchi_vaqt TEXT
        );
        CREATE TABLE IF NOT EXISTS sorovnama (
            id            INTEGER,
            first_name    TEXT,
            last_name     TEXT,
            user_name     TEXT,
            vaqt          TEXT,
            ism           TEXT,
            familya       TEXT,
            yosh          INTEGER,
            telefon       TEXT
        );
        CREATE TABLE IF NOT EXISTS yonalish_royxat (
            id            INTEGER,
            first_name    TEXT,
            last_name     TEXT,
            user_name     TEXT,
            vaqt          TEXT,
            ism           TEXT,
            familya       TEXT,
            yosh          INTEGER,
            telefon       TEXT,
            yonalish      TEXT
        );
    """)
    con.commit()
    con.close()

def get_lang(context, update=None):
    if context and 'lang' in context.user_data:
        return context.user_data['lang']
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

def get_registration_count(table, user_id):
    con = db_connect()
    cur = con.cursor()
    cur.execute(f"SELECT COUNT(*) FROM {table} WHERE id=?", (user_id,))
    count = cur.fetchone()[0]
    con.close()
    return count

def main_menu_markup(lang):
    t = LANG_TEXTS[lang]
    buttons = [
        [t['menu_about'], t['menu_yonalish']],
        [t['menu_hujjat'], t['menu_manzil']],
        [t['menu_sorov'], t['menu_tanlash']],
        [t['menu_admin']],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def format_tanlash_keyboard(lang, step_num):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t['format_rasm'], callback_data=f"format_rasm_{step_num}"),
            InlineKeyboardButton(t['format_fayl'], callback_data=f"format_fayl_{step_num}"),
        ]
    ])

def cancel_keyboard(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup(
        [[KeyboardButton(t['cancel'])]],
        resize_keyboard=True
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀  /start VA TIL TANLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update, context):
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
            InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
            InlineKeyboardButton("🇰🇿 Қазақша", callback_data="set_lang_kk")
        ]
    ])
    await update.message.reply_text(
        "🌐 Iltimos, bot tilini tanlang / Пожалуйста, выберите язык бота / Тілді таңдаңыз:",
        reply_markup=keyboard
    )
    return TIL_TANLASH

async def select_lang_callback(update, context):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[2]
    context.user_data['lang'] = lang

    user = query.from_user
    context.user_data.update({
        'id': user.id,
        'first_name': user.first_name or "",
        'last_name': user.last_name or "",
        'user_name': user.username or "",
    })

    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT id FROM foydalanuvchilar WHERE id=?", (user.id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO foydalanuvchilar VALUES (?,?,?,?,?,?)",
            (user.id, user.first_name, user.last_name, user.username, lang, str(datetime.datetime.now()))
        )
    else:
        cur.execute("UPDATE foydalanuvchilar SET lang=? WHERE id=?", (lang, user.id))
    con.commit()
    con.close()

    t = LANG_TEXTS[lang]
    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"👋 *Salom / Привет / Сәлем, {user.first_name}!* \n\n" + t['welcome'],
        parse_mode="Markdown",
        reply_markup=main_menu_markup(lang)
    )
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  ASOSIY MENYU
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def text(update, context):
    msg = update.message.text
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]

    if msg == t['menu_about']:
        await update.message.reply_text(t['about_text'], parse_mode="Markdown")
        return TANLA

    elif msg == t['menu_yonalish']:
        await update.message.reply_text(t['yonalish_text'], parse_mode="Markdown")
        return TANLA

    elif msg == t['menu_hujjat']:
        await update.message.reply_text(
            t['hujjat_intro'],
            parse_mode="Markdown",
            reply_markup=format_tanlash_keyboard(lang, 1)
        )
        return HUJJAT_FORMAT_1

    elif msg == t['menu_manzil']:
        await update.message.reply_text(
            f"📍 *Google Maps:* https://maps.app.goo.gl/rm7LTHWLpZ7JsKmu6",
            parse_mode="Markdown"
        )
        return TANLA

    elif msg == t['menu_sorov']:
        uid = update.message.from_user.id
        count = get_registration_count('sorovnama', uid)
        if count >= MAX_REGISTRATIONS:
            await update.message.reply_text(t['limit_sorov'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(
            t['enter_name'],
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(lang)
        )
        return SOROV_ISM

    elif msg == t['menu_tanlash']:
        uid = update.message.from_user.id
        count = get_registration_count('yonalish_royxat', uid)
        if count >= MAX_REGISTRATIONS:
            await update.message.reply_text(t['limit_yonalish'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(
            t['enter_name'],
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(lang)
        )
        return YONALISH_ISM

    elif msg == t['menu_admin']:
        await update.message.reply_text(
            f"💬 *Telegram:* {ADMIN_USERNAME}\n📞 *Phone:* `{ADMIN_PHONE}`",
            parse_mode="Markdown"
        )
        return TANLA
    else:
        await update.message.reply_text(t['unknown'], parse_mode="Markdown")
        return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❌  BEKOR QILISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def cancel_handler(update, context):
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]
    await update.message.reply_text(
        t['cancelled'],
        parse_mode="Markdown",
        reply_markup=main_menu_markup(lang)
    )
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📤  HUJJATLAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def format_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)

    parts = data.split("_")
    format_turi = parts[1]
    step = int(parts[2])

    context.user_data[f'hujjat_format_{step}'] = format_turi

    txt = f"📥 {HUJJAT_NOMLAR[lang][step]} ({format_turi.upper()})"
    await query.edit_message_text(txt, parse_mode="Markdown")
    return HUJJAT_STATES[step]

async def hujjat_handler(update, context, step):
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]
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
        logger.error(f"Kanalga yuborishda xatolik: {e}")

    if step < 4:
        next_step = step + 1
        next_doc_title = HUJJAT_NOMLAR[lang][next_step]
        await update.message.reply_text(
            f"{SUCCESS} {t['success_received']}\n\n🟢 *{next_step}-Bosqich: {next_doc_title}*\n❓ Formatni tanlang:",
            parse_mode="Markdown",
            reply_markup=format_tanlash_keyboard(lang, next_step)
        )
        return HUJJAT_FORMAT_STATES[next_step]
    else:
        await update.message.reply_text(t['all_docs_success'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA

async def hujjat_1(update, context): return await hujjat_handler(update, context, 1)
async def hujjat_2(update, context): return await hujjat_handler(update, context, 2)
async def hujjat_3(update, context): return await hujjat_handler(update, context, 3)
async def hujjat_4(update, context): return await hujjat_handler(update, context, 4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📝  SO'ROVNOMA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def sorov_ism(update, context):
    lang = get_lang(context, update)
    context.user_data['sorov_ism'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_surname'],
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(lang)
    )
    return SOROV_FAMILYA

async def sorov_familya(update, context):
    lang = get_lang(context, update)
    context.user_data['sorov_familya'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_age'],
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(lang)
    )
    return SOROV_YOSH

async def sorov_yosh(update, context):
    lang = get_lang(context, update)
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            LANG_TEXTS[lang]['invalid_age'],
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(lang)
        )
        return SOROV_YOSH
    context.user_data['sorov_yosh'] = yosh
    k = [
        [KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)],
        [KeyboardButton(LANG_TEXTS[lang]['cancel'])],
    ]
    await update.message.reply_text(
        LANG_TEXTS[lang]['phone_intro'],
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True)
    )
    return SOROV_TELEFON

async def sorov_telefon(update, context):
    lang = get_lang(context, update)
    telefon = update.message.contact.phone_number
    user = update.message.from_user

    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO sorovnama VALUES (?,?,?,?,?,?,?,?,?)",
        (user.id, user.first_name, user.last_name, user.username, str(datetime.datetime.now()),
         context.user_data.get('sorov_ism'), context.user_data.get('sorov_familya'),
         context.user_data.get('sorov_yosh'), telefon)
    )
    con.commit()
    con.close()

    await update.message.reply_text("🎉 Muvaffaqiyatli!", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  YO'NALISH TANLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    lang = get_lang(context, update)
    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_surname'],
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(lang)
    )
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    lang = get_lang(context, update)
    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_age'],
        parse_mode="Markdown",
        reply_markup=cancel_keyboard(lang)
    )
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    lang = get_lang(context, update)
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            LANG_TEXTS[lang]['invalid_age'],
            parse_mode="Markdown",
            reply_markup=cancel_keyboard(lang)
        )
        return YONALISH_YOSH
    context.user_data['yonalish_yosh'] = yosh
    k = [
        [KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)],
        [KeyboardButton(LANG_TEXTS[lang]['cancel'])],
    ]
    await update.message.reply_text(
        LANG_TEXTS[lang]['phone_intro'],
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True)
    )
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    lang = get_lang(context, update)
    context.user_data['yonalish_telefon'] = update.message.contact.phone_number
    user = update.message.from_user
    if 'user_name' not in context.user_data:
        context.user_data['user_name'] = user.username or ""

    yonalishlar = [
        ("🔬 Biotexnologiya", "Biotexnologiya"),
        ("🌍 Ekologiya", "Ekologiya"),
        ("💻 Axborot tizimlar", "Axborot_tizimlar"),
        ("⚙️ Avtomatizatsiya", "Avtomatizatsiya"),
        ("🚚 Transport", "Transport"),
        ("⚡ Elektroenergetika", "Elektroenergetika"),
        ("🧑‍🏫 Pedagogika", "Pedagogika"),
        ("🧠 Sun'iy intellekt", "Suniy_intellekt"),
        ("💼 Hisob va audit", "Hisob_audit"),
        ("✈️ Turizm", "Turizm"),
    ]

    keyboard = []
    for i in range(0, len(yonalishlar), 2):
        row = [InlineKeyboardButton(yonalishlar[i][0], callback_data=yonalishlar[i][1])]
        if i + 1 < len(yonalishlar):
            row.append(InlineKeyboardButton(yonalishlar[i+1][0], callback_data=yonalishlar[i+1][1]))
        keyboard.append(row)

    keyboard.append([InlineKeyboardButton(LANG_TEXTS[lang]['cancel'], callback_data="bekor")])
    await update.message.reply_text(
        LANG_TEXTS[lang]['select_yonalish_title'],
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TANLA

YONALISH_MAP = {
    "Biotexnologiya": "🔬 Biotexnologiya",
    "Ekologiya": "🌍 Ekologiya",
    "Axborot_tizimlar": "💻 Axborot tizimlar",
    "Avtomatizatsiya": "⚙️ Avtomatizatsiya",
    "Transport": "🚚 Transport",
    "Elektroenergetika": "⚡ Elektroenergetika",
    "Pedagogika": "🧑‍🏫 Pedagogika",
    "Suniy_intellekt": "🧠 Sun'iy intellekt",
    "Hisob_audit": "💼 Hisob va audit",
    "Turizm": "✈️ Turizm",
}

async def callback_data(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)

    if data == "bekor":
        await query.edit_message_text("❌", parse_mode="Markdown")
        return TANLA

    yonalish = YONALISH_MAP.get(data)
    context.user_data['yonalish'] = yonalish

    user_id = query.message.chat_id

    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT INTO yonalish_royxat VALUES (?,?,?,?,?,?,?,?,?,?)",
        (user_id, "", "", "", str(datetime.datetime.now()), context.user_data.get('yonalish_ism'),
         context.user_data.get('yonalish_familya'), context.user_data.get('yonalish_yosh'),
         context.user_data.get('yonalish_telefon'), yonalish)
    )
    con.commit()
    con.close()

    # Kanalga foydalanuvchi ma'lumotlarini yuborish
    username_raw = context.user_data.get('user_name', '')
    username = f"@{username_raw}" if username_raw else f"ID: {user_id}"
    kanal_xabar = (
        f"📋 *Yangi Yo'nalish Arizasi!*\n"
        f"{'━' * 22}\n"
        f"👤 *Telegram:* {username}\n"
        f"🆔 *ID:* `{user_id}`\n"
        f"{'━' * 22}\n"
        f"📝 *Ism:* {context.user_data.get('yonalish_ism', '—')}\n"
        f"📝 *Familya:* {context.user_data.get('yonalish_familya', '—')}\n"
        f"🎂 *Yosh:* {context.user_data.get('yonalish_yosh', '—')}\n"
        f"📞 *Telefon:* `{context.user_data.get('yonalish_telefon', '—')}`\n"
        f"{'━' * 22}\n"
        f"🎓 *Tanlagan yo'nalish:* {yonalish}"
    )
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=kanal_xabar,
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Kanalga yo'nalish yuborishda xatolik: {e}")

    await query.edit_message_text(LANG_TEXTS[lang]['ariza_success'], parse_mode="Markdown")
    await context.bot.send_message(chat_id=user_id, text="🏠", reply_markup=main_menu_markup(lang))
    return TANLA

async def menyuga_qaytish(update, context):
    lang = get_lang(context, update)
    await update.message.reply_text("🏠", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖  MAIN RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN xatoligi!")

    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    back_filter = filters.Regex("^🔙 Menyuga qaytish$|^🔙 Назад в меню$|^🔙 Мәзірге қайту$")
    bekor_filter = filters.Regex("^❌ Bekor qilish$|^❌ Отмена$|^❌ Бас тарту$")
    media_filter = filters.PHOTO | filters.Document.ALL | filters.TEXT

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIL_TANLASH: [CallbackQueryHandler(select_lang_callback, pattern="^set_lang_")],
            TANLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, text),
                CallbackQueryHandler(callback_data)
            ],
            HUJJAT_FORMAT_1: [MessageHandler(back_filter, menyuga_qaytish), CallbackQueryHandler(format_callback)],
            HUJJAT_FORMAT_2: [MessageHandler(back_filter, menyuga_qaytish), CallbackQueryHandler(format_callback)],
            HUJJAT_FORMAT_3: [MessageHandler(back_filter, menyuga_qaytish), CallbackQueryHandler(format_callback)],
            HUJJAT_FORMAT_4: [MessageHandler(back_filter, menyuga_qaytish), CallbackQueryHandler(format_callback)],
            HUJJAT_1: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(media_filter, hujjat_1)],
            HUJJAT_2: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(media_filter, hujjat_2)],
            HUJJAT_3: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(media_filter, hujjat_3)],
            HUJJAT_4: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(media_filter, hujjat_4)],
            SOROV_ISM: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_ism)
            ],
            SOROV_FAMILYA: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_familya)
            ],
            SOROV_YOSH: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_yosh)
            ],
            SOROV_TELEFON: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.CONTACT, sorov_telefon)
            ],
            YONALISH_ISM: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)
            ],
            YONALISH_FAMILYA: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)
            ],
            YONALISH_YOSH: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)
            ],
            YONALISH_TELEFON: [
                MessageHandler(bekor_filter, cancel_handler),
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.CONTACT, yonalish_telefon)
            ],
        },
        fallbacks=[CommandHandler('start', start)]
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == '__main__':
    main()
