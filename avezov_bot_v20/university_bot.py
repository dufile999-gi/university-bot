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
# ⚙️  WEB SERVER (Render/Railway uchun)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')

    def log_message(self, format, *args):
        pass  # Web server loglarini o'chirish

threading.Thread(
    target=lambda: HTTPServer(('0.0.0.0', 8080), Handler).serve_forever(),
    daemon=True
).start()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️  SOZLAMALAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Su1tonov0"
ADMIN_PHONE = "+998996454671"
DB_PATH = "universitet.db"
UNI_PHOTO_URL = "https://storage.googleapis.com/createsite-uz-bucket/blog/1722071060_chirchiq-auezov.jpg"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔑  KONVERSIYA HOLATLARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
TIL_TANLASH = "til_tanlash"
TANLA = "tanla"
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = "hf1", "hf2", "hf3", "hf4"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "h1", "h2", "h3", "h4"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON, YONALISH_TANLASH = "yi", "yf", "yy", "yt", "yonalish_tanlash"
MAG_ISM, MAG_FAMILYA, MAG_YOSH, MAG_TELEFON, MAG_TANLASH = "mi", "mf", "my", "mt", "mag_tanlash"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL LUG'ATI (UZ, RU, KK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANG_TEXTS = {
    'uz': {
        'welcome': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!",
        'lang_selected': "✅ *O'zbek tili* tanlandi!",
        'menu_about': "🏛 Universitet haqida",
        'menu_bakalavr': "🎓 Bakalavriat",
        'menu_magistratura': "📚 Magistratura",
        'menu_hujjat': "📝 Hujjat topshirish",
        'menu_manzil': "📍 Manzil",
        'menu_bakalavr_tanlash': "📋 Bakalavriat yo'nalishlari",
        'menu_magistratura_tanlash': "🎓 Magistratura yo'nalishlari",
        'menu_contact': "📞 Aloqa",
        'back': "🔙 Orqaga",
        'cancel': "❌ Bekor qilish",
        'change_lang': "🌐 Tilni o'zgartirish",
        'about_title': "🏛 *M.AUEZOV NOMIDAGI JANUBIY QOZOG'ISTON UNIVERSITETI*",
        'about_text': "📌 *1943 yilda tashkil etilgan*\n\n🇰🇿 Qozog'istonning eng yirik universitetlaridan biri\n\n📚 50+ ta yo'nalish\n👨‍🎓 15 000+ talaba\n🏛 12 ta fakultet\n🌍 Xalqaro hamkorlik: Erasmus+, dual diplom\n\n🔗 *Batafsil ma'lumot:*\n[🌐 Oliygoh.uz](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *BAKALAVRIAT YO'NALISHLARI* (11 ta)\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm\n⚖️ Yurisprudensiya\n\n📚 *O'qish muddati:* 4 yil",
        'magistratura_text': "🎓 *MAGISTRATURA YO'NALISHLARI* (5 ta)\n\n📊 Iqtisodiyot\n⚖️ Yurisprudensiya\n💻 Axborot tizimlari\n🌍 Ekologiya\n📈 Menejment\n\n📚 *O'qish muddati:* 2 yil",
        'hujjat_intro': "📋 *KERAKLI HUJJATLAR RO'YXATI*\n\n1️⃣ Diplom/Attestat\n2️⃣ Pasport nusxasi\n3️⃣ 0.86 Med-ma'lumotnoma\n4️⃣ 3x4 rasm (6 dona)\n\n▸ *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm",
        'format_fayl': "📎 Fayl",
        'enter_name': "✍️ *Ismingizni kiriting:*",
        'enter_surname': "✍️ *Familiyangizni kiriting:*",
        'enter_age': "✍️ *Yoshingizni kiriting:*",
        'invalid_age_bak': "⚠️ Xato! Bakalavriat uchun yosh 14 dan 60 gacha bo'lishi kerak.",
        'invalid_age_mag': "⚠️ Xato! Magistratura uchun yosh 21 dan 65 gacha bo'lishi kerak.",
        'send_phone': "📞 Telefon raqam",
        'phone_intro': "📞 *Telefon raqamingizni kiriting:*\n📝 *Namuna:* `+998901234567`",
        'invalid_phone': "⚠️ Xato! +998901234567 formatida yozing",
        'success_received': "✅ Qabul qilindi!",
        'all_docs_success': "🎉 *BARCHA HUJJATLAR TOPSHIRILDI!*\n\n👨‍💼 Admin tez orada siz bilan bog'lanadi.\n\n⭐ Botimizdan foydalanganingiz uchun rahmat!",
        'select_bakalavr_title': "🎓 *BAKALAVRIAT YO'NALISHLARIDAN BIRINI TANLANG:*",
        'select_magistratura_title': "🎓 *MAGISTRATURA YO'NALISHLARIDAN BIRINI TANLANG:*",
        'reg_success': "🎉 *Yo'nalish muvaffaqiyatli tanlandi!*\n\n✅ Ma'lumotlaringiz qabul qilindi.\n📝 Endi hujjat topshirishingiz mumkin.",
        'already_registered_bak': "✨ Siz allaqachon bakalavriat yo'nalishini tanlagansiz!",
        'already_registered_mag': "✨ Siz allaqachon magistratura yo'nalishini tanlagansiz!",
        'reg_cancelled': "❌ Jarayon bekor qilindi.",
        'unknown': "❓ Tushunarsiz buyruq. Iltimos menyudan tanlang.",
        'error_need_file': "⚠️ Fayl formatida yuboring! (PDF, DOC, TXT va boshqalar)",
        'error_need_photo': "⚠️ Rasm formatida yuboring! (JPEG, PNG va boshqalar)",
        'warning_in_progress': "⚠️ Siz hozir jarayon ichdasiz!\n\nIltimos so'ralgan ma'lumotni kiriting yoki:\n❌ *Bekor qilish* tugmasini bosing.",
        'channel_caption': "📋 *YANGI HUJJAT!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *BAKALAVRIAT TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n📚 Yo'nalish: *{yonalish}*\n👤 Ism: {ism}\n👤 Familiya: {familya}\n🎂 Yosh: {yosh}",
        'magistratura_channel_caption': "📚 *MAGISTRATURA TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n🎓 Magistratura: *{yonalish}*\n👤 Ism: {ism}\n👤 Familiya: {familya}\n🎂 Yosh: {yosh}",
        'manzil_text': "📍 *UNIVERSITET MANZILI*\n\n🏛 M.Auezov nomidagi Janubiy Qozog'iston universiteti\n🇺🇿 Chirchiq filiali\n🏙 Toshkent viloyati, Chirchiq shahri\n\n🗺 [Google Maps da ko'rish](https://maps.google.com)",
        'contact_text': "📞 *BIZ BILAN BOG'LANISH*\n\n📞 Telefon: {phone}\n💬 Telegram: {username}",
        'channel_error': "⚠️ Kanalga yuborishda xatolik. Admin bilan bog'laning: {username}",
    },
    'ru': {
        'welcome': "🏛 *Южно-Казахстанский университет им. М.Ауезова* Добро пожаловать в официального бота приёмной комиссии Чирчикского филиала!",
        'lang_selected': "✅ *Русский язык выбран*!",
        'menu_about': "🏛 Об университете",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Подать документы",
        'menu_manzil': "📍 Адрес",
        'menu_bakalavr_tanlash': "📋 Направления бакалавриата",
        'menu_magistratura_tanlash': "🎓 Направления магистратуры",
        'menu_contact': "📞 Контакты",
        'back': "🔙 Назад",
        'cancel': "❌ Отмена",
        'change_lang': "🌐 Сменить язык",
        'about_title': "🏛 *ЮЖНО-КАЗАХСТАНСКИЙ УНИВЕРСИТЕТ ИМ. М.АУЕЗОВА*",
        'about_text': "📌 *Основан в 1943 году*\n\n🇰🇿 Один из крупнейших вузов Казахстана\n\n📚 50+ направлений\n👨‍🎓 15 000+ студентов\n🏛 12 факультетов\n🌍 Международное сотрудничество: Erasmus+, двойные дипломы\n\n🔗 *Подробнее:*\n[🌐 Oliygoh.uz](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *НАПРАВЛЕНИЯ БАКАЛАВРИАТА* (11)\n\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Транспорт\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект\n💼 Учет и аудит\n✈️ Туризм\n⚖️ Юриспруденция\n\n📚 *Срок обучения:* 4 года",
        'magistratura_text': "🎓 *НАПРАВЛЕНИЯ МАГИСТРАТУРЫ* (5)\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Информационные системы\n🌍 Экология\n📈 Менеджмент\n\n📚 *Срок обучения:* 2 года",
        'hujjat_intro': "📋 *СПИСОК ДОКУМЕНТОВ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Копия паспорта\n3️⃣ Мед-справка 0.86\n4️⃣ Фото 3x4 (6 шт)\n\n▸ *1-этап: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ Изображение",
        'format_fayl': "📎 Файл",
        'enter_name': "✍️ *Введите имя:*",
        'enter_surname': "✍️ *Введите фамилию:*",
        'enter_age': "✍️ *Введите возраст:*",
        'invalid_age_bak': "⚠️ Ошибка! Для бакалавриата возраст должен быть от 14 до 60 лет.",
        'invalid_age_mag': "⚠️ Ошибка! Для магистратуры возраст должен быть от 21 до 65 лет.",
        'send_phone': "📞 Номер телефона",
        'phone_intro': "📞 *Введите номер телефона:*\n📝 *Пример:* `+998901234567`",
        'invalid_phone': "⚠️ Ошибка! Формат: +998901234567",
        'success_received': "✅ Принято!",
        'all_docs_success': "🎉 *ВСЕ ДОКУМЕНТЫ ПОДАНЫ!*\n\n👨‍💼 Администратор свяжется с вами.\n\n⭐ Спасибо за использование бота!",
        'select_bakalavr_title': "🎓 *ВЫБЕРИТЕ НАПРАВЛЕНИЕ БАКАЛАВРИАТА:*",
        'select_magistratura_title': "🎓 *ВЫБЕРИТЕ НАПРАВЛЕНИЕ МАГИСТРАТУРЫ:*",
        'reg_success': "🎉 *Направление успешно выбрано!*\n\n✅ Ваши данные приняты.\n📝 Теперь можете подать документы.",
        'already_registered_bak': "✨ Вы уже выбрали направление бакалавриата!",
        'already_registered_mag': "✨ Вы уже выбрали направление магистратуры!",
        'reg_cancelled': "❌ Процесс отменен.",
        'unknown': "❓ Неизвестная команда. Пожалуйста, выберите из меню.",
        'error_need_file': "⚠️ Отправьте файл! (PDF, DOC, TXT и другие)",
        'error_need_photo': "⚠️ Отправьте фото! (JPEG, PNG и другие)",
        'warning_in_progress': "⚠️ Вы в процессе заполнения!\n\nВведите запрашиваемую информацию или:\n❌ Нажмите *Отмена* для выхода.",
        'channel_caption': "📋 *НОВЫЙ ДОКУМЕНТ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📂 Документ: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *ВЫБРАН БАКАЛАВРИАТ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n📚 Направление: *{yonalish}*\n👤 Имя: {ism}\n👤 Фамилия: {familya}\n🎂 Возраст: {yosh}",
        'magistratura_channel_caption': "📚 *ВЫБРАНА МАГИСТРАТУРА!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n🎓 Магистратура: *{yonalish}*\n👤 Имя: {ism}\n👤 Фамилия: {familya}\n🎂 Возраст: {yosh}",
        'manzil_text': "📍 *АДРЕС УНИВЕРСИТЕТА*\n\n🏛 Южно-Казахстанский университет им. М.Ауезова\n🇺🇿 Чирчикский филиал\n🏙 Ташкентская область, г.Чирчик\n\n🗺 [Google Maps](https://maps.google.com)",
        'contact_text': "📞 *КОНТАКТЫ*\n\n📞 Телефон: {phone}\n💬 Telegram: {username}",
        'channel_error': "⚠️ Ошибка отправки в канал. Свяжитесь с администратором: {username}",
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы ОҚУ* Шыршық филиалының ресми қабылдау ботына қош келдіңіз!",
        'lang_selected': "✅ *Қазақ тілі таңдалды*!",
        'menu_about': "🏛 Университет туралы",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Құжат тапсыру",
        'menu_manzil': "📍 Мекенжай",
        'menu_bakalavr_tanlash': "📋 Бакалавриат бағыттары",
        'menu_magistratura_tanlash': "🎓 Магистратура бағыттары",
        'menu_contact': "📞 Байланыс",
        'back': "🔙 Артқа",
        'cancel': "❌ Болдырмау",
        'change_lang': "🌐 Тілді өзгерту",
        'about_title': "🏛 *М.ӘУЕЗОВ АТЫНДАҒЫ ОҚУ*",
        'about_text': "📌 *1943 жылы құрылған*\n\n🇰🇿 Қазақстанның ірі университеттерінің бірі\n\n📚 50+ бағыт\n👨‍🎓 15 000+ студент\n🏛 12 факультет\n🌍 Халықаралық ынтымақтастық: Erasmus+, қос диплом\n\n🔗 *Толығырақ:*\n[🌐 Oliygoh.uz](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *БАКАЛАВРИАТ БАҒЫТТАРЫ* (11)\n\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматтандыру\n🚚 Көлік\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм\n⚖️ Юриспруденция\n\n📚 *Оқу мерзімі:* 4 жыл",
        'magistratura_text': "🎓 *МАГИСТРАТУРА БАҒЫТТАРЫ* (5)\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Ақпараттық жүйелер\n🌍 Экология\n📈 Менеджмент\n\n📚 *Оқу мерзімі:* 2 жыл",
        'hujjat_intro': "📋 *ҚҰЖАТТАР ТІЗІМІ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт көшірмесі\n3️⃣ 0.86 Мед-анықтама\n4️⃣ 3x4 сурет (6 дана)\n\n▸ *1-кезең: Диплом/Аттестат*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет",
        'format_fayl': "📎 Файл",
        'enter_name': "✍️ *Атыңызды жазыңыз:*",
        'enter_surname': "✍️ *Тегіңізді жазыңыз:*",
        'enter_age': "✍️ *Жасыңызды жазыңыз:*",
        'invalid_age_bak': "⚠️ Қате! Бакалавриат үшін жас 14-тен 60-қа дейін болуы керек.",
        'invalid_age_mag': "⚠️ Қате! Магистратура үшін жас 21-ден 65-ке дейін болуы керек.",
        'send_phone': "📞 Телефон нөмірі",
        'phone_intro': "📞 *Телефон нөміріңізді жазыңыз:*\n📝 *Мысалы:* `+998901234567`",
        'invalid_phone': "⚠️ Қате! +998901234567 форматында жазыңыз",
        'success_received': "✅ Қабылданды!",
        'all_docs_success': "🎉 *БАРЛЫҚ ҚҰЖАТТАР ТАПСЫРЫЛДЫ!*\n\n👨‍💼 Әкімші жақын арада хабарласады.\n\n⭐ Ботты қолданғаныңызға рахмет!",
        'select_bakalavr_title': "🎓 *БАКАЛАВРИАТ БАҒЫТТАРЫН ТАҢДАҢЫЗ:*",
        'select_magistratura_title': "🎓 *МАГИСТРАТУРА БАҒЫТТАРЫН ТАҢДАҢЫЗ:*",
        'reg_success': "🎉 *Бағыт сәтті таңдалды!*\n\n✅ Деректеріңіз қабылданды.\n📝 Енді құжат тапсыра аласыз.",
        'already_registered_bak': "✨ Сіз бакалавриат бағытын таңдап қойдыңыз!",
        'already_registered_mag': "✨ Сіз магистратура бағытын таңдап қойдыңыз!",
        'reg_cancelled': "❌ Процесс болдырылды.",
        'unknown': "❓ Белгісіз команда. Мәзірден таңдаңыз.",
        'error_need_file': "⚠️ Файл жіберіңіз! (PDF, DOC, TXT және басқалар)",
        'error_need_photo': "⚠️ Сурет жіберіңіз! (JPEG, PNG және басқалар)",
        'warning_in_progress': "⚠️ Сіз процесте жүрсіз!\n\nСұралған ақпаратты енгізіңіз немесе:\n❌ *Болдырмау* батырмасын басыңыз.",
        'channel_caption': "📋 *ЖАҢА ҚҰЖАТ!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📂 Құжат: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *БАКАЛАВРИАТ ТАҢДАЛДЫ!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n📚 Бағыт: *{yonalish}*\n👤 Аты: {ism}\n👤 Тегі: {familya}\n🎂 Жасы: {yosh}",
        'magistratura_channel_caption': "📚 *МАГИСТРАТУРА ТАҢДАЛДЫ!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n🎓 Магистратура: *{yonalish}*\n👤 Аты: {ism}\n👤 Тегі: {familya}\n🎂 Жасы: {yosh}",
        'manzil_text': "📍 *УНИВЕРСИТЕТ МЕКЕНЖАЙЫ*\n\n🏛 М.Әуезов атындағы ОҚУ\n🇺🇿 Шыршық филиалы\n🏙 Ташкент облысы, Шыршық қаласы\n\n🗺 [Google Maps](https://maps.google.com)",
        'contact_text': "📞 *БАЙЛАНЫС*\n\n📞 Телефон: {phone}\n💬 Telegram: {username}",
        'channel_error': "⚠️ Каналға жіберу қатесі. Әкімшімен хабарласыңыз: {username}",
    }
}

