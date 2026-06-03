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

# ─────────────────────────────────────────────
# ⚙️  SOZLAMALAR
# ─────────────────────────────────────────────
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"
ADMIN_PHONE = "+998996844483"
DB_PATH = "universitet.db"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ─────────────────────────────────────────────
# 🗄️  MA'LUMOTLAR BAZASI
# ─────────────────────────────────────────────
def db_connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = db_connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id          INTEGER PRIMARY KEY,
            first_name  TEXT,
            last_name   TEXT,
            user_name   TEXT,
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

# ─────────────────────────────────────────────
# 🎨  DIZAYN ELEMENTLARI
# ─────────────────────────────────────────────
SEPARATOR = "═" * 30

YONALISHLAR_TEXT = f"""
🎓 *TA'LIM YO'NALISHLARI*
{SEPARATOR}

🔬 *6B05120* — Biotexnologiya
🌍 *6B05210* — Ekologiya
💻 *6B06120* — Axborot tizimlar
⚙️ *6B07150* — Avtomatizatsiya va boshqaruv
🚚 *6B07130* — Transport texnikasi
⚡ *6B07110* — Elektroenergetika
🧑‍🏫 *6B01310* — Pedagogika va boshlang'ich ta'lim
🧠 *6B06121* — Sun'iy intellekt texnologiyalari
💼 *6B04130* — Hisob va audit
✈️ *6B11110* — Turizm

{SEPARATOR}
📌 _Hujjat topshirish uchun pastdagi menyudan foydalaning._
"""

HUJJATLAR_ROYXATI = f"""
📋 *KERAKLI HUJJATLAR RO'YXATI*
{SEPARATOR}

1️⃣ 📗 Diplom yoki Atestat
2️⃣ 🪪 Pasport nusxasi
3️⃣ 🗂 0.86 Meditsina ma'lumotnomasi
4️⃣ 📸 3×4 — 6 dona oq-qora rasm

{SEPARATOR}
"""

# Conversation states
TANLA = "tanla"
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "hujjat_1", "hujjat_2", "hujjat_3", "hujjat_4"
SOROV_ISM, SOROV_FAMILYA, SOROV_YOSH, SOROV_TELEFON = "sorov_ism", "sorov_familya", "sorov_yosh", "sorov_telefon"
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON = "yonalish_ism", "yonalish_familya", "yonalish_yosh", "yonalish_telefon"

