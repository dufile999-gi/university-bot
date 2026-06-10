from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import re
import os
import sqlite3
import datetime
import logging
import csv
import io
import asyncio
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, 
    ReplyKeyboardMarkup, KeyboardButton, Update
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters, ContextTypes
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
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"  # ✅ BU QATOR QO'SHILDI!
ADMIN_ID = 8596949743
ADMIN_PHONE = "+998996844483"
DB_PATH = "universitet.db"
ABOUT_PHOTO_URL = "https://storage.googleapis.com/createsite-uz-bucket/blog/1722071060_chirchiq-auezov.jpg"

# Universitet rasmlari
UNI_PHOTOS = [
    "https://storage.googleapis.com/createsite-uz-bucket/blog/1722071060_chirchiq-auezov.jpg",
]

# Qabul muddati
QABUL_START = (6, 1)
QABUL_END = (9, 1)

logging.basicConfig(format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# Konversiya holatlari
TIL_TANLASH = "til_tanlash"
TANLA = "tanla"
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = "hf1", "hf2", "hf3", "hf4"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "h1", "h2", "h3", "h4"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON, YONALISH_TANLASH = "yi", "yf", "yy", "yt", "yonalish_tanlash"
MAG_ISM, MAG_FAMILYA, MAG_YOSH, MAG_TELEFON, MAG_TANLASH = "mi", "mf", "my", "mt", "mag_tanlash"
ADMIN_REVIEW = "admin_review"
ADMIN_BROADCAST = "admin_broadcast"
ADMIN_SETTINGS = "admin_settings"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🌐  TIL LUG'ATI
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
        'menu_status': "📊 Hujjat holati",
        'menu_schedule': "📅 Imtihon jadvali",
        'menu_contact': "📞 Aloqa",
        'menu_admin': "⚙️ Admin panel",
        'back': "🔙 Orqaga",
        'cancel': "❌ Bekor qilish",
        'change_lang': "🌐 Tilni o'zgartirish",
        'about_title': "🏛 *M.AUEZOV NOMIDAGI JANUBIY QOZOG'ISTON UNIVERSITETI*",
        'about_desc': "📌 *Umumiy ma'lumot:*\n• Tashkil etilgan: 1943 yil\n• Rektor: Qojamjarov Gulmurat Tolibayevich\n• Talabalar soni: 15 000+\n• Fakultetlar: 12 ta\n• Yo'nalishlar: 50+",
        'about_history': "📜 *Tarixi:*\nUniversitet 1943 yilda Chimkent pedagogika instituti sifatida tashkil etilgan.",
        'about_faculties': "🏛 *FAKULTETLAR:*\n1. Fizika-matematika\n2. Kimyo-biologiya\n3. Filologiya\n4. Tarix\n5. Iqtisodiyot\n6. Huquq\n7. Pedagogika\n8. Axborot texnologiyalari\n9. Muhandislik\n10. Sport\n11. Xorijiy tillar\n12. San'at",
        'about_international': "🌍 *Xalqaro hamkorlik:*\n• Erasmus+ dasturi\n• Dual diplom dasturlari\n• 50 dan ortiq xorijiy universitetlar",
        'about_achievements': "🏆 *Yutuqlar:*\n• Respublika olimpiadalari sovrindorlari\n• Xalqaro grantlar\n• Ilmiy loyihalar",
        'about_contact': "📞 *Bog'lanish:*\n📍 Manzil: Chirchiq shahri\n📞 Telefon: {phone}\n💬 Telegram: {username}",
        'bakalavr_text': "👑 *BAKALAVRIAT YO'NALISHLARI (10 ta)*\n\n🔬 Biotexnologiya\n🌍 Ekologiya\n💻 Axborot tizimlar\n⚙️ Avtomatizatsiya\n🚚 Transport\n⚡ Elektroenergetika\n🧑‍🏫 Pedagogika\n🧠 Sun'iy intellekt\n💼 Hisob va audit\n✈️ Turizm",
        'bakalavr_detail': "📚 *Bakalavriat haqida:*\n• O'qish muddati: 4 yil\n• Kunduzgi va sirtqi bo'lim",
        'magistratura_text': "🎓 *MAGISTRATURA YO'NALISHLARI (4 ta)*\n\n📊 Iqtisodiyot\n⚖️ Yurisprudensiya\n💻 Axborot tizimlari\n🌍 Ekologiya",
        'magistratura_detail': "📚 *Magistratura haqida:*\n• O'qish muddati: 2 yil",
        'hujjat_intro': "📋 *KERAKLI HUJJATLAR RO'YXATI*\n\n1️⃣ Diplom/Attestat\n2️⃣ Pasport\n3️⃣ Med-ma'lumotnoma\n4️⃣ 3x4 rasm\n\n🟢 *1-Bosqich:*\n❓ Formatni tanlang:",
        'format_rasm': "🖼️ Rasm",
        'format_fayl': "📎 Fayl",
        'enter_name': "✍️ *Ismingizni kiriting:*",
        'enter_surname': "✍️ *Familiyangizni kiriting:*",
        'enter_age': "✍️ *Yoshingizni kiriting:*",
        'invalid_age': "⚠️ Xato! Bakalavriat: 14-60, Magistratura: 21-65",
        'send_phone': "📞 Telefon raqamni yuborish",
        'phone_intro': "📞 *Telefon raqamingizni kiriting:*\n📝 *Namuna:* `+998901234567`",
        'invalid_phone': "⚠️ Xato! +998901234567 formatida yozing",
        'success_received': "✅ Qabul qilindi!",
        'all_docs_success': "🎉 Barcha hujjatlar topshirildi!",
        'select_bakalavr_title': "🎓 *BAKALAVRIAT YO'NALISHLARIDAN BIRINI TANLANG:*",
        'select_magistratura_title': "🎓 *MAGISTRATURA YO'NALISHLARIDAN BIRINI TANLANG:*",
        'reg_success': "🎉 Yo'nalish muvaffaqiyatli tanlandi!",
        'reg_cancelled': "❌ Jarayon bekor qilindi.",
        'unknown': "❓ Tushunarsiz buyruq",
        'error_need_file': "⚠️ Fayl formatida yuboring!",
        'error_need_photo': "⚠️ Rasm formatida yuboring!",
        'warning_in_progress': "⚠️ Jarayondasiz! Iltimos so'ralgan ma'lumotni kiriting.",
        'channel_caption': "📋 *Yangi Hujjat!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📂 Hujjat: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *BAKALAVRIAT TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n📚 Yo'nalish: *{yonalish}*\n👤 Ism: {ism}\n👤 Fam: {familya}\n🎂 Yosh: {yosh}",
        'magistratura_channel_caption': "📚 *MAGISTRATURA TANLANDI!*\n\n👤 Foydalanuvchi: {user}\n🆔 ID: `{uid}`\n📞 Tel: `{phone}`\n🎓 Magistratura: *{yonalish}*\n👤 Ism: {ism}\n👤 Fam: {familya}\n🎂 Yosh: {yosh}",
        'manzil_text': "📍 *Universitet manzili:*\nChirchiq shahri, Toshkent viloyati\n🗺 [Google Maps](https://maps.google.com)",
        'schedule_title': "📅 *IMTIHON JADVALI 2024*\n\n",
        'schedule_bakalavr': "🎓 *Bakalavriat imtihonlari:*\n📆 10-avgust – 20-avgust 2024",
        'schedule_magistratura': "📚 *Magistratura imtihonlari:*\n📆 5-avgust – 15-avgust 2024",
        'schedule_note': "📌 *Eslatma:* Imtihon joyi haqida alohida xabar beriladi.",
        'status_title': "📊 *HUJJAT HOLATINGIZ*\n\n",
        'status_not_found': "❌ Siz hali hujjat topshirmagansiz!",
        'status_docs': "📄 *Hujjatlar holati:*\n",
        'status_doc1': "1️⃣ Diplom/Attestat: {status}",
        'status_doc2': "2️⃣ Pasport: {status}",
        'status_doc3': "3️⃣ Med-ma'lumotnoma: {status}",
        'status_doc4': "4️⃣ 3×4 rasm: {status}",
        'status_approved': "✅ Qabul qilindi",
        'status_pending': "⏳ Tekshirilmoqda",
        'status_rejected': "❌ Qayta topshiring",
        'status_not_submitted': "⭕ Topshirilmagan",
        'status_yonalish': "🎓 *Yo'nalish:* {yonalish}\n",
        'status_phone': "📞 *Telefon:* {phone}\n",
        'reminder_title': "🔔 *ESLATMA!*\n\n",
        'reminder_7days': "📢 Hujjat topshirish muddatiga *7 kun* qoldi!",
        'reminder_3days': "⚠️ Hujjat topshirish muddatiga *3 kun* qoldi!",
        'reminder_1day': "🚨 *OXIRGI KUN!*",
        'deadline_passed': "⛔ *QABUL YOPILDI!*",
        'admin_title': "⚙️ *ADMIN PANEL*\n\n👋 Xush kelibsiz, Administrator!",
        'admin_stats': "📊 Statistika",
        'admin_review': "📋 Hujjat tekshirish",
        'admin_broadcast': "📨 Ommaviy xabar",
        'admin_settings': "⚙️ Sozlamalar",
        'admin_users': "👥 Foydalanuvchilar",
        'admin_export': "📁 Eksport",
        'admin_back': "🔙 Menyuga qaytish",
        'stats_title': "📊 *STATISTIKA MA'LUMOTLARI*\n\n",
        'stats_bakalavr': "🎓 Bakalavriat: {count} ta",
        'stats_magistratura': "📚 Magistratura: {count} ta",
        'stats_total': "👥 Jami foydalanuvchilar: {count} ta",
        'stats_docs': "📄 Hujjatlar:\n1️⃣ Diplom: {d1}\n2️⃣ Pasport: {d2}\n3️⃣ Med: {d3}\n4️⃣ Rasm: {d4}",
        'stats_approved': "✅ Tasdiqlangan: {count}",
        'stats_rejected': "❌ Rad etilgan: {count}",
        'stats_days': "⏰ Qabul tugashiga: {days} kun",
        'review_title': "📋 *HUJJAT TEKSHIRUVI*\n\n",
        'review_pending': "⏳ Holat: Tekshirilmoqda",
        'review_approved': "✅ Holat: Qabul qilindi",
        'review_rejected': "❌ Holat: Qayta topshiring\n\nSabab: {reason}",
        'review_approve': "✅ Tasdiqlash",
        'review_reject': "❌ Rad etish",
        'review_reason': "✍️ Rad etish sababini kiriting:",
        'review_notification': "📨 *Hujjatingiz tekshirildi!*\n\n{status}",
        'broadcast_title': "📨 *OMMAVIY XABAR YUBORISH*\n\nXabar matnini kiriting:",
        'broadcast_sending': "⏳ Xabar yuborilmoqda...",
        'broadcast_sent': "✅ Xabar yuborildi!\n\n📨 Yuborilgan: {sent}\n❌ Yuborilmagan: {failed}",
        'settings_title': "⚙️ *SOZLAMALAR*\n\n",
        'settings_deadline': "📅 Qabul muddati",
        'settings_info': "ℹ️ Bot haqida",
        'settings_reset': "🔄 Qayta ishga tushirish",
        'deadline_current': "📅 *Joriy qabul muddati:*\n{start} - {end}",
        'deadline_set': "🔄 Yangi muddatni kiriting (YYYY-MM-DD):",
        'users_title': "👥 *FOYDALANUVCHILAR RO'YXATI*\n\n",
        'users_count': "Jami: {count} ta foydalanuvchi",
        'contact_text': "📞 *BIZ BILAN BOG'LANISH*\n\n📞 Telefon: {phone}\n💬 Telegram: {username}"
    },
    'ru': {
        'welcome': "🏛 *Южно-Казахстанский университет им. М.Ауезова* Добро пожаловать!",
        'lang_selected': "✅ *Русский язык выбран*!",
        'menu_about': "🏛 Об университете",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Подать документы",
        'menu_manzil': "📍 Адрес",
        'menu_bakalavr_tanlash': "📋 Направления бакалавриата",
        'menu_magistratura_tanlash': "🎓 Направления магистратуры",
        'menu_status': "📊 Статус документов",
        'menu_schedule': "📅 Расписание экзаменов",
        'menu_contact': "📞 Контакты",
        'menu_admin': "⚙️ Админ панель",
        'back': "🔙 Назад",
        'cancel': "❌ Отмена",
        'change_lang': "🌐 Сменить язык",
        'about_title': "🏛 *ЮЖНО-КАЗАХСТАНСКИЙ УНИВЕРСИТЕТ ИМ. М.АУЕЗОВА*",
        'about_desc': "📌 *Общая информация:*\n• Основан: 1943 г.\n• Студентов: 15 000+",
        'about_history': "📜 *История:*\nОснован в 1943 году.",
        'about_faculties': "🏛 *ФАКУЛЬТЕТЫ:*\n12 факультетов",
        'about_international': "🌍 *Международное сотрудничество:*\n• Erasmus+\n• Двойные дипломы",
        'about_achievements': "🏆 *Достижения:*\nПобедители олимпиад",
        'about_contact': "📞 *Контакты:*\n📍 Адрес: г.Чирчик\n📞 Телефон: {phone}\n💬 Telegram: {username}",
        'bakalavr_text': "👑 *НАПРАВЛЕНИЯ БАКАЛАВРИАТА*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Информационные системы\n⚙️ Автоматизация\n🚚 Транспорт\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Искусственный интеллект\n💼 Учет и аудит\n✈️ Туризм",
        'bakalavr_detail': "📚 *О бакалавриате:*\n• Срок: 4 года",
        'magistratura_text': "🎓 *НАПРАВЛЕНИЯ МАГИСТРАТУРЫ*\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Информационные системы\n🌍 Экология",
        'magistratura_detail': "📚 *О магистратуре:*\n• Срок: 2 года",
        'hujjat_intro': "📋 *СПИСОК ДОКУМЕНТОВ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ Мед-справка\n4️⃣ Фото 3x4\n\n🟢 *1-этап:*\n❓ Выберите формат:",
        'format_rasm': "🖼️ Изображение",
        'format_fayl': "📎 Файл",
        'enter_name': "✍️ *Введите имя:*",
        'enter_surname': "✍️ *Введите фамилию:*",
        'enter_age': "✍️ *Введите возраст:*",
        'invalid_age': "⚠️ Ошибка! Бакалавриат: 14-60, Магистратура: 21-65",
        'send_phone': "📞 Отправить номер",
        'phone_intro': "📞 *Введите номер телефона:*\n📝 *Пример:* `+998901234567`",
        'invalid_phone': "⚠️ Ошибка! Формат: +998901234567",
        'success_received': "✅ Принято!",
        'all_docs_success': "🎉 Все документы поданы!",
        'select_bakalavr_title': "🎓 *ВЫБЕРИТЕ НАПРАВЛЕНИЕ БАКАЛАВРИАТА:*",
        'select_magistratura_title': "🎓 *ВЫБЕРИТЕ НАПРАВЛЕНИЕ МАГИСТРАТУРЫ:*",
        'reg_success': "🎉 Направление успешно выбрано!",
        'reg_cancelled': "❌ Процесс отменен.",
        'unknown': "❓ Неизвестная команда",
        'error_need_file': "⚠️ Отправьте файл!",
        'error_need_photo': "⚠️ Отправьте фото!",
        'warning_in_progress': "⚠️ Вы в процессе!",
        'channel_caption': "📋 *Новый документ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📂 Документ: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *ВЫБРАН БАКАЛАВРИАТ!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n📚 Направление: *{yonalish}*\n👤 Имя: {ism}\n👤 Фам: {familya}\n🎂 Возраст: {yosh}",
        'magistratura_channel_caption': "📚 *ВЫБРАНА МАГИСТРАТУРА!*\n\n👤 Пользователь: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n🎓 Магистратура: *{yonalish}*\n👤 Имя: {ism}\n👤 Фам: {familya}\n🎂 Возраст: {yosh}",
        'manzil_text': "📍 *Адрес:* г.Чирчик, Ташкентская область\n🗺 [Google Maps](https://maps.google.com)",
        'schedule_title': "📅 *РАСПИСАНИЕ ЭКЗАМЕНОВ 2024*\n\n",
        'schedule_bakalavr': "🎓 *Бакалавриат:*\n📆 10-20 августа 2024",
        'schedule_magistratura': "📚 *Магистратура:*\n📆 5-15 августа 2024",
        'schedule_note': "📌 *Примечание:* О месте сообщим дополнительно.",
        'status_title': "📊 *СТАТУС ДОКУМЕНТОВ*\n\n",
        'status_not_found': "❌ Вы еще не подавали документы!",
        'status_docs': "📄 *Статус документов:*\n",
        'status_doc1': "1️⃣ Диплом/Аттестат: {status}",
        'status_doc2': "2️⃣ Паспорт: {status}",
        'status_doc3': "3️⃣ Мед-справка: {status}",
        'status_doc4': "4️⃣ Фото 3×4: {status}",
        'status_approved': "✅ Принято",
        'status_pending': "⏳ На проверке",
        'status_rejected': "❌ Отправьте заново",
        'status_not_submitted': "⭕ Не подано",
        'status_yonalish': "🎓 *Направление:* {yonalish}\n",
        'status_phone': "📞 *Телефон:* {phone}\n",
        'reminder_title': "🔔 *НАПОМИНАНИЕ!*\n\n",
        'reminder_7days': "📢 До окончания приема *7 дней*!",
        'reminder_3days': "⚠️ До окончания приема *3 дня*!",
        'reminder_1day': "🚨 *ПОСЛЕДНИЙ ДЕНЬ!*",
        'deadline_passed': "⛔ *ПРИЕМ ЗАКРЫТ!*",
        'admin_title': "⚙️ *АДМИН ПАНЕЛЬ*\n\n👋 Добро пожаловать!",
        'admin_stats': "📊 Статистика",
        'admin_review': "📋 Проверить документы",
        'admin_broadcast': "📨 Рассылка",
        'admin_settings': "⚙️ Настройки",
        'admin_users': "👥 Пользователи",
        'admin_export': "📁 Экспорт",
        'admin_back': "🔙 Назад",
        'stats_title': "📊 *СТАТИСТИКА*\n\n",
        'stats_bakalavr': "🎓 Бакалавриат: {count}",
        'stats_magistratura': "📚 Магистратура: {count}",
        'stats_total': "👥 Всего: {count}",
        'stats_docs': "📄 Документы:\n1️⃣ Диплом: {d1}\n2️⃣ Паспорт: {d2}\n3️⃣ Мед: {d3}\n4️⃣ Фото: {d4}",
        'stats_approved': "✅ Одобрено: {count}",
        'stats_rejected': "❌ Отклонено: {count}",
        'stats_days': "⏰ До конца: {days} дней",
        'review_title': "📋 *ПРОВЕРКА ДОКУМЕНТОВ*\n\n",
        'review_pending': "⏳ Статус: На проверке",
        'review_approved': "✅ Статус: Принято",
        'review_rejected': "❌ Статус: Отправьте заново\n\nПричина: {reason}",
        'review_approve': "✅ Одобрить",
        'review_reject': "❌ Отклонить",
        'review_reason': "✍️ Введите причину отказа:",
        'review_notification': "📨 *Ваши документы проверены!*\n\n{status}",
        'broadcast_title': "📨 *РАССЫЛКА СООБЩЕНИЙ*\n\nВведите текст:",
        'broadcast_sending': "⏳ Отправка...",
        'broadcast_sent': "✅ Отправлено!\n\n📨 Успешно: {sent}\n❌ Ошибок: {failed}",
        'settings_title': "⚙️ *НАСТРОЙКИ*\n\n",
        'settings_deadline': "📅 Срок приема",
        'settings_info': "ℹ️ О боте",
        'settings_reset': "🔄 Перезапуск",
        'deadline_current': "📅 *Текущий срок:*\n{start} - {end}",
        'deadline_set': "🔄 Введите новый срок (ГГГГ-ММ-ДД):",
        'users_title': "👥 *ПОЛЬЗОВАТЕЛИ*\n\n",
        'users_count': "Всего: {count}",
        'contact_text': "📞 *КОНТАКТЫ*\n\n📞 Телефон: {phone}\n💬 Telegram: {username}"
    },
    'kk': {
        'welcome': "🏛 *М.Әуезов атындағы ОҚУ* Шыршық филиалына қош келдіңіз!",
        'lang_selected': "✅ *Қазақ тілі таңдалды*!",
        'menu_about': "🏛 Университет туралы",
        'menu_bakalavr': "🎓 Бакалавриат",
        'menu_magistratura': "📚 Магистратура",
        'menu_hujjat': "📝 Құжат тапсыру",
        'menu_manzil': "📍 Мекенжай",
        'menu_bakalavr_tanlash': "📋 Бакалавриат бағыттары",
        'menu_magistratura_tanlash': "🎓 Магистратура бағыттары",
        'menu_status': "📊 Құжат күйі",
        'menu_schedule': "📅 Емтихан кестесі",
        'menu_contact': "📞 Байланыс",
        'menu_admin': "⚙️ Әкім панелі",
        'back': "🔙 Артқа",
        'cancel': "❌ Болдырмау",
        'change_lang': "🌐 Тілді өзгерту",
        'about_title': "🏛 *М.ӘУЕЗОВ АТЫНДАҒЫ ОҚУ*",
        'about_desc': "📌 *Жалпы мәлімет:*\n• Құрылған: 1943 ж\n• Студенттер: 15 000+",
        'about_history': "📜 *Тарихы:*\n1943 жылы құрылған.",
        'about_faculties': "🏛 *ФАКУЛЬТЕТТЕР:*\n12 факультет",
        'about_international': "🌍 *Халықаралық ынтымақтастық:*\n• Erasmus+\n• Қос диплом",
        'about_achievements': "🏆 *Жетістіктер:*\nОлимпиада жеңімпаздары",
        'about_contact': "📞 *Байланыс:*\n📍 Мекенжай: Шыршық қ.\n📞 Телефон: {phone}\n💬 Telegram: {username}",
        'bakalavr_text': "👑 *БАКАЛАВРИАТ БАҒЫТТАРЫ*\n\n🔬 Биотехнология\n🌍 Экология\n💻 Ақпараттық жүйелер\n⚙️ Автоматтандыру\n🚚 Көлік\n⚡ Электроэнергетика\n🧑‍🏫 Педагогика\n🧠 Жасанды интеллект\n💼 Есеп және аудит\n✈️ Туризм",
        'bakalavr_detail': "📚 *Бакалавриат туралы:*\n• Оқу мерзімі: 4 жыл",
        'magistratura_text': "🎓 *МАГИСТРАТУРА БАҒЫТТАРЫ*\n\n📊 Экономика\n⚖️ Юриспруденция\n💻 Ақпараттық жүйелер\n🌍 Экология",
        'magistratura_detail': "📚 *Магистратура туралы:*\n• Оқу мерзімі: 2 жыл",
        'hujjat_intro': "📋 *ҚҰЖАТТАР ТІЗІМІ*\n\n1️⃣ Диплом/Аттестат\n2️⃣ Паспорт\n3️⃣ Мед-анықтама\n4️⃣ 3x4 сурет\n\n🟢 *1-кезең:*\n❓ Форматты таңдаңыз:",
        'format_rasm': "🖼️ Сурет",
        'format_fayl': "📎 Файл",
        'enter_name': "✍️ *Атыңызды жазыңыз:*",
        'enter_surname': "✍️ *Тегіңізді жазыңыз:*",
        'enter_age': "✍️ *Жасыңызды жазыңыз:*",
        'invalid_age': "⚠️ Қате! Бакалавриат: 14-60, Магистратура: 21-65",
        'send_phone': "📞 Телефон жіберу",
        'phone_intro': "📞 *Телефон нөміріңізді жазыңыз:*\n📝 *Мысалы:* `+998901234567`",
        'invalid_phone': "⚠️ Қате! +998901234567 форматында жазыңыз",
        'success_received': "✅ Қабылданды!",
        'all_docs_success': "🎉 Барлық құжаттар тапсырылды!",
        'select_bakalavr_title': "🎓 *БАКАЛАВРИАТ БАҒЫТТАРЫН ТАҢДАҢЫЗ:*",
        'select_magistratura_title': "🎓 *МАГИСТРАТУРА БАҒЫТТАРЫН ТАҢДАҢЫЗ:*",
        'reg_success': "🎉 Бағыт сәтті таңдалды!",
        'reg_cancelled': "❌ Процесс болдырылды.",
        'unknown': "❓ Белгісіз команда",
        'error_need_file': "⚠️ Файл жіберіңіз!",
        'error_need_photo': "⚠️ Сурет жіберіңіз!",
        'warning_in_progress': "⚠️ Процесс жүріп жатыр!",
        'channel_caption': "📋 *Жаңа Құжат!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📂 Құжат: *{doc_name}*",
        'yonalish_channel_caption': "🎓 *БАКАЛАВРИАТ ТАҢДАЛДЫ!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n📚 Бағыт: *{yonalish}*\n👤 Аты: {ism}\n👤 Тегі: {familya}\n🎂 Жасы: {yosh}",
        'magistratura_channel_caption': "📚 *МАГИСТРАТУРА ТАҢДАЛДЫ!*\n\n👤 Қолданушы: {user}\n🆔 ID: `{uid}`\n📞 Тел: `{phone}`\n🎓 Магистратура: *{yonalish}*\n👤 Аты: {ism}\n👤 Тегі: {familya}\n🎂 Жасы: {yosh}",
        'manzil_text': "📍 *Мекенжай:* Шыршық қ., Ташкент обл.\n🗺 [Google Maps](https://maps.google.com)",
        'schedule_title': "📅 *ЕМТИХАН КЕСТЕСІ 2024*\n\n",
        'schedule_bakalavr': "🎓 *Бакалавриат:*\n📆 10-20 тамыз 2024",
        'schedule_magistratura': "📚 *Магистратура:*\n📆 5-15 тамыз 2024",
        'schedule_note': "📌 *Ескерту:* Орны туралы қосымша хабарланады.",
        'status_title': "📊 *ҚҰЖАТ КҮЙІҢІЗ*\n\n",
        'status_not_found': "❌ Сіз әлі құжат тапсырған жоқсыз!",
        'status_docs': "📄 *Құжаттар күйі:*\n",
        'status_doc1': "1️⃣ Диплом/Аттестат: {status}",
        'status_doc2': "2️⃣ Паспорт: {status}",
        'status_doc3': "3️⃣ Мед-анықтама: {status}",
        'status_doc4': "4️⃣ 3×4 сурет: {status}",
        'status_approved': "✅ Қабылданды",
        'status_pending': "⏳ Тексерілуде",
        'status_rejected': "❌ Қайта тапсырыңыз",
        'status_not_submitted': "⭕ Тапсырылмаған",
        'status_yonalish': "🎓 *Бағыт:* {yonalish}\n",
        'status_phone': "📞 *Телефон:* {phone}\n",
        'reminder_title': "🔔 *ЕСКЕРТУ!*\n\n",
        'reminder_7days': "📢 Құжат тапсыруға *7 күн* қалды!",
        'reminder_3days': "⚠️ Құжат тапсыруға *3 күн* қалды!",
        'reminder_1day': "🚨 *СОҢҒЫ КҮН!*",
        'deadline_passed': "⛔ *ҚАБЫЛДАУ БІТТІ!*",
        'admin_title': "⚙️ *ӘКІМ ПАНЕЛІ*\n\n👋 Қош келдіңіз!",
        'admin_stats': "📊 Статистика",
        'admin_review': "📋 Құжаттарды тексеру",
        'admin_broadcast': "📨 Хабарлама жіберу",
        'admin_settings': "⚙️ Баптаулар",
        'admin_users': "👥 Пайдаланушылар",
        'admin_export': "📁 Экспорт",
        'admin_back': "🔙 Мәзірге оралу",
        'stats_title': "📊 *СТАТИСТИКА*\n\n",
        'stats_bakalavr': "🎓 Бакалавриат: {count}",
        'stats_magistratura': "📚 Магистратура: {count}",
        'stats_total': "👥 Барлығы: {count}",
        'stats_docs': "📄 Құжаттар:\n1️⃣ Диплом: {d1}\n2️⃣ Паспорт: {d2}\n3️⃣ Мед: {d3}\n4️⃣ Сурет: {d4}",
        'stats_approved': "✅ Мақұлданған: {count}",
        'stats_rejected': "❌ Қайтарылған: {count}",
        'stats_days': "⏰ Қабылдау бітуге: {days} күн",
        'review_title': "📋 *ҚҰЖАТТАРДЫ ТЕКСЕРУ*\n\n",
        'review_pending': "⏳ Күйі: Тексерілуде",
        'review_approved': "✅ Күйі: Қабылданды",
        'review_rejected': "❌ Күйі: Қайта тапсырыңыз\n\nСебебі: {reason}",
        'review_approve': "✅ Мақұлдау",
        'review_reject': "❌ Қайтару",
        'review_reason': "✍️ Қайтару себебін жазыңыз:",
        'review_notification': "📨 *Құжаттарыңыз тексерілді!*\n\n{status}",
        'broadcast_title': "📨 *ХАБАРЛАМА ЖІБЕРУ*\n\nМәтінді енгізіңіз:",
        'broadcast_sending': "⏳ Жіберілуде...",
        'broadcast_sent': "✅ Жіберілді!\n\n📨 Жеткізілген: {sent}\n❌ Қате: {failed}",
        'settings_title': "⚙️ *БАПТАУЛАР*\n\n",
        'settings_deadline': "📅 Қабылдау мерзімі",
        'settings_info': "ℹ️ Бот туралы",
        'settings_reset': "🔄 Қайта іске қосу",
        'deadline_current': "📅 *Ағымдағы мерзім:*\n{start} - {end}",
        'deadline_set': "🔄 Жаңа мерзім (ЖЖЖЖ-АА-КК):",
        'users_title': "👥 *ПАЙДАЛАНУШЫЛАР*\n\n",
        'users_count': "Барлығы: {count}",
        'contact_text': "📞 *БАЙЛАНЫС*\n\n📞 Телефон: {phone}\n💬 Telegram: {username}"
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
        CREATE TABLE IF NOT EXISTS hujjat_status (
            user_id INTEGER PRIMARY KEY, 
            doc1 INTEGER DEFAULT 0, 
            doc2 INTEGER DEFAULT 0, 
            doc3 INTEGER DEFAULT 0, 
            doc4 INTEGER DEFAULT 0,
            doc1_status TEXT DEFAULT 'pending',
            doc2_status TEXT DEFAULT 'pending',
            doc3_status TEXT DEFAULT 'pending',
            doc4_status TEXT DEFAULT 'pending',
            last_update TEXT
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
    cur.execute("INSERT OR IGNORE INTO hujjat_status (user_id, doc1, doc2, doc3, doc4, doc1_status, doc2_status, doc3_status, doc4_status, last_update) VALUES (?,0,0,0,0,'pending','pending','pending','pending',?)", (user_id, str(datetime.datetime.now())))
    cur.execute(f"UPDATE hujjat_status SET doc{doc_num}=1, last_update=? WHERE user_id=?", (str(datetime.datetime.now()), user_id))
    con.commit()
    con.close()

def get_hujjat_status(user_id):
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT doc1, doc2, doc3, doc4, doc1_status, doc2_status, doc3_status, doc4_status FROM hujjat_status WHERE user_id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    if row:
        return {'docs': (row[0], row[1], row[2], row[3]), 'status': (row[4], row[5], row[6], row[7])}
    return {'docs': (0,0,0,0), 'status': ('pending','pending','pending','pending')}

def update_hujjat_review(user_id, doc_num, status):
    con = db_connect()
    cur = con.cursor()
    cur.execute(f"UPDATE hujjat_status SET doc{doc_num}_status=?, last_update=? WHERE user_id=?", (status, str(datetime.datetime.now()), user_id))
    con.commit()
    con.close()

def get_user_info(user_id):
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT ism, familya, yosh, telefon, yonalish FROM bakalavr_royxat WHERE id=?", (user_id,))
    row = cur.fetchone()
    if row:
        con.close()
        return {'ism': row[0], 'familya': row[1], 'yosh': row[2], 'telefon': row[3], 'yonalish': row[4]}
    cur.execute("SELECT ism, familya, yosh, telefon, yonalish FROM magistratura_royxat WHERE id=?", (user_id,))
    row = cur.fetchone()
    con.close()
    if row:
        return {'ism': row[0], 'familya': row[1], 'yosh': row[2], 'telefon': row[3], 'yonalish': row[4]}
    return None

def get_all_users():
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT id FROM bakalavr_royxat UNION SELECT id FROM magistratura_royxat")
    users = [row[0] for row in cur.fetchall()]
    con.close()
    return users

def get_all_users_with_info():
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT id, ism, familya, telefon, yonalish FROM bakalavr_royxat")
    bakalavr = cur.fetchall()
    cur.execute("SELECT id, ism, familya, telefon, yonalish FROM magistratura_royxat")
    magistratura = cur.fetchall()
    con.close()
    return bakalavr, magistratura

def is_qabul_open():
    today = datetime.datetime.now()
    start = datetime.datetime(today.year, QABUL_START[0], QABUL_START[1])
    end = datetime.datetime(today.year, QABUL_END[0], QABUL_END[1])
    return start <= today <= end

def get_deadline_days():
    today = datetime.datetime.now()
    end = datetime.datetime(today.year, QABUL_END[0], QABUL_END[1])
    return (end - today).days

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
        [t['menu_status'], t['menu_schedule']],
        [t['menu_contact'], t['menu_admin']],
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

def admin_menu_markup(lang):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📊 " + t['admin_stats'], callback_data="admin_stats")],
        [InlineKeyboardButton("📋 " + t['admin_review'], callback_data="admin_review_list")],
        [InlineKeyboardButton("📨 " + t['admin_broadcast'], callback_data="admin_broadcast")],
        [InlineKeyboardButton("⚙️ " + t['admin_settings'], callback_data="admin_settings")],
        [InlineKeyboardButton("👥 " + t['admin_users'], callback_data="admin_users")],
        [InlineKeyboardButton("📁 " + t['admin_export'], callback_data="admin_export")],
        [InlineKeyboardButton("🔙 " + t['admin_back'], callback_data="admin_back")]
    ])

