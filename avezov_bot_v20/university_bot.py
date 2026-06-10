from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re
import os
import sqlite3
import datetime
import logging
import csv
import io
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
# ⚙️  WEB SERVER
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
# ⚙️  SOZLAMALAR
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

# Konversiya holatlari
TIL_TANLASH = "til_tanlash"
TANLA = "tanla"
# Bakalavriat
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = "hf1", "hf2", "hf3", "hf4"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "h1", "h2", "h3", "h4"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON, YONALISH_TANLASH = "yi", "yf", "yy", "yt", "yonalish_tanlash"
# Magistratura
MAG_ISM, MAG_FAMILYA, MAG_YOSH, MAG_TELEFON, MAG_TANLASH = "mi", "mf", "my", "mt", "mag_tanlash"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL LUG'ATI (UZ, RU, KK)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
LANG_TEXTS = {
    'uz': {
        'welcome': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!\n\n👇 _Davom etish uchun tilni tanlang:_",
        'lang_selected': "✅ *O'zbek tili* tanlandi!",
        'menu_about': "🏛 Universitet haqida",
        'menu_bakalavr': "🎓 Bakalavriat",
        'menu_magistratura': "📚 Magistratura",
        'menu_hujjat': "📝 Hujjat topshirish",
        'menu_manzil': "📍 Manzil",
        'menu_bakalavr_tanlash': "📋 Bakalavriat yo'nalishlari",
        'menu_magistratura_tanlash': "🎓 Magistratura yo'nalishlari",
        'menu_admin': "👤 Admin bilan bog'lanish",
        'back': "🔙 Orqaga",
        'cancel': "❌ Bekor qilish",
        'change_lang': "🌐 Tilni o'zgartirish",
        'about_text': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti Chirchiq filiali*\n\nChirchiq shahrida universitetning yangi zamonaviy filiali o'z ishini boshlamoqda!\n\n🔗 [Batafsil ma'lumot](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *BAKALAVRIAT YO'NALISHLARI*\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'magistratura_text': "🎓 *MAGISTRATURA YO'NALISHLARI*\n\n📊 Iqtisodiyot\n⚖️ Yurisprudensiya\n💻 Axborot tizimlari\n🌍 Ekologiya",
        'hujjat_intro': "📋 *KERAKLI HUJJATLAR RO'YXATI*\n\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ 0.86 Med-ma'lumotnoma\n4️⃣ 3x4 rasm (6 dona)\n\n🟢 *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm ko'rinishida",
        'format_fayl': "📎 Fayl ko'rinishida",
        'yonalish_allready': "✨ *Siz bakalavriat yo'nalishini tanlab bo'lgansiz!*",
        'magistratura_allready': "✨ *Siz magistratura yo'nalishini tanlab bo'lgansiz!*",
        'enter_name': "✍️ *Ismingizni kiriting:*",
        'enter_surname': "✍️ *Familiyangizni kiriting:*",
        'enter_age': "✍️ *Yoshingizni kiriting:*",
        'invalid_age': "⚠️ *Xatolik:* Noto'g'ri yosh! Bakalavriat: 14-60, Magistratura: 21-65",
        'send_phone': "📞 Telefon raqamni yuborish",
        'phone_intro': "📞 *Telefon raqamingizni kiriting:*\n\nPastdagi tugmani bosing yoki qo'lda yozing.\n📝 *Namuna:* `+998901234567`",
        'invalid_phone': "⚠️ *Xatolik:* Raqam formati noto'g'ri!",
        'success_received': "✅ Qabul qilindi!",
        'all_docs_success': "🎉 Barcha hujjatlar topshirildi! Tez orada bog'lanamiz.",
        'select_bakalavr_title': "🎓 *BAKALAVRIAT YO'NALISHLARIDAN BIRINI TANLANG:*",
        'select_magistratura_title': "🎓 *MAGISTRATURA YO'NALISHLARIDAN BIRINI TANLANG:*",
        'unknown': "❓ Noma'lum xabar.",
        'error_need_file': "⚠️ *Xatolik:* Fayl formatida yuboring!",
        'error_need_photo': "⚠️ *Xatolik:* Rasm formatida yuboring!",
        'channel_caption': "📋 *Yangi Hujjat!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *BAKALAVRIAT TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n📚 Yo'nalish: *{yonalish}*\n👤 Ism: {ism}\n👤 Fam: {familya}\n🎂 Yosh: {yosh}",
        'magistratura_channel_caption': "📚 *MAGISTRATURA TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n🎓 Magistratura: *{yonalish}*\n👤 Ism: {ism}\n👤 Fam: {familya}\n🎂 Yosh: {yosh}",
        'reg_cancelled': "❌ Jarayon bekor qilindi.",
        'reg_success': "🎉 Yo'nalish muvaffaqiyatli tanlandi!",
        'manzil_text': "📍 *Universitet manzili:* Chirchiq shahri, Toshkent viloyati.\n🗺 [Xarita](http://maps.google.com)",
        # Xatolik va yo'l ko'rsatish xabarlari
        'warning_in_progress': "⚠️ *Siz hozir ro'yxatdan o'tish jarayonidasiz!*\n\n📝 Sizdan so'ralgan ma'lumotni kiriting:\n{current_step}\n\n❌ Jarayonni to'xtatish uchun **Bekor qilish** tugmasini bosing.\n🔙 Menyuga qaytish uchun **Orqaga** tugmasini bosing.",
        'step_name': "✍️ Ismingiz",
        'step_surname': "✍️ Familiyangiz",
        'step_age': "🎂 Yoshingiz",
        'step_phone': "📞 Telefon raqamingiz",
        'step_format': "📎 Hujjat formati",
        'step_document': "📄 Hujjat fayli/rasmi",
        'wrong_input': "❌ *Xato ma'lumot kiritdingiz!*\n\n📝 Sizdan {expected} so'ralgan edi.\n\n✅ Iltimos, to'g'ri ma'lumot kiriting yoki ❌ Bekor qilish tugmasini bosing.",
        'menu_pressed': "ℹ️ *Siz ro'yxatdan o'tish jarayonidasiz!*\n\n{current_step} kiritishingiz kerak.\n\n🚫 Iltimos, menyu tugmalarini ishlatmang!",
        'help_text': "🤝 *Yordam*\n\nBotdan foydalanish tartibi:\n\n1. 📋 Bakalavriat yoki Magistratura yo'nalishini tanlang\n2. 📝 So'ralgan ma'lumotlarni to'g'ri kiriting\n3. 📎 Hujjatlarni rasm yoki fayl sifatida yuklang\n4. ✅ Jarayon tugagach, admin siz bilan bog'lanadi\n\n❌ Xato kiritgan bo'lsangiz, jarayonni bekor qilib qaytadan boshlang."
    },
    'ru': {
        'welcome': "🏛 *Южно-Казахстанский университет им. М.Ауезова* Добро пожаловать!\n\n👇 _Выберите язык:_",
        'lang_selected': "✅ *Русский язык выбран*!",
        'menu_about': "🏛 Об университете",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Подать документы",
        'menu_manzil': "📍 Адрес",
        'menu_bakalavr_tanlash': "📋 Направления бакалавриата",
        'menu_magistratura_tanlash': "🎓 Направления магистратуры",
        'menu_admin': "👤 Связаться с админом",
        'back': "🔙 Назад",
        'cancel': "❌ Отмена",
        'change_lang': "🌐 Сменить язык",
        'about_text': "🏛 *Южно-Казахстанский университет им. М.Ауезова Чирчикский филиал*\n\nВ городе Чирчик открывается новый современный филиал!\n\n🔗 [Подробнее](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *НАПРАВЛЕНИЯ БАКАЛАВРИАТА*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Транспорт\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект\n💼 Учет и аудит\n✈️ Туризм",
        'magistratura_text': "🎓 *НАПРАВЛЕНИЯ МАГИСТРАТУРЫ*\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Информационные системы\n🌍 Экология",
        'hujjat_intro': "📋 *СПИСОК ДОКУМЕНТОВ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ Мед-справка 0.86\n4️⃣ Фото 3x4 (6 шт)\n\n🟢 *1-этап: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ Изображение",
        'format_fayl': "📎 Файл",
        'yonalish_allready': "✨ *Вы уже выбрали направление бакалавриата!*",
        'magistratura_allready': "✨ *Вы уже выбрали направление магистратуры!*",
        'enter_name': "✍️ *Введите имя:*",
        'enter_surname': "✍️ *Введите фамилию:*",
        'enter_age': "✍️ *Введите возраст:*",
        'invalid_age': "⚠️ *Ошибка:* Бакалавриат: 14-60, Магистратура: 21-65",
        'send_phone': "📞 Отправить номер",
        'phone_intro': "📞 *Введите номер телефона:*\n📝 *Пример:* `+998901234567`",
        'invalid_phone': "⚠️ *Ошибка:* Неверный формат!",
        'success_received': "✅ Принято!",
        'all_docs_success': "🎉 Все документы поданы! Свяжемся с вами.",
        'select_bakalavr_title': "🎓 *ВЫБЕРИТЕ НАПРАВЛЕНИЕ БАКАЛАВРИАТА:*",
        'select_magistratura_title': "🎓 *ВЫБЕРИТЕ НАПРАВЛЕНИЕ МАГИСТРАТУРЫ:*",
        'unknown': "❓ Неизвестная команда.",
        'error_need_file': "⚠️ Отправьте файл!",
        'error_need_photo': "⚠️ Отправьте фото!",
        'channel_caption': "📋 *Новый документ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📂 Документ: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *ВЫБРАН БАКАЛАВРИАТ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n📚 Направление: *{yonalish}*\n👤 Имя: {ism}\n👤 Фам: {familya}\n🎂 Возраст: {yosh}",
        'magistratura_channel_caption': "📚 *ВЫБРАНА МАГИСТРАТУРА!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n🎓 Магистратура: *{yonalish}*\n👤 Имя: {ism}\n👤 Фам: {familya}\n🎂 Возраст: {yosh}",
        'reg_cancelled': "❌ Процесс отменен.",
        'reg_success': "🎉 Направление успешно выбрано!",
        'manzil_text': "📍 *Адрес:* г.Чирчик, Ташкентская область.\n🗺 [Карта](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Вы находитесь в процессе регистрации!*\n\n📝 Введите запрашиваемую информацию:\n{current_step}\n\n❌ Чтобы остановить процесс, нажмите **Отмена**\n🔙 Чтобы вернуться в меню, нажмите **Назад**",
        'step_name': "✍️ Ваше имя",
        'step_surname': "✍️ Ваша фамилия",
        'step_age': "🎂 Ваш возраст",
        'step_phone': "📞 Ваш номер телефона",
        'step_format': "📎 Формат документа",
        'step_document': "📄 Файл/Фото документа",
        'wrong_input': "❌ *Неверный ввод!*\n\n📝 Ожидалось: {expected}\n\n✅ Пожалуйста, введите правильные данные или нажмите ❌ Отмена.",
        'menu_pressed': "ℹ️ *Вы в процессе регистрации!*\n\nНеобходимо ввести: {current_step}\n\n🚫 Пожалуйста, не используйте кнопки меню!",
        'help_text': "🤝 *Помощь*\n\nКак пользоваться ботом:\n\n1. 📋 Выберите направление бакалавриата или магистратуры\n2. 📝 Введите запрашиваемые данные правильно\n3. 📎 Загрузите документы в виде фото или файла\n4. ✅ После завершения администратор свяжется с вами\n\n❌ Если ошиблись, отмените процесс и начните заново."
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы ОҚУ* Шыршық филиалына қош келдіңіз!\n\n👇 _Тілді таңдаңыз:_",
        'lang_selected': "✅ *Қазақ тілі таңдалды*!",
        'menu_about': "🏛 Университет туралы",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Құжат тапсыру",
        'menu_manzil': "📍 Мекенжай",
        'menu_bakalavr_tanlash': "📋 Бакалавриат бағыттары",
        'menu_magistratura_tanlash': "🎓 Магистратура бағыттары",
        'menu_admin': "👤 Әкімге жазу",
        'back': "🔙 Артқа",
        'cancel': "❌ Болдырмау",
        'change_lang': "🌐 Тілді өзгерту",
        'about_text': "🏛 *М.Әуезов атындағы ОҚУ Шыршық филиалы*\n\nШыршық қаласында заманауи филиал ашылды!\n\n🔗 [Толығырақ](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *БАКАЛАВРИАТ БАҒЫТТАРЫ*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматтандыру\n🚚 Көлік\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм",
        'magistratura_text': "🎓 *МАГИСТРАТУРА БАҒЫТТАРЫ*\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Ақпараттық жүйелер\n🌍 Экология",
        'hujjat_intro': "📋 *ҚҰЖАТТАР ТІЗІМІ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ 0.86 Мед-анықтама\n4️⃣ 3x4 сурет (6 дана)\n\n🟢 *1-кезең: Диплом/Аттестат*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет түрінде",
        'format_fayl': "📎 Файл түрінде",
        'yonalish_allready': "✨ *Бакалавриат бағыты таңдалған!*",
        'magistratura_allready': "✨ *Магистратура бағыты таңдалған!*",
        'enter_name': "✍️ *Атыңызды жазыңыз:*",
        'enter_surname': "✍️ *Тегіңізді жазыңыз:*",
        'enter_age': "✍️ *Жасыңызды жазыңыз:*",
        'invalid_age': "⚠️ *Қате:* Бакалавриат: 14-60, Магистратура: 21-65",
        'send_phone': "📞 Телефон жіберу",
        'phone_intro': "📞 *Телефон нөміріңізді жазыңыз:*\n📝 *Мысалы:* `+998901234567`",
        'invalid_phone': "⚠️ *Қате:* Нөмір дұрыс емес!",
        'success_received': "✅ Қабылданды!",
        'all_docs_success': "🎉 Барлық құжаттар тапсырылды!",
        'select_bakalavr_title': "🎓 *БАКАЛАВРИАТ БАҒЫТТАРЫН ТАҢДАҢЫЗ:*",
        'select_magistratura_title': "🎓 *МАГИСТРАТУРА БАҒЫТТАРЫН ТАҢДАҢЫЗ:*",
        'unknown': "❓ Белгісіз команда.",
        'error_need_file': "⚠️ Файл жіберіңіз!",
        'error_need_photo': "⚠️ Сурет жіберіңіз!",
        'channel_caption': "📋 *Жаңа Құжат!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📂 Құжат: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *БАКАЛАВРИАТ ТАҢДАЛДЫ!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n📚 Бағыт: *{yonalish}*\n👤 Аты: {ism}\n👤 Тегі: {familya}\n🎂 Жасы: {yosh}",
        'magistratura_channel_caption': "📚 *МАГИСТРАТУРА ТАҢДАЛДЫ!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n🎓 Магистратура: *{yonalish}*\n👤 Аты: {ism}\n👤 Тегі: {familya}\n🎂 Жасы: {yosh}",
        'reg_cancelled': "❌ Процесс болдырылды.",
        'reg_success': "🎉 Бағыт сәтті таңдалды!",
        'manzil_text': "📍 *Мекенжай:* Шыршық қ., Ташкент обл.\n🗺 [Карта](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Сіз тіркелу процесіндесіз!*\n\n📝 Сұралған ақпаратты енгізіңіз:\n{current_step}\n\n❌ Процесті тоқтату үшін **Болдырмау** басыңыз\n🔙 Мәзірге оралу үшін **Артқа** басыңыз",
        'step_name': "✍️ Атыңыз",
        'step_surname': "✍️ Тегіңіз",
        'step_age': "🎂 Жасыңыз",
        'step_phone': "📞 Телефон нөміріңіз",
        'step_format': "📎 Құжат форматы",
        'step_document': "📄 Құжат файлы/суреті",
        'wrong_input': "❌ *Қате енгізу!*\n\n📝 Күтілген: {expected}\n\n✅ Дұрыс деректерді енгізіңіз немесе ❌ Болдырмау басыңыз.",
        'menu_pressed': "ℹ️ *Сіз тіркелу процесіндесіз!*\n\nЕнгізу қажет: {current_step}\n\n🚫 Мәзір түймелерін пайдаланбаңыз!",
        'help_text': "🤝 *Көмек*\n\nБотты пайдалану тәртібі:\n\n1. 📋 Бакалавриат немесе Магистратура бағытын таңдаңыз\n2. 📝 Сұралған деректерді дұрыс енгізіңіз\n3. 📎 Құжаттарды сурет немесе файл ретінде жүктеңіз\n4. ✅ Процесс аяқталған соң, әкімші сізге хабарласады\n\n❌ Қате енгізсеңіз, процесті болдырмап, қайта бастаңыз."
    }
}