def main_menu_markup():
    buttons = [
        ["🎓 Universitet haqida", "🗃️ Yo'nalishlar"],
        ["📝 Hujjat topshirish", "📍 Manzil"],
        ["🗂 So'rovnoma", "📋 Yo'nalish tanlash"],
        ["👤 Admin bilan bog'lanish"],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

# ─────────────────────────────────────────────
# 🚀  /start
# ─────────────────────────────────────────────
async def start(update, context):
    user = update.message.from_user
    con = db_connect()
    cur = con.cursor()

    context.user_data.update({
        'id': user.id,
        'first_name': user.first_name or "",
        'last_name': user.last_name or "",
        'user_name': user.username or "",
    })

    cur.execute("SELECT id FROM foydalanuvchilar WHERE id=?", (user.id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO foydalanuvchilar VALUES (?,?,?,?,?)",
            (user.id, user.first_name, user.last_name, user.username, datetime.datetime.now())
        )
        con.commit()
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=(
                    f"🆕 *Yangi foydalanuvchi!*\n{SEPARATOR}\n"
                    f"🆔 ID: `{user.id}`\n"
                    f"👤 Ismi: {user.first_name} {user.last_name or ''}\n"
                    f"💬 Username: @{user.username or 'yoq'}\n"
                    f"⏰ Vaqt: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"Kanalga yuborishda xato: {e}")
    con.close()

    await update.message.reply_text(
        f"👋 *Assalomu alaykum, {user.first_name}!*\n\n"
        f"{SEPARATOR}\n\n"
        f"🎓 Siz hozirda *M.Auezov nomidagi Janubiy Qozog'iston universiteti*\n"
        f"Chirchiq filialiga hujjat topshirish botiga ulangansiz.\n\n"
        f"📌 *Bu yerda siz:*\n"
        f"✅ Ta'lim yo'nalishlarini ko'rasiz\n"
        f"✅ Hujjatlarni onlayn topshirasiz\n"
        f"✅ So'rovnomani to'ldirasiz\n"
        f"✅ Yo'nalish tanlaysiz\n\n"
        f"{SEPARATOR}\n\n"
        f"👇 *Quyidagi menyudan boshlang:*",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

# ─────────────────────────────────────────────
# 📋  ASOSIY MENYU
# ─────────────────────────────────────────────
async def text(update, context):
    msg = update.message.text

    if msg == "🎓 Universitet haqida":
        await update.message.reply_text(
            "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti*\n"
            f"{SEPARATOR}\n"
            "📍 Chirchiqda filial tashkil etilmoqda!\n\n"
            "🔗 Batafsil: [oliygoh.uz](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        return TANLA

    elif msg == "🗃️ Yo'nalishlar":
        await update.message.reply_text(YONALISHLAR_TEXT, parse_mode="Markdown")
        return TANLA

    elif msg == "📝 Hujjat topshirish":
        await update.message.reply_text(
            HUJJATLAR_ROYXATI + "\n📗 *Birinchi navbatda Diplom yoki Atestat rasmini yuboring:*",
            parse_mode="Markdown"
        )
        return HUJJAT_1

    elif msg == "📍 Manzil":
        await update.message.reply_text(
            f"📍 *Universitetning manzili:*\n{SEPARATOR}\n"
            "🗺 Quyidagi havolani bosib, Google Maps orqali yo'l toping:\n\n"
            "👉 https://maps.app.goo.gl/rm7LTHWLpZ7JsKmu6",
            parse_mode="Markdown"
        )
        return TANLA

    elif msg == "🗂 So'rovnoma":
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT id FROM sorovnama WHERE id=?", (update.message.from_user.id,))
        mavjud = cur.fetchone()
        con.close()
        if mavjud:
            await update.message.reply_text(
                "✅ *Siz allaqachon so'rovnomani to'ldirdingiz!*\n"
                "_Qayta to'ldirish shart emas._",
                parse_mode="Markdown"
            )
            return TANLA
        await update.message.reply_text(
            f"📝 *SO'ROVNOMA*\n{SEPARATOR}\n\n"
            "👤 *To'liq ismingizni* kiriting:\n_(Masalan: Abdullayev Ali)_",
            parse_mode="Markdown"
        )
        return SOROV_ISM

    elif msg == "📋 Yo'nalish tanlash":
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT id FROM yonalish_royxat WHERE id=?", (update.message.from_user.id,))
        mavjud = cur.fetchone()
        con.close()
        if mavjud:
            await update.message.reply_text(
                "✅ *Siz allaqachon yo'nalish tanlagansiz!*\n"
                "_Qayta ro'yxatdan o'tish shart emas._",
                parse_mode="Markdown"
            )
            return TANLA
        await update.message.reply_text(
            f"📋 *YO'NALISH TANLASH*\n{SEPARATOR}\n\n"
            "👤 *To'liq ismingizni* kiriting:\n_(Masalan: Abdullayev Ali)_",
            parse_mode="Markdown"
        )
        return YONALISH_ISM

    elif msg == "👤 Admin bilan bog'lanish":
        await update.message.reply_text(
            f"👤 *ADMIN BILAN BOG'LANISH*\n{SEPARATOR}\n\n"
            f"💬 Telegram: {ADMIN_USERNAME}\n"
            f"📞 Telefon: `{ADMIN_PHONE}`\n\n"
            "⚡️ Admin ish vaqti: *09:00 — 18:00*",
            parse_mode="Markdown"
        )
        return TANLA

    else:
        await update.message.reply_text(
            "❓ *Noma'lum buyruq*\n\n"
            "Iltimos, quyidagi menyudan foydalaning 👇\n"
            "_Yoki /menyu buyrug'ini yuboring._",
            parse_mode="Markdown"
        )
        return TANLA

# ─────────────────────────────────────────────
# 📸  HUJJAT TOPSHIRISH
# ─────────────────────────────────────────────
async def _send_photo_to_channel(context, update, caption):
    user = update.message.from_user
    photo = update.message.photo[-1]
    try:
        await context.bot.send_photo(
            chat_id=CHANNEL_USERNAME,
            photo=photo.file_id,
            caption=(
                f"📎 {caption}\n{SEPARATOR}\n"
                f"👤 {user.full_name}\n"
                f"🆔 ID: `{user.id}`\n"
                f"⏰ {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Kanalga rasm yuborishda xato: {e}")

async def hujjat_1(update, context):
    if not update.message.photo:
        await update.message.reply_text("🖼️ Iltimos, faqat *rasm* yuboring!", parse_mode="Markdown")
        return HUJJAT_1
    await _send_photo_to_channel(context, update, "📗 Diplom / Atestat")
    await update.message.reply_text(
        f"✅ *Qabul qilindi!*\n{SEPARATOR}\n\n"
        "2️⃣ Endi *Pasport nusxasi* rasmini yuboring: 🪪",
        parse_mode="Markdown"
    )
    return HUJJAT_2

async def hujjat_2(update, context):
    if not update.message.photo:
        await update.message.reply_text("🖼️ Iltimos, faqat *rasm* yuboring!", parse_mode="Markdown")
        return HUJJAT_2
    await _send_photo_to_channel(context, update, "🪪 Pasport nusxasi")
    await update.message.reply_text(
        f"✅ *Qabul qilindi!*\n{SEPARATOR}\n\n"
        "3️⃣ Endi *0.86 Meditsina ma'lumotnomasi* rasmini yuboring: 🗂",
        parse_mode="Markdown"
    )
    return HUJJAT_3

async def hujjat_3(update, context):
    if not update.message.photo:
        await update.message.reply_text("🖼️ Iltimos, faqat *rasm* yuboring!", parse_mode="Markdown")
        return HUJJAT_3
    await _send_photo_to_channel(context, update, "🗂 0.86 Meditsina ma'lumotnomasi")
    await update.message.reply_text(
        f"✅ *Qabul qilindi!*\n{SEPARATOR}\n\n"
        "4️⃣ *3×4 formatdagi 6 dona oq-qora rasmning* bitta fotosuratini yuboring: 📸",
        parse_mode="Markdown"
    )
    return HUJJAT_4

async def hujjat_4(update, context):
    if not update.message.photo:
        await update.message.reply_text("🖼️ Iltimos, faqat *rasm* yuboring!", parse_mode="Markdown")
        return HUJJAT_4
    await _send_photo_to_channel(context, update, "📸 3×4 oq-qora rasm (6 dona)")
    await update.message.reply_text(
        f"🎉 *Barcha hujjatlar qabul qilindi!*\n{SEPARATOR}\n\n"
        "📍 Endi asl nusxalarni papkaga solib, quyidagi manzilga olib keling:\n\n"
        "👉 https://maps.app.goo.gl/rm7LTHWLpZ7JsKmu6\n\n"
        "✅ _Tez orada siz bilan bog'lanamiz!_",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

# ─────────────────────────────────────────────
# 📝  SO'ROVNOMA
# ─────────────────────────────────────────────
async def sorov_ism(update, context):
    context.user_data['sorov_ism'] = update.message.text.strip()
    await update.message.reply_text(
        "✅ Ism saqlandi!\n\n"
        "👥 *Familiyangizni* kiriting:\n_(Masalan: Abdullayev)_",
        parse_mode="Markdown"
    )
    return SOROV_FAMILYA

async def sorov_familya(update, context):
    context.user_data['sorov_familya'] = update.message.text.strip()
    await update.message.reply_text(
        "✅ Familiya saqlandi!\n\n"
        "🎂 *Yoshingizni* kiriting:\n_(Masalan: 19)_",
        parse_mode="Markdown"
    )
    return SOROV_YOSH

async def sorov_yosh(update, context):
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            "⚠️ Iltimos, to'g'ri yosh kiriting *(14 — 60 oralig'ida)*.",
            parse_mode="Markdown"
        )
        return SOROV_YOSH
    context.user_data['sorov_yosh'] = yosh
    k = [
        [KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton("🔙 Menyuga qaytish")],
    ]
    await update.message.reply_text(
        "✅ Yosh saqlandi!\n\n"
        "📞 *Telefon raqamingizni* yuboring:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True)
    )
    return SOROV_TELEFON

async def sorov_telefon(update, context):
    telefon = update.message.contact.phone_number
    user = update.message.from_user
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO sorovnama VALUES (?,?,?,?,?,?,?,?,?)",
        (
            user.id, user.first_name, user.last_name or "", user.username or "",
            datetime.datetime.now().strftime('%d.%m.%Y %H:%M'),
            context.user_data.get('sorov_ism', ''),
            context.user_data.get('sorov_familya', ''),
            context.user_data.get('sorov_yosh', ''),
            telefon
        )
    )
    con.commit()
    con.close()

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=(
                f"📝 *SO'ROVNOMA TO'LDIRILDI*\n{SEPARATOR}\n"
                f"🆔 ID: `{user.id}`\n"
                f"👤 Telegram: {user.first_name} {user.last_name or ''}\n"
                f"💬 @{user.username or 'yoq'}\n"
                f"📌 Ism: {context.user_data.get('sorov_ism')}\n"
                f"📌 Familiya: {context.user_data.get('sorov_familya')}\n"
                f"🎂 Yosh: {context.user_data.get('sorov_yosh')}\n"
                f"📞 Telefon: {telefon}\n"
                f"⏰ {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Kanalga xabar yuborishda xato: {e}")

    await update.message.reply_text(
        f"🎉 *So'rovnoma muvaffaqiyatli yuborildi!*\n{SEPARATOR}\n\n"
        "✅ Tez orada siz bilan bog'lanamiz.\n"
        "📋 *Yo'nalish tanlash* uchun menyudan foydalaning.",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

# ─────────────────────────────────────────────
# 🎓  YO'NALISH TANLASH
# ─────────────────────────────────────────────
async def yonalish_ism(update, context):
    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(
        "✅ Ism saqlandi!\n\n👥 *Familiyangizni* kiriting:",
        parse_mode="Markdown"
    )
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(
        "✅ Familiya saqlandi!\n\n🎂 *Yoshingizni* kiriting:",
        parse_mode="Markdown"
    )
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            "⚠️ Iltimos, to'g'ri yosh kiriting *(14 — 60 oralig'ida)*.",
            parse_mode="Markdown"
        )
        return YONALISH_YOSH
    context.user_data['yonalish_yosh'] = yosh
    k = [
        [KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton("🔙 Menyuga qaytish")],
    ]
    await update.message.reply_text(
        "✅ Yosh saqlandi!\n\n📞 *Telefon raqamingizni* yuboring:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True)
    )
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    context.user_data['yonalish_telefon'] = update.message.contact.phone_number
    yonalishlar = [
        ("🔬 6B05120 — Biotexnologiya", "Biotexnologiya"),
        ("🌍 6B05210 — Ekologiya", "Ekologiya"),
        ("💻 6B06120 — Axborot tizimlar", "Axborot_tizimlar"),
        ("⚙️ 6B07150 — Avtomatizatsiya va boshqaruv", "Avtomatizatsiya"),
        ("🚚 6B07130 — Transport texnikasi", "Transport"),
        ("⚡ 6B07110 — Elektroenergetika", "Elektroenergetika"),
        ("🧑‍🏫 6B01310 — Pedagogika", "Pedagogika"),
        ("🧠 6B06121 — Sun'iy intellekt", "SuniyIntellekt"),
        ("💼 6B04130 — Hisob va audit", "HisobAudit"),
        ("✈️ 6B11110 — Turizm", "Turizm"),
    ]
    keyboard = [[InlineKeyboardButton(t, callback_data=cb)] for t, cb in yonalishlar]
    keyboard.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="bekor")])
    await update.message.reply_text(
        f"🎓 *YO'NALISHNI TANLANG:*\n{SEPARATOR}",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TANLA

# ─────────────────────────────────────────────
# 🎛️  CALLBACK
# ─────────────────────────────────────────────
YONALISH_MAP = {
    "Biotexnologiya": "🔬 6B05120 — Biotexnologiya",
    "Ekologiya": "🌍 6B05210 — Ekologiya",
    "Axborot_tizimlar": "💻 6B06120 — Axborot tizimlar",
    "Avtomatizatsiya": "⚙️ 6B07150 — Avtomatizatsiya va boshqaruv",
    "Transport": "🚚 6B07130 — Transport texnikasi",
    "Elektroenergetika": "⚡ 6B07110 — Elektroenergetika",
    "Pedagogika": "🧑‍🏫 6B01310 — Pedagogika",
    "SuniyIntellekt": "🧠 6B06121 — Sun'iy intellekt texnologiyalari",
    "HisobAudit": "💼 6B04130 — Hisob va audit",
    "Turizm": "✈️ 6B11110 — Turizm",
}

async def callback_data(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "bekor":
        await query.edit_message_text("❌ *Bekor qilindi.*", parse_mode="Markdown")
        return

    yonalish = YONALISH_MAP.get(data)
    if not yonalish:
        await query.edit_message_text("⚠️ Noma'lum tanlov.", parse_mode="Markdown")
        return

    context.user_data['yonalish'] = yonalish

    kerakli = ['yonalish_ism', 'yonalish_familya', 'yonalish_yosh', 'yonalish_telefon']
    if not all(k in context.user_data for k in kerakli):
        await query.edit_message_text(
            "⚠️ *Ma'lumotlar topilmadi.*\nIltimos, qaytadan boshlang: /start",
            parse_mode="Markdown"
        )
        return

    user_id = context.user_data.get('id', query.message.chat_id)
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO yonalish_royxat VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            user_id,
            context.user_data.get('first_name', ''),
            context.user_data.get('last_name', ''),
            context.user_data.get('user_name', ''),
            datetime.datetime.now().strftime('%d.%m.%Y %H:%M'),
            context.user_data['yonalish_ism'],
            context.user_data['yonalish_familya'],
            context.user_data['yonalish_yosh'],
            context.user_data['yonalish_telefon'],
            yonalish
        )
    )
    con.commit()
    con.close()

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=(
                f"🎓 *YO'NALISH TANLANDI*\n{SEPARATOR}\n"
                f"🆔 ID: `{user_id}`\n"
                f"📌 Ism: {context.user_data['yonalish_ism']}\n"
                f"📌 Familiya: {context.user_data['yonalish_familya']}\n"
                f"🎂 Yosh: {context.user_data['yonalish_yosh']}\n"
                f"📞 Telefon: {context.user_data['yonalish_telefon']}\n"
                f"🎯 Yo'nalish: {yonalish}\n"
                f"⏰ {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Kanalga xabar yuborishda xato: {e}")

    await query.edit_message_text(
        f"✅ *Ro'yxatdan o'tdingiz!*\n{SEPARATOR}\n\n"
        f"🎯 Tanlangan yo'nalish:\n*{yonalish}*\n\n"
        "📞 Tez orada siz bilan bog'lanamiz!",
        parse_mode="Markdown"
    )
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="🏠 *Asosiy menyu:*",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )

# ─────────────────────────────────────────────
# 🔙  MENYUGA QAYTISH
# ─────────────────────────────────────────────
async def menyuga_qaytish(update, context):
    await update.message.reply_text(
        "🏠 *Asosiy menyu:*",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

async def menyu(update, context):
    await update.message.reply_text(
        "🏠 *Asosiy menyu:*",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

async def tugash(update, context):
    await update.message.reply_text(
        "👋 *Suhbat yakunlandi.*\nQayta boshlash uchun /start yuboring.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ─────────────────────────────────────────────
# 🤖  MAIN
# ─────────────────────────────────────────────
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN topilmadi! .env faylini tekshiring.")

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    back_filter = filters.Regex("^🔙 Menyuga qaytish$")

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TANLA: [MessageHandler(filters.TEXT & ~filters.COMMAND, text)],

            HUJJAT_1: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), hujjat_1),
            ],
            HUJJAT_2: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), hujjat_2),
            ],
            HUJJAT_3: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), hujjat_3),
            ],
            HUJJAT_4: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(filters.PHOTO | (filters.TEXT & ~filters.COMMAND), hujjat_4),
            ],

            SOROV_ISM:     [MessageHandler(back_filter, menyuga_qaytish),
                            MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_ism)],
            SOROV_FAMILYA: [MessageHandler(back_filter, menyuga_qaytish),
                            MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_familya)],
            SOROV_YOSH:    [MessageHandler(back_filter, menyuga_qaytish),
                            MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_yosh)],
            SOROV_TELEFON: [MessageHandler(back_filter, menyuga_qaytish),
                            MessageHandler(filters.CONTACT, sorov_telefon)],

            YONALISH_ISM:     [MessageHandler(back_filter, menyuga_qaytish),
                               MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)],
            YONALISH_FAMILYA: [MessageHandler(back_filter, menyuga_qaytish),
                               MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)],
            YONALISH_YOSH:    [MessageHandler(back_filter, menyuga_qaytish),
                               MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)],
            YONALISH_TELEFON: [MessageHandler(back_filter, menyuga_qaytish),
                               MessageHandler(filters.CONTACT, yonalish_telefon)],
        },
        fallbacks=[
            CommandHandler('tugash', tugash),
            CommandHandler('menyu', menyu),
            CommandHandler('start', start),
            MessageHandler(back_filter, menyuga_qaytish),
        ]
    )

    app.add_handler(conv)
    app.add_handler(CallbackQueryHandler(callback_data))

    app.bot.set_my_commands  # commands set via post_init instead
    logger.info("✅ Bot ishga tushdi!")
    app.run_polling()

if __name__ == '__main__':
    main()
    from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'Bot ishlayapti!')
    def log_message(self, format, *args):
        pass

def run_server():
    server = HTTPServer(('0.0.0.0', 8080), Handler)
    server.serve_forever()

threading.Thread(target=run_server, daemon=True).start()