def review_list_keyboard(users, lang, page=0):
    t = LANG_TEXTS[lang]
    keyboard = []
    start = page * 5
    end = min(start + 5, len(users))
    for i in range(start, end):
        user = users[i]
        name = f"{user['ism']} {user['familya']}"[:20]
        keyboard.append([InlineKeyboardButton(f"👤 {name}", callback_data=f"review_user_{user['user_id']}_{user['doc_num']}")])
    if len(users) > 5:
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("◀️ Oldingi", callback_data=f"review_page_{page-1}"))
        if end < len(users):
            nav_row.append(InlineKeyboardButton("Keyingi ▶️", callback_data=f"review_page_{page+1}"))
        if nav_row:
            keyboard.append(nav_row)
    keyboard.append([InlineKeyboardButton("🔙 " + t['admin_back'], callback_data="admin_back")])
    return InlineKeyboardMarkup(keyboard)

def review_actions_keyboard(lang, user_id, doc_num):
    t = LANG_TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ " + t['review_approve'], callback_data=f"review_approve_{user_id}_{doc_num}")],
        [InlineKeyboardButton("❌ " + t['review_reject'], callback_data=f"review_reject_{user_id}_{doc_num}")],
        [InlineKeyboardButton("🔙 " + t['admin_back'], callback_data="admin_back")]
    ])

