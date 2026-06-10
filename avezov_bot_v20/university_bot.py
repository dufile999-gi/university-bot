from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
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

# Render/Heroku serverlarida bot o'chib qolmasligi uchun kichik HTTP Web-Server
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args): pass

threading.Thread(target=lambda: HTTPServer(('0.0.0.0', 8080), Handler).serve_forever(), daemon=True).start()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️  SOZLAMALAR & DIZAYN (YANGILANDI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "7963384260:AAFl1m6g8w_p93K8S5L8B-xT_Y7Dq6R2bI4")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"
ADMIN_PHONE = "+998996844483"
DB_PATH = "universitet.db"
MAX_REGISTRATIONS = 5

# Vizual Dizayn uchun Dizayn Elementlari (Rasmlar va Havolalar)
ABOUT_PHOTO_URL = "https://raw.githubusercontent.com/aiogram/aiogram/dev/assets/logo.png" # Shu yerga universitet binosi rasmi linkini qo'ying
MAP_LATITUDE = 41.468307   # M.Auezov Chirchiq filiali aniq geo koordinatalari (Misol tariqasida)
MAP_LONGITUDE = 69.582845

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

SEP = "━━━━━━━━━━━━━━━━━━━━"

# Conversation (Suhbat) holatlari
TIL_TANLASH, TANLA = "til_tanlash", "tanla"
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = "hf1", "hf2", "hf3", "hf4"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "h1", "h2", "h3", "h4"
SOROV_ISM, SOROV_FAMILYA, SOROV_YOSH, SOROV_TELEFON = "si", "sf", "sy", "st"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON = "yi", "yf", "yy", "yt"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL LUG'ATI (DIZAYN VA MATNLAR KUCHAYTIRILDI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANG_TEXTS = {
    'uz': {
        'welcome': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston Universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!\n\n👇 _Davom etish uchun menyudan foydalaning:_",
        'menu_about': "🎓 Universitet haqida", 'menu_yonalish': "🗃️ Yo'nalishlar",
        'menu_hujjat': "📝 Hujjat topshirish", 'menu_manzil': "📍 Manzil",
        'menu_sorov': "🗂 So'rovnoma", 'menu_tanlash': "📋 Yo'nalish tanlash",
        'menu_admin': "👤 Admin bilan bog'lanish", 'back': "🔙 Menyuga qaytish",
        
        'about_text': (
            f"🏛 *M.Auezov nomidagi Janubiy Qozog'iston Universiteti*\n"
            f"_{SEP}_\n\n"
            f"Chirchiq shahrida universitetning yangi, zamonaviy va xalqaro andozalarga mos keluvchi filiali o'z ishini boshlamoqda! "
            f"Biz talabalarga eng yuqori darajadagi ta'lim, malakali professor-o'qituvchilar hamda zamonaviy laboratoriyalarni kafolatlaymiz.\n\n"
            f"🌐 *Rasmiy veb-sayt:* [auezov.edu.kz](https://auezov.edu.kz)\n"
            f"📢 *Telegram kanal:* {CHANNEL_USERNAME}\n\n"
            f"👇 _Batafsil ma'lumot olish uchun tugmalardan foydalaning:_"
        ),
        'btn_site': "🌐 Veb-saytga o'tish", 'btn_channel': "📢 Telegram Kanal",
        
        'manzil_text': (
            f"📍 *UNIVERSITET MANZILI*\n"
            f"_{SEP}_\n\n"
            f"🏢 *Manzil:* Toshkent viloyati, Chirchiq shahri, Navoiy ko'chasi, 4-bino.\n"
            f"📌 *Mo'ljal:* Chirchiq shahar xalq ta'limi bo'limi yaqinida.\n\n"
            f"🗺 _Quyida sizga qulay bo'lishi uchun universitetning aniq geo-lokatsiyasini ham yubordik!_"
        ),
        
        'yonalish_text': f"👑 *TA'LIM YO'NALISHLARI*\n*{SEP}*\n\n⚖️ Yurisprudensiya\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'hujjat_intro': f"📋 *KERAKLI HUJJATLAR RO'YXATI*\n*{SEP}*\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ 0.86 Ma'lumotnoma\n4️⃣ 3x4 rasm\n\n🟢 *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm ko'rinishida", 'format_fayl': "📎 Fayl ko'rinishida",
        'enter_name': "✍️ *Ismingizni kiriting:*", 'enter_surname': "✍️ *Familiyangizni kiriting:*",
        'enter_age': "✍️ *Yoshingizni kiriting (raqamlarda):*", 'invalid_age': "⚠️ Noto'g'ri yosh kiritildi (14-60)!",
        'send_phone': "📞 Telefon raqamni yuborish", 'phone_intro': "📞 Pastdagi tugma orqali telefon raqamingizni yuboring:",
        'success_received': "✨ Muvaffaqiyatli qabul qilindi!",
        
        'all_docs_success': (
            f"🎉 *TABRIKLAYMIZ!*\n"
            f"Barcha kerakli hujjatlaringiz muvaffaqiyatli topshirildi. Qabul komissiyasi tez orada siz bilan bog'lanadi!\n\n"
            f"🏢 *Universitetimiz manzili:* Chirchiq shahri, Navoiy ko'chasi, 4-bino.\n"
            f"🗺 Oflayn kelmoqchi bo'lsangiz, lokatsiya pastda biriktirilgan."
        ),
        
        'select_yonalish_title': "🎓 *RO'YXATDAGI YO'NALISHLARDAN BIRINI TANLANG:*", 'cancel': "❌ Bekor qilish",
        'ariza_success': "🎉 Arizangiz muvaffaqiyatli ro'yxatga olindi!", 
        'unknown': "❓ Noma'lum buyruq. Iltimos, menyudagi tugmalardan foydalaning.",
        'error_need_file': "⚠️ Iltimos, hujjatni fayl (document) sifatida yuboring.",
        'error_need_photo': "⚠️ Iltimos, hujjatni rasm (photo) sifatida yuboring.",
        'channel_caption': "📋 *Yangi Hujjat!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat: *{doc_name}*",
        'cancelled': "❌ *Amal bekor qilindi.* Asosiy menyuga qaytdingiz.",
        'limit_error': "⛔ Maksimal ro'yxatdan o'tish chegarasiga yetgansiz!",
        'state_error': "⚠️ Siz hozir ma'lumot kiritish bosqichidasiz! Iltimos, davom eting yoki quyidagi tugma orqali bekor qiling."
    },
    'ru': {
        'welcome': "🏛 Добро пожаловать в официальный бот приема Чирчикского филиала *ЮКУ имени М. Ауэзова*!\n\n👇 _Используйте меню ниже:_ ",
        'menu_about': "🎓 Об университете", 'menu_yonalish': "🗃️ Направления",
        'menu_hujjat': "📝 Подача документов", 'menu_manzil': "📍 Адрес",
        'menu_sorov': "🗂 Анкета", 'menu_tanlash': "📋 Выбор направления",
        'menu_admin': "👤 Связь с админом", 'back': "🔙 Назад в меню",
        
        'about_text': (
            f"🏛 *Южно-Казахстанский Университет имени М. Ауэзова*\n"
            f"_{SEP}_\n\n"
            f"Новый современный филиал университета начинает свою деятельность в городе Чирчик! "
            f"Мы гарантируем высокий уровень образования, квалифицированный преподавательский состав и передовые лаборатории.\n\n"
            f"🌐 *Официальный сайт:* [auezov.edu.kz](https://auezov.edu.kz)\n"
            f"📢 *Telegram канал:* {CHANNEL_USERNAME}\n\n"
            f"👇 _Используйте кнопки ниже для подробностей:_"
        ),
        'btn_site': "🌐 Перейти на сайт", 'btn_channel': "📢 Telegram Канал",
        
        'manzil_text': (
            f"📍 *АДРЕС УНИВЕРСИТЕТА*\n"
            f"_{SEP}_\n\n"
            f"🏢 *Адрес:* Ташкентская область, город Чирчик, улица Навои, здание 4.\n"
            f"📌 *Ориентир:* Рядом с городским отделом народного образования.\n\n"
            f"🗺 _Ниже мы также отправили точную гео-локацию университета для вашего удобства!_"
        ),
        
        'yonalish_text': f"👑 *НАПРАВЛЕНИЯ ОБУЧЕНИЯ*\n*{SEP}*\n\n⚖️ Юриспруденция\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Транспорт\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект\n💼 Учет и充дит\n✈️ Туризм",
        'hujjat_intro': f"📋 *СПИСОК ДОКУМЕНТОВ*\n*{SEP}*\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ Мед. справка 0.86\n4️⃣ Фото 3х4\n\n🟢 *Этап 1: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ В виде фото", 'format_fayl': "📎 В виде файла",
        'enter_name': "✍️ *Введите ваше имя:*", 'enter_surname': "✍️ *Введите вашу фамилию:*",
        'enter_age': "✍️ *Введите ваш возраст (цифрами):*", 'invalid_age': "⚠️ Некорректный возраст (14-60)!",
        'send_phone': "📞 Отправить номер", 'phone_intro': "📞 Отправьте свой номер телефона с помощью кнопки ниже:",
        'success_received': "✨ Успешно принято!",
        
        'all_docs_success': (
            f"🎉 *ПОЗДРАВЛЯЕМ!*\n"
            f"Все необходимые документы успешно поданы. Приемная комиссия свяжется с вами в ближайшее время!\n\n"
            f"🏢 *Адрес университета:* город Чирчик, улица Навои, здание 4.\n"
            f"🗺 Точная локация прикреплена ниже."
        ),
        
        'select_yonalish_title': "🎓 *ВЫБЕРИТЕ ОДНО ИЗ НАПРАВЛЕНИЙ:*", 'cancel': "❌ Отмена",
        'ariza_success': "🎉 Ваша заявка успешно зарегистрирована!", 
        'unknown': "❓ Неизвестная команда. Пожалуйста, используйте кнопки меню.",
        'error_need_file': "⚠️ Пожалуйста, отправьте документ как файл (document).",
        'error_need_photo': "⚠️ Пожалуйста, отправьте документ как фото (photo).",
        'channel_caption': "📋 *Новый документ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📂 Документ: *{doc_name}*",
        'cancelled': "❌ *Действие отменено.* Вы вернулись в главное меню.",
        'limit_error': "⛔ Вы достигли максимального лимита регистраций!",
        'state_error': "⚠️ Вы находитесь на этапе ввода данных! Продолжайте или нажмите кнопку отмены."
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы Оңтүстік Қазақстан Университеті* Шыршық филиалының ресми қабылдау ботына қош келдіңіз!\n\n👇 _Жалғастыру үшін мәзірді пайдаланыңыз:_ ",
        'menu_about': "🎓 Университет туралы", 'menu_yonalish': "🗃️ Мамандықтар",
        'menu_hujjat': "📝 Құжат тапсыру", 'menu_manzil': "📍 Мекен-жай",
        'menu_sorov': "🗂 Сауалнама", 'menu_tanlash': "📋 Мамандық таңдау",
        'menu_admin': "👤 Админмен байланыс", 'back': "🔙 Мәзірге қайту",
        
        'about_text': (
            f"🏛 *М.Әуезов атындағы Оңтүстік Қазақстан Университеті*\n"
            f"_{SEP}_\n\n"
            f"Шыршық қаласында университеттің жаңа, заманауи және халықаралық талаптарға сай филиалы өз жұмысын бастауда! "
            f"Біз студенттерге жоғары деңгейлі білім, білікті профессор-оқытушылар құрамы мен заманауи зертханаларға кепілдік береміз.\n\n"
            f"🌐 *Ресми веб-сайт:* [auezov.edu.kz](https://auezov.edu.kz)\n"
            f"📢 *Telegram канал:* {CHANNEL_USERNAME}\n\n"
            f"👇 _Толық ақпарат алу үшін батырмаларды қолданыңыз:_"
        ),
        'btn_site': "🌐 Веб-сайтқа өту", 'btn_channel': "📢 Telegram Канал",
        
        'manzil_text': (
            f"📍 *УНИВЕРСИТЕТ МЕКЕН-ЖАЙЫ*\n"
            f"_{SEP}_\n\n"
            f"🏢 *Мекен-жай:* Ташкент облысы, Шыршық қаласы, Науаи көшесі, 4-үй.\n"
            f"📌 *Бағдар:* Шыршық қалалық халыққа білім беру бөлімінің жанында.\n\n"
            f"🗺 _Төменде сізге ыңғайлы болуы үшін университеттің нақты гео-локациясын жібердік!_"
        ),
        
        'yonalish_text': f"👑 *БІЛІМ БЕРУ БАҒДАРЛАМАЛАРЫ*\n*{SEP}*\n\n⚖️ Юриспруденция\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматизация\n🚚 Көлік техникасы\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм",
        'hujjat_intro': f"📋 *ҚАЖЕТТІ ҚҰЖАТТАР*\n*{SEP}*\n1️⃣ Диплом/Аттестат\n2️⃣ Төлқұжат\n3️⃣ 0.86 Анықтама\n4️⃣ 3x4 photo\n\n🟢 *1-Кезең: Диплом немесе Аттестат*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет түрінде", 'format_fayl': "📎 Файл түрінде",
        'enter_name': "✍️ *Атыңызды енгізіңіз:*", 'enter_surname': "✍️ *Тегіңізді енгізіңіз:*",
        'enter_age': "✍️ *Жасыңызды енгізіңіз (санмен):*", 'invalid_age': "⚠️ Жас қате енгізілді (14-60)!",
        'send_phone': "📞 Телефон жіберу", 'phone_intro': "📞 Төмендегі арнайы батырма арқылы telephone нөміріңізді жіберіңіз:",
        'success_received': "✨ Сәтті қабылданды!",
        
        'all_docs_success': (
            f"🎉 *ҚҰТТЫҚТАЙМЫЗ!*\n"
            f"Барлық қажетті құжаттарыңыз сәтті тапсырылды. Қабылдау комиссиясы жақын арада сізбен байланысады!\n\n"
            f"🏢 *Университет мекен-жайы:* Шыршық қаласы, Науаи көшесі, 4-үй.\n"
            f"🗺 Нақты локация төменде бекітілген."
        ),
        
        'select_yonalish_title': "🎓 *ТІЗІМДЕГІ МАМАНДЫҚТАРДЫҢ БІРІН ТАҢДАҢЫЗ:*", 'cancel': "❌ Бас тарту",
        'ariza_success': "🎉 Өтінішіңіз sәтті тіркелді!", 
        'unknown': "❓ Белгісіз бұйрық. Мәзір батырмаларын қолданыңыз.",
        'error_need_file': "⚠️ Құжатты файл (document) ретінде жіберіңіз.",
        'error_need_photo': "⚠️ Құжатты сурет (photo) ретінде жіберіңіз.",
        'channel_caption': "📋 *Жаңа құжат!*\n\n👤 Пайдаланушы: {user}\n🆔 ID: `{uid}`\n📂 Құжат: *{doc_name}*",
        'cancelled': "❌ *Бас тартылды.* Басты мәзірге оралдыңыз.",
        'limit_error': "⛔ Максималды шекке жеттіңіз!",
        'state_error': "⚠️ Сіз қазір мәлімет енгізу кезеңіндесіз! Жалғастырыңыз немесе бас тарту батырмасын басыңыз."
    }
}