# Hujjat nomlari
HUJJAT_NOMLAR = {
    'uz': {1: "📗 Diplom / Attestat", 2: "🪪 Pasport", 3: "📋 Med-ma'lumotnoma", 4: "📸 3×4 rasm"},
    'ru': {1: "📗 Диплом / Аттестат", 2: "🪪 Паспорт", 3: "📋 Мед-справка", 4: "📸 Фото 3×4"},
    'kk': {1: "📗 Диплом / Аттестат", 2: "🪪 Паспорт", 3: "📋 Мед-анықтама", 4: "📸 3×4 сурет"}
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

# Bakalavriat yo'nalishlari (10 ta)
BAKALAVR_YONALISHLAR = {
    'uz': {
        "Biotexnologiya": "🔬 Biotexnologiya", "Ekologiya": "🌍 Ekologiya",
        "Axborot_tizimlar": "💻 Axborot tizimlar", "Avtomatizatsiya": "⚙️ Avtomatizatsiya",
        "Transport": "🚚 Transport", "Elektroenergetika": "⚡ Elektroenergetika",
        "Pedagogika": "🧑‍🏫 Pedagogika", "Suniy_intellekt": "🧠 Sun'iy intellekt",
        "Hisob_audit": "💼 Hisob va audit", "Turizm": "✈️ Turizm"
    },
    'ru': {
        "Biotexnologiya": "🔬 Биотехнология", "Ekologiya": "🌍 Экология",
        "Axborot_tizimlar": "💻 Информационные системы", "Avtomatizatsiya": "⚙️ Автоматизация",
        "Transport": "🚚 Транспорт", "Elektroenergetika": "⚡ Электроэнергетика",
        "Pedagogika": "🧑‍🏫 Педагогика", "Suniy_intellekt": "🧠 Искусственный интеллект",
        "Hisob_audit": "💼 Учет и аудит", "Turizm": "✈️ Туризм"
    },
    'kk': {
        "Biotexnologiya": "🔬 Биотехнология", "Ekologiya": "🌍 Экология",
        "Axborot_tizimlar": "💻 Ақпараттық жүйелер", "Avtomatizatsiya": "⚙️ Автоматтандыру",
        "Transport": "🚚 Көлік", "Elektroenergetika": "⚡ Электроэнергетика",
        "Pedagogika": "🧑‍🏫 Педагогика", "Suniy_intellekt": "🧠 Жасанды интеллект",
        "Hisob_audit": "💼 Есеп және аудит", "Turizm": "✈️ Туризм"
    }
}

# Magistratura yo'nalishlari (4 ta)
MAGISTRATURA_YONALISHLAR = {
    'uz': {
        "Iqtisodiyot": "📊 Iqtisodiyot",
        "Yurisprudensiya": "⚖️ Yurisprudensiya",
        "Axborot_tizimlari": "💻 Axborot tizimlari",
        "Ekologiya": "🌍 Ekologiya"
    },
    'ru': {
        "Iqtisodiyot": "📊 Экономика",
        "Yurisprudensiya": "⚖️ Юриспруденция",
        "Axborot_tizimlari": "💻 Информационные системы",
        "Ekologiya": "🌍 Экология"
    },
    'kk': {
        "Iqtisodiyot": "📊 Экономика",
        "Yurisprudensiya": "⚖️ Юриспруденция",
        "Axborot_tizimlari": "💻 Ақпараттық жүйелер",
        "Ekologiya": "🌍 Экология"
    }
}

# Step nomlari (yo'l ko'rsatish uchun)
STEP_NAMES = {
    YONALISH_ISM: "step_name",
    YONALISH_FAMILYA: "step_surname",
    YONALISH_YOSH: "step_age",
    YONALISH_TELEFON: "step_phone",
    MAG_ISM: "step_name",
    MAG_FAMILYA: "step_surname",
    MAG_YOSH: "step_age",
    MAG_TELEFON: "step_phone",
    HUJJAT_FORMAT_1: "step_format",
    HUJJAT_FORMAT_2: "step_format",
    HUJJAT_FORMAT_3: "step_format",
    HUJJAT_FORMAT_4: "step_format",
    HUJJAT_1: "step_document",
    HUJJAT_2: "step_document",
    HUJJAT_3: "step_document",
    HUJJAT_4: "step_document",
}

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗄️  MA'LUMOTLAR BAZASI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def db_connect(): return sqlite3.connect(DB_PATH)

def init_db():
    con = db_connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, lang TEXT, birinchi_vaqt TEXT);
        CREATE TABLE IF NOT EXISTS bakalavr_royxat (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT, yonalish TEXT);
        CREATE TABLE IF NOT EXISTS magistratura_royxat (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT, yonalish TEXT);
        CREATE TABLE IF NOT EXISTS hujjat_status (user_id INTEGER PRIMARY KEY, doc1 INTEGER DEFAULT 0, doc2 INTEGER DEFAULT 0, doc3 INTEGER DEFAULT 0, doc4 INTEGER DEFAULT 0, last_update TEXT);
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

