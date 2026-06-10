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
# Bakalavriat uchun
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = "hf1", "hf2", "hf3", "hf4"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "h1", "h2", "h3", "h4"
SOROV_ISM, SOROV_FAMILYA, SOROV_YOSH, SOROV_TELEFON = "si", "sf", "sy", "st"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON, YONALISH_TANLASH = "yi", "yf", "yy", "yt", "yonalish_tanlash"
# Magistratura uchun
MAG_ISM, MAG_FAMILYA, MAG_YOSH, MAG_TELEFON, MAG_TANLASH = "mi", "mf", "my", "mt", "mag_tanlash"
# Yangi state'lar
FAQ_STATE = "faq_state"
APPOINTMENT_NAME, APPOINTMENT_PHONE, APPOINTMENT_DATE, APPOINTMENT_TIME = "an", "ap", "ad", "at"
EDIT_SOROV_NAME, EDIT_SOROV_SURNAME, EDIT_SOROV_AGE, EDIT_SOROV_PHONE = "esn", "ess", "esa", "esp"

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
        'menu_sorov': "🗂 So'rovnoma",
        'menu_bakalavr_tanlash': "📋 Bakalavriat yo'nalishlari",
        'menu_magistratura_tanlash': "🎓 Magistratura yo'nalishlari",
        'menu_admin': "👤 Admin bilan bog'lanish",
        'menu_faq': "❓ Savol-Javob",
        'menu_appointment': "📅 Onlayn qabul",
        'menu_status': "📊 Hujjat holati",
        'menu_edit': "✏️ Ma'lumotlarni o'zgartirish",
        'menu_samples': "📄 Hujjat namunalari",
        'back': "🔙 Orqaga",
        'cancel': "❌ Bekor qilish",
        'change_lang': "🌐 Tilni o'zgartirish",
        'about_text': "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti Chirchiq filiali*\n\nChirchiq shahrida universitetning yangi zamonaviy filiali o'z ishini boshlamoqda!\n\n🔗 [Batafsil ma'lumot](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *BAKALAVRIAT YO'NALISHLARI*\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'magistratura_text': "🎓 *MAGISTRATURA YO'NALISHLARI*\n\n📊 Iqtisodiyot\n⚖️ Yurisprudensiya\n💻 Axborot tizimlari\n🌍 Ekologiya\n📈 Menejment\n🧑‍🏫 Pedagogika\n🧠 Psixologiya\n📖 Tilshunoslik",
        'hujjat_intro': "📋 *KERAKLI HUJJATLAR RO'YXATI*\n\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ 0.86 Med-ma'lumotnoma\n4️⃣ 3x4 rasm (6 dona)\n\n🟢 *1-Bosqich: Diplom yoki Attestat*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm ko'rinishida",
        'format_fayl': "📎 Fayl ko'rinishida",
        'sorov_allready': "✨ *Siz so'rovnomani to'ldirib bo'lgansiz!*",
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
        'unknown': "❓ Noma'lum xabar. Iltimos, menyu tugmalaridan foydalaning.",
        'error_need_file': "⚠️ *Xatolik:* Fayl formatida yuboring!",
        'error_need_photo': "⚠️ *Xatolik:* Rasm formatida yuboring!",
        'channel_caption': "📋 *Yangi Hujjat!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *BAKALAVRIAT TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n📚 Yo'nalish: *{yonalish}*\n👤 Ism: {ism}\n👤 Fam: {familya}\n🎂 Yosh: {yosh}",
        'magistratura_channel_caption': "📚 *MAGISTRATURA TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n🎓 Magistratura: *{yonalish}*\n👤 Ism: {ism}\n👤 Fam: {familya}\n🎂 Yosh: {yosh}",
        'reg_cancelled': "❌ Jarayon bekor qilindi.",
        'reg_success': "🎉 Yo'nalish muvaffaqiyatli tanlandi!",
        'manzil_text': "📍 *Universitet manzili:* Chirchiq shahri, Toshkent viloyati.\n🗺 [Xarita](http://maps.google.com)",
        'warning_in_progress': "⚠️ *Siz ro'yxatdan o'tish jarayonidasiz!*\n\nJoriy so'ralgan ma'lumotni yuboring yoki **❌ Bekor qilish** tugmasini bosing.",
        'faq_title': "❓ *TEZ-TEZ SO'RALADIGAN SAVOLLAR*\n\n",
        'faq1': "1️⃣ *Hujjat topshirish muddati?*\n➡️ 2024-yil 1-sentyabrgacha.\n\n",
        'faq2': "2️⃣ *Qabul shartlari?*\n➡️ O'rta ma'lumot (11 sinf) yoki diplom.\n\n",
        'faq3': "3️⃣ *Yotoqxona bormi?*\n➡️ Ha, chet ellik va viloyat talabalari uchun.\n\n",
        'faq4': "4️⃣ *Kontrakt narxi?*\n➡️ Yo'nalishga qarab 15-25 million so'm.\n\n",
        'faq5': "5️⃣ *Imtiyozlar?*\n➡️ Ha, a'lochi va kam ta'minlanganlar uchun.\n\n",
        'faq6': "6️⃣ *Diplom qayerda amal qiladi?*\n➡️ O'zbekiston va Qozog'istonda.\n\n",
        'faq7': "7️⃣ *Ma'lumot qayerdan?*\n➡️ @Auezov_data kanaliga obuna bo'ling!\n\n",
        'faq_back': "🔙 Savollardan chiqish",
        'appointment_title': "📅 *ONLAYN QABUL YOZILISH*\n\nMa'lumotlaringizni kiriting:",
        'appointment_name': "✍️ *Ismingiz:*",
        'appointment_phone': "📞 *Telefon raqam:*",
        'appointment_date': "📅 *Qabul kuni (2024-12-20):*",
        'appointment_time': "⏰ *Qabul vaqti (14:00):*",
        'appointment_success': "✅ *Qabulga yozildingiz!*\n\n📅 Sana: {date}\n⏰ Vaqt: {time}\n\nTez orada bog'lanamiz!",
        'edit_title': "✏️ *MA'LUMOTLARNI O'ZGARTIRISH*\n\nQaysi ma'lumotni o'zgartirmoqchisiz?",
        'edit_name': "✍️ *Yangi ismingiz:*",
        'edit_surname': "✍️ *Yangi familiyangiz:*",
        'edit_age': "🎂 *Yangi yoshingiz:*",
        'edit_phone': "📞 *Yangi telefon raqam:*",
        'edit_success': "✅ *Ma'lumot o'zgartirildi!*",
        'status_title': "📊 *HUJJAT HOLATINGIZ*\n\n",
        'status_not_found': "❌ Siz hali hujjat topshirmagansiz!",
        'status_docs_received': "📄 *Topshirilgan hujjatlar:* {count}/4\n",
        'status_yonalish': "🎓 *Bakalavriat:* {yonalish}\n",
        'status_magistratura': "📚 *Magistratura:* {yonalish}\n",
        'status_phone': "📞 *Telefon:* {phone}\n",
        'status_waiting': "⏳ Holat: *Ko'rib chiqilmoqda*",
        'samples_title': "📄 *HUJJAT NAMUNALARI*\n\nQuyidagi namunalarni yuklab oling:",
        'sample_diplom': "🎓 Diplom/Attestat",
        'sample_passport': "🪪 Pasport",
        'sample_medical': "🏥 Tibbiy ma'lumotnoma",
        'sample_photo': "📸 Rasm talablari",
        'sample_not_available': "⚠️ Namuna hozircha mavjud emas."
    },
    'ru': {
        'welcome': "🏛 *Южно-Казахстанский университет им. М.Ауезова* Добро пожаловать!\n\n👇 _Выберите язык:_",
        'lang_selected': "✅ *Русский язык выбран*!",
        'menu_about': "🏛 Об университете",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Подать документы",
        'menu_manzil': "📍 Адрес",
        'menu_sorov': "🗂 Анкета",
        'menu_bakalavr_tanlash': "📋 Направления бакалавриата",
        'menu_magistratura_tanlash': "🎓 Направления магистратуры",
        'menu_admin': "👤 Связаться с админом",
        'menu_faq': "❓ Вопросы-Ответы",
        'menu_appointment': "📅 Онлайн запись",
        'menu_status': "📊 Статус документов",
        'menu_edit': "✏️ Редактировать",
        'menu_samples': "📄 Образцы",
        'back': "🔙 Назад",
        'cancel': "❌ Отмена",
        'change_lang': "🌐 Сменить язык",
        'about_text': "🏛 *Южно-Казахстанский университет им. М.Ауезова Чирчикский филиал*\n\nВ городе Чирчик открывается новый современный филиал!\n\n🔗 [Подробнее](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *НАПРАВЛЕНИЯ БАКАЛАВРИАТА*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Транспорт\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект\n💼 Учет и аудит\n✈️ Туризм",
        'magistratura_text': "🎓 *НАПРАВЛЕНИЯ МАГИСТРАТУРЫ*\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Информационные системы\n🌍 Экология\n📈 Менеджмент\n🧑‍🏫 Педагогика\n🧠 Психология\n📖 Лингвистика",
        'hujjat_intro': "📋 *СПИСОК ДОКУМЕНТОВ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ Мед-справка 0.86\n4️⃣ Фото 3x4 (6 шт)\n\n🟢 *1-этап: Диплом или Аттестат*\n❓ Выберите формат:",
        'format_rasm': "🖼️ Изображение",
        'format_fayl': "📎 Файл",
        'sorov_allready': "✨ *Вы уже заполнили анкету!*",
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
        'warning_in_progress': "⚠️ *Вы в процессе регистрации!*\nОтправьте запрашиваемую информацию.",
        'faq_title': "❓ *ЧАСТО ЗАДАВАЕМЫЕ ВОПРОСЫ*\n\n",
        'faq1': "1️⃣ *Срок подачи документов?*\n➡️ До 1 сентября 2024 года.\n\n",
        'faq2': "2️⃣ *Условия поступления?*\n➡️ Среднее образование (11 классов).\n\n",
        'faq3': "3️⃣ *Есть общежитие?*\n➡️ Да, для иногородних.\n\n",
        'faq4': "4️⃣ *Стоимость контракта?*\n➡️ 15-25 миллионов сумов.\n\n",
        'faq5': "5️⃣ *Льготы?*\n➡️ Для отличников и малообеспеченных.\n\n",
        'faq6': "6️⃣ *Где действует диплом?*\n➡️ В Узбекистане и Казахстане.\n\n",
        'faq7': "7️⃣ *Где узнать информацию?*\n➡️ Подпишитесь на @Auezov_data!\n\n",
        'faq_back': "🔙 Выйти",
        'appointment_title': "📅 *ЗАПИСЬ НА ПРИЕМ*\n\nВведите данные:",
        'appointment_name': "✍️ *Имя:*",
        'appointment_phone': "📞 *Телефон:*",
        'appointment_date': "📅 *Дата (2024-12-20):*",
        'appointment_time': "⏰ *Время (14:00):*",
        'appointment_success': "✅ *Вы записаны!*\n\n📅 Дата: {date}\n⏰ Время: {time}",
        'edit_title': "✏️ *РЕДАКТИРОВАНИЕ*\n\nЧто хотите изменить?",
        'edit_name': "✍️ *Новое имя:*",
        'edit_surname': "✍️ *Новая фамилия:*",
        'edit_age': "🎂 *Новый возраст:*",
        'edit_phone': "📞 *Новый телефон:*",
        'edit_success': "✅ *Данные изменены!*",
        'status_title': "📊 *СТАТУС ДОКУМЕНТОВ*\n\n",
        'status_not_found': "❌ Вы еще не подавали документы!",
        'status_docs_received': "📄 *Поданные документы:* {count}/4\n",
        'status_yonalish': "🎓 *Бакалавриат:* {yonalish}\n",
        'status_magistratura': "📚 *Магистратура:* {yonalish}\n",
        'status_phone': "📞 *Телефон:* {phone}\n",
        'status_waiting': "⏳ Статус: *Рассматривается*",
        'samples_title': "📄 *ОБРАЗЦЫ ДОКУМЕНТОВ*\n\nСкачайте образцы:",
        'sample_diplom': "🎓 Диплом/Аттестат",
        'sample_passport': "🪪 Паспорт",
        'sample_medical': "🏥 Медсправка",
        'sample_photo': "📸 Требования к фото",
        'sample_not_available': "⚠️ Образец недоступен."
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы ОҚУ* Шыршық филиалына қош келдіңіз!\n\n👇 _Тілді таңдаңыз:_",
        'lang_selected': "✅ *Қазақ тілі таңдалды*!",
        'menu_about': "🏛 Университет туралы",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Құжат тапсыру",
        'menu_manzil': "📍 Мекенжай",
        'menu_sorov': "🗂 Сауалнама",
        'menu_bakalavr_tanlash': "📋 Бакалавриат бағыттары",
        'menu_magistratura_tanlash': "🎓 Магистратура бағыттары",
        'menu_admin': "👤 Әкімге жазу",
        'menu_faq': "❓ Сұрақ-Жауап",
        'menu_appointment': "📅 Онлайн жазылу",
        'menu_status': "📊 Құжат күйі",
        'menu_edit': "✏️ Өзгерту",
        'menu_samples': "📄 Үлгілер",
        'back': "🔙 Артқа",
        'cancel': "❌ Болдырмау",
        'change_lang': "🌐 Тілді өзгерту",
        'about_text': "🏛 *М.Әуезов атындағы ОҚУ Шыршық филиалы*\n\nШыршық қаласында заманауи филиал ашылды!\n\n🔗 [Толығырақ](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiali)",
        'bakalavr_text': "👑 *БАКАЛАВРИАТ БАҒЫТТАРЫ*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматтандыру\n🚚 Көлік\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм",
        'magistratura_text': "🎓 *МАГИСТРАТУРА БАҒЫТТАРЫ*\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Ақпараттық жүйелер\n🌍 Экология\n📈 Менеджмент\n🧑‍🏫 Педагогика\n🧠 Психология\n📖 Лингвистика",
        'hujjat_intro': "📋 *ҚҰЖАТТАР ТІЗІМІ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ 0.86 Мед-анықтама\n4️⃣ 3x4 сурет (6 дана)\n\n🟢 *1-кезең: Диплом/Аттестат*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет түрінде",
        'format_fayl': "📎 Файл түрінде",
        'sorov_allready': "✨ *Сауалнама толтырылған!*",
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
        'warning_in_progress': "⚠️ *Сіз тіркелу процесіндесіз!*\nСұралған ақпаратты жіберіңіз.",
        'faq_title': "❓ *ЖИІ ҚОЙЫЛАТЫН СҰРАҚТАР*\n\n",
        'faq1': "1️⃣ *Құжат тапсыру мерзімі?*\n➡️ 2024 ж. 1 қыркүйекке дейін.\n\n",
        'faq2': "2️⃣ *Қабылдау шарттары?*\n➡️ Орта білім (11 сынып).\n\n",
        'faq3': "3️⃣ *Жатақхана бар ма?*\n➡️ Иә, облыстан келгендерге.\n\n",
        'faq4': "4️⃣ *Контракт қанша?*\n➡️ 15-25 миллион сом.\n\n",
        'faq5': "5️⃣ *Жеңілдіктер?*\n➡️ Үздік және аз қамтылғандарға.\n\n",
        'faq6': "6️⃣ *Диплом қайда жарамды?*\n➡️ Өзбекстан мен Қазақстанда.\n\n",
        'faq7': "7️⃣ *Ақпарат қайдан?*\n➡️ @Auezov_data арнасына жазылыңыз!\n\n",
        'faq_back': "🔙 Шығу",
        'appointment_title': "📅 *ОНЛАЙН ЖАЗЫЛУ*\n\nДеректеріңізді енгізіңіз:",
        'appointment_name': "✍️ *Атыңыз:*",
        'appointment_phone': "📞 *Телефон:*",
        'appointment_date': "📅 *Күні (2024-12-20):*",
        'appointment_time': "⏰ *Уақыты (14:00):*",
        'appointment_success': "✅ *Сіз жазылдыңыз!*\n\n📅 Күні: {date}\n⏰ Уақыты: {time}",
        'edit_title': "✏️ *ДЕРЕКТЕРДІ ӨЗГЕРТУ*\n\nНені өзгерткіңіз келеді?",
        'edit_name': "✍️ *Жаңа атыңыз:*",
        'edit_surname': "✍️ *Жаңа тегіңіз:*",
        'edit_age': "🎂 *Жаңа жасыңыз:*",
        'edit_phone': "📞 *Жаңа телефон:*",
        'edit_success': "✅ *Деректер өзгертілді!*",
        'status_title': "📊 *ҚҰЖАТ КҮЙІҢІЗ*\n\n",
        'status_not_found': "❌ Сіз әлі құжат тапсырған жоқсыз!",
        'status_docs_received': "📄 *Тапсырылған құжаттар:* {count}/4\n",
        'status_yonalish': "🎓 *Бакалавриат:* {yonalish}\n",
        'status_magistratura': "📚 *Магистратура:* {yonalish}\n",
        'status_phone': "📞 *Телефон:* {phone}\n",
        'status_waiting': "⏳ Күйі: *Қаралуда*",
        'samples_title': "📄 *ҚҰЖАТ ҮЛГІЛЕРІ*\n\nҮлгілерді жүктеңіз:",
        'sample_diplom': "🎓 Диплом/Аттестат",
        'sample_passport': "🪪 Паспорт",
        'sample_medical': "🏥 Мед-анықтама",
        'sample_photo': "📸 Сурет талаптары",
        'sample_not_available': "⚠️ Үлгі жоқ."
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

# Bakalavriat yo'nalishlari
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

# Magistratura yo'nalishlari
MAGISTRATURA_YONALISHLAR = {
    'uz': {
        "Iqtisodiyot": "📊 Iqtisodiyot",
        "Yurisprudensiya": "⚖️ Yurisprudensiya",
        "Axborot_tizimlari": "💻 Axborot tizimlari",
        "Ekologiya": "🌍 Ekologiya",
        "Menejment": "📈 Menejment",
        "Pedagogika": "🧑‍🏫 Pedagogika",
        "Psixologiya": "🧠 Psixologiya",
        "Tilshunoslik": "📖 Tilshunoslik"
    },
    'ru': {
        "Iqtisodiyot": "📊 Экономика",
        "Yurisprudensiya": "⚖️ Юриспруденция",
        "Axborot_tizimlari": "💻 Информационные системы",
        "Ekologiya": "🌍 Экология",
        "Menejment": "📈 Менеджмент",
        "Pedagogika": "🧑‍🏫 Педагогика",
        "Psixologiya": "🧠 Психология",
        "Tilshunoslik": "📖 Лингвистика"
    },
    'kk': {
        "Iqtisodiyot": "📊 Экономика",
        "Yurisprudensiya": "⚖️ Юриспруденция",
        "Axborot_tizimlari": "💻 Ақпараттық жүйелер",
        "Ekologiya": "🌍 Экология",
        "Menejment": "📈 Менеджмент",
        "Pedagogika": "🧑‍🏫 Педагогика",
        "Psixologiya": "🧠 Психология",
        "Tilshunoslik": "📖 Лингвистика"
    }
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
        CREATE TABLE IF NOT EXISTS sorovnama (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT);
        CREATE TABLE IF NOT EXISTS bakalavr_royxat (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT, yonalish TEXT);
        CREATE TABLE IF NOT EXISTS magistratura_royxat (id INTEGER PRIMARY KEY, first_name TEXT, last_name TEXT, user_name TEXT, vaqt TEXT, ism TEXT, familya TEXT, yosh INTEGER, telefon TEXT, yonalish TEXT);
        CREATE TABLE IF NOT EXISTS appointments (id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, name TEXT, phone TEXT, date TEXT, time TEXT, status TEXT, created_at TEXT);
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
        [t['menu_about'], t['menu_bakalavr'], t['menu_magistratura']],
        [t['menu_hujjat'], t['menu_manzil']],
        [t['menu_sorov'], t['menu_bakalavr_tanlash'], t['menu_magistratura_tanlash']],
        [t['menu_faq'], t['menu_appointment']],
        [t['menu_status'], t['menu_edit']],
        [t['menu_samples'], t['menu_admin']],
        [t['change_lang']],
    ], resize_keyboard=True)

