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
    ReplyKeyboardMarkup, KeyboardButton, Update
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "7314275083:AAHe_G3...")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"
ADMIN_PHONE = "+998996844483"
DB_PATH = "universitet.db"
ABOUT_PHOTO_URL = "https://storage.googleapis.com/createsite-uz-bucket/blog/1722071060_chirchiq-auezov.jpg"

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Konversiya holatlari (States)
TIL_TANLASH = "til_tanlash"
TANLA = "tanla"
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = "hf1", "hf2", "hf3", "hf4"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "h1", "h2", "h3", "h4"
SOROV_ISM, SOROV_FAMILYA, SOROV_YOSH, SOROV_TELEFON = "si", "sf", "sy", "st"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON, YONALISH_TANLASH = "yi", "yf", "yy", "yt", "yonalish_tanlash"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL LUG'ATI (UZ, RU, KK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANG_TEXTS = {
    'uz': {
        'welcome': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!\n\n👇 _Davom etish uchun tilni tanlang:_",
        'lang_selected': "✅ *O'zbek tili* tanlandi!",
        'menu_about': "🎓 Universitet haqida",
        'menu_yonalish': "🗃️ Yo'nalishlar",
        'menu_hujjat': "📝 Hujjat topshirish",
        'menu_manzil': "📍 Manzil",
        'menu_sorov': "🗂 So'rovnoma",
        'menu_tanlash': "📋 Yo'nalish tanlash",
        'menu_admin': "👤 Admin bilan bog'lanish",
        'back': "🔙 Menyuga qaytish",
        'cancel': "❌ Bekor qilish",
        'change_lang': "🌐 Tilni o'zgartirish",
        'about_text': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti Chirchiq filiali*\n\nChirchiq shahrida universitetning yangi zamonaviy filiali o'z ishini boshlamoqda!\n\n🔗 [Batafsil ma'lumot (Oliygoh.uz)](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'yonalish_text': "👑 *TA'LIM YO'NALISHLARI*\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'hujjat_intro': "📋 *KERAKLI HUJJATLAR RO'YXATI*\n\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ 0.86 Med-ma'lumotnoma\n4️⃣ 3x4 rasm (6 dona)\n\n🟢 *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm ko'rinishida",
        'format_fayl': "📎 Fayl ko'rinishida",
        'sorov_allready': "✨ *Siz so'rovnomani to'ldirib bo'lgansiz!*",
        'yonalish_allready': "✨ *Siz yo'nalishni tanlab bo'lgansiz!*",
        'enter_name': "✍️ *Ismingizni kiriting:*",
        'enter_surname': "✍️ *Familiyangizni kiriting:*",
        'enter_age': "✍️ *Yoshingizni kiriting (faqat raqamlarda):*",
        'invalid_age': "⚠️ *Xatolik:* Noto'g'ri yosh! 14 va 60 yosh oralig'ida faqat raqam kiriting.",
        'send_phone': "📞 Telefon raqamni yuborish",
        'phone_intro': "📞 *Telefon raqamingizni kiriting:*\n\nPastdagi tugmani bosing yoki qo'lda yozing.\n📝 *Namuna:* `+998901234567`",
        'invalid_phone': "⚠️ *Xatolik:* Raqam formati noto'g'ri! Qayta urinib ko'ring.",
        'success_received': "✨ Muvaffaqiyatli qabul qilindi!",
        'all_docs_success': "🎉 Barcha hujjatlar topshirildi! Tez orada bog'lanamiz.",
        'select_yonalish_title': "🎓 *RO'YXATDAGI YO'NALISHLARDAN BIRINI TANLANG:*",
        'unknown': "❓ Noma'lum xabar yoki buyruq. Iltimos, pastdagi menyu tugmalaridan foydalaning.",
        'error_need_file': "⚠️ *Xatolik:* Siz fayl formatini tanlagansiz! Hujjatni fayl (Document) sifatida biriktirib yuboring.",
        'error_need_photo': "⚠️ *Xatolik:* Siz rasm formatini tanlagansiz! Hujjatni oddiy rasm (Photo) ko'rinishida yuboring.",
        'channel_caption': "📋 *Yangi Hujjat Keldi!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat turi: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *YANGI YO'NALISH TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Telefon: `{phone}`\n📚 Tanlangan yo'nalish: *{yonalish}*\n👤 Ism: {ism}\n👤 Familiya: {familya}\n🎂 Yosh: {yosh}",
        'reg_cancelled': "❌ Jarayon bekor qilindi va bosh menyuga qaytildi.",
        'reg_success': "🎉 Yo'nalish muvaffaqiyatli tanlandi!",
        'manzil_text': "📍 *Universitet manzili:*\nChirchiq shahri, Toshkent viloyati.\n🗺 [Google Maps Xaritasi](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Siz hozir ro'yxatdan o'tish jarayonidasiz!*\n\nIltimos, joriy so'ralgan ma'lumotni yuboring. Agar jarayonni to'xtatmoqchi bo'lsangiz, **❌ Bekor qilish** yoki **🔙 Menyuga qaytish** tugmasini bosing."
    },
    'ru': {
        'welcome': "🏛 *Южно-Казахстанский университет имени М.Ауезова* Добро пожаловать в официальный бот приема Чирчикского филиала!\n\n👇 _Для продолжения выберите язык:_",
        'lang_selected': "✅ *Выбран русский язык*!",
        'menu_about': "🎓 Об университете",
        'menu_yonalish': "🗃️ Направления",
        'menu_hujjat': "📝 Подать документы",
        'menu_manzil': "📍 Адрес",
        'menu_sorov': "🗂 Анкета",
        'menu_tanlash': "📋 Выбрать направление",
        'menu_admin': "👤 Связаться с админом",
        'back': "🔙 Вернуться в меню",
        'cancel': "❌ Отменить",
        'change_lang': "🌐 Сменить язык",
        'about_text': "🏛 *Южно-Казахстанский университет имени М.Ауезова Чирчикский филиал*\n\nВ городе Чирчик открывается новый современный филиал университета!\n\n🔗 [Подробнее (Oliygoh.uz)](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'yonalish_text': "👑 *НАПРАВЛЕНИЯ ОБУЧЕНИЯ*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Транспорт\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект\n💼 Учет и аудит\n✈️ Туризм",
        'hujjat_intro': "📋 *СПИСОК НЕОБХОДИМЫХ ДОКУМЕНТОВ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ Мед-справка 0.86\n4️⃣ Фото 3x4 (6 шт)\n\n🟢 *1-этап: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ В виде изображения",
        'format_fayl': "📎 В виде файла",
        'sorov_allready': "✨ *Вы уже заполнили анкету!*",
        'yonalish_allready': "✨ *Вы уже выбрали направление!*",
        'enter_name': "✍️ *Введите ваше имя:*",
        'enter_surname': "✍️ *Введите вашу фамилию:*",
        'enter_age': "✍️ *Введите ваш возраст (только цифры):*",
        'invalid_age': "⚠️ *Ошибка:* Неверный возраст! Введите число от 14 до 60.",
        'send_phone': "📞 Отправить номер телефона",
        'phone_intro': "📞 *Введите ваш номер телефона:*\n\nНажмите кнопку ниже или введите вручную.\n📝 *Пример:* `+998901234567`",
        'invalid_phone': "⚠️ *Ошибка:* Неверный формат номера! Попробуйте снова.",
        'success_received': "✨ Успешно принято!",
        'all_docs_success': "🎉 Все документы поданы! Мы свяжемся с вами в ближайшее время.",
        'select_yonalish_title': "🎓 *ВЫБЕРИТЕ ОДНО ИЗ НАПРАВЛЕНИЙ:*",
        'unknown': "❓ Неизвестное сообщение или команда. Пожалуйста, используйте кнопки меню.",
        'error_need_file': "⚠️ *Ошибка:* Вы выбрали формат файла! Отправьте документ как файл.",
        'error_need_photo': "⚠️ *Ошибка:* Вы выбрали формат изображения! Отправьте документ как фото.",
        'channel_caption': "📋 *Новый документ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📂 Тип документа: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *ВЫБРАНО НОВОЕ НАПРАВЛЕНИЕ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📞 Телефон: `{phone}`\n📚 Выбранное направление: *{yonalish}*\n👤 Имя: {ism}\n👤 Фамилия: {familya}\n🎂 Возраст: {yosh}",
        'reg_cancelled': "❌ Процесс отменен, возврат в главное меню.",
        'reg_success': "🎉 Направление успешно выбрано!",
        'manzil_text': "📍 *Адрес университета:*\nГород Чирчик, Ташкентская область.\n🗺 [Карта Google Maps](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Вы находитесь в процессе регистрации!*\n\nПожалуйста, отправьте запрашиваемую информацию. Чтобы остановить процесс, нажмите **❌ Отменить** или **🔙 Вернуться в меню**."
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан университеті* Шыршық филиалының ресми қабылдау ботына қош келдіңіз!\n\n👇 _Жалғастыру үшін тілді таңдаңыз:_",
        'lang_selected': "✅ *Қазақ тілі* таңдалды!",
        'menu_about': "🎓 Университет туралы",
        'menu_yonalish': "🗃️ Бағыттар",
        'menu_hujjat': "📝 Құжат тапсыру",
        'menu_manzil': "📍 Мекенжай",
        'menu_sorov': "🗂 Сауалнама",
        'menu_tanlash': "📋 Бағыт таңдау",
        'menu_admin': "👤 Әкіммен байланысу",
        'back': "🔙 Мәзірге оралу",
        'cancel': "❌ Болдырмау",
        'change_lang': "🌐 Тілді өзгерту",
        'about_text': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан университеті Шыршық филиалы*\n\nШыршық қаласында университеттің заманауи филиалы өз жұмысын бастайды!\n\n🔗 [Толық ақпарат (Oliygoh.uz)](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'yonalish_text': "👑 *ОҚУ БАҒЫТТАРЫ*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматтандыру\n🚚 Көлік\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм",
        'hujjat_intro': "📋 *ҚАЖЕТТІ ҚҰЖАТТАР ТІЗІМІ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ 0.86 Мед-анықтама\n4️⃣ 3x4 сурет (6 дана)\n\n🟢 *1-кезең: Диплом немесе Аттестат*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет түрінде",
        'format_fayl': "📎 Файл түрінде",
        'sorov_allready': "✨ *Сіз сауалнаманы толтырып қойғансыз!*",
        'yonalish_allready': "✨ *Сіз бағытты таңдап қойғансыз!*",
        'enter_name': "✍️ *Атыңызды жазыңыз:*",
        'enter_surname': "✍️ *Тегіңізді жазыңыз:*",
        'enter_age': "✍️ *Жасыңызды жазыңыз (тек сандармен):*",
        'invalid_age': "⚠️ *Қате:* Жас дұрыс емес! 14 пен 60 аралығындағы санды жазыңыз.",
        'send_phone': "📞 Телефон нөмірін жіберу",
        'phone_intro': "📞 *Телефон нөміріңізді жазыңыз:*\n\nТөмендегі түймені басыңыз немесе қолмен жазыңыз.\n📝 *Мысалы:* `+998901234567`",
        'invalid_phone': "⚠️ *Қате:* Нөмір форматы дұрыс емес! Қайтадан көріңіз.",
        'success_received': "✨ Сәтті қабылданды!",
        'all_docs_success': "🎉 Барлық құжаттар тапсырылды! Біз сізге жақын арада хабарласамыз.",
        'select_yonalish_title': "🎓 *ТІЗІМДЕГІ БАҒЫТТАРДЫҢ БІРІН ТАҢДАҢЫЗ:*",
        'unknown': "❓ Белгісіз хабар немесе бұйрық. Төмендегі мәзір түймелерін пайдаланыңыз.",
        'error_need_file': "⚠️ *Қате:* Сіз файл форматын таңдадыңыз! Құжатты файл түрінде жіберіңіз.",
        'error_need_photo': "⚠️ *Қате:* Сіз сурет форматын таңдадыңыз! Құжатты сурет түрінде жіберіңіз.",
        'channel_caption': "📋 *Жаңа Құжат Келді!*\n\n👤 Пайдаланушы: {user}\n🆔 ID: `{uid}`\n📂 Құжат түрі: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *ЖАҢА БАҒЫТ ТАҢДАЛДЫ!*\n\n👤 Пайдаланушы: {user}\n🆔 ID: `{uid}`\n📞 Телефон: `{phone}`\n📚 Таңдалған бағыт: *{yonalish}*\n👤 Аты: {ism}\n👤 Тегі: {familya}\n🎂 Жасы: {yosh}",
        'reg_cancelled': "❌ Процесс болдырылды және бас мәзірге оралды.",
        'reg_success': "🎉 Бағыт сәтті таңдалды!",
        'manzil_text': "📍 *Университет мекенжайы:*\nШыршық қаласы, Ташкент облысы.\n🗺 [Google Maps Картасы](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Сіз қазір тіркелу процесіндесіз!*\n\nӨтінеміз, сұралған ақпаратты жіберіңіз. Процесті тоқтату үшін **❌ Болдырмау** немесе **🔙 Мәзірге оралу** түймесін басыңыз."
    }
}