def update_hujjat_status(user_id, doc_num):
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR IGNORE INTO hujjat_status (user_id, doc1, doc2, doc3, doc4, last_update) VALUES (?,0,0,0,0,?)", (user_id, str(datetime.datetime.now())))
    cur.execute(f"UPDATE hujjat_status SET doc{doc_num}=1, last_update=? WHERE user_id=?", (str(datetime.datetime.now()), user_id))
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
        [t['menu_admin']],
        [t['change_lang']],
    ], resize_keyboard=True)

def cancel_back_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([[t['back'], t['cancel']]], resize_keyboard=True)

def format_tanlash_keyboard(lang, step_num):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t['format_rasm'], callback_data=f"format_rasm_{step_num}"),
         InlineKeyboardButton(t['format_fayl'], callback_data=f"format_fayl_{step_num}")]
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
    if not text: return False
    t = LANG_TEXTS[lang]
    menu = [t['menu_about'], t['menu_bakalavr'], t['menu_magistratura'], t['menu_hujjat'],
            t['menu_manzil'], t['menu_bakalavr_tanlash'], t['menu_magistratura_tanlash'],
            t['menu_admin'], t['change_lang']]
    return text in menu

def is_cancel_or_back(text, lang):
    if not text: return False
    t = LANG_TEXTS[lang]
    return text in [t['cancel'], t['back']]