def is_any_menu_button(text, lang):
    if not text: return False
    t = LANG_TEXTS[lang]
    menu = [t['menu_about'], t['menu_bakalavr'], t['menu_magistratura'], t['menu_hujjat'],
            t['menu_manzil'], t['menu_bakalavr_tanlash'], t['menu_magistratura_tanlash'],
            t['menu_status'], t['menu_schedule'], t['menu_contact'], t['menu_admin'], t['change_lang']]
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
        await query.message.reply_text(LANG_TEXTS[lang]['welcome'], parse_mode="Markdown", reply_markup=main_menu_markup(lang))
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
        text = f"{t['about_title']}\n\n"
        text += f"{t['about_desc']}\n\n"
        text += f"{t['about_history']}\n\n"
        text += f"{t['about_faculties']}\n\n"
        text += f"{t['about_international']}\n\n"
        text += f"{t['about_achievements']}\n\n"
        text += t['about_contact'].format(phone=ADMIN_PHONE, username=ADMIN_USERNAME)
        try:
            await update.message.reply_photo(photo=ABOUT_PHOTO_URL, caption=text, parse_mode="Markdown")
        except:
            await update.message.reply_text(text, parse_mode="Markdown")
        return TANLA

    if msg == t['menu_bakalavr']:
        text = f"{t['bakalavr_text']}\n\n{t['bakalavr_detail']}"
        await update.message.reply_text(text, parse_mode="Markdown")
        return TANLA

    if msg == t['menu_magistratura']:
        text = f"{t['magistratura_text']}\n\n{t['magistratura_detail']}"
        await update.message.reply_text(text, parse_mode="Markdown")
        return TANLA

    if msg == t['menu_hujjat']:
        if not is_qabul_open():
            await update.message.reply_text(t['deadline_passed'], parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['hujjat_intro'], parse_mode="Markdown", reply_markup=format_tanlash_keyboard(lang, 1))
        return HUJJAT_FORMAT_1

    if msg == t['menu_manzil']:
        await update.message.reply_text(t['manzil_text'], parse_mode="Markdown")
        return TANLA

    if msg == t['menu_bakalavr_tanlash']:
        if check_already_registered(user_id, "bakalavr_royxat"):
            await update.message.reply_text("✨ Siz allaqachon bakalavriat yo'nalishini tanlagansiz!", parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return YONALISH_ISM

    if msg == t['menu_magistratura_tanlash']:
        if check_already_registered(user_id, "magistratura_royxat"):
            await update.message.reply_text("✨ Siz allaqachon magistratura yo'nalishini tanlagansiz!", parse_mode="Markdown")
            return TANLA
        await update.message.reply_text(t['enter_name'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
        return MAG_ISM

    if msg == t['menu_status']:
        hujjat_data = get_hujjat_status(user_id)
        docs = hujjat_data['docs']
        statuses = hujjat_data['status']
        
        if sum(docs) == 0 and not get_user_info(user_id):
            await update.message.reply_text(t['status_not_found'], parse_mode="Markdown")
            return TANLA
        
        status_map = {
            'pending': t['status_pending'],
            'approved': t['status_approved'],
            'rejected': t['status_rejected']
        }
        
        text = t['status_title']
        text += t['status_docs']
        text += t['status_doc1'].format(status=status_map.get(statuses[0], t['status_not_submitted'] if docs[0]==0 else t['status_pending'])) + "\n"
        text += t['status_doc2'].format(status=status_map.get(statuses[1], t['status_not_submitted'] if docs[1]==0 else t['status_pending'])) + "\n"
        text += t['status_doc3'].format(status=status_map.get(statuses[2], t['status_not_submitted'] if docs[2]==0 else t['status_pending'])) + "\n"
        text += t['status_doc4'].format(status=status_map.get(statuses[3], t['status_not_submitted'] if docs[3]==0 else t['status_pending'])) + "\n\n"
        
        user_info = get_user_info(user_id)
        if user_info:
            text += t['status_yonalish'].format(yonalish=user_info['yonalish'])
            text += t['status_phone'].format(phone=user_info['telefon'])
        
        await update.message.reply_text(text, parse_mode="Markdown")
        return TANLA

    if msg == t['menu_schedule']:
        text = t['schedule_title']
        text += t['schedule_bakalavr'] + "\n\n"
        text += t['schedule_magistratura'] + "\n\n"
        text += t['schedule_note']
        await update.message.reply_text(text, parse_mode="Markdown")
        return TANLA

    if msg == t['menu_contact']:
        text = t['contact_text'].format(phone=ADMIN_PHONE, username=ADMIN_USERNAME)
        await update.message.reply_text(text, parse_mode="Markdown")
        return TANLA

    if msg == t['menu_admin']:
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Bu bo'lim faqat admin uchun!")
            return TANLA
        await update.message.reply_text(t['admin_title'], parse_mode="Markdown", reply_markup=admin_menu_markup(lang))
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
        elif update.message.photo:
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
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
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
    cur.execute("INSERT OR REPLACE INTO bakalavr_royxat VALUES (?,?,?,?,?,?,?,?,?,?)", 
                (user_id, query.from_user.first_name, query.from_user.last_name, query.from_user.username, 
                 str(datetime.datetime.now()), context.user_data.get('yonalish_ism'), 
                 context.user_data.get('yonalish_familya'), context.user_data.get('yonalish_yosh'), 
                 context.user_data.get('yonalish_telefon'), yonalish))
    con.commit()
    con.close()
    
    username = f"@{query.from_user.username}" if query.from_user.username else f"[{query.from_user.first_name}](tg://user?id={user_id})"
    caption = LANG_TEXTS[lang]['yonalish_channel_caption'].format(
        user=username, uid=user_id, phone=context.user_data.get('yonalish_telefon'),
        yonalish=yonalish, ism=context.user_data.get('yonalish_ism'),
        familya=context.user_data.get('yonalish_familya'), yosh=context.user_data.get('yonalish_yosh')
    )
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
            await update.message.reply_text(LANG_TEXTS[lang]['invalid_phone'], parse_mode="Markdown", reply_markup=cancel_back_markup(lang))
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
    cur.execute("INSERT OR REPLACE INTO magistratura_royxat VALUES (?,?,?,?,?,?,?,?,?,?)", 
                (user_id, query.from_user.first_name, query.from_user.last_name, query.from_user.username, 
                 str(datetime.datetime.now()), context.user_data.get('mag_ism'), 
                 context.user_data.get('mag_familya'), context.user_data.get('mag_yosh'), 
                 context.user_data.get('mag_telefon'), yonalish))
    con.commit()
    con.close()
    
    username = f"@{query.from_user.username}" if query.from_user.username else f"[{query.from_user.first_name}](tg://user?id={user_id})"
    caption = LANG_TEXTS[lang]['magistratura_channel_caption'].format(
        user=username, uid=user_id, phone=context.user_data.get('mag_telefon'),
        yonalish=yonalish, ism=context.user_data.get('mag_ism'),
        familya=context.user_data.get('mag_familya'), yosh=context.user_data.get('mag_yosh')
    )
    try:
        await context.bot.send_message(CHANNEL_USERNAME, caption, parse_mode="Markdown")
    except Exception as e:
        logger.error(f"Kanalga yuborish xato: {e}")
    
    await query.edit_message_text(LANG_TEXTS[lang]['reg_success'], parse_mode="Markdown")
    await context.bot.send_message(user_id, "🏠 Bosh menyu", reply_markup=main_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📊  ADMIN PANEL FUNKSIYALARI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

async def check_deadline_reminders(context: ContextTypes.DEFAULT_TYPE):
    days_left = get_deadline_days()
    if days_left in [7, 3, 1]:
        reminder_key = f'reminder_{days_left}days'
        users = get_all_users()
        for user_id in users:
            try:
                lang = get_user_lang(user_id)
                text = LANG_TEXTS[lang]['reminder_title'] + LANG_TEXTS[lang][reminder_key]
                await context.bot.send_message(chat_id=user_id, text=text, parse_mode="Markdown")
            except:
                pass

async def admin_stats(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT COUNT(*) FROM bakalavr_royxat")
    bak = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM magistratura_royxat")
    mag = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hujjat_status WHERE doc1=1")
    d1 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hujjat_status WHERE doc2=1")
    d2 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hujjat_status WHERE doc3=1")
    d3 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hujjat_status WHERE doc4=1")
    d4 = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hujjat_status WHERE doc1_status='approved'")
    approved = cur.fetchone()[0]
    cur.execute("SELECT COUNT(*) FROM hujjat_status WHERE doc1_status='rejected'")
    rejected = cur.fetchone()[0]
    con.close()
    
    days_left = get_deadline_days()
    
    text = t['stats_title']
    text += t['stats_bakalavr'].format(count=bak) + "\n"
    text += t['stats_magistratura'].format(count=mag) + "\n"
    text += t['stats_total'].format(count=bak+mag) + "\n\n"
    text += t['stats_docs'].format(d1=d1, d2=d2, d3=d3, d4=d4) + "\n\n"
    text += t['stats_approved'].format(count=approved) + "\n"
    text += t['stats_rejected'].format(count=rejected) + "\n\n"
    text += t['stats_days'].format(days=days_left)
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_menu_markup(lang))

async def admin_review_list(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    con = db_connect()
    cur = con.cursor()
    cur.execute("SELECT user_id, doc1, doc2, doc3, doc4, doc1_status, doc2_status, doc3_status, doc4_status FROM hujjat_status")
    rows = cur.fetchall()
    con.close()
    
    users = []
    for row in rows:
        user_id, d1, d2, d3, d4, s1, s2, s3, s4 = row
        user_info = get_user_info(user_id)
        if user_info:
            for doc_num in range(1, 5):
                if row[doc_num] == 1 and row[4+doc_num] == 'pending':
                    users.append({
                        'user_id': user_id,
                        'ism': user_info['ism'],
                        'familya': user_info['familya'],
                        'doc_num': doc_num
                    })
    
    if not users:
        await query.edit_message_text("📋 *Tekshiriladigan hujjatlar yo'q*", parse_mode="Markdown", reply_markup=admin_menu_markup(lang))
        return
    
    context.user_data['review_users'] = users
    context.user_data['review_page'] = 0
    await query.edit_message_text("📋 *Tekshiriladigan hujjatlar:*", parse_mode="Markdown", reply_markup=review_list_keyboard(users, lang, 0))

async def review_list_page(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    page = int(data.split("_")[2])
    lang = get_user_lang(query.from_user.id)
    users = context.user_data.get('review_users', [])
    await query.edit_message_text("📋 *Tekshiriladigan hujjatlar:*", parse_mode="Markdown", reply_markup=review_list_keyboard(users, lang, page))

async def review_user(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("_")
    user_id = int(parts[2])
    doc_num = int(parts[3])
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    user_info = get_user_info(user_id)
    
    if not user_info:
        await query.edit_message_text("❌ Foydalanuvchi topilmadi", reply_markup=admin_menu_markup(lang))
        return
    
    text = f"{t['review_title']}"
    text += f"👤 *Foydalanuvchi:* {user_info['ism']} {user_info['familya']}\n"
    text += f"📞 *Telefon:* {user_info['telefon']}\n"
    text += f"🎓 *Yo'nalish:* {user_info['yonalish']}\n"
    text += f"📄 *Hujjat:* {HUJJAT_NOMLAR[lang][doc_num]}\n\n"
    text += t['review_pending']
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=review_actions_keyboard(lang, user_id, doc_num))

async def review_approve(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("_")
    user_id = int(parts[2])
    doc_num = int(parts[3])
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    update_hujjat_review(user_id, doc_num, 'approved')
    
    user_lang = get_user_lang(user_id)
    status_text = LANG_TEXTS[user_lang]['review_approved']
    await context.bot.send_message(
        chat_id=user_id,
        text=LANG_TEXTS[user_lang]['review_notification'].format(status=status_text),
        parse_mode="Markdown"
    )
    
    await query.edit_message_text("✅ *Hujjat tasdiqlandi!*", parse_mode="Markdown", reply_markup=admin_menu_markup(lang))
    await admin_review_list(update, context)

async def review_reject_request(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data
    parts = data.split("_")
    context.user_data['reject_user_id'] = int(parts[2])
    context.user_data['reject_doc_num'] = int(parts[3])
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    await query.edit_message_text(
        f"{t['review_reason']}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bekor qilish", callback_data="admin_review_list")]])
    )
    return ADMIN_REVIEW

async def review_reject_process(update, context):
    reason = update.message.text
    user_id = context.user_data.get('reject_user_id')
    doc_num = context.user_data.get('reject_doc_num')
    lang = get_user_lang(update.effective_user.id)
    t = LANG_TEXTS[lang]
    
    update_hujjat_review(user_id, doc_num, 'rejected')
    
    user_lang = get_user_lang(user_id)
    status_text = LANG_TEXTS[user_lang]['review_rejected'].format(reason=reason)
    await context.bot.send_message(
        chat_id=user_id,
        text=LANG_TEXTS[user_lang]['review_notification'].format(status=status_text),
        parse_mode="Markdown"
    )
    
    await update.message.reply_text("❌ *Hujjat rad etildi!*", parse_mode="Markdown")
    await update.message.reply_text(t['admin_title'], parse_mode="Markdown", reply_markup=admin_menu_markup(lang))
    return TANLA

async def admin_broadcast(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    await query.edit_message_text(
        t['broadcast_title'],
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Bekor qilish", callback_data="admin_back")]])
    )
    context.user_data['broadcast_mode'] = True
    return TANLA

async def process_broadcast(update, context):
    if not context.user_data.get('broadcast_mode'):
        return TANLA
    
    msg_text = update.message.text
    lang = get_user_lang(update.effective_user.id)
    t = LANG_TEXTS[lang]
    users = get_all_users()
    
    sent = 0
    failed = 0
    status_msg = await update.message.reply_text(t['broadcast_sending'])
    
    for user_id in users:
        try:
            await context.bot.send_message(chat_id=user_id, text=msg_text, parse_mode="Markdown")
            sent += 1
            await asyncio.sleep(0.05)
        except:
            failed += 1
    
    await status_msg.edit_text(t['broadcast_sent'].format(sent=sent, failed=failed))
    context.user_data['broadcast_mode'] = False
    await update.message.reply_text(t['admin_title'], parse_mode="Markdown", reply_markup=admin_menu_markup(lang))
    return TANLA

async def admin_settings(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    text = t['settings_title']
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup([
        [InlineKeyboardButton("ℹ️ " + t['settings_info'], callback_data="settings_info")],
        [InlineKeyboardButton("🔙 " + t['admin_back'], callback_data="admin_back")]
    ]))

async def settings_info(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    info_text = "ℹ️ *BOT HAQIDA*\n\n"
    info_text += "📌 *Versiya:* 2.0.0\n"
    info_text += "📅 *Ishlab chiqarilgan:* 2024\n"
    info_text += "👨‍💻 *Dasturchi:* @Saman2611\n"
    info_text += "🎯 *Maqsad:* Qabul jarayonini avtomatlashtirish\n\n"
    info_text += "✨ *Funksiyalar:*\n"
    info_text += "• Bakalavriat va Magistratura yo'nalishlari\n"
    info_text += "• Hujjat topshirish\n"
    info_text += "• Hujjat holatini tekshirish\n"
    info_text += "• Imtihon jadvali\n"
    info_text += "• Admin panel\n"
    info_text += "• 3 til"
    
    await query.edit_message_text(info_text, parse_mode="Markdown", reply_markup=admin_menu_markup(lang))

async def admin_users(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    
    bakalavr, magistratura = get_all_users_with_info()
    
    text = t['users_title']
    text += f"🎓 *Bakalavriat:* {len(bakalavr)} ta\n"
    text += f"📚 *Magistratura:* {len(magistratura)} ta\n"
    text += t['users_count'].format(count=len(bakalavr)+len(magistratura))
    
    await query.edit_message_text(text, parse_mode="Markdown", reply_markup=admin_menu_markup(lang))

async def admin_export_callback(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    
    await query.edit_message_text("📁 *Eksport qilish...*", parse_mode="Markdown")
    
    con = db_connect()
    for table in ['bakalavr_royxat', 'magistratura_royxat', 'hujjat_status']:
        cur = con.cursor()
        cur.execute(f"SELECT * FROM {table}")
        data = cur.fetchall()
        if data:
            csv_file = io.StringIO()
            writer = csv.writer(csv_file)
            writer.writerow([desc[0] for desc in cur.description])
            writer.writerows(data)
            await context.bot.send_document(
                chat_id=query.from_user.id,
                document=io.BytesIO(csv_file.getvalue().encode('utf-8-sig')),
                filename=f"{table}.csv"
            )
    con.close()
    
    await context.bot.send_message(
        chat_id=query.from_user.id,
        text="✅ *Eksport tugallandi!*",
        parse_mode="Markdown",
        reply_markup=admin_menu_markup(lang)
    )

async def admin_back(update, context):
    query = update.callback_query
    await query.answer()
    lang = get_user_lang(query.from_user.id)
    t = LANG_TEXTS[lang]
    await query.edit_message_text(t['admin_title'], parse_mode="Markdown", reply_markup=admin_menu_markup(lang))
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 👤  ADMIN COMMANDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def admin_statistika(update, context):
    if update.effective_user.id != ADMIN_ID:
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
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("❌ Faqat admin!")
        return
    con = db_connect()
    for table in ['bakalavr_royxat', 'magistratura_royxat', 'hujjat_status']:
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
    if update.effective_user.id != ADMIN_ID:
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
    if not BOT_TOKEN or BOT_TOKEN == "":
        print("❌ BOT_TOKEN xato! Iltimos .env faylga tokeningizni yozing!")
        return
    
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()
    
    # Admin buyruqlar
    app.add_handler(CommandHandler("users", admin_statistika))
    app.add_handler(CommandHandler("export", admin_export))
    app.add_handler(CommandHandler("search", admin_search))
    
    # Eslatma scheduler
    job_queue = app.job_queue
    if job_queue:
        job_queue.run_daily(check_deadline_reminders, time=datetime.time(hour=9, minute=0))

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TIL_TANLASH: [CallbackQueryHandler(lang_callback), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
            TANLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher), 
                    CallbackQueryHandler(bakalavr_callback), CallbackQueryHandler(magistratura_callback),
                    CallbackQueryHandler(admin_stats, pattern="^admin_stats$"),
                    CallbackQueryHandler(admin_review_list, pattern="^admin_review_list$"),
                    CallbackQueryHandler(review_list_page, pattern="^review_page_"),
                    CallbackQueryHandler(review_user, pattern="^review_user_"),
                    CallbackQueryHandler(review_approve, pattern="^review_approve_"),
                    CallbackQueryHandler(review_reject_request, pattern="^review_reject_"),
                    CallbackQueryHandler(admin_broadcast, pattern="^admin_broadcast$"),
                    CallbackQueryHandler(admin_settings, pattern="^admin_settings$"),
                    CallbackQueryHandler(settings_info, pattern="^settings_info$"),
                    CallbackQueryHandler(admin_users, pattern="^admin_users$"),
                    CallbackQueryHandler(admin_export_callback, pattern="^admin_export$"),
                    CallbackQueryHandler(admin_back, pattern="^admin_back$"),
                    MessageHandler(filters.TEXT & ~filters.COMMAND, process_broadcast)],
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
            ADMIN_REVIEW: [MessageHandler(filters.TEXT & ~filters.COMMAND, review_reject_process)],
        },
        fallbacks=[CommandHandler('start', start), MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu_dispatcher)],
        allow_reentry=True
    )
    app.add_handler(conv)
    
    print("✅ QABUL BOTI ISHGA TUSHDI!")
    print(f"👤 ADMIN ID: {ADMIN_ID}")
    print("📊 Admin buyruqlar: /users, /export, /search")
    print("⏰ Eslatmalar: har kuni 9:00 da")
    print("")
    print("📱 MENU TARTIBI:")
    print("━" * 30)
    print("🏛 Universitet haqida")
    print("🎓 Bakalavriat     | 📚 Magistratura")
    print("📝 Hujjat topshirish | 📍 Manzil")
    print("📋 Bakalavriat yo'nalishlari | 🎓 Magistratura yo'nalishlari")
    print("📊 Hujjat holati   | 📅 Imtihon jadvali")
    print("📞 Aloqa          | ⚙️ Admin panel")
    print("🌐 Tilni o'zgartirish")
    print("━" * 30)
    
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
