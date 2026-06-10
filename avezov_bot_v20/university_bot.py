from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re

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
# ⚙️  SOZLAMALAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"
ADMIN_PHONE = "+998996844483"
DB_PATH = "universitet.db"

ABOUT_PHOTO_URL = "https://storage.googleapis.com/createsite-uz-bucket/blog/1722071060_chirchiq-auezov.jpg"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

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
# 🌐  TIL LUG'ATI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANG_TEXTS = {
    'uz': {
        'welcome': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!\n\n👇 _Davom etish uchun quyidagi menyudan foydalaning:_",
        'menu_about': "🎓 Universitet haqida", 'menu_yonalish': "🗃️ Yo'nalishlar",
        'menu_hujjat': "📝 Hujjat topshirish", 'menu_manzil': "📍 Manzil",
        'menu_sorov': "🗂 So'rovnoma", 'menu_tanlash': "📋 Yo'nalish tanlash",
        'menu_admin': "👤 Admin bilan bog'lanish", 'back': "🔙 Menyuga qaytish",
        'about_text': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti Chirchiq filiali*\n\nChirchiq shahrida universitetning yangi zamonaviy filiali o'z ishini boshlamoqda! Bu yerda talabalar xalqaro standartlarga mos ta'lim olishlari uchun barcha sharoitlar yaratilgan.\n\n🔗 [Batafsil ma'lumotni Oliygoh.uz saytida o'qing](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
        'yonalish_text': "👑 *TA'LIM YO'NALISHLARI*\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'hujjat_intro': "📋 *KERAKLI HUJJATLAR RO'YXATI*\n\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ 0.86 Med-ma'lumotnoma\n4️⃣ 3x4 rasm (6 dona)\n\n🟢 *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm ko'rinishida", 'format_fayl': "📎 Fayl ko'rinishida",
        'sorov_allready': "✨ *Siz so'rovnomani to'ldirib bo'lgansiz! Qayta ro'yxatdan o'tish mumkin emas.*", 
        'yonalish_allready': "✨ *Siz yo'nalishni tanlab bo'lgansiz! Qayta ro'yxatdan o'tish mumkin emas.*",
        'enter_name': "✍️ *To'liq ismingizni kiriting:*", 'enter_surname': "✍️ *Familiyangizni kiriting:*",
        'enter_age': "✍️ *Yoshingizni kiriting (faqat raqamlarda):*", 
        'invalid_age': "⚠️ *Xatolik:* Noto'g'ri yosh kiritildi! Iltimos, faqat raqamlardan foydalaning va yoshingiz 14 va 60 yosh oralig'ida bo'lsin.",
        'send_phone': "📞 Telefon raqamni yuborish", 
        'phone_intro': "📞 *Telefon raqamingizni kiriting:*\n\nPastdagi tugmani bosib avtomat yuborishingiz yoki qo'lda yozib qoldirishingiz mumkin.\n\n📝 *Namuna:* `+998901234567` yoki `901234567`",
        'invalid_phone': "⚠️ *Xatolik:* Telefon raqami formati noto'g'ri! Iltimos, raqamni namuna bo'yicha to'g'ri yozing.\n\n📝 *Namuna:* `+998901234567`",
        'success_received': "✨ Muvaffaqiyatli qabul qilindi!", 'all_docs_success': "🎉 Barcha hujjatlar topshirildi! Tez orada bog'lanamiz.",
        'select_yonalish_title': "🎓 *RO'YXATDAGI YO'NALISHLARDAN BIRINI TANLANG:*", 'cancel': "❌ Bekor qilish",
        'ariza_success': "🎉 Arizangiz muvaffaqiyatli ro'yxatga olindi va saqlandi!", 'unknown': "❓ Noma'lum buyruq.",
        'error_need_file': "⚠️ *Xatolik:* Siz fayl (Document) ko'rinishida yuborishni tanlagansiz! Iltimos, hujjatni rasm qilib emas, fayl sifatida biriktirib yuboring.",
        'error_need_photo': "⚠️ *Xatolik:* Siz rasm (Photo) ko'rinishida yuborishni tanlagansiz! Iltimos, hujjatni fayl qilib emas, oddiy rasm ko'rinishida yuboring.",
        'channel_caption': "📋 *Yangi Hujjat Keldi!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat turi: *{doc_name}*",
        'reg_cancelled': "❌ Jarayon bekor qilindi.", 'reg_success': "🎉 Ro'yxatdan muvaffaqiyatli o'tdingiz!",
        'manzil_text': "📍 *Universitet manzili:*\nChirchiq shahri, Toshkent viloyati, O'zbekiston.\n\n🗺 *Google Maps orqali aniq lokatsiya:* [Xaritani ochish](https://maps.google.com/?q=Chirchiq)"
    },
    'ru': {
        'welcome': "🏛 Добро пожаловать в официальный bot приема Чирчикского филиала *Южно-Казахстанского университета имени М. Ауэзова*!\n\n👇 _Используйте меню ниже для продолжения:_ ",
        'menu_about': "🎓 Об университете", 'menu_yonalish': "🗃️ Направления",
        'menu_hujjat': "📝 Подача документов", 'menu_manzil': "📍 Адрес",
        'menu_sorov': "🗂 Анкета", 'menu_tanlash': "📋 Выбор направления",
        'menu_admin': "👤 Связь с админом", 'back': "🔙 Назад в меню",
        'about_text': "🏛 *Чирчикский филиал Южно-Казахстанского университета имени М. Ауэзова*\n\nВ городе Чирчик начинает работу новый современный филиал университета! Здесь созданы все условия для получения студентами образования, соответствующего международным стандартам.\n\n🔗 [Подробнее на сайте Oliygoh.uz](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
        'yonalish_text': "👑 *НАПРАВЛЕНИЯ ОБУЧЕНИЯ*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Трaнспорт\n⚡ Электроэнергетика\n🧑‍🏫 Администрация\n🧠 Искусственный интеллект\n💼 Учет и аудит\n✈️ Туризм",
        'hujjat_intro': "📋 *СПИСОК НЕОБХОДИМЫХ ДОКУМЕНТОВ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Копия паспорта\n3️⃣ Мед. справка 0.86\n4️⃣ Фото 3х4 (6 шт)\n\n🟢 *Этап 1: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ В виде фото", 'format_fayl': "📎 В виде файла",
        'sorov_allready': "✨ *Вы уже заполнили анкету! Повторная регистрация невозможна.*", 
        'yonalish_allready': "✨ *Вы уже выбрали направление! Повторный выбор невозможен.*",
        'enter_name': "✍️ *Введите ваше имя:*", 'enter_surname': "✍️ *Введите вашу фамилию:*",
        'enter_age': "✍️ *Введите ваш возраст (цифрами):*", 
        'invalid_age': "⚠️ *Ошибка:* Некорректный возраст! Пожалуйста, введите возраст цифрами в диапазоне от 14 до 60 лет.",
        'send_phone': "📞 Отправить номер телефона", 
        'phone_intro': "📞 *Введите ваш номер телефона:*\n\nВы можете нажать кнопку ниже или ввести номер вручную.\n\n📝 *Пример:* `+998901234567` или `901234567`",
        'invalid_phone': "⚠️ *Ошибка:* Неверный формат номера! Пожалуйста, введите номер телефона правильно согласно примеру.\n\n📝 *Пример:* `+998901234567`",
        'success_received': "✨ Успешно принято!", 'all_docs_success': "🎉 Все документы поданы! Скоро мы с вами свяжемся.",
        'select_yonalish_title': "🎓 *ВЫБЕРИТЕ ОДНО ИЗ НАПРАВЛЕНИЙ:*", 'cancel': "❌ Отмена",
        'ariza_success': "🎉 Ваша заявка успешно зарегистрирована!", 'unknown': "❓ Неизвестная команда.",
        'error_need_file': "⚠️ *Ошибка:* Вы выбрали отправку в виде файла! Пожалуйста, прикрепите документ как файл (Document).",
        'error_need_photo': "⚠️ *Ошибка:* Вы выбрали отправку в виде фото! Пожалуйста, отправьте документ как обычное фото (Photo).",
        'channel_caption': "📋 *Поступил новый документ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📂 Тип документа: *{doc_name}*",
        'reg_cancelled': "❌ Процесс отменен.", 'reg_success': "🎉 Вы успешно зарегистрировались!",
        'manzil_text': "📍 *Адрес университета:*\nГород Чирчик, Ташкентская область, Узбекистан.\n\n🗺 *Точная локация на Google Maps:* [Открыть карту](https://maps.google.com/?q=Chirchiq)"
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан университеті* Шыршық филиалының ресми қабылдау ботына қош келдіңіз!\n\n👇 _Жалғастыру үшін төмендегі мәзірді пайдаланыңыз:_ ",
        'menu_about': "🎓 Университет туралы", 'menu_yonalish': "🗃️ Мамандықтар",
        'menu_hujjat': "📝 Құжат тапсыру", 'menu_manzil': "📍 Мекен-жай",
        'menu_sorov': "🗂 Сауалнама", 'menu_tanlash': "📋 Мамандық таңдау",
        'menu_admin': "👤 Админмен байланыс", 'back': "🔙 Мәзірге қайту",
        'about_text': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан университеті Шыршық филиалы*\n\nШыршық қаласында университеттің жаңа заманауи филиалы өз жұмысын бастауда! Мұнда студенттердің халықаралық стандарттарға сай білім алуы үшін барлық жағдай жасалған.\n\n🔗 [Толығырақ Oliygoh.uz сайтында оқыңыз](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
        'yonalish_text': "👑 *БІЛІМ БЕРУ БАҒДАРЛАМАЛАРЫ*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматизация\n🚚 Көлік техникасы\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм",
        'hujjat_intro': "📋 *ҚАЖЕТТІ ҚҰЖАТТАР ТІЗІМІ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Төлқұжат көшірмесі\n3️⃣ 0.86 Мед. анықтама\n4️⃣ 3x4 photo (6 дана)\n\n🟢 *1-Кезең: Диплом немесе Аттестат*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет түрінде", 'format_fayl': "📎 Файл түрінде",
        'sorov_allready': "✨ *Сіз tobacco толтырып қойғансыз! Қайта тіркелу мүмкін емес.*", 
        'yonalish_allready': "✨ *Сіз мамандықты таңдап қойғансыз! Қайта таңдау мүмкін емес.*",
        'enter_name': "✍️ *Толық атыңызды енгізіңіз:*", 'enter_surname': "✍️ *Тегіңізді енгізіңіз:*",
        'enter_age': "✍️ *Жасыңызды енгізіңіз (санмен):*", 
        'invalid_age': "⚠️ *Қате:* Жасыңыз қате енгізілді! Тек сандарды қолданыңыз және жасыңыз 14 пен 60 аралығында болуы керек.",
        'send_phone': "📞 Телефон нөмірін жіберу", 
        'phone_intro': "📞 *Телефон нөміріңізді енгізіңіз:*\n\nTөмендегі батырманы басу арқылы немесе қолмен жазып қалдыра аласыз.\n\n📝 *Мысал:* `+998901234567` немесе `901234567`",
        'invalid_phone': "⚠️ *Қате:* Телефон нөмірінің форматы қате! Мысалға қарап дұрыс енгізіңіз.\n\n📝 *Мысал:* `+998901234567`",
        'success_received': "✨ Сәтті қабылданды!", 'all_docs_success': "🎉 Барлық құжаттар тапсырылды! Тез арада хабарласамыз.",
        'select_yonalish_title': "🎓 *ТІЗІМДЕГІ МАМАНДЫҚТАРДЫҢ БІРІН ТАҢДАҢЫЗ:*", 'cancel': "❌ Бас тарту",
        'ariza_success': "🎉 Өтінішіңіз सәтті тіркелді!", 'unknown': "❓ Белгісіз бұйрық.",
        'error_need_file': "⚠️ *Қате:* Сіз файл түрінде жіберуді таңдадыңыз! Құжатты файл (Document) ретінде жіберіңіз.",
        'error_need_photo': "⚠️ *Қате:* Сіз сурет түрінде жіберуді таңдадыңыз! Құжатты сурет (Photo) ретінде жіберіңіз.",
        'channel_caption': "📋 *Жаңа құжат түсті!*\n\n👤 Пайдаланушы: {user}\n🆔 ID: `{uid}`\n📂 Құжат түрі: *{doc_name}*",
        'reg_cancelled': "❌ Бас тартылды.", 'reg_success': "🎉 Сіз sәтті тіркелдіңіз!",
        'manzil_text': "📍 *Университет мекен-жайы:*\nШыршық қаласы, Ташкент облысы, Өзбекстан.\n\n🗺 *Google Maps арқылы нақты локация:* [Картаны ашу](https://maps.google.com/?q=Chirchiq)"
    }
}

HUJJAT_NOMLAR = {
    'uz': {1: "📗 Diplom / Attestat", 2: "🪪 Pasport nusxasi", 3: "🗂 0.86 Meditsina ma'lumotnomasi", 4: "📸 3×4 oq-qora rasm (6 dona)"},
    'ru': {1: "📗 Диплом / Аттестат", 2: "🪪 Копия паспорта", 3: "🗂 Мед. справка 0.86", 4: "📸 Фото 3×4 (6 шт)"},
    'kk': {1: "📗 Диплом / Аттестат", 2: "🪪 Төлқұжат көшірмесі", 3: "🗂 0.86 Мед. анықтама", 4: "📸 3×4 photo (6 дана)"}
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗄️  MA'LUMOTLAR BAZASI AUX FUNKSIYALARI
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
            id            INTEGER PRIMARY KEY,
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
            id            INTEGER PRIMARY KEY,
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

def check_already_registered(user_id, table_name):
    con = db_connect()
    cur = con.cursor()
    cur.execute(f"SELECT id FROM {table_name} WHERE id=?", (user_id,))
    res = cur.fetchone()
    con.close()
    return True if res else False

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

def main_menu_markup(lang):
    t = LANG_TEXTS[lang]
    buttons = [
        [t['menu_about'], t['menu_yonalish']],
        [t['menu_hujjat'], t['menu_manzil']],
        [t['menu_sorov'], t['menu_tanlash']],
        [t['menu_admin']],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def cancel_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([[t['cancel']]], resize_keyboard=True)

def format_tanlash_keyboard(lang, step_num):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t['format_rasm'], callback_data=f"format_rasm_{step_num}"),
            InlineKeyboardButton(t['format_fayl'], callback_data=f"format_fayl_{step_num}"),
        ]
    ])