def validate_phone(phone):
    clean = re.sub(r'[\s\-()]+', '', phone)
    if re.match(r'^\+?[1-9]\d{6,14}$', clean): return clean
    return None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🛡️  PIPELINE GUARD (TAKOMILLASHTIRILGAN)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def process_step_guard(update, context, current_state):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    msg = update.message.text if update.message else None
    
    # Cancel yoki Back tekshirish
    if msg and is_cancel_or_back(msg, lang):
        await update.message.reply_text(t['reg_cancelled'], reply_markup=main_menu_markup(lang))
        return "FORCE_CAN_MENU"
    
    # Menyu tugmasi bosilganmi?
    if msg and is_any_menu_button(msg, lang):
        # Qaysi stepda ekanligini aniqlab, to'g'ri yo'lni ko'rsatish
        step_key = STEP_NAMES.get(current_state, "step_name")
        step_text = t.get(step_key, "ma'lumot")
        await update.message.reply_text(
            t['menu_pressed'].format(current_step=step_text), 
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return "FORCE_STAY"
    
    return "PROCEED"

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
        cur.execute("INSERT INTO foydalanuvchilar VALUES (?,?,?,?,?,?)", (user.id, user.first_name, user.last_name, user.username, 'uz', str(datetime.datetime.now())))
        lang = 'uz'
    else:
        lang = row[1] if row[1] else 'uz'
    con.commit()
    con.close()
    context.user_data['lang'] = lang
    await update.message.reply_text(LANG_TEXTS[lang]['welcome'], parse_mode="Markdown", reply_markup=lang_tanlash_keyboard())
    return TIL_TANLASH

async def lang_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        set_user_lang(query.from_user.id, lang)
        context.user_data['lang'] = lang
        await query.edit_message_text(LANG_TEXTS[lang]['lang_selected'], parse_mode="Markdown")
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
    msg = update.message.text
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]

    if msg == t['change_lang']:
        await update.message.reply_text("🌐 Tilni tanlang:", parse_mode="Markdown", reply_markup=lang_tanlash_keyboard())
        return TIL_TANLASH

    if msg == t['menu_about']:
        try:
            await update.message.reply_photo(photo=ABOUT_PHOTO_URL, caption=t['about_text'], parse_mode="Markdown")
        except:
            await update.message.reply_text(t['about_text'], parse_mode="Markdown")
        return TANLA

    if msg == t['menu_bakalavr']:
        await update.message.reply_text(t['bakalavr_text'], parse_mode="Markdown")
        return TANLA

    if msg == t['menu_magistratura']:
        await update.message.reply_text(t['magistratura_text'], parse_mode="Markdown")
        return TANLA

    if msg == t['menu_hujjat']:
        await update.message.reply_text(t['hujjat_intro'], parse_mode="Markdown", reply_markup=format_tanlash_keyboard(lang, 1))
        return HUJJAT_FORMAT_1

    if msg == t['menu_manzil']:
        await update.message.reply_text(t['manzil_text'], parse_mode="Markdown")
        return TANLA

    if msg == t['menu_bakalavr_tanlash']:
        if check_already_registered(user_id, "bakalavr_royxat"):
            await update.message.reply_text(t['yonalish_allready'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return YONALISH_ISM

    if msg == t['menu_magistratura_tanlash']:
        if check_already_registered(user_id, "magistratura_royxat"):
            await update.message.reply_text(t['magistratura_allready'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return MAG_ISM

    if msg == t['menu_admin']:
        await update.message.reply_text(f"💬 {ADMIN_USERNAME}\n📞 `{ADMIN_PHONE}`", parse_mode="Markdown")
        return TANLA

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
    parts = data.split("_")
    format_turi, step = parts[1], int(parts[2])
    context.user_data[f'hujjat_format_{step}'] = format_turi
    await query.message.reply_text(
        f"📥 {HUJJAT_NOMLAR[lang][step]} ({format_turi.upper()} ko'rinishida)\n\n👇 Yuklang:", 
        reply_markup=cancel_back_markup(lang)
    )
    return HUJJAT_STATES[step]

async def hujjat_handler(update, context, step):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    # Guard - agar xato bo'lsa to'g'ri yo'lni ko'rsatadi
    guard = await process_step_guard(update, context, HUJJAT_STATES[step])
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return HUJJAT_STATES[step]
    
    fmt = context.user_data.get(f'hujjat_format_{step}', 'rasm')
    
    # Xato format tekshiruvi
    if fmt == 'fayl' and not update.message.document:
        await update.message.reply_text(t['error_need_file'], parse_mode="Markdown")
        return HUJJAT_STATES[step]
    if fmt == 'rasm' and not update.message.photo:
        await update.message.reply_text(t['error_need_photo'], parse_mode="Markdown")
        return HUJJAT_STATES[step]
    
    user = update.message.from_user
    username = f"@{user.username}" if user.username else f"[{user.first_name}](tg://user?id={user.id})"
    caption = t['channel_caption'].format(user=username, uid=user.id, doc_name=HUJJAT_NOMLAR[lang][step])
    try:
        if update.message.document:
            await context.bot.send_document(CHANNEL_USERNAME, update.message.document.file_id, caption=caption, parse_mode="Markdown")
        else:
            await context.bot.send_photo(CHANNEL_USERNAME, update.message.photo[-1].file_id, caption=caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kanalga yuborish xato: {e}")
    update_hujjat_status(user_id, step)
    
    if step < 4:
        ns = step + 1
        await update.message.reply_text(
            f"{t['success_received']}\n\n🟢 *{ns}-Bosqich: {HUJJAT_NOMLAR[lang][ns]}*\n❓ Format:", 
            parse_mode="Markdown", 
            reply_markup=format_tanlash_keyboard(lang, ns)
        )
        return HUJJAT_FORMAT_STATES[ns]
    else:
        await update.message.reply_text(t['all_docs_success'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA

async def hujjat_1(update, context): return await hujjat_handler(update, context, 1)
async def hujjat_2(update, context): return await hujjat_handler(update, context, 2)
async def hujjat_3(update, context): return await hujjat_handler(update, context, 3)
async def hujjat_4(update, context): return await hujjat_handler(update, context, 4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  BAKALAVRIAT TANLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, YONALISH_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_ISM
    
    if not update.message or not update.message.text:
        await update.message.reply_text(t['enter_name'], reply_markup=cancel_back_markup(lang))
        return YONALISH_ISM
    
    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(t['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, YONALISH_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_FAMILYA
    
    if not update.message or not update.message.text:
        await update.message.reply_text(t['enter_surname'], reply_markup=cancel_back_markup(lang))
        return YONALISH_FAMILYA
    
    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(t['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, YONALISH_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_YOSH
    
    yosh = update.message.text.strip() if (update.message and update.message.text) else ""
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            t['wrong_input'].format(expected=t['step_age']), 
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return YONALISH_YOSH
    
    context.user_data['yonalish_yosh'] = yosh
    btn = [[KeyboardButton(t['send_phone'], request_contact=True)], [KeyboardButton(t['back']), KeyboardButton(t['cancel'])]]
    await update.message.reply_text(t['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True))
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, YONALISH_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_TELEFON
    
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(
                t['wrong_input'].format(expected=t['step_phone']), 
                parse_mode="Markdown",
                reply_markup=cancel_back_markup(lang)
            )
            return YONALISH_TELEFON
    else:
        await update.message.reply_text(
            t['wrong_input'].format(expected=t['step_phone']), 
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return YONALISH_TELEFON
    
    context.user_data['yonalish_telefon'] = phone
    await update.message.reply_text(t['select_bakalavr_title'], parse_mode="Markdown", reply_markup=bakalavr_keyboard(lang))
    return YONALISH_TANLASH

async def bakalavr_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if not data.startswith("bak_"):
        return TANLA
    key = data.replace("bak_", "")
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    if key not in BAKALAVR_YONALISHLAR[lang]:
        return TANLA
    yonalish = BAKALAVR_YONALISHLAR[lang][key]
    
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO bakalavr_royxat VALUES (?,?,?,?,?,?,?,?,?,?)", 
                (user_id, query.from_user.first_name, query.from_user.last_name, query.from_user.username, 
                 str(datetime.datetime.now()), context.user_data.get('yonalish_ism'), 
                 context.user_data.get('yonalish_familya'), context.user_data.get('yonalish_yosh'), 
                 context.user_data.get('yonalish_telefon'), yonalish))
    con.commit()
    con.close()
    
    username = f"@{query.from_user.username}" if query.from_user.username else f"[{query.from_user.first_name}](tg://user?id={user_id})"
    caption = t['yonalish_channel_caption'].format(
        user=username, uid=user_id, phone=context.user_data.get('yonalish_telefon'),
        yonalish=yonalish, ism=context.user_data.get('yonalish_ism'),
        familya=context.user_data.get('yonalish_familya'), yosh=context.user_data.get('yonalish_yosh')
    )
    try:
        await context.bot.send_message(CHANNEL_USERNAME, caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kanalga yuborish xato: {e}")
    
    await query.edit_message_text(t['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📚  MAGISTRATURA TANLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def magistratura_ism(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, MAG_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_ISM
    
    if not update.message or not update.message.text:
        await update.message.reply_text(t['enter_name'], reply_markup=cancel_back_markup(lang))
        return MAG_ISM
    
    context.user_data['mag_ism'] = update.message.text.strip()
    await update.message.reply_text(t['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return MAG_FAMILYA

async def magistratura_familya(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, MAG_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_FAMILYA
    
    if not update.message or not update.message.text:
        await update.message.reply_text(t['enter_surname'], reply_markup=cancel_back_markup(lang))
        return MAG_FAMILYA
    
    context.user_data['mag_familya'] = update.message.text.strip()
    await update.message.reply_text(t['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return MAG_YOSH

async def magistratura_yosh(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, MAG_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_YOSH
    
    yosh = update.message.text.strip() if (update.message and update.message.text) else ""
    if not yosh.isdigit() or not (21 <= int(yosh) <= 65):
        await update.message.reply_text(
            t['wrong_input'].format(expected=t['step_age']), 
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return MAG_YOSH
    
    context.user_data['mag_yosh'] = yosh
    btn = [[KeyboardButton(t['send_phone'], request_contact=True)], [KeyboardButton(t['back']), KeyboardButton(t['cancel'])]]
    await update.message.reply_text(t['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True))
    return MAG_TELEFON

async def magistratura_telefon(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    guard = await process_step_guard(update, context, MAG_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_TELEFON
    
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(
                t['wrong_input'].format(expected=t['step_phone']), 
                parse_mode="Markdown",
                reply_markup=cancel_back_markup(lang)
            )
            return MAG_TELEFON
    else:
        await update.message.reply_text(
            t['wrong_input'].format(expected=t['step_phone']), 
            parse_mode="Markdown",
            reply_markup=cancel_back_markup(lang)
        )
        return MAG_TELEFON
    
    context.user_data['mag_telefon'] = phone
    await update.message.reply_text(t['select_magistratura_title'], parse_mode="Markdown", reply_markup=magistratura_keyboard(lang))
    return MAG_TANLASH

async def magistratura_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    if not data.startswith("mag_"):
        return TANLA
    key = data.replace("mag_", "")
    user_id = query.from_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    
    if key not in MAGISTRATURA_YONALISHLAR[lang]:
        return TANLA
    yonalish = MAGISTRATURA_YONALISHLAR[lang][key]
    
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO magistratura_royxat VALUES (?,?,?,?,?,?,?,?,?,?)", 
                (user_id, query.from_user.first_name, query.from_user.last_name, query.from_user.username, 
                 str(datetime.datetime.now()), context.user_data.get('mag_ism'), 
                 context.user_data.get('mag_familya'), context.user_data.get('mag_yosh'), 
                 context.user_data.get('mag_telefon'), yonalish))
    con.commit()
    con.close()
    
    username = f"@{query.from_user.username}" if query.from_user.username else f"[{query.from_user.first_name}](tg://user?id={user_id})"
    caption = t['magistratura_channel_caption'].format(
        user=username, uid=user_id, phone=context.user_data.get('mag_telefon'),
        yonalish=yonalish, ism=context.user_data.get('mag_ism'),
        familya=context.user_data.get('mag_familya'), yosh=context.user_data.get('mag_yosh')
    )
    try:
        await context.bot.send_message(CHANNEL_USERNAME, caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kanalga yuborish xato: {e}")
    
    await query.edit_message_text(t['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👤  ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def admin_statistika(update, context):
    if update.effective_user.username != "Saman2611":
        await update.message.reply_text("❌ Faqat admin!")
        return
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM bakalavr_royxat")
    bak = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM magistratura_royxat")
    mag = cur.fetchone()[0]
    con.close()
    await update.message.reply_text(f"📊 *STATISTIKA*\n\n🎓 Bakalavriat: {bak}\n📚 Magistratura: {mag}", parse_mode="Markdown")

async def admin_export(update, context):
    if update.effective_user.username != "Saman2611":
        await update.message.reply_text("❌ Faqat admin!")
        return
    con = db_connect()
    for table in ['bakalavr_royxat', 'magistratura_royxat']:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {table}")
        data = cur.fetchall()
        if data:
            csv_file = io.StringIO()
            writer = csv.writer(csv_file)
            writer.writerow([desc[0] for desc in cur.description])
            writer.writerows(data)
            await update.message.reply_document(io.BytesIO(csv_file.getvalue().encode('utf-8-sig')), filename=f"{table}.csv")
    con.close()

async def admin_search(update, context):
    if update.effective_user.username != "Saman2611":
        await update.message.reply_text("❌ Faqat admin!")
        return
    if not context.args:
        await update.message.reply_text("🔍 /search +998901234567 yoki /search ism")
        return
    term = ' '.join(context.args)
    con = db_connect()
    cur = con.cursor()
    text = f"🔍 '{term}' bo'yicha natijalar:\n\n"
    for table in ['bakalavr_royxat', 'magistratura_royxat']:
        cur.execute(f"SELECT ism, familya, telefon, yonalish FROM {table} WHERE ism LIKE ? OR familya LIKE ? OR telefon LIKE ?", (f'%{term}%', f'%{term}%', f'%{term}%'))
        rows = cur.fetchall()
        if rows:
            text += f"📋 {table}:\n"
            for row in rows:
                text += f"• {row[0]} {row[1]} | {row[2]} | {row[3]}\n"
            text += "\n"
    con.close()
    await update.message.reply_text(text, parse_mode="Markdown")

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖  MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    if not BOT_TOKEN or BOT_TOKEN == "7314275083:AAHe_G3...":
        raise ValueError("❌ BOT_TOKEN xato!")
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("users", admin_statistika))
    app.add_handler(CommandHandler("export", admin_export))
    app.add_handler(CommandHandler("search", admin_search))

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIL_TANLASH: [CallbackQueryHandler(lang_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            TANLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher), 
                    CallbackQueryHandler(bakalavr_callback), CallbackQueryHandler(magistratura_callback)],
            HUJJAT_FORMAT_1: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_2: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_3: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_4: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_1: [MessageHandler(filters.ALL, hujjat_1)], 
            HUJJAT_2: [MessageHandler(filters.ALL, hujjat_2)],
            HUJJAT_3: [MessageHandler(filters.ALL, hujjat_3)], 
            HUJJAT_4: [MessageHandler(filters.ALL, hujjat_4)],
            YONALISH_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)], 
            YONALISH_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)],
            YONALISH_YOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)], 
            YONALISH_TELEFON: [MessageHandler(filters.ALL, yonalish_telefon)],
            YONALISH_TANLASH: [CallbackQueryHandler(bakalavr_callback)],
            MAG_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_ism)], 
            MAG_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_familya)],
            MAG_YOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_yosh)], 
            MAG_TELEFON: [MessageHandler(filters.ALL, magistratura_telefon)],
            MAG_TANLASH: [CallbackQueryHandler(magistratura_callback)],
        },
        fallbacks=[CommandHandler('start', start), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
        allow_reentry=True
    )
    app.add_handler(conv)
    print("✅ BOT ISHGA TUSHDI!")
    print("📊 Admin: /users, /export, /search")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