def cancel_back_markup(lang):
    t = LANG_TEXTS[lang]
    return ReplyKeyboardMarkup([[t['back'], t['cancel']]], resize_keyboard=True)

def edit_menu_markup(lang):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✏️ Ism", callback_data="edit_name"),
         InlineKeyboardButton("✏️ Familiya", callback_data="edit_surname")],
        [InlineKeyboardButton("🎂 Yosh", callback_data="edit_age"),
         InlineKeyboardButton("📞 Telefon", callback_data="edit_phone")],
        [InlineKeyboardButton(t['back'], callback_data="edit_back")]
    ])

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

def samples_keyboard(lang):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(t['sample_diplom'], callback_data="sample_diplom")],
        [InlineKeyboardButton(t['sample_passport'], callback_data="sample_passport")],
        [InlineKeyboardButton(t['sample_medical'], callback_data="sample_medical")],
        [InlineKeyboardButton(t['sample_photo'], callback_data="sample_photo")],
        [InlineKeyboardButton(t['back'], callback_data="samples_back")]
    ])

def is_any_menu_button(text, lang):
    if not text: return False
    t = LANG_TEXTS[lang]
    menu = [t['menu_about'], t['menu_bakalavr'], t['menu_magistratura'], t['menu_hujjat'],
            t['menu_manzil'], t['menu_sorov'], t['menu_bakalavr_tanlash'], t['menu_magistratura_tanlash'],
            t['menu_admin'], t['menu_faq'], t['menu_appointment'], t['menu_status'], 
            t['menu_edit'], t['menu_samples'], t['change_lang']]
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
# 🛡️  GUARD
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def process_step_guard(update, context, current_state):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    msg = update.message.text if update.message else None
    
    if msg:
        if is_cancel_or_back(msg, lang):
            await update.message.reply_text(t['reg_cancelled'], reply_markup=main_menu_markup(lang))
            return "FORCE_CAN_MENU"
        if is_any_menu_button(msg, lang):
            await update.message.reply_text(t['warning_in_progress'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
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
        await query.message.reply_text(LANG_TEXTS[lang]['welcome'].replace("tilni tanlang", "quyidagi menyudan foydalaning"), parse_mode="Markdown", reply_markup=main_menu_markup(lang))
        return TANLA
    return TIL_TANLASH

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  MENYU DISPATCHER
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

    if msg == t['menu_sorov']:
        if check_already_registered(user_id, "sorovnama"):
            await update.message.reply_text(t['sorov_allready'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return SOROV_ISM

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

    if msg == t['menu_faq']:
        faq = t['faq_title'] + t['faq1'] + t['faq2'] + t['faq3'] + t['faq4'] + t['faq5'] + t['faq6'] + t['faq7']
        await update.message.reply_text(faq, parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup([[t['faq_back']]], resize_keyboard=True))
        return FAQ_STATE

    if msg == t['menu_appointment']:
        await update.message.reply_text(t['appointment_title'], parse_mode="Markdown")
        await update.message.reply_text(t['appointment_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return APPOINTMENT_NAME

    if msg == t['menu_status']:
        doc_status = get_hujjat_status(user_id)
        submitted = sum(doc_status)
        if submitted == 0 and not check_already_registered(user_id, "bakalavr_royxat") and not check_already_registered(user_id, "magistratura_royxat"):
            await update.message.reply_text(t['status_not_found'], parse_mode="Markdown")
            return TANLA
        status = t['status_title'] + t['status_docs_received'].format(count=submitted)
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT yonalish, telefon FROM bakalavr_royxat WHERE id=?", (user_id,))
        row = cur.fetchone()
        if row:
            status += t['status_yonalish'].format(yonalish=row[0])
            status += t['status_phone'].format(phone=row[1])
        cur.execute("SELECT yonalish, telefon FROM magistratura_royxat WHERE id=?", (user_id,))
        row = cur.fetchone()
        if row:
            status += t['status_magistratura'].format(yonalish=row[0])
            if not status.__contains__(row[1]):
                status += t['status_phone'].format(phone=row[1])
        con.close()
        status += t['status_waiting']
        await update.message.reply_text(status, parse_mode="Markdown")
        return TANLA

    if msg == t['menu_edit']:
        await update.message.reply_text(t['edit_title'], parse_mode="Markdown", reply_markup=edit_menu_markup(lang))
        return TANLA

    if msg == t['menu_samples']:
        await update.message.reply_text(t['samples_title'], parse_mode="Markdown", reply_markup=samples_keyboard(lang))
        return TANLA

    if msg == t['menu_admin']:
        await update.message.reply_text(f"💬 {ADMIN_USERNAME}\n📞 `{ADMIN_PHONE}`", parse_mode="Markdown")
        return TANLA

    if msg == t['faq_back']:
        await update.message.reply_text(t['welcome'].replace("tilni tanlang", "quyidagi menyudan foydalaning"), parse_mode="Markdown", reply_markup=main_menu_markup(lang))
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
    await query.message.reply_text(f"📥 {HUJJAT_NOMLAR[lang][step]} ({format_turi.upper()} ko'rinishida)\n\n👇 Yuklang:", reply_markup=cancel_back_markup(lang))
    return HUJJAT_STATES[step]

async def hujjat_handler(update, context, step):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    t = LANG_TEXTS[lang]
    guard = await process_step_guard(update, context, HUJJAT_STATES[step])
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return HUJJAT_STATES[step]
    fmt = context.user_data.get(f'hujjat_format_{step}', 'rasm')
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
        await update.message.reply_text(f"{t['success_received']}\n\n🟢 *{ns}-Bosqich: {HUJJAT_NOMLAR[lang][ns]}*\n❓ Format:", parse_mode="Markdown", reply_markup=format_tanlash_keyboard(lang, ns))
        return HUJJAT_FORMAT_STATES[ns]
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
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, SOROV_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_ISM
    context.user_data['sorov_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return SOROV_FAMILYA

async def sorov_familya(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, SOROV_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_FAMILYA
    context.user_data['sorov_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return SOROV_YOSH

async def sorov_yosh(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, SOROV_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_YOSH
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return SOROV_YOSH
    context.user_data['sorov_yosh'] = yosh
    btn = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['back']), KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True))
    return SOROV_TELEFON

async def sorov_telefon(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, SOROV_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return SOROV_TELEFON
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return SOROV_TELEFON
    user = update.message.from_user
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO sorovnama VALUES (?,?,?,?,?,?,?,?,?)", (user.id, user.first_name, user.last_name, user.username, str(datetime.datetime.now()), context.user_data['sorov_ism'], context.user_data['sorov_familya'], context.user_data['sorov_yosh'], phone))
    con.commit()
    con.close()
    await update.message.reply_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  BAKALAVRIAT TANLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_ISM
    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_FAMILYA
    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_YOSH
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return YONALISH_YOSH
    context.user_data['yonalish_yosh'] = yosh
    btn = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['back']), KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True))
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, YONALISH_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return YONALISH_TELEFON
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return YONALISH_TELEFON
    context.user_data['yonalish_telefon'] = phone
    await update.message.reply_text(LANG_TEXTS[lang]['select_bakalavr_title'], parse_mode="Markdown", reply_markup=bakalavr_keyboard(lang))
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
    if key not in BAKALAVR_YONALISHLAR[lang]:
        return TANLA
    yonalish = BAKALAVR_YONALISHLAR[lang][key]
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO bakalavr_royxat VALUES (?,?,?,?,?,?,?,?,?,?)", (user_id, query.from_user.first_name, query.from_user.last_name, query.from_user.username, str(datetime.datetime.now()), context.user_data.get('yonalish_ism'), context.user_data.get('yonalish_familya'), context.user_data.get('yonalish_yosh'), context.user_data.get('yonalish_telefon'), yonalish))
    con.commit()
    con.close()
    username = f"@{query.from_user.username}" if query.from_user.username else f"[{query.from_user.first_name}](tg://user?id={user_id})"
    caption = LANG_TEXTS[lang]['yonalish_channel_caption'].format(user=username, uid=user_id, phone=context.user_data.get('yonalish_telefon'), yonalish=yonalish, ism=context.user_data.get('yonalish_ism'), familya=context.user_data.get('yonalish_familya'), yosh=context.user_data.get('yonalish_yosh'))
    try:
        await context.bot.send_message(CHANNEL_USERNAME, caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kanalga yuborish xato: {e}")
    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📚  MAGISTRATURA TANLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def magistratura_ism(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_ISM)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_ISM
    context.user_data['mag_ism'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_surname'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return MAG_FAMILYA

async def magistratura_familya(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_FAMILYA)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_FAMILYA
    context.user_data['mag_familya'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['enter_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return MAG_YOSH

async def magistratura_yosh(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_YOSH)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_YOSH
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (21 <= int(yosh) <= 65):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return MAG_YOSH
    context.user_data['mag_yosh'] = yosh
    btn = [[KeyboardButton(LANG_TEXTS[lang]['send_phone'], request_contact=True)], [KeyboardButton(LANG_TEXTS[lang]['back']), KeyboardButton(LANG_TEXTS[lang]['cancel'])]]
    await update.message.reply_text(LANG_TEXTS[lang]['phone_intro'], parse_mode="Markdown", reply_markup=ReplyKeyboardMarkup(btn, resize_keyboard=True))
    return MAG_TELEFON

async def magistratura_telefon(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, MAG_TELEFON)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return MAG_TELEFON
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return MAG_TELEFON
    context.user_data['mag_telefon'] = phone
    await update.message.reply_text(LANG_TEXTS[lang]['select_magistratura_title'], parse_mode="Markdown", reply_markup=magistratura_keyboard(lang))
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
    if key not in MAGISTRATURA_YONALISHLAR[lang]:
        return TANLA
    yonalish = MAGISTRATURA_YONALISHLAR[lang][key]
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT OR REPLACE INTO magistratura_royxat VALUES (?,?,?,?,?,?,?,?,?,?)", (user_id, query.from_user.first_name, query.from_user.last_name, query.from_user.username, str(datetime.datetime.now()), context.user_data.get('mag_ism'), context.user_data.get('mag_familya'), context.user_data.get('mag_yosh'), context.user_data.get('mag_telefon'), yonalish))
    con.commit()
    con.close()
    username = f"@{query.from_user.username}" if query.from_user.username else f"[{query.from_user.first_name}](tg://user?id={user_id})"
    caption = LANG_TEXTS[lang]['magistratura_channel_caption'].format(user=username, uid=user_id, phone=context.user_data.get('mag_telefon'), yonalish=yonalish, ism=context.user_data.get('mag_ism'), familya=context.user_data.get('mag_familya'), yosh=context.user_data.get('mag_yosh'))
    try:
        await context.bot.send_message(CHANNEL_USERNAME, caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kanalga yuborish xato: {e}")
    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📅  QABUL YOZILISH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def appointment_name(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, APPOINTMENT_NAME)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return APPOINTMENT_NAME
    context.user_data['app_name'] = update.message.text.strip()
    await update.message.reply_text(LANG_TEXTS[lang]['appointment_phone'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return APPOINTMENT_PHONE

async def appointment_phone(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, APPOINTMENT_PHONE)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return APPOINTMENT_PHONE
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return APPOINTMENT_PHONE
    context.user_data['app_phone'] = phone
    await update.message.reply_text(LANG_TEXTS[lang]['appointment_date'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return APPOINTMENT_DATE

async def appointment_date(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, APPOINTMENT_DATE)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return APPOINTMENT_DATE
    date = update.message.text.strip()
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date):
        await update.message.reply_text("❌ Format: 2024-12-20")
        return APPOINTMENT_DATE
    context.user_data['app_date'] = date
    await update.message.reply_text(LANG_TEXTS[lang]['appointment_time'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
    return APPOINTMENT_TIME

async def appointment_time(update, context):
    lang = get_user_lang(update.effective_user.id)
    guard = await process_step_guard(update, context, APPOINTMENT_TIME)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return APPOINTMENT_TIME
    time = update.message.text.strip()
    if not re.match(r'^\d{2}:\d{2}$', time):
        await update.message.reply_text("❌ Format: 14:00")
        return APPOINTMENT_TIME
    user_id = update.effective_user.id
    con = db_connect()
    cur = con.cursor()
    cur.execute("INSERT INTO appointments (user_id, name, phone, date, time, status, created_at) VALUES (?,?,?,?,?,?,?)", (user_id, context.user_data['app_name'], context.user_data['app_phone'], context.user_data['app_date'], time, 'pending', str(datetime.datetime.now())))
    con.commit()
    con.close()
    admin_text = f"📅 Yangi qabul!\n👤 {context.user_data['app_name']}\n📞 {context.user_data['app_phone']}\n📅 {context.user_data['app_date']}\n⏰ {time}"
    try:
        await context.bot.send_message(ADMIN_USERNAME, admin_text)
    except:
        pass
    await update.message.reply_text(LANG_TEXTS[lang]['appointment_success'].format(date=context.user_data['app_date'], time=time), parse_mode="Markdown", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ✏️  TAHRIRLASH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def edit_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_user_lang(query.from_user.id)
    if data == "edit_back":
        await query.edit_message_text(LANG_TEXTS[lang]['edit_title'], reply_markup=edit_menu_markup(lang))
        return TANLA
    elif data == "edit_name":
        await query.message.reply_text(LANG_TEXTS[lang]['edit_name'], reply_markup=cancel_back_markup(lang))
        return EDIT_SOROV_NAME
    elif data == "edit_surname":
        await query.message.reply_text(LANG_TEXTS[lang]['edit_surname'], reply_markup=cancel_back_markup(lang))
        return EDIT_SOROV_SURNAME
    elif data == "edit_age":
        await query.message.reply_text(LANG_TEXTS[lang]['edit_age'], reply_markup=cancel_back_markup(lang))
        return EDIT_SOROV_AGE
    elif data == "edit_phone":
        await query.message.reply_text(LANG_TEXTS[lang]['edit_phone'], reply_markup=cancel_back_markup(lang))
        return EDIT_SOROV_PHONE
    return TANLA

async def edit_name_handler(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, EDIT_SOROV_NAME)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return EDIT_SOROV_NAME
    con = db_connect()
    cur = con.cursor()
    cur.execute("UPDATE sorovnama SET ism=? WHERE id=?", (update.message.text.strip(), user_id))
    con.commit()
    con.close()
    await update.message.reply_text(LANG_TEXTS[lang]['edit_success'], reply_markup=main_menu_markup(lang))
    return TANLA

async def edit_surname_handler(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, EDIT_SOROV_SURNAME)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return EDIT_SOROV_SURNAME
    con = db_connect()
    cur = con.cursor()
    cur.execute("UPDATE sorovnama SET familya=? WHERE id=?", (update.message.text.strip(), user_id))
    con.commit()
    con.close()
    await update.message.reply_text(LANG_TEXTS[lang]['edit_success'], reply_markup=main_menu_markup(lang))
    return TANLA

async def edit_age_handler(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, EDIT_SOROV_AGE)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return EDIT_SOROV_AGE
    age = update.message.text.strip()
    if not age.isdigit() or not (14 <= int(age) <= 60):
        await update.message.reply_text(LANG_TEXTS[lang]['invalid_age'], parse_mode="Markdown")
        return EDIT_SOROV_AGE
    con = db_connect()
    cur = con.cursor()
    cur.execute("UPDATE sorovnama SET yosh=? WHERE id=?", (int(age), user_id))
    con.commit()
    con.close()
    await update.message.reply_text(LANG_TEXTS[lang]['edit_success'], reply_markup=main_menu_markup(lang))
    return TANLA

async def edit_phone_handler(update, context):
    user_id = update.effective_user.id
    lang = get_user_lang(user_id)
    guard = await process_step_guard(update, context, EDIT_SOROV_PHONE)
    if guard == "FORCE_CAN_MENU": return TANLA
    if guard == "FORCE_STAY": return EDIT_SOROV_PHONE
    phone = None
    if update.message.contact:
        phone = update.message.contact.phone_number
    elif update.message.text:
        phone = validate_phone(update.message.text.strip())
        if not phone:
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown")
            return EDIT_SOROV_PHONE
    con = db_connect()
    cur = con.cursor()
    cur.execute("UPDATE sorovnama SET telefon=? WHERE id=?", (phone, user_id))
    con.commit()
    con.close()
    await update.message.reply_text(LANG_TEXTS[lang]['edit_success'], reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📄  NAMUNALAR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def samples_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    lang = get_user_lang(query.from_user.id)
    samples = {
        'sample_diplom': "📄 *Diplom/Attestat namunasi*\n\nRangli nusxa, aniq ko'rinadigan bo'lishi kerak.",
        'sample_passport': "🪪 *Pasport namunasi*\n\n1-2 sahifalar, rangli nusxa.",
        'sample_medical': "🏥 *Tibbiy ma'lumotnoma namunasi*\n\n0.86 shakl, rasmiy muhr bilan.",
        'sample_photo': "📸 *Rasm talablari*\n\n3x4, oq fon, formal kiyim."
    }
    if data in samples:
        await query.edit_message_text(samples[data], parse_mode="Markdown")
        await context.bot.send_message(query.from_user.id, "🔙 /start bosing")
    elif data == "samples_back":
        t = LANG_TEXTS[lang]
        await query.edit_message_text(t['samples_title'], parse_mode="Markdown", reply_markup=samples_keyboard(lang))

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👤  ADMIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def admin_statistika(update, context):
    if update.effective_user.username != "Saman2611":
        await update.message.reply_text("❌ Faqat admin!")
        return
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM sorovnama")
    sorov = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM bakalavr_royxat")
    bak = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM magistratura_royxat")
    mag = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM appointments")
    app = cur.fetchone()[0]
    con.close()
    await update.message.reply_text(f"📊 *STATISTIKA*\n\n📝 So'rovnoma: {sorov}\n🎓 Bakalavriat: {bak}\n📚 Magistratura: {mag}\n📅 Qabullar: {app}", parse_mode="Markdown")

async def admin_export(update, context):
    if update.effective_user.username != "Saman2611":
        await update.message.reply_text("❌ Faqat admin!")
        return
    con = db_connect()
    for table in ['sorovnama', 'bakalavr_royxat', 'magistratura_royxat', 'appointments']:
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
    for table in ['sorovnama', 'bakalavr_royxat', 'magistratura_royxat']:
        cur.execute(f"SELECT ism, familya, telefon FROM {table} WHERE ism LIKE ? OR familya LIKE ? OR telefon LIKE ?", (f'%{term}%', f'%{term}%', f'%{term}%'))
        rows = cur.fetchall()
        if rows:
            text += f"📋 {table}:\n"
            for row in rows:
                text += f"• {row[0]} {row[1]} | {row[2]}\n"
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
            TANLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher), CallbackQueryHandler(bakalavr_callback), CallbackQueryHandler(magistratura_callback), CallbackQueryHandler(edit_callback, pattern="^edit_"), CallbackQueryHandler(samples_callback, pattern="^sample_|^samples_back$")],
            FAQ_STATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            APPOINTMENT_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, appointment_name)],
            APPOINTMENT_PHONE: [MessageHandler(filters.ALL, appointment_phone)],
            APPOINTMENT_DATE: [MessageHandler(filters.TEXT & ~filters.COMMAND, appointment_date)],
            APPOINTMENT_TIME: [MessageHandler(filters.TEXT & ~filters.COMMAND, appointment_time)],
            EDIT_SOROV_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_name_handler)],
            EDIT_SOROV_SURNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_surname_handler)],
            EDIT_SOROV_AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, edit_age_handler)],
            EDIT_SOROV_PHONE: [MessageHandler(filters.ALL, edit_phone_handler)],
            HUJJAT_FORMAT_1: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_2: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_3: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_FORMAT_4: [CallbackQueryHandler(format_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            HUJJAT_1: [MessageHandler(filters.ALL, hujjat_1)], HUJJAT_2: [MessageHandler(filters.ALL, hujjat_2)],
            HUJJAT_3: [MessageHandler(filters.ALL, hujjat_3)], HUJJAT_4: [MessageHandler(filters.ALL, hujjat_4)],
            SOROV_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_ism)], SOROV_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_familya)],
            SOROV_YOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_yosh)], SOROV_TELEFON: [MessageHandler(filters.ALL, sorov_telefon)],
            YONALISH_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)], YONALISH_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)],
            YONALISH_YOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)], YONALISH_TELEFON: [MessageHandler(filters.ALL, yonalish_telefon)],
            YONALISH_TANLASH: [CallbackQueryHandler(bakalavr_callback)],
            MAG_ISM: [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_ism)], MAG_FAMILYA: [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_familya)],
            MAG_YOSH: [MessageHandler(filters.TEXT & ~filters.COMMAND, magistratura_yosh)], MAG_TELEFON: [MessageHandler(filters.ALL, magistratura_telefon)],
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