HUJJAT_NOMLAR = {
    'uz': {1: "📗 Diplom / Attestat", 2: "🪪 Pasport", 3: "📋 Med-ma'lumotnoma", 4: "📸 3×4 rasm"},
    'ru': {1: "📗 Диплом / Аттестат", 2: "🪪 Паспорт", 3: "📋 Мед-справка", 4: "📸 Фото 3×4"},
    'kk': {1: "📗 Диплом / Аттестат", 2: "🪪 Паспорт", 3: "📋 Мед-анықтама", 4: "📸 3×4 сурет"}
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

# Bakalavriat yo'nalishlari (11 ta)
BAKALAVR_YONALISHLAR = {
    'uz': {
        "Biotexnologiya": "🔬 Biotexnologiya", "Ekologiya": "🌍 Ekologiya",
        "Axborot_tizimlar": "💻 Axborot tizimlar", "Avtomatizatsiya": "⚙️ Avtomatizatsiya",
        "Transport": "🚚 Transport", "Elektroenergetika": "⚡ Elektroenergetika",
        "Pedagogika": "🧑‍🏫 Pedagogika", "Suniy_intellekt": "🧠 Sun'iy intellekt",
        "Hisob_audit": "💼 Hisob va audit", "Turizm": "✈️ Turizm",
        "Yurisprudensiya": "⚖️ Yurisprudensiya"
    },
    'ru': {
        "Biotexnologiya": "🔬 Биотехнология", "Ekologiya": "🌍 Экология",
        "Axborot_tizimlar": "💻 Информационные системы", "Avtomatizatsiya": "⚙️ Автоматизация",
        "Transport": "🚚 Транспорт", "Elektroenergetika": "⚡ Электроэнергетика",
        "Pedagogika": "🧑‍🏫 Педагогика", "Suniy_intellekt": "🧠 Искусственный интеллект",
        "Hisob_audit": "💼 Учет и аудит", "Turizm": "✈️ Туризм",
        "Yurisprudensiya": "⚖️ Юриспруденция"
    },
    'kk': {
        "Biotexnologiya": "🔬 Биотехнология", "Ekologiya": "🌍 Экология",
        "Axborot_tizimlar": "💻 Ақпараттық жүйелер", "Avtomatizatsiya": "⚙️ Автоматтандыру",
        "Transport": "🚚 Көлік", "Elektroenergetika": "⚡ Электроэнергетика",
        "Pedagogika": "🧑‍🏫 Педагогика", "Suniy_intellekt": "🧠 Жасанды интеллект",
        "Hisob_audit": "💼 Есеп және аудит", "Turizm": "✈️ Туризм",
        "Yurisprudensiya": "⚖️ Юриспруденция"
    }
}

# Magistratura yo'nalishlari (5 ta)
MAGISTRATURA_YONALISHLAR = {
    'uz': {
        "Iqtisodiyot": "📊 Iqtisodiyot",
        "Yurisprudensiya": "⚖️ Yurisprudensiya",
        "Axborot_tizimlari": "💻 Axborot tizimlari",
        "Ekologiya": "🌍 Ekologiya",
        "Menejment": "📈 Menejment"
    },
    'ru': {
        "Iqtisodiyot": "📊 Экономика",
        "Yurisprudensiya": "⚖️ Юриспруденция",
        "Axborot_tizimlari": "💻 Информационные системы",
        "Ekologiya": "🌍 Экология",
        "Menejment": "📈 Менеджмент"
    },
    'kk': {
        "Iqtisodiyot": "📊 Экономика",
        "Yurisprudensiya": "⚖️ Юриспруденция",
        "Axborot_tizimlari": "💻 Ақпараттық жүйелер",
        "Ekologiya": "🌍 Экология",
        "Menejment": "📈 Менеджмент"
    }
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗄️  MA'LUMOTLAR BAZASI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def db_connect():
    # check_same_thread=False — threading bilan ishlash uchun zarur
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    con = db_connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            user_name TEXT,
            lang TEXT DEFAULT 'uz',
            birinchi_vaqt TEXT
        );
        CREATE TABLE IF NOT EXISTS bakalavr_royxat (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            user_name TEXT,
            vaqt TEXT,
            ism TEXT,
            familya TEXT,
            yosh INTEGER,
            telefon TEXT,
            yonalish TEXT
        );
        CREATE TABLE IF NOT EXISTS magistratura_royxat (
            id INTEGER PRIMARY KEY,
            first_name TEXT,
            last_name TEXT,
            user_name TEXT,
            vaqt TEXT,
            ism TEXT,
            familya TEXT,
            yosh INTEGER,
            telefon TEXT,
            yonalish TEXT
        );
        CREATE TABLE IF NOT EXISTS hujjat_status (
            user_id INTEGER PRIMARY KEY,
            doc1 INTEGER DEFAULT 0,
            doc2 INTEGER DEFAULT 0,
            doc3 INTEGER DEFAULT 0,
            doc4 INTEGER DEFAULT 0,
            last_update TEXT
        );
    """)
    con.commit()
    con.close()
    logger.info("✅ Ma'lumotlar bazasi tayyor.")

def check_already_registered(user_id, table_name):
    """Foydalanuvchi allaqachon ro'yxatdan o'tganini tekshiradi."""
    con = db_connect()
    cur = con.cursor()
    cur.execute(f"SELECT id FROM {table_name} WHERE id=?", (user_id,))
    res = cur.fetchone()
    con.close()
    return bool(res)

def get_user_lang(user_id):
    """Foydalanuvchi tilini DB dan oladi."""
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT lang FROM foydalanuvchilar WHERE id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    return row[0] if row and row[0] else 'uz'

def set_user_lang(user_id, lang):
    """Foydalanuvchi tilini DB ga saqlaydi."""
    con = db_connect()
    cur = con.cursor()
    cur.execute("UPDATE foydalanuvchilar SET lang=? WHERE id=?", (lang, user_id))
    con.commit()
    con.close()

def update_hujjat_status(user_id, doc_num):
    """Hujjat yuborilganini belgilaydi."""
    now = str(datetime.datetime.now())
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR IGNORE INTO hujjat_status (user_id, doc1, doc2, doc3, doc4, last_update) VALUES (?,0,0,0,0,?)",
        (user_id, now)
    )
    cur.execute(
        f"UPDATE hujjat_status SET doc{doc_num}=1, last_update=? WHERE user_id=?",
        (now, user_id)
    )
    con.commit()
    con.close()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎛️  KLAVIATURALAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main_menu_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([
        [t['menu_about']],
        [t['menu_bakalavr'], t['menu_magistratura']],
        [t['menu_hujjat'], t['menu_manzil']],
        [t['menu_bakalavr_tanlash'], t['menu_magistratura_tanlash']],
        [t['menu_contact']],
        [t['change_lang']],
    ], resize_keyboard=True)

def cancel_back_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([[t['back'], t['cancel']]], resize_keyboard=True)

def format_tanlash_keyboard(lang, step_num):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton(t['format_rasm'], callback_data=f"format_rasm_{step_num}"),
            InlineKeyboardButton(t['format_fayl'], callback_data=f"format_fayl_{step_num}")
        ]
    ])

def bakalavr_keyboard(lang):
    keyboard = []
    yonalishlar = list(BAKALAVR_YONALISHLAR[lang].items())
    for i in range(0, len(yonalishlar), 2):
        row = [InlineKeyboardButton(yonalishlar[i][1], callback_data=f"bak_{yonalishlar[i][0]}")]
        if i + 1 < len(yonalishlar):
            row.append(InlineKeyboardButton(yonalishlar[i+1][1], callback_data=f"bak_{yonalishlar[i+1][0]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def magistratura_keyboard(lang):
    keyboard = []
    yonalishlar = list(MAGISTRATURA_YONALISHLAR[lang].items())
    for i in range(0, len(yonalishlar), 2):
        row = [InlineKeyboardButton(yonalishlar[i][1], callback_data=f"mag_{yonalishlar[i][0]}")]
        if i + 1 < len(yonalishlar):
            row.append(InlineKeyboardButton(yonalishlar[i+1][1], callback_data=f"mag_{yonalishlar[i+1][0]}"))
        keyboard.append(row)
    return InlineKeyboardMarkup(keyboard)

def lang_tanlash_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbek tili", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский язык", callback_data="lang_ru")],
        [InlineKeyboardButton("🇰🇿 Қазақ тілі", callback_data="lang_kk")],
    ])

def is_any_menu_button(text, lang):
    """Matn asosiy menyu tugmalaridan biri ekanini tekshiradi."""
    if not text:
        return False
    t = LANG_TEXTS[lang]
    menu_buttons = [
        t['menu_about'], t['menu_bakalavr'], t['menu_magistratura'],
        t['menu_hujjat'], t['menu_manzil'], t['menu_bakalavr_tanlash'],
        t['menu_magistratura_tanlash'], t['menu_contact'], t['change_lang']
    ]
    return text in menu_buttons

def is_cancel_or_back(text, lang):
    """Matn bekor qilish yoki orqaga tugmasi ekanini tekshiradi."""
    if not text:
        return False
    t = LANG_TEXTS[lang]
    return text in [t['cancel'], t['back']]

def validate_phone(phone):
    """Telefon raqamni tekshiradi va tozalaydi."""
    clean = re.sub(r'[\s\-()]+', '', phone)
    # O'zbekiston raqamlari uchun: +998XXXXXXXXX
    if re.match(r'^\+998\d{9}$', clean):
        return clean
    # Umumiy xalqaro format
    if re.match(r'^\+?[1-9]\d{6,14}$', clean):
        return clean
    return None

def get_username_link(user):
    """Telegram username yoki mention link qaytaradi."""
    if user.username:
        return f"@{user.username}"
    return f"[{user.first_name}](tg://user?id={user.id})"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛡️  GUARD — Jarayon paytida boshqa tugma bosishni oldini oladi
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def process_step_guard(update, context, current_state):
    """
    Qaytaradi:
      "FORCE_CAN_MENU" — bekor qilingan, menyuga qaytish
      "FORCE_STAY"     — jarayonda, shu holatda qolish
      "PROCEED"        — davom etish
    """
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    msg = update.message.text if update.message else None

    if msg:
        if is_cancel_or_back(msg, lang):
            await update.message.reply_text(
                t['reg_cancelled'],
                reply_markup=main_menu_markup(lang)
            )
            return "FORCE_CAN_MENU"
        if is_any_menu_button(msg, lang):
            await update.message.reply_text(
                t['warning_in_progress'],
                parse_mode="Markdown",
                reply_markup=cancel_back_markup(lang)
            )
            return "FORCE_STAY"
    return "PROCEED"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📨  KANALGA XABAR YUBORISH YORDAMCHI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def send_to_channel(context, text=None, document=None, photo=None, caption=None):
    """
    Kanalga xabar, fayl yoki rasm yuboradi.
    Xatolik bo'lsa False qaytaradi.
    """
    try:
        if document:
            await context.bot.send_document(CHANNEL_USERNAME, document, caption=caption, parse_mode="Markdown")
        elif photo:
            await context.bot.send_photo(CHANNEL_USERNAME, photo, caption=caption, parse_mode="Markdown")
        elif text:
            await context.bot.send_message(CHANNEL_USERNAME, text, parse_mode="Markdown")
        return True
    except Exception as e:
        logger.error(f"Kanalga yuborish xatosi: {e}")
        return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀  START
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update, context):
    user = update.effective_user

    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT id, lang FROM foydalanuvchilar WHERE id=?", (user.id,))
    row = cur.fetchone()
    if not row:
        cur.execute(
            "INSERT INTO foydalanuvchilar VALUES (?,?,?,?,?,?)",
            (user.id, user.first_name, user.last_name, user.username, 'uz', str(datetime.datetime.now()))
        )
        lang = 'uz'
        logger.info(f"Yangi foydalanuvchi: {user.id} | @{user.username}")
    else:
        lang = row[1] if row[1] else 'uz'
    con.commit()
    con.close()

    context.user_data.clear()  # Eski ma'lumotlarni tozalash
    context.user_data['lang'] = lang

    await update.message.reply_text(
        LANG_TEXTS[lang]['welcome'],
        parse_mode="Markdown",
        reply_markup=lang_tanlash_keyboard()
    )
    return TIL_TANLASH

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL TANLASH CALLBACK
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def lang_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("lang_"):
        lang = data.split("_")[1]
        if lang not in LANG_TEXTS:
            return TIL_TANLASH
        set_user_lang(query.from_user.id, lang)
        context.user_data['lang'] = lang
        await query.edit_message_text(LANG_TEXTS[lang]['lang_selected'], parse_mode="Markdown")
        await query.message.reply_text(
            LANG_TEXTS[lang]['welcome'],
            parse_mode="Markdown",
            reply_markup=main_menu_markup(lang)
        )
        return TANLA
    return TIL_TANLASH

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  BOSH MENYU DISPATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def main_menu_dispatcher(update, context):
    msg = update.message.text
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]

    # Tilni o'zgartirish
    if msg == t['change_lang']:
        await update.message.reply_text(
            "🌐 Tilni tanlang / Выберите язык / Тілді таңдаңыз:",
            reply_markup=lang_tanlash_keyboard()
        )
        return TIL_TANLASH

    # Universitet haqida
    if msg == t['menu_about']:
        try:
            await update.message.reply_photo(
                photo=UNI_PHOTO_URL,
                caption=t['about_text'],
                parse_mode="Markdown"
            )
        except Exception:
            await update.message.reply_text(t['about_text'], parse_mode="Markdown")
        return TANLA

    # Bakalavriat ma'lumoti
    if msg == t['menu_bakalavr']:
        await update.message.reply_text(t['bakalavr_text'], parse_mode="Markdown")
        return TANLA

    # Magistratura ma'lumoti
    if msg == t['menu_magistratura']:
        await update.message.reply_text(t['magistratura_text'], parse_mode="Markdown")
        return TANLA

    # Hujjat topshirish
    if msg == t['menu_hujjat']:
        await update.message.reply_text(
            t['hujjat_intro'],
            parse_mode="Markdown",
            reply_markup=format_tanlash_keyboard(lang, 1)
        )
        return HUJJAT_FORMAT_1

    # Manzil
    if msg == t['menu_manzil']:
        await update.message.reply_text(t['manzil_text'], parse_mode="Markdown")
        return TANLA

    # Bakalavriat yo'nalishini tanlash
    if msg == t['menu_bakalavr_tanlash']:
        if check_already_registered(user_id, "bakalavr_royxat"):
            await update.message.reply_text(t['already_registered_bak'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(
            t['enter_name'],
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return YONALISH_ISM

    # Magistratura yo'nalishini tanlash
    if msg == t['menu_magistratura_tanlash']:
        if check_already_registered(user_id, "magistratura_royxat"):
            await update.message.reply_text(t['already_registered_mag'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(
            t['enter_name'],
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return MAG_ISM

    # Aloqa
    if msg == t['menu_contact']:
        text = t['contact_text'].format(phone=ADMIN_PHONE, username=ADMIN_USERNAME)
        await update.message.reply_text(text, parse_mode="Markdown")
        return TANLA

    # Noma'lum buyruq
    await update.message.reply_text(t['unknown'], reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📤  HUJJAT TOPSHIRISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def format_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_user_lang(query.from_user.id)

    # format_rasm_1 yoki format_fayl_2 shaklida keladi
    parts = data.split("_")  # ["format", "rasm"|"fayl", "1"]
    if len(parts) < 3:
        return TANLA

    format_turi = parts[1]   # "rasm" yoki "fayl"
    step = int(parts[2])

    context.user_data[f'hujjat_format_{step}'] = format_turi
    doc_name = HUJJAT_NOMLAR[lang][step]

    await query.message.reply_text(
        f"📥 *{doc_name}*\n"
        f"📎 Format: *{format_turi.upper()}*\n\n"
        f"👇 Iltimos yuklang:",
        parse_mode="Markdown",
        reply_markup=cancel_back_markup(lang)
    )
    return HUJJAT_STATES[step]

async def hujjat_handler(update, context, step):
    """Barcha hujjat steplari uchun umumiy handler."""
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]

    # Matn kelgan bo'lsa guard tekshiruvi (cancel/back/menu)
    if update.message and update.message.text:
        guard = await process_step_guard(update, context, HUJJAT_STATES[step])
        if guard == "FORCE_CAN_MENU":
            return TANLA
        if guard == "FORCE_STAY":
            return HUJJAT_STATES[step]

    fmt = context.user_data.get(f'hujjat_format_{step}', 'rasm')

    # Format tekshiruvi
    if fmt == 'fayl' and not update.message.document:
        await update.message.reply_text(t['error_need_file'], parse_mode="Markdown")
        return HUJJAT_STATES[step]

    if fmt == 'rasm' and not update.message.photo:
        await update.message.reply_text(t['error_need_photo'], parse_mode="Markdown")
        return HUJJAT_STATES[step]

    user = update.message.from_user
    username = get_username_link(user)
    caption = t['channel_caption'].format(
        user=username, uid=user.id, doc_name=HUJJAT_NOMLAR[lang][step]
    )

    # Kanalga yuborish
    ok = False
    if update.message.document:
        ok = await send_to_channel(context, document=update.message.document.file_id, caption=caption)
    elif update.message.photo:
        ok = await send_to_channel(context, photo=update.message.photo[-1].file_id, caption=caption)

    if not ok:
        await update.message.reply_text(
            t['channel_error'].format(username=ADMIN_USERNAME),
            parse_mode="Markdown"
        )
        # Xatolik bo'lsa ham davom ettiramiz, foydalanuvchi jarayonini to'xtatmaymiz

    update_hujjat_status(user_id, step)

    # Keyingi bosqich
    if step < 4:
        ns = step + 1
        await update.message.reply_text(
            f"{t['success_received']}\n\n"
            f"🟢 *{ns}-Bosqich: {HUJJAT_NOMLAR[lang][ns]}*\n"
            f"❓ Format tanlang:",
            parse_mode="Markdown",
            reply_markup=format_tanlash_keyboard(lang, ns)
        )
        return HUJJAT_FORMAT_STATES[ns]
    else:
        await update.message.reply_text(
            t['all_docs_success'],
            parse_mode="Markdown",
            reply_markup=main_menu_markup(lang)
        )
        return TANLA

async def hujjat_1(update, context): return await hujjat_handler(update, context, 1)
async def hujjat_2(update, context): return await hujjat_handler(update, context, 2)
async def hujjat_3(update, context): return await hujjat_handler(update, context, 3)
async def hujjat_4(update, context): return await hujjat_handler(update, context, 4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  BAKALAVRIAT TANLASH — Ma'lumot yig'ish
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_ISM
    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_surname'],
        parse_mode="Markdown",
        reply_markup=cancel_back_markup(lang)
    )
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_FAMILYA
    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_age'],
        parse_mode="Markdown",
        reply_markup=cancel_back_markup(lang)
    )
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_YOSH
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            LANG_TEXTS[lang]['invalid_age_bak'],
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return YONALISH_YOSH
    context.user_data['yonalish_yosh'] = yosh
    t = LANG_TEXTS[lang]
    btn = [
        [KeyboardButton(t['send_phone'], request_contact=True)],
        [KeyboardButton(t['back']), KeyboardButton(t['cancel'])]
    ]
    await update.message.reply_text(
        t['phone_intro'],
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True)
    )
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_TELEFON

    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
        # + belgisi yo'q bo'lsa qo'shamiz
        if not phone.startswith('+'):
            phone = '+' + phone
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(
                LANG_TEXTS[lang]['invalid_phone'],
                parse_mode="Markdown",
                reply_markup=cancel_back_markup(lang)
            )
            return YONALISH_TELEFON

    context.user_data['yonalish_telefon'] = phone
    await update.message.reply_text(
        LANG_TEXTS[lang]['select_bakalavr_title'],
        parse_mode="Markdown",
        reply_markup=bakalavr_keyboard(lang)
    )
    return YONALISH_TANLASH

async def bakalavr_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if not data.startswith("bak_"):
        return TANLA

    key = data[4:]  # "bak_" ni olib tashlaymiz
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    if key not in BAKALAVR_YONALISHLAR[lang]:
        return TANLA

    yonalish = BAKALAVR_YONALISHLAR[lang][key]

    # DB ga saqlash
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO bakalavr_royxat VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            user_id, query.from_user.first_name, query.from_user.last_name,
            query.from_user.username, str(datetime.datetime.now()),
            context.user_data.get('yonalish_ism'),
            context.user_data.get('yonalish_familya'),
            context.user_data.get('yonalish_yosh'),
            context.user_data.get('yonalish_telefon'),
            yonalish
        )
    )
    con.commit()
    con.close()

    # Kanalga xabar
    username = get_username_link(query.from_user)
    caption = LANG_TEXTS[lang]['yonalish_channel_caption'].format(
        user=username, uid=user_id,
        phone=context.user_data.get('yonalish_telefon'),
        yonalish=yonalish,
        ism=context.user_data.get('yonalish_ism'),
        familya=context.user_data.get('yonalish_familya'),
        yosh=context.user_data.get('yonalish_yosh')
    )
    await send_to_channel(context, text=caption)

    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_menu_markup(lang))
    logger.info(f"Bakalavriat tanlandi: user={user_id}, yo'nalish={yonalish}")
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📚  MAGISTRATURA TANLASH — Ma'lumot yig'ish
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def magistratura_ism(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_ISM
    context.user_data['mag_ism'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_surname'],
        parse_mode="Markdown",
        reply_markup=cancel_back_markup(lang)
    )
    return MAG_FAMILYA

async def magistratura_familya(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_FAMILYA
    context.user_data['mag_familya'] = update.message.text.strip()
    await update.message.reply_text(
        LANG_TEXTS[lang]['enter_age'],
        parse_mode="Markdown",
        reply_markup=cancel_back_markup(lang)
    )
    return MAG_YOSH

async def magistratura_yosh(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_YOSH
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (21 <= int(yosh) <= 65):
        await update.message.reply_text(
            LANG_TEXTS[lang]['invalid_age_mag'],
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return MAG_YOSH
    context.user_data['mag_yosh'] = yosh
    t = LANG_TEXTS[lang]
    btn = [
        [KeyboardButton(t['send_phone'], request_contact=True)],
        [KeyboardButton(t['back']), KeyboardButton(t['cancel'])]
    ]
    await update.message.reply_text(
        t['phone_intro'],
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True)
    )
    return MAG_TELEFON

async def magistratura_telefon(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_TELEFON

    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
        if not phone.startswith('+'):
            phone = '+' + phone
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(
                LANG_TEXTS[lang]['invalid_phone'],
                parse_mode="Markdown",
                reply_markup=cancel_back_markup(lang)
            )
            return MAG_TELEFON

    context.user_data['mag_telefon'] = phone
    await update.message.reply_text(
        LANG_TEXTS[lang]['select_magistratura_title'],
        parse_mode="Markdown",
        reply_markup=magistratura_keyboard(lang)
    )
    return MAG_TANLASH

async def magistratura_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if not data.startswith("mag_"):
        return TANLA

    key = data[4:]  # "mag_" ni olib tashlaymiz
    user_id = query.from_user.id
    lang = get_user_lang(user_id)

    if key not in MAGISTRATURA_YONALISHLAR[lang]:
        return TANLA

    yonalish = MAGISTRATURA_YONALISHLAR[lang][key]

    # DB ga saqlash
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO magistratura_royxat VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            user_id, query.from_user.first_name, query.from_user.last_name,
            query.from_user.username, str(datetime.datetime.now()),
            context.user_data.get('mag_ism'),
            context.user_data.get('mag_familya'),
            context.user_data.get('mag_yosh'),
            context.user_data.get('mag_telefon'),
            yonalish
        )
    )
    con.commit()
    con.close()

    # Kanalga xabar
    username = get_username_link(query.from_user)
    caption = LANG_TEXTS[lang]['magistratura_channel_caption'].format(
        user=username, uid=user_id,
        phone=context.user_data.get('mag_telefon'),
        yonalish=yonalish,
        ism=context.user_data.get('mag_ism'),
        familya=context.user_data.get('mag_familya'),
        yosh=context.user_data.get('mag_yosh')
    )
    await send_to_channel(context, text=caption)

    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_menu_markup(lang))
    logger.info(f"Magistratura tanlandi: user={user_id}, yo'nalish={yonalish}")
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN topilmadi! .env faylni tekshiring.")
        return

    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            # Til tanlash
            TIL_TANLASH: [
                CallbackQueryHandler(lang_callback, pattern="^lang_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
            ],
            # Asosiy menyu
            TANLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher),
                # FIX: pattern bilan aniq ajratildi — ikki handler konflikt qilmaydi
                CallbackQueryHandler(bakalavr_callback, pattern="^bak_"),
                CallbackQueryHandler(magistratura_callback, pattern="^mag_"),
            ],
            # Hujjat format tanlash (har bir bosqich uchun)
            HUJJAT_FORMAT_1: [
                CallbackQueryHandler(format_callback, pattern="^format_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
            ],
            HUJJAT_FORMAT_2: [
                CallbackQueryHandler(format_callback, pattern="^format_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
            ],
            HUJJAT_FORMAT_3: [
                CallbackQueryHandler(format_callback, pattern="^format_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
            ],
            HUJJAT_FORMAT_4: [
                CallbackQueryHandler(format_callback, pattern="^format_"),
                MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
            ],
            # Hujjat qabul qilish (fayl yoki rasm)
            HUJJAT_1: [MessageHandler(filters.ALL, hujjat_1)],
            HUJJAT_2: [MessageHandler(filters.ALL, hujjat_2)],
            HUJJAT_3: [MessageHandler(filters.ALL, hujjat_3)],
            HUJJAT_4: [MessageHandler(filters.ALL, hujjat_4)],
            # Bakalavriat ro'yxatga olish
            YONALISH_ISM:     [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)],
            YONALISH_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)],
            YONALISH_YOSH:    [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)],
            YONALISH_TELEFON: [MessageHandler(filters.ALL, yonalish_telefon)],
            YONALISH_TANLASH: [CallbackQueryHandler(bakalavr_callback, pattern="^bak_")],
            # Magistratura ro'yxatga olish
            MAG_ISM:     [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_ism)],
            MAG_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_familya)],
            MAG_YOSH:    [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_yosh)],
            MAG_TELEFON: [MessageHandler(filters.ALL, magistratura_telefon)],
            MAG_TANLASH: [CallbackQueryHandler(magistratura_callback, pattern="^mag_")],
        },
        fallbacks=[
            CommandHandler('start', start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)
        ],
        allow_reentry=True
    )
    app.add_handler(conv)

    print("=" * 50)
    print("✅ QABUL BOTI ISHGA TUSHDI!")
    print("=" * 50)
    print(f"📞 Admin: {ADMIN_PHONE} | {ADMIN_USERNAME}")
    print(f"📨 Kanal: {CHANNEL_USERNAME}")
    print(f"🎓 Bakalavriat: 11 ta yo'nalish")
    print(f"📚 Magistratura: 5 ta yo'nalish")
    print("=" * 50)

    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