HUJJAT_NOMLAR = {
    'uz': {1: "📗 Diplom / Attestat", 2: "🪪 Pasport nusxasi", 3: "🗂 0.86 Med-ma'lumotnoma", 4: "📸 3×4 rasm (6 dona)"},
    'ru': {1: "📗 Диплом / Аттестат", 2: "🪪 Копия паспорта", 3: "🗂 Мед-справка 0.86", 4: "📸 Фото 3×4 (6 шт)"},
    'kk': {1: "📗 Диплом / Аттестат", 2: "🪪 Паспорт көшірмесі", 3: "🗂 0.86 Мед-анықтама", 4: "📸 3×4 сурет (6 дана)"}
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

# Yo'nalishlar nomlari (3 tilda)
YONALISH_NAMES = {
    'uz': {
        "Biotexnologiya": "🔬 Biotexnologiya",
        "Ekologiya": "🌍 Ekologiya",
        "Axborot_tizimlar": "💻 Axborot tizimlar",
        "Avtomatizatsiya": "⚙️ Avtomatizatsiya",
        "Transport": "🚚 Transport",
        "Elektroenergetika": "⚡ Elektroenergetika",
        "Pedagogika": "🧑‍🏫 Pedagogika",
        "Suniy_intellekt": "🧠 Sun'iy intellekt",
        "Hisob_audit": "💼 Hisob va audit",
        "Turizm": "✈️ Turizm"
    },
    'ru': {
        "Biotexnologiya": "🔬 Биотехнология",
        "Ekologiya": "🌍 Экология",
        "Axborot_tizimlar": "💻 Информационные системы",
        "Avtomatizatsiya": "⚙️ Автоматизация",
        "Transport": "🚚 Транспорт",
        "Elektroenergetika": "⚡ Электроэнергетика",
        "Pedagogika": "🧑‍🏫 Педагогика",
        "Suniy_intellekt": "🧠 Искусственный интеллект",
        "Hisob_audit": "💼 Учет и аудит",
        "Turizm": "✈️ Туризм"
    },
    'kk': {
        "Biotexnologiya": "🔬 Биотехнология",
        "Ekologiya": "🌍 Экология",
        "Axborot_tizimlar": "💻 Ақпараттық жүйелер",
        "Avtomatizatsiya": "⚙️ Автоматтандыру",
        "Transport": "🚚 Көлік",
        "Elektroenergetika": "⚡ Электроэнергетика",
        "Pedagogika": "🧑‍🏫 Педагогика",
        "Suniy_intellekt": "🧠 Жасанды интеллект",
        "Hisob_audit": "💼 Есеп және аудит",
        "Turizm": "✈️ Туризм"
    }
}

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

def get_user_lang(user_id):
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT lang FROM foydalanuvchilar WHERE id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    return row[0] if row and row[0] else 'uz'

def set_user_lang(user_id, lang):
    con = db_connect()
    cur = con.cursor()
    cur.execute("UPDATE foydalanuvchilar SET lang=? WHERE id=?", (lang, user_id))
    con.commit()
    con.close()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎛️  KLAVIATURA INTERFEYSLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_menu_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([
        [t['menu_about'], t['menu_yonalish']],
        [t['menu_hujjat'], t['menu_manzil']],
        [t['menu_sorov'], t['menu_tanlash']],
        [t['menu_admin'], t['change_lang']],
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

def yonalish_tanlash_keyboard(lang):
    keyboard = []
    yonalishlar = list(YONALISH_NAMES[lang].items())
    for i in range(0, len(yonalishlar), 2):
        row = [InlineKeyboardButton(yonalishlar[i][1], callback_data=yonalishlar[i][0])]
        if i + 1 < len(yonalishlar):
            row.append(InlineKeyboardButton(yonalishlar[i+1][1], callback_data=yonalishlar[i+1][0]))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def lang_tanlash_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский язык", callback_data="lang_ru")],
        [InlineKeyboardButton("🇰🇿 Қазақ тілі", callback_data="lang_kk")],
    ])

def is_any_menu_button(text_to_check, lang):
    if not text_to_check: return False
    t = LANG_TEXTS[lang]
    menu_buttons = [t['menu_about'], t['menu_yonalish'], t['menu_hujjat'], 
                    t['menu_manzil'], t['menu_sorov'], t['menu_tanlash'], 
                    t['menu_admin'], t['change_lang']]
    return text_to_check in menu_buttons

def is_cancel_or_back(text_to_check, lang):
    if not text_to_check: return False
    t = LANG_TEXTS[lang]
    return text_to_check in [t['cancel'], t['back']]

def validate_phone(phone_str):
    clean_phone = re.sub(r'[\s\-()]+', '', phone_str)
    if re.match(r'^\+?[1-9]\d{6,14}$', clean_phone): return clean_phone
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛡️  PIPELINE GUARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def process_step_guard(update, context, current_state):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    msg_text = update.message.text if (update.message and update.message.text) else None
    
    if msg_text:
        if is_cancel_or_back(msg_text, lang):
            await update.message.reply_text(t['reg_cancelled'], reply_markup=main_menu_markup(lang))
            return "FORCE_CAN_MENU"
            
        if is_any_menu_button(msg_text, lang):
            await update.message.reply_text(t['warning_in_progress'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
            return "FORCE_STAY"
            
    return "PROCEED"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀  START COMMAND
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update, context):
    user = update.effective_user
    
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT id, lang FROM foydalanuvchilar WHERE id=?", (user.id,))
    row = cur.fetchone()
    
    if not row:
        cur.execute("INSERT INTO foydalanuvchilar VALUES (?,?,?,?,?,?)", 
                   (user.id, user.first_name, user.last_name, user.username, 'uz', str(datetime.datetime.now())))
        lang = 'uz'
    else:
        lang = row[1] if row[1] else 'uz'
    con.commit()
    con.close()
    
    context.user_data['lang'] = lang
    
    # Til tanlash uchun inline keyboard
    await update.message.reply_text(
        LANG_TEXTS[lang]['welcome'], 
        parse_mode="Markdown", 
        reply_markup=lang_tanlash_keyboard()
    )
    return TIL_TANLASH

async def lang_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        user_id = query.from_user.id
        set_user_lang(user_id, lang)
        context.user_data['lang'] = lang
        
        await query.edit_message_text(
            LANG_TEXTS[lang]['lang_selected'],
            parse_mode="Markdown"
        )
        await query.message.reply_text(
            LANG_TEXTS[lang]['welcome'].replace("tilni tanlang", "quyidagi menyudan foydalaning"),
            parse_mode="Markdown",
            reply_markup=main_menu_markup(lang)
        )
        return TANLA
    
    return TIL_TANLASH

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  BOSH MENYU DISPATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def main_menu_dispatcher(update, context):
    msg = update.message.text if update.message else None
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    uid = update.message.from_user.id if update.message else None

    if not msg:
        await update.message.reply_text(t['unknown'], reply_markup=main_menu_markup(lang))
        return TANLA

    # Tilni o'zgartirish
    if msg == t['change_lang']:
        await update.message.reply_text(
            "🌐 *Tilni tanlang / Выберите язык / Тілді таңдаңыз:*",
            parse_mode="Markdown",
            reply_markup=lang_tanlash_keyboard()
        )
        return TIL_TANLASH

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
            await update.message.reply_text(t['sorov_allready'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return SOROV_ISM

    elif msg == t['menu_tanlash']:
        if check_already_registered(uid, "yonalish_royxat"):
            await update.message.reply_text(t['yonalish_allready'], parse_mode="Markdown")
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
# 📤  HUJJAT TOPSHIRISH OQIMI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def format_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    parts = data.split("_")
    format_turi, step = parts[1], int(parts[2])
    context.user_data[f'hujjat_format_{step}'] = format_turi
    
    await query.message.reply_text(
        text=f"📥 {HUJJAT_NOMLAR[lang][step]} ({format_turi.upper()} ko'rinishida)\n\n👇 Iltimos, fayl yoki rasmni shu yerga yuklang:", 
        reply_markup=cancel_back_markup(lang)
    )
    return HUJJAT_STATES[step]

async def hujjat_handler(update, context, step):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, HUJJAT_STATES[step])
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
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, SOROV_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_ISM
    
    if not update.message or not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_name'])
        return SOROV_ISM

    context.user_data['sorov_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return SOROV_FAMILYA

async def sorov_familya(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, SOROV_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_FAMILYA
    
    if not update.message or not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'])
        return SOROV_FAMILYA

    context.user_data['sorov_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return SOROV_YOSH

async def sorov_yosh(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, SOROV_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_YOSH
    
    yosh = update.message.text.strip() if (update.message and update.message.text) else ""
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return SOROV_YOSH
        
    context.user_data['sorov_yosh'] = yosh
    k = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['back']), KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True))
    return SOROV_TELEFON

async def sorov_telefon(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, SOROV_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_TELEFON

    telefon = None
    if update.message.contact: 
        telefon = update.message.contact.phone_number
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
    cur.execute("INSERT OR REPLACE INTO sorovnama (id, first_name, last_name, user_name, vaqt, ism, familya, yosh, telefon) VALUES (?,?,?,?,?,?,?,?,?)", 
                (user.id, user.first_name, user.last_name, user.username, str(datetime.datetime.now()), 
                 context.user_data.get('sorov_ism'), context.user_data.get('sorov_familya'), 
                 context.user_data.get('sorov_yosh'), telefon))
    con.commit()
    con.close()

    await update.message.reply_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  YO'NALISH TANLASH OQIMI (KANALGA XABAR YUBORADI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, YONALISH_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_ISM
    
    if not update.message or not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_name'])
        return YONALISH_ISM

    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, YONALISH_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_FAMILYA
    
    if not update.message or not update.message.text:
        await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'])
        return YONALISH_FAMILYA

    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, YONALISH_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_YOSH
    
    yosh = update.message.text.strip() if (update.message and update.message.text) else ""
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return YONALISH_YOSH
        
    context.user_data['yonalish_yosh'] = yosh
    k = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['back']), KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True))
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, YONALISH_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_TELEFON

    telefon = None
    if update.message.contact: 
        telefon = update.message.contact.phone_number
    elif update.message.text:
        telefon = validate_phone(update.message.text.strip())
        if not telefon:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return YONALISH_TELEFON
    else:
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
        return YONALISH_TELEFON

    context.user_data['yonalish_telefon'] = telefon
    
    await update.message.reply_text(
        LANG_TEXTS[lang]['select_yonalish_title'], 
        parse_mode="Markdown", 
        reply_markup=yonalish_tanlash_keyboard(lang)
    )
    return YONALISH_TANLASH

async def yonalish_tanlash_callback(update, context):
    """Yo'nalish tanlash callback handler - kanalga xabar yuboradi"""
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    
    # Tekshirish: foydalanuvchi oldin tanlaganmi?
    if check_already_registered(user_id, "yonalish_royxat"):
        await query.edit_message_text(LANG_TEXTS[lang]['yonalish_allready'], parse_mode="Markdown")
        return TANLA
    
    # Yo'nalishni tekshirish
    if data not in YONALISH_NAMES[lang]:
        return TANLA
        
    yonalish = YONALISH_NAMES[lang][data]
    
    # Bazaga saqlash
    con = db_connect()
    cur = con.cursor()
    cur.execute("""INSERT OR REPLACE INTO yonalish_royxat 
                  (id, first_name, last_name, user_name, vaqt, ism, familya, yosh, telefon, yonalish) 
                  VALUES (?,?,?,?,?,?,?,?,?,?)""", 
                (user_id, query.from_user.first_name, query.from_user.last_name, 
                 query.from_user.username, str(datetime.datetime.now()), 
                 context.user_data.get('yonalish_ism'), context.user_data.get('yonalish_familya'), 
                 context.user_data.get('yonalish_yosh'), context.user_data.get('yonalish_telefon'), yonalish))
    con.commit()
    con.close()
    
    # KANALGA XABAR YUBORISH (barcha ma'lumotlar bilan)
    username = f"@{query.from_user.username}" if query.from_user.username else f"[{query.from_user.first_name}](tg://user?id={user_id})"
    caption_txt = LANG_TEXTS[lang]['yonalish_channel_caption'].format(
        user=username,
        uid=user_id,
        phone=context.user_data.get('yonalish_telefon'),
        yonalish=yonalish,
        ism=context.user_data.get('yonalish_ism'),
        familya=context.user_data.get('yonalish_familya'),
        yosh=context.user_data.get('yonalish_yosh')
    )
    
    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=caption_txt,
            parse_mode="Markdown"
        )
        logger.info(f"Yo'nalish tanlash kanalga yuborildi: {yonalish}")
    except Exception as e:
        logger.error(f"Kanalga yuborishda xato: {e}")
    
    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(
        chat_id=user_id, 
        text="🏠 Bosh menyuga qaytdingiz.", 
        reply_markup=main_menu_markup(lang)
    )
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
    for i, row in enumerate(sorov_rows, 1): 
        matn += f"{i}. {row[0]} {row[1]} -> `{row[2]}`\n"
    matn += "\n" + "━" * 15 + "\n\n"
    matn += f"🎓 *Yo'nalish tanlaganlar ({len(yonalish_rows)} ta):*\n"
    for i, row in enumerate(yonalish_rows, 1): 
        matn += f"{i}. {row[0]} {row[1]} | *{row[3]}* -> `{row[2]}`\n"
    await update.message.reply_text(matn, parse_mode="Markdown")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖  MAIN RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    if not BOT_TOKEN or BOT_TOKEN == "7314275083:AAHe_G3...":
        raise ValueError("❌ BOT_TOKEN xatoligi! Iltimos, .env faylda tokeningizni to'g'ri kiriting!")
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("users", admin_statistika))

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIL_TANLASH: [
                CallbackQueryHandler(lang_callback),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
            ],
            TANLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher), 
                CallbackQueryHandler(yonalish_tanlash_callback)
            ],
            
            HUJJAT_FORMAT_1: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_2: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_3: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_4: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            
            HUJJAT_1: [MessageHandler(filters.ALL, hujjat_1)],
            HUJJAT_2: [MessageHandler(filters.ALL, hujjat_2)],
            HUJJAT_3: [MessageHandler(filters.ALL, hujjat_3)],
            HUJJAT_4: [MessageHandler(filters.ALL, hujjat_4)],
            
            SOROV_ISM:     [MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_ism)],
            SOROV_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_familya)],
            SOROV_YOSH:    [MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_yosh)],
            SOROV_TELEFON: [MessageHandler(filters.ALL, sorov_telefon)],
            
            YONALISH_ISM:     [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)],
            YONALISH_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)],
            YONALISH_YOSH:    [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)],
            YONALISH_TELEFON: [MessageHandler(filters.ALL, yonalish_telefon)],
            YONALISH_TANLASH: [CallbackQueryHandler(yonalish_tanlash_callback)],
        },
        fallbacks=[
            CommandHandler('start', start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
        ],
        allow_reentry=True
    )

    app.add_handler(conv)
    
    print("✅ Bot ishga tushdi! Polling orqali ishlayapti...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