def is_menu_button(text_to_check):
    if not text_to_check:
        return False
    for lang in LANG_TEXTS:
        for key, value in LANG_TEXTS[lang].items():
            if key.startswith('menu_') or key == 'back' or key == 'cancel':
                if text_to_check == value:
                    return True
    return False

def validate_phone(phone_str):
    # Telefon raqam faqat raqamlar va plyusdan iborat bo'lishi va uzunligi 7 tadan 15 tagacha bo'lishi kerak
    clean_phone = re.sub(r'[\s\-()]+', '', phone_str)
    if re.match(r'^\+?[1-9]\d{6,14}$', clean_phone):
        return clean_phone
    return None

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
        text=t['welcome'],
        parse_mode="Markdown",
        reply_markup=main_menu_markup(lang)
    )
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  ASOSIY MENYU INTERFEYSI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def text(update, context):
    msg = update.message.text
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]
    uid = update.message.from_user.id

    if msg == t['cancel']:
        await update.message.reply_text(t['reg_cancelled'], reply_markup=main_menu_markup(lang))
        return TANLA

    if msg == t['menu_about']:
        try:
            await update.message.reply_photo(
                photo=ABOUT_PHOTO_URL,
                caption=t['about_text'],
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.error(f"Rasm yuborishda xatolik: {e}")
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
            t['manzil_text'],
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        return TANLA

    elif msg == t['menu_sorov']:
        if check_already_registered(uid, "sorovnama"):
            await update.message.reply_text(t['sorov_allready'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
        return SOROV_ISM

    elif msg == t['menu_tanlash']:
        if check_already_registered(uid, "yonalish_royxat"):
            await update.message.reply_text(t['yonalish_allready'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
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
# 📤  HUJJATLAR VALIDATSIYASI & JO'NATISH
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
    
    if update.message and update.message.text and is_menu_button(update.message.text):
        return await text(update, context)

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
        logger.error(f"Kanalga xatolik: {e}")

    if step < 4:
        next_step = step + 1
        next_doc_title = HUJJAT_NOMLAR[lang][next_step]
        await update.message.reply_text(
            f"{t['success_received']}\n\n🟢 *{next_step}-Bosqich: {next_doc_title}*\n❓ Formatni tanlang:",
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
# 📝  SO'ROVNOMA BOSQICHMA-BOSQICH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def sorov_ism(update, context):
    if is_menu_button(update.message.text): return await text(update, context)
    lang = get_lang(context, update)
    if check_already_registered(update.message.from_user.id, "sorovnama"):
        await update.message.reply_text(LANG_TEXTS[lang]['sorov_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
    context.user_data['sorov_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
    return SOROV_FAMILYA

async def sorov_familya(update, context):
    if is_menu_button(update.message.text): return await text(update, context)
    lang = get_lang(context, update)
    if check_already_registered(update.message.from_user.id, "sorovnama"):
        await update.message.reply_text(LANG_TEXTS[lang]['sorov_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
    context.user_data['sorov_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
    return SOROV_YOSH

async def sorov_yosh(update, context):
    if is_menu_button(update.message.text): return await text(update, context)
    lang = get_lang(context, update)
    if check_already_registered(update.message.from_user.id, "sorovnama"):
        await update.message.reply_text(LANG_TEXTS[lang]['sorov_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
    
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        # Aqlli xatolik ko'rsatish
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
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
    if update.message.text and is_menu_button(update.message.text): return await text(update, context)
    uid = update.message.from_user.id
    
    if check_already_registered(uid, "sorovnama"):
        await update.message.reply_text(LANG_TEXTS[lang]['sorov_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA

    telefon = None
    # Agar foydalanuvchi tugmani bosib yuborgan bo'lsa
    if update.message.contact:
        telefon = update.message.contact.phone_number
    # Agar foydalanuvchi matn ko'rinishida qo'lda yozgan bo'lsa
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
    cur.execute(
        "INSERT OR REPLACE INTO sorovnama VALUES (?,?,?,?,?,?,?,?,?)",
        (user.id, user.first_name, user.last_name, user.username, str(datetime.datetime.now()),
         context.user_data.get('sorov_ism'), context.user_data.get('sorov_familya'), context.user_data.get('sorov_yosh'), telefon)
    )
    con.commit()
    con.close()

    await update.message.reply_text(LANG_TEXTS[lang]['reg_success'], reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  YO'NALISH TANLASH BOSQICHMA-BOSQICH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    if is_menu_button(update.message.text): return await text(update, context)
    lang = get_lang(context, update)
    if check_already_registered(update.message.from_user.id, "yonalish_royxat"):
        await update.message.reply_text(LANG_TEXTS[lang]['yonalish_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    if is_menu_button(update.message.text): return await text(update, context)
    lang = get_lang(context, update)
    if check_already_registered(update.message.from_user.id, "yonalish_royxat"):
        await update.message.reply_text(LANG_TEXTS[lang]['yonalish_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    if is_menu_button(update.message.text): return await text(update, context)
    lang = get_lang(context, update)
    if check_already_registered(update.message.from_user.id, "yonalish_royxat"):
        await update.message.reply_text(LANG_TEXTS[lang]['yonalish_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
        
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_markup(lang))
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
    if update.message.text and is_menu_button(update.message.text): return await text(update, context)
    uid = update.message.from_user.id

    if check_already_registered(uid, "yonalish_royxat"):
        await update.message.reply_text(LANG_TEXTS[lang]['yonalish_allready'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
    
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
        if i + 1 < len(yonalishlar):
            row.append(InlineKeyboardButton(yonalishlar[i+1][0], callback_data=yonalishlar[i+1][1]))
        keyboard.append(row)
        
    await update.message.reply_text(
        LANG_TEXTS[lang]['select_yonalish_title'],
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TANLA

YONALISH_MAP = {
    "Biotexnologiya": "🔬 Biotexnologiya", "Ekologiya": "🌍 Ekologiya",
    "Axborot_tizimlar": "💻 Axborot tizimlar", "Avtomatizatsiya": "⚙️ Avtomatizatsiya",
    "Transport": "🚚 Transport", "Elektroenergetika": "⚡ Elektroenergetika",
    "Pedagogika": "🧑‍🏫 Pedagogika", "Suniy_intellekt": "🧠 Sun'iy intellekt",
    "Hisob_audit": "💼 Hisob va audit", "Turizm": "✈️ Turizm",
}

async def callback_data(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_lang(context)
    user_id = query.message.chat_id

    if data.startswith("format_") or data.startswith("set_lang_") or data == "bekor":
        return 

    if check_already_registered(user_id, "yonalish_royxat"):
        await query.edit_message_text(LANG_TEXTS[lang]['yonalish_allready'], parse_mode="Markdown")
        return TANLA

    yonalish = YONALISH_MAP.get(data)
    context.user_data['yonalish'] = yonalish

    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO yonalish_royxat VALUES (?,?,?,?,?,?,?,?,?,?)",
        (user_id, "", "", "", str(datetime.datetime.now()), context.user_data.get('yonalish_ism'),
         context.user_data.get('yonalish_familya'), context.user_data.get('yonalish_yosh'), context.user_data.get('yonalish_telefon'), yonalish)
    )
    con.commit()
    con.close()

    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(chat_id=user_id, text="🏠 Bosh menyuga qaytdingiz.", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👤  ADMIN STATISTIKA
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
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN xatoligi!")

    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    
    menu_buttons_filter = filters.TEXT & ~filters.COMMAND

    app.add_handler(CommandHandler("users", admin_statistika))

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIL_TANLASH: [CallbackQueryHandler(select_lang_callback, pattern="^set_lang_")],
            TANLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, text),
                CallbackQueryHandler(callback_data)
            ],
            HUJJAT_FORMAT_1: [MessageHandler(menu_buttons_filter, text), CallbackQueryHandler(format_callback)],
            HUJJAT_FORMAT_2: [MessageHandler(menu_buttons_filter, text), CallbackQueryHandler(format_callback)],
            HUJJAT_FORMAT_3: [MessageHandler(menu_buttons_filter, text), CallbackQueryHandler(format_callback)],
            HUJJAT_FORMAT_4: [MessageHandler(menu_buttons_filter, text), CallbackQueryHandler(format_callback)],
            HUJJAT_1: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.ALL, hujjat_1)],
            HUJJAT_2: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.ALL, hujjat_2)],
            HUJJAT_3: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.ALL, hujjat_3)],
            HUJJAT_4: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.ALL, hujjat_4)],
            
            SOROV_ISM:     [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_ism)],
            SOROV_FAMILYA: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_familya)],
            SOROV_YOSH:    [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_yosh)],
            SOROV_TELEFON: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.ALL, sorov_telefon)],
            
            YONALISH_ISM:     [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)],
            YONALISH_FAMILYA: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)],
            YONALISH_YOSH:    [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)],
            YONALISH_TELEFON: [MessageHandler(menu_buttons_filter, text), MessageHandler(filters.ALL, yonalish_telefon)],
        },
        fallbacks=[CommandHandler('start', start)],
        allow_reentry=True
    )

    app.add_handler(conv)
    app.run_polling()

if __name__ == '__main__':
    main()