HUJJAT_NOMLAR = {
    'uz': {1: "📗 Diplom / Attestat", 2: "🪪 Pasport nusxasi", 3: "🗂 0.86 Med-ma'lumotnoma", 4: "📸 3×4 rasm"},
    'ru': {1: "📗 Диплом / Аттестат", 2: "🪪 Копия паспорта", 3: "🗂 Мед. справка 0.86", 4: "📸 Фото 3×4"},
    'kk': {1: "📗 Диплом / Аттестат", 2: "🪪 Төлқұжат көшірмесі", 3: "🗂 0.86 Мед. анықтама", 4: "📸 3×4 фото"}
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗄️  MA'LUMOTLAR BAZASI (SQLite)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def db_connect(): return sqlite3.connect(DB_PATH)

def init_db():
    con = db_connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, lang TEXT, vaqt TEXT);
        CREATE TABLE IF NOT EXISTS sorovnama (id INTEGER, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT);
        CREATE TABLE IF NOT EXISTS yonalish_royxat (id INTEGER, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT, yonalish TEXT);
    """)
    con.commit()
    con.close()

def get_lang(context, update=None):
    if context and 'lang' in context.user_data: return context.user_data['lang']
    if update and update.message:
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT lang FROM foydalanuvchilar WHERE id=?", (update.message.from_user.id,))
        res = cur.fetchone()
        con.close()
        if res:
            context.user_data['lang'] = res[0]
            return res[0]
    return 'uz'

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  TUGMALAR GENERATORI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_menu_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([
        [t['menu_about'], t['menu_yonalish']],
        [t['menu_hujjat'], t['menu_manzil']],
        [t['menu_sorov'], t['menu_tanlash']],
        [t['menu_admin']]
    ], resize_keyboard=True)

def format_tanlash_keyboard(lang, step_num):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t['format_rasm'], callback_data=f"format_rasm_{step_num}"),
         InlineKeyboardButton(t['format_fayl'], callback_data=f"format_fayl_{step_num}")],
        [InlineKeyboardButton(t['back'], callback_data="hujjat_orqaga")]
    ])

def cancel_keyboard(lang):
    return ReplyKeyboardMarkup([[KeyboardButton(LANG_TEXTS[lang]['cancel'])]], resize_keyboard=True)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀  START VA ASOSIY MATNLAR BOSHQRUVI (RASM VA SAYTLAR QO'SHILDI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update, context):
    context.user_data.clear()
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="set_lang_uz"),
         InlineKeyboardButton("🇷🇺 Русский", callback_data="set_lang_ru"),
         InlineKeyboardButton("🇰🇿 Қазақша", callback_data="set_lang_kk")]
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
    cur.execute("INSERT OR REPLACE INTO foydalanuvchilar VALUES (?,?,?,?,?,?)", 
                (user.id, user.first_name, user.last_name, user.username, lang, str(datetime.datetime.now())))
    con.commit()
    con.close()

    await query.message.delete()
    await context.bot.send_message(chat_id=query.message.chat_id, text=LANG_TEXTS[lang]['welcome'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
    return TANLA

async def text_handler(update, context):
    msg = update.message.text
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]

    # 🎓 UNIVERSITET HAQIDA (YANGI DIZAYN - RASM + TUGMALAR)
    if msg == t['menu_about']:
        inline_links = InlineKeyboardMarkup([
            [InlineKeyboardButton(t['btn_site'], url="https://auezov.edu.kz"),
             InlineKeyboardButton(t['btn_channel'], url=f"https://t.me/{CHANNEL_USERNAME.replace('@','')}" )]
        ])
        # Rasm bilan chiroyli xabar chiqarish
        try:
            await update.message.reply_photo(photo=ABOUT_PHOTO_URL, caption=t['about_text'], parse_mode="Markdown", reply_markup=inline_links)
        except Exception:
            # Agar rasm yuklanishida xatolik bo'lsa, faqat matnning o'zini yuboradi
            await update.message.reply_text(t['about_text'], parse_mode="Markdown", reply_markup=inline_links)
        return TANLA
        
    elif msg == t['menu_yonalish']:
        await update.message.reply_text(t['yonalish_text'], parse_mode="Markdown")
        return TANLA
        
    # 📍 MANZIL BO'LIMI (TO'G'RILANDI VA GEO LOKATSIYA QO'SHILDI)
    elif msg == t['menu_manzil']:
        await update.message.reply_text(t['manzil_text'], parse_mode="Markdown")
        await update.message.reply_location(latitude=MAP_LATITUDE, longitude=MAP_LONGITUDE)
        return TANLA
        
    elif msg == t['menu_admin']:
        await update.message.reply_text(f"💬 *Admin:* {ADMIN_USERNAME}\n📞 *Tel:* `{ADMIN_PHONE}`", parse_mode="Markdown")
        return TANLA
    elif msg == t['menu_hujjat']:
        await update.message.reply_text(t['hujjat_intro'], parse_mode="Markdown", reply_markup=format_tanlash_keyboard(lang, 1))
        return HUJJAT_FORMAT_1
    elif msg in [t['menu_sorov'], t['menu_tanlash']]:
        context.user_data['rejim'] = 'sorov' if msg == t['menu_sorov'] else 'yonalish'
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_keyboard(lang))
        return SOROV_ISM if msg == t['menu_sorov'] else YONALISH_ISM
    
    await update.message.reply_text(t['unknown'], reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ❌  BEKOR QILISH VA CHALG'ISH FILTRLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def cancel_handler(update, context):
    lang = get_lang(context, update)
    context.user_data.clear()
    await update.message.reply_text(LANG_TEXTS[lang]['cancelled'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
    return TANLA

async def inline_back_handler(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.message.delete()
    await context.bot.send_message(chat_id=query.message.chat_id, text="🏠 Menyu", reply_markup=main_menu_markup(lang))
    return TANLA

async def state_error_handler(update, context):
    lang = get_lang(context, update)
    await update.message.reply_text(LANG_TEXTS[lang]['state_error'], reply_markup=cancel_keyboard(lang))
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📤  HUJJAT YUKLASH (YAKUNIDA MANZIL CHIQADIGAN QILINDI)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def format_callback(update, context):
    query = update.callback_query
    await query.answer()
    if query.data == "hujjat_orqaga": return await inline_back_handler(update, context)
    
    _, fmt, step = query.data.split("_")
    step = int(step)
    lang = get_lang(context)
    context.user_data[f'fmt_{step}'] = fmt

    await query.message.delete()
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text=f"📥 {HUJJAT_NOMLAR[lang][step]} ({fmt.upper()}) formatida yuboring yoki bekor qiling:",
        reply_markup=cancel_keyboard(lang)
    )
    return HUJJAT_STATES[step]

async def hujjat_save(update, context, step):
    lang = get_lang(context, update)
    t = LANG_TEXTS[lang]
    fmt = context.user_data.get(f'fmt_{step}', 'rasm')

    if fmt == 'fayl' and not update.message.document:
        await update.message.reply_text(t['error_need_file'])
        return HUJJAT_STATES[step]
    if fmt == 'rasm' and not update.message.photo:
        await update.message.reply_text(t['error_need_photo'])
        return HUJJAT_STATES[step]

    user = update.message.from_user
    uname = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
    caption = t['channel_caption'].format(user=uname, uid=user.id, doc_name=HUJJAT_NOMLAR[lang][step])

    try:
        if update.message.document:
            await context.bot.send_document(chat_id=CHANNEL_USERNAME, document=update.message.document.file_id, caption=caption, parse_mode="Markdown")
        else:
            await context.bot.send_photo(chat_id=CHANNEL_USERNAME, photo=update.message.photo[-1].file_id, caption=caption, parse_mode="Markdown")
    except Exception as e: logger.error(f"Kanal xatosi: {e}")

    if step < 4:
        next_s = step + 1
        await update.message.reply_text(f"✨ {t['success_received']}\n\n🟢 *{next_s}-Bosqich:* {HUJJAT_NOMLAR[lang][next_s]}", 
                                       parse_mode="Markdown", reply_markup=format_tanlash_keyboard(lang, next_s))
        return HUJJAT_FORMAT_STATES[next_s]
    
    # 🔥 HUJJATLAR TUGAGANIDAN KEYIN MANZIL VA LOKATSIYA CHIQARISH
    await update.message.reply_text(t['all_docs_success'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
    await update.message.reply_location(latitude=MAP_LATITUDE, longitude=MAP_LONGITUDE)
    return TANLA

async def h1(update, context): return await hujjat_save(update, context, 1)
async def h2(update, context): return await hujjat_save(update, context, 2)
async def h3(update, context): return await hujjat_save(update, context, 3)
async def h4(update, context): return await hujjat_save(update, context, 4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗂️  ANKETA / YO'NALISH INPUT MATRIX LOGIC
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def input_ism(update, context):
    lang = get_lang(context, update)
    rejim = context.user_data.get('rejim')
    context.user_data['p_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], reply_markup=cancel_keyboard(lang))
    return SOROV_FAMILYA if rejim == 'sorov' else YONALISH_FAMILYA

async def input_familya(update, context):
    lang = get_lang(context, update)
    rejim = context.user_data.get('rejim')
    context.user_data['p_fam'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], reply_markup=cancel_keyboard(lang))
    return SOROV_YOSH if rejim == 'sorov' else YONALISH_YOSH

async def input_yosh(update, context):
    lang = get_lang(context, update)
    rejim = context.user_data.get('rejim')
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'])
        return None
    context.user_data['p_yosh'] = int(yosh)
    
    k = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True))
    return SOROV_TELEFON if rejim == 'sorov' else YONALISH_TELEFON

async def input_telefon(update, context):
    lang = get_lang(context, update)
    if not update.message.contact:
        await update.message.reply_text("⚠️ Telefon raqamingizni yuborish tugmasini bosing!")
        return None
    
    context.user_data['p_tel'] = update.message.contact.phone_number
    rejim = context.user_data.get('rejim')

    if rejim == 'sorov':
        user = update.message.from_user
        con = db_connect()
        cur = con.cursor()
        cur.execute("INSERT INTO sorovnama VALUES (?,?,?,?,?,?,?,?,?)",
                    (user.id, user.first_name, user.last_name, user.username, str(datetime.datetime.now()),
                     context.user_data['p_ism'], context.user_data['p_fam'], context.user_data['p_yosh'], context.user_data['p_tel']))
        con.commit()
        con.close()
        await update.message.reply_text(LANG_TEXTS[lang]['ariza_success'], reply_markup=main_menu_markup(lang))
        return TANLA
    else:
        yonalishlar = [
            ("⚖️ Yurisprudensiya", "Yur"), ("🔬 Biotexnologiya", "Bio"),
            ("🌍 Ekologiya", "Eko"), ("💻 Axborot tizimlar", "IT"),
            ("⚙️ Avtomatizatsiya", "Avto"), ("🚚 Transport", "Trans"),
            ("⚡ Elektroenergetika", "Energo"), ("🧑‍🏫 Pedagogika", "Ped"),
            ("🧠 Sun'iy intellekt", "AI"), ("💼 Hisob va audit", "Audit"),
            ("✈️ Turizm", "Turizm")
        ]
        keyboard = []
        for i in range(0, len(yonalishlar), 2):
            row = [InlineKeyboardButton(yonalishlar[i][0], callback_data=f"yon_{yonalishlar[i][1]}")]
            if i + 1 < len(yonalishlar): row.append(InlineKeyboardButton(yonalishlar[i+1][0], callback_data=f"yon_{yonalishlar[i+1][1]}"))
            keyboard.append(row)
        keyboard.append([InlineKeyboardButton(LANG_TEXTS[lang]['cancel'], callback_data="yon_bekor")])
        
        await update.message.reply_text(LANG_TEXTS[lang]['select_yonalish_title'], reply_markup=InlineKeyboardMarkup(keyboard))
        return TANLA

YONALISH_MAP = {
    "Yur": "⚖️ Yurisprudensiya", "Bio": "🔬 Biotexnologiya", "Eko": "🌍 Ekologiya", "IT": "💻 Axborot tizimlar",
    "Avto": "⚙️ Avtomatizatsiya", "Trans": "🚚 Transport", "Energo": "⚡ Elektroenergetika", "Ped": "🧑‍🏫 Pedagogika",
    "AI": "🧠 Sun'iy intellekt", "Audit": "💼 Hisob va audit", "Turizm": "✈️ Turizm"
}

async def yonalish_callback(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    data = query.data.split("_")[1]

    if data == "bekor":
        await query.message.delete()
        await context.bot.send_message(chat_id=query.message.chat_id, text=LANG_TEXTS[lang]['cancelled'], reply_markup=main_menu_markup(lang))
        return TANLA

    yon_nomi = YONALISH_MAP.get(data)
    user_id = query.message.chat_id
    user = query.from_user

    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT INTO yonalish_royxat VALUES (?,?,?,?,?,?,?,?,?,?)",
                (user_id, user.first_name, user.last_name, user.username, str(datetime.datetime.now()),
                 context.user_data.get('p_ism'), context.user_data.get('p_fam'), context.user_data.get('p_yosh'), context.user_data.get('p_tel'), yon_nomi))
    con.commit()
    con.close()

    uname = f"@{user.username}" if user.username else f"ID: {user_id}"
    report = f"📋 *Yangi Yo'nalish Arizasi!*\n{SEP}\n👤 *User:* {uname}\n📝 *F.I.O:* {context.user_data.get('p_fam')} {context.user_data.get('p_ism')}\n📞 *Tel:* `{context.user_data.get('p_tel')}`\n🎓 *Yo'nalish:* {yon_nomi}"
    try: await context.bot.send_message(chat_id=CHANNEL_USERNAME, text=report, parse_mode="Markdown")
    except Exception as e: logger.error(f"Kanal xatosi: {e}")

    await query.edit_message_text(LANG_TEXTS[lang]['ariza_success'])
    await context.bot.send_message(chat_id=user_id, text="Asosiy sahifa", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖  MAIN ENGINE RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    bekor_filt = filters.Regex("^❌ Bekor qilish$|^❌ Отмена$|^❌ Бас тарту$")

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start), MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler)],
        states={
            TIL_TANLASH: [CallbackQueryHandler(select_lang_callback, pattern="^set_lang_")],
            TANLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler), CallbackQueryHandler(yonalish_callback, pattern="^yon_")],
            
            HUJJAT_FORMAT_1: [CallbackQueryHandler(format_callback), MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, state_error_handler)],
            HUJJAT_FORMAT_2: [CallbackQueryHandler(format_callback), MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, state_error_handler)],
            HUJJAT_FORMAT_3: [CallbackQueryHandler(format_callback), MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, state_error_handler)],
            HUJJAT_FORMAT_4: [CallbackQueryHandler(format_callback), MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, state_error_handler)],
            
            HUJJAT_1: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, h1)],
            HUJJAT_2: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, h2)],
            HUJJAT_3: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, h3)],
            HUJJAT_4: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.ALL, h4)],
            
            SOROV_ISM: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, input_ism), MessageHandler(filters.ALL, state_error_handler)],
            SOROV_FAMILYA: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, input_familya), MessageHandler(filters.ALL, state_error_handler)],
            SOROV_YOSH: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, input_yosh), MessageHandler(filters.ALL, state_error_handler)],
            SOROV_TELEFON: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.CONTACT, input_telefon), MessageHandler(filters.ALL, state_error_handler)],
            
            YONALISH_ISM: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, input_ism), MessageHandler(filters.ALL, state_error_handler)],
            YONALISH_FAMILYA: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, input_familya), MessageHandler(filters.ALL, state_error_handler)],
            YONALISH_YOSH: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.TEXT & ~filters.COMMAND, input_yosh), MessageHandler(filters.ALL, state_error_handler)],
            YONALISH_TELEFON: [MessageHandler(bekor_filt, cancel_handler), MessageHandler(filters.CONTACT, input_telefon), MessageHandler(filters.ALL, state_error_handler)],
        },
        fallbacks=[MessageHandler(bekor_filt, cancel_handler), CommandHandler('start', start)]
    )

    app.add_handler(conv)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, text_handler))

    logger.info("🤖 Bot 100% yangi dizayn bilan ishlamoqda...")
    app.run_polling()

if __name__ == '__main__':
    main()
