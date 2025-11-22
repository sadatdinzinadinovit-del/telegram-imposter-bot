# imposter_bot_500plus.py
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
import random
import sqlite3
import asyncio
from collections import Counter
import logging
import os

# ─────────────────── SOZLASH ───────────────────
TOKEN = "8318613317:AAFlX1anNGwzUKXAfELvtCllz8ZW4f_x14U"
ADMIN_ID = 2084462108
# ──────────────────────────────────────────────

# Log qo'shish
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database faylini o'chirish va yangisini yaratish
if os.path.exists("imposter.db"):
    os.remove("imposter.db")
    print("✅ Eski database o'chirildi")

# Yangi database yaratish
conn = sqlite3.connect("imposter.db", check_same_thread=False)
c = conn.cursor()

# TO'LIQ YANGI JADVALLAR
c.executescript('''
CREATE TABLE channels (
    channel_id TEXT PRIMARY KEY,
    channel_name TEXT,
    required BOOLEAN DEFAULT 1
);

CREATE TABLE users (
    user_id INTEGER PRIMARY KEY,
    name TEXT,
    username TEXT,
    games INTEGER DEFAULT 0,
    wins INTEGER DEFAULT 0,
    imp_wins INTEGER DEFAULT 0,
    crew_wins INTEGER DEFAULT 0,
    rating INTEGER DEFAULT 1000,
    joined_date DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE subscriptions (
    user_id INTEGER,
    channel_id TEXT,
    subscribed BOOLEAN DEFAULT 0,
    PRIMARY KEY (user_id, channel_id)
);
''')
conn.commit()
print("✅ Yangi database yaratildi")

games = {}
user_states = {}

# ─────────────────── AI TOPIC SERVICE ───────────────────
class AITopicService:
    @staticmethod
    async def get_ai_topic():
        """AI orqali cheksiz yangi mavzular yaratish"""
        try:
            return await AITopicService._generate_noun_topic()
        except Exception as e:
            logger.error(f"AI topic xatosi: {e}")
            fallback_real = await AITopicService._get_fallback_topic()
            fallback_fake = await AITopicService._get_fake_fallback_topic()
            return fallback_real, fallback_fake

    @staticmethod
    async def _generate_noun_topic():
        """Faqat noun (ot) lardan topic yaratish - 500+ SOZ"""
        categories = {
            # Uskunalar (50 ta)
            "equipment": [
                "telefon", "kompyuter", "noutbuk", "planshet", "televizor", "smartfon",
                "muzlatgich", "mikrotolqin pech", "kir yuvish mashinasi", "changyutgich",
                "konditsioner", "issiqxona", "mikroskop", "teleskop", "kamera", "fotoapparat",
                "printer", "skaner", "wi-fi router", "powerbank", "smart soat", "naushnik",
                "kolonka", "proyektor", "monitor", "klaviatura", "sichqoncha", "web-kamera",
                "hard disk", "SSD", "operativ xotira", "protsessor", "videokarta", "blok pitaniya",
                "modem", "switch", "server", "planshet qalami", "elektron kitob", "GPS navigator",
                "fitnes-braslet", "aqlli uy tizimi", "robot-tozalagich", "dron", "3D printer",
                "virtual reality", "playstation", "xbox", "nintendo", "gamepad"
            ],

            # Taomlar (25 ta)
            "foods": [
                "Pizza", "Burger", "Pasta", "Sushi", "Kebab",
                "Biryani", "Tacos", "Fried Chicken", "Steak", "Salad",
                "Ramen", "Shawarma", "Sandwich", "Hotdog", "Soup",
                "Dessert", "Ice Cream", "Chocolate", "Pancakes", "Waffles",
                "Rice", "Noodles", "Fish and Chips", "Dumplings", "Curry"
            ],
            
            # Mevalar va sabzavotlar (60+)
            "fruits_veggies": [
                "olma", "banan", "apelsin", "limon", "nok", "shaftoli", "uzum", "anor", "xurmo",
                "qovun", "tarvuz", "greypfrut", "mandarin", "kiwi", "avakado", "anjir", "olxo'ri",
                "gilos", "qulupnay", "malina", "yerqulupnay", "kartoshka", "pomidor", "bodring",
                "sabzi", "piyoz", "sarimsoq", "qalampir", "karam", "salat", "baqlajon", "qovoq",
                "loviya", "no'xat", "mosh", "sholg'om", "rediska", "brokoli", "karnabit", "shpinat",
                "petrushka", "ukrop", "basil", "rayhon", "qalampircha", "pomidor paste", "tuz",
                "qalampir qora", "zira", "zarcho'va", "dimlama", "salat bargi", "kashnich", "lavlagi",
                "qizil sabzi", "sariq sabzi", "qovoq po'chog'i", "kartoshka chipsi", "pishloq"
            ],
            
            # Aktyorlar va aktrisalar (50+)
            "actors": [
                "Leonardo DiCaprio", "Brad Pitt", "Tom Cruise", "Johnny Depp", "Will Smith",
                "Robert Downey Jr", "Tom Hanks", "Denzel Washington", "Morgan Freeman",
                "Matt Damon", "George Clooney", "Bruce Willis", "Arnold Schwarzenegger",
                "Sylvester Stallone", "Jackie Chan", "Keanu Reeves", "Chris Hemsworth",
                "Chris Evans", "Robert Pattinson", "Daniel Radcliffe", "Jennifer Lawrence",
                "Emma Watson", "Scarlett Johansson", "Angelina Jolie", "Meryl Streep",
                "Natalie Portman", "Margot Robbie", "Anne Hathaway", "Julia Roberts",
                "Sandra Bullock", "Nicole Kidman", "Charlize Theron", "Gal Gadot",
                "Zendaya", "Emma Stone", "Jessica Chastain", "Cate Blanchett", "Helen Mirren",
                "Judi Dench", "Kate Winslet", "Penelope Cruz", "Salma Hayek", "Priyanka Chopra",
                "Deepika Padukone", "Aishwarya Rai", "Shah Rukh Khan", "Amitabh Bachchan",
                "Jack Nicholson", "Al Pacino", "Robert De Niro"
            ],
            
            # Filmlar va seriallar (60+)
            "movies_series": [
                "Titanic", "Avatar", "Avengers", "Harry Potter", "The Lord of the Rings",
                "Game of Thrones", "Breaking Bad", "Stranger Things", "Friends", "La Casa de Papel",
                "The Witcher", "Squid Game", "Peaky Blinders", "Pulp Fiction", "Inception",
                "The Matrix", "Forrest Gump", "The Godfather", "Star Wars", "Jurassic Park",
                "Spider-Man", "Batman", "Superman", "Iron Man", "Black Panther", "Wonder Woman",
                "The Dark Knight", "Fight Club", "The Shawshank Redemption", "The Silence of the Lambs",
                "Gladiator", "Braveheart", "Troy", "300", "The Hunger Games", "Twilight",
                "Pirates of the Caribbean", "Transformers", "Fast and Furious", "Mission Impossible",
                "James Bond", "John Wick", "The Terminator", "Back to the Future", "Home Alone",
                "The Lion King", "Frozen", "Toy Story", "Finding Nemo", "Shrek", "The Simpsons",
                "South Park", "Rick and Morty", "The Big Bang Theory", "How I Met Your Mother",
                "The Office", "Sherlock", "Doctor Who", "Money Heist", "Narcos"
            ],
            
            # Futbol klublari (50+)
            "football_clubs": [
                "Barcelona", "Real Madrid", "Manchester United", "Manchester City", "Liverpool",
                "Chelsea", "Arsenal", "Bayern Munich", "PSG", "Juventus", "AC Milan", "Inter Milan",
                "Ajax", "Borussia Dortmund", "Atletico Madrid", "Tottenham", "Napoli", "Roma",
                "Benfica", "Porto", "Celtic", "Rangers", "Galatasaray", "Fenerbahce", "Besiktas",
                "Zenit", "Spartak Moscow", "CSKA Moscow", "Shakhtar Donetsk", "Dynamo Kyiv",
                "Red Bull Salzburg", "Basel", "Young Boys", "Club Brugge", "Anderlecht",
                "Lyon", "Marseille", "Monaco", "Lille", "Leicester City", "West Ham", "Everton",
                "Newcastle", "Aston Villa", "Leeds United", "Wolves", "Brighton", "Crystal Palace",
                "Southampton", "Burnley"
            ],
            
            # Sport turlari (40+)
            "sports": [
                "futbol", "basketbol", "tennis", "voleybol", "beysbol", "golf", "boks", "MMA",
                "suzish", "gimnastika", "atletika", "velosport", "motorsport", "chang'i sporti",
                "figurali uchish", "xokkey", "krikett", "rugby", "badminton", "stol tennisi",
                "bilyard", "shaxmat", "shashka", "karate", "judo", "taekwondo", "kung-fu",
                "jimnastika", "akrobatika", "sport raqslari", "yugurish", "sakrash", "uloatish",
                "og'ir atletika", "bodibilding", "krosfit", "yoga", "pilates", "fitness", "trx"
            ],
            
            # Mamlakatlar (60+)
            "countries": [
                "O'zbekiston", "AQSh", "Rossiya", "Xitoy", "Yaponiya", "Koreya", "Germaniya",
                "Fransiya", "Italiya", "Ispaniya", "Braziliya", "Argentina", "Meksika", "Kanada",
                "Avstraliya", "Hindiston", "Turkiya", "Misr", "Saudiya Arabistoni", "Shvetsiya",
                "Norvegiya", "Finlandiya", "Daniya", "Niderlandiya", "Belgiya", "Shveytsariya",
                "Avstriya", "Polsha", "Chexiya", "Slovakiya", "Vengriya", "Ruminiya", "Bolgariya",
                "Gretsiya", "Portugaliya", "Ukraina", "Belarus", "Qozog'iston", "Qirg'iziston",
                "Tojikiston", "Turkmaniston", "Ozarbayjon", "Armaniston", "Gruziya", "Isroil",
                "Iroq", "Eron", "Afg'oniston", "Pokiston", "Bangladesh", "Indoneziya", "Tailand",
                "Vyetnam", "Filippin", "Malayziya", "Singapur", "Maroko", "Janubiy Afrika", "Kenya"
            ],
            
            # Hayvonlar (70+)
            "animals": [
                "sher", "fil", "zebra", "jirafa", "ayiq", "bo'ri", "tulki", "quyon", "sichqon",
                "kalamush", "maymun", "orangutan", "gorilla", "timsoh", "ilon", "kobra", "baliq",
                "akula", "kit", "delfin", "burgut", "qarg'a", "laylak", "bayoq", "qush", "kaptar",
                "buloq", "qizilqurt", "chumoli", "ari", "kapalak", "chivin", "pasha", "chayon",
                "o'rgimchak", "qurbaqa", "salamandra", "toshbaqa", "kaltakesak", "tungi", "sassiqko'zan",
                "bo'ri", "yo'lbars", "gepard", "jaguar", "leopard", "puma", "ris", "sirtlon",
                "shakal", "mungo", "yumronqoziq", "kirpi", "ko'rsichqon", "suv sichqoni", "qunduz",
                "moxovoy", "suviti", "morskoy kot", "tyulen", "mors", "pingvin", "flamingo",
                "lebed", "gus", "o'rdak", "burgut", "qirg'iy", "lochin", "boyo'g'li", "qarg'a",
                "zog'", "tovus", "kakadu", "toti"
            ],
            
            # Mashinalar (50+)
            "cars": [
                "Mercedes", "BMW", "Audi", "Toyota", "Honda", "Ford", "Chevrolet", "Tesla",
                "Porsche", "Ferrari", "Lamborghini", "Bugatti", "Lexus", "Hyundai", "Kia",
                "Nissan", "Volkswagen", "Volvo", "Subaru", "Mazda", "Mitsubishi", "Suzuki",
                "Jeep", "Land Rover", "Range Rover", "Jaguar", "Mini", "Fiat", "Alfa Romeo",
                "Maserati", "Bentley", "Rolls-Royce", "Aston Martin", "McLaren", "Koenigsegg",
                "Pagani", "Lada", "GAZ", "UAZ", "Chevrolet Camaro", "Ford Mustang", "Dodge Challenger",
                "Nissan GT-R", "Toyota Supra", "Honda Civic", "Volkswagen Golf", "BMW M3",
                "Audi RS6", "Mercedes AMG", "Porsche 911"
            ],
            
            # O'yinlar (50+)
            "games": [
                "PUBG", "Minecraft", "Fortnite", "Call of Duty", "GTA", "The Legend of Zelda",
                "Super Mario", "FIFA", "PES", "Counter-Strike", "Dota", "League of Legends",
                "Valorant", "Among Us", "Roblox", "Clash of Clans", "Candy Crush", "Angry Birds",
                "Temple Run", "Subway Surfers", "Pokemon Go", "World of Warcraft", "Diablo",
                "Overwatch", "Apex Legends", "Rainbow Six Siege", "Battlefield", "Assassin's Creed",
                "Far Cry", "Watch Dogs", "Cyberpunk 2077", "The Witcher", "Dark Souls", "Elden Ring",
                "Resident Evil", "Silent Hill", "Need for Speed", "Forza Horizon", "Gran Turismo",
                "The Sims", "SimCity", "Civilization", "Age of Empires", "StarCraft", "Warcraft",
                "Mortal Kombat", "Street Fighter", "Tekken", "Super Smash Bros", "Animal Crossing"
            ]
        }
        
        # Tasodifiy kategoriya tanlash
        category_name = random.choice(list(categories.keys()))
        category_items = categories[category_name]
        
        # Kategoriyadan 2 ta farqli element tanlash
        if len(category_items) >= 2:
            real_topic, fake_topic = random.sample(category_items, 2)
            return real_topic, fake_topic
        else:
            real_topic = category_items[0]
            other_categories = [cat for cat_name, cat in categories.items() if cat_name != category_name]
            fake_category = random.choice(other_categories)
            fake_topic = random.choice(fake_category)
            return real_topic, fake_topic

    @staticmethod
    async def _get_fallback_topic():
        fallback_topics = ["telefon", "olma", "Leonardo DiCaprio", "Barcelona", "sher"]
        return random.choice(fallback_topics)

    @staticmethod
    async def _get_fake_fallback_topic():
        fallback_topics = ["kompyuter", "banan", "Brad Pitt", "Real Madrid", "fil"]
        return random.choice(fallback_topics)

# ─────────────────── ADMIN PANELI ───────────────────
class AdminPanel:
    @staticmethod
    async def admin_panel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            await update.message.reply_text("❌ Siz admin emassiz!")
            return

        keyboard = [
            [InlineKeyboardButton("📊 Statistika", callback_data="admin_stats")],
            [InlineKeyboardButton("📢 Xabar yuborish", callback_data="admin_broadcast")],
            [InlineKeyboardButton("📢 Kanal qo'shish", callback_data="admin_add_channel")],
            [InlineKeyboardButton("❌ Kanal olib tashlash", callback_data="admin_remove_channel")],
            [InlineKeyboardButton("📋 Kanallar ro'yxati", callback_data="admin_list_channels")]
        ]
        
        await update.message.reply_text(
            "🛠 **Admin Panel**\nQuyidagi funksiyalardan foydalaning:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    @staticmethod
    async def admin_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        if q.from_user.id != ADMIN_ID:
            return

        try:
            total_users = c.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            total_games = c.execute("SELECT SUM(games) FROM users").fetchone()[0] or 0
            active_games = len(games)
            
            stats_text = (
                f"📊 **Bot Statistikalari**\n\n"
                f"👥 Jami foydalanuvchilar: {total_users}\n"
                f"🎮 Jami o'yinlar: {total_games}\n"
                f"🔄 Faol o'yinlar: {active_games}"
            )
            
            await q.edit_message_text(stats_text)
        except Exception as e:
            await q.edit_message_text(f"❌ Statistika olishda xato: {e}")

    @staticmethod
    async def add_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        if q.from_user.id != ADMIN_ID:
            return

        await q.edit_message_text(
            "📢 Yangi kanal qo'shish uchun:\n"
            "Kanal ID sini @username formatida yuboring:\n\n"
            "Masalan: @my_channel"
        )
        user_states[ADMIN_ID] = "waiting_channel_id"

    @staticmethod
    async def handle_channel_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            return

        if ADMIN_ID in user_states and user_states[ADMIN_ID] == "waiting_channel_id":
            channel_id = update.message.text.strip()
            
            if not channel_id.startswith('@'):
                await update.message.reply_text("❌ Kanal @username formatida bo'lishi kerak!")
                return

            try:
                c.execute("INSERT OR REPLACE INTO channels (channel_id, channel_name) VALUES (?, ?)", 
                         (channel_id, channel_id))
                conn.commit()
                
                await update.message.reply_text(f"✅ Kanal qo'shildi: {channel_id}")
                del user_states[ADMIN_ID]
                
            except Exception as e:
                await update.message.reply_text(f"❌ Xato: {e}")

    @staticmethod
    async def list_channels(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        if q.from_user.id != ADMIN_ID:
            return

        try:
            channels = c.execute("SELECT channel_id, channel_name FROM channels").fetchall()
            
            if not channels:
                await q.edit_message_text("📋 Hech qanday kanal qo'shilmagan.")
                return

            channels_text = "📋 **Majburiy Kanallar:**\n\n"
            for i, (channel_id, name) in enumerate(channels, 1):
                channels_text += f"{i}. {name}\n"

            keyboard = [[InlineKeyboardButton("🗑 Kanal olib tashlash", callback_data="admin_remove_channel")]]
            await q.edit_message_text(channels_text, reply_markup=InlineKeyboardMarkup(keyboard))
        except Exception as e:
            await q.edit_message_text(f"❌ Kanallarni olishda xato: {e}")

    @staticmethod
    async def remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        if q.from_user.id != ADMIN_ID:
            return

        try:
            channels = c.execute("SELECT channel_id, channel_name FROM channels").fetchall()
            
            if not channels:
                await q.edit_message_text("❌ Olib tashlash uchun kanal yo'q.")
                return

            keyboard = []
            for channel_id, name in channels:
                keyboard.append([InlineKeyboardButton(f"❌ {name}", callback_data=f"remove_{channel_id}")])
            
            keyboard.append([InlineKeyboardButton("🔙 Orqaga", callback_data="admin_panel")])
            
            await q.edit_message_text(
                "Olib tashlamoqchi bo'lgan kanalni tanlang:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        except Exception as e:
            await q.edit_message_text(f"❌ Xato: {e}")

    @staticmethod
    async def handle_remove_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        if q.from_user.id != ADMIN_ID:
            return

        channel_id = q.data.replace("remove_", "")
        
        try:
            c.execute("DELETE FROM channels WHERE channel_id = ?", (channel_id,))
            conn.commit()
            
            await q.edit_message_text(f"✅ Kanal olib tashlandi: {channel_id}")
        except Exception as e:
            await q.edit_message_text(f"❌ Xato: {e}")

    @staticmethod
    async def broadcast_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
        q = update.callback_query
        if q.from_user.id != ADMIN_ID:
            return

        await q.edit_message_text(
            "📢 Hammaga yubormoqchi bo'lgan xabaringizni yuboring:"
        )
        user_states[ADMIN_ID] = "waiting_broadcast_message"

    @staticmethod
    async def handle_broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if update.effective_user.id != ADMIN_ID:
            return

        if ADMIN_ID in user_states and user_states[ADMIN_ID] == "waiting_broadcast_message":
            message_text = update.message.text
            
            try:
                users = c.execute("SELECT user_id FROM users").fetchall()
                
                success_count = 0
                fail_count = 0
                
                for (user_id,) in users:
                    try:
                        await context.bot.send_message(
                            user_id,
                            f"📢 **Botdan xabar:**\n\n{message_text}"
                        )
                        success_count += 1
                        await asyncio.sleep(0.1)
                    except Exception:
                        fail_count += 1
                
                await update.message.reply_text(
                    f"📊 **Xabar yuborish natijasi:**\n\n"
                    f"✅ Muvaffaqiyatli: {success_count}\n"
                    f"❌ Xato: {fail_count}\n"
                    f"👥 Jami: {len(users)}"
                )
                del user_states[ADMIN_ID]
            except Exception as e:
                await update.message.reply_text(f"❌ Xabar yuborishda xato: {e}")

# ─────────────────── O'YIN BOSHLASH ───────────────────
async def newgame(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        
        # Obuna tekshirish
        channels = c.execute("SELECT channel_id FROM channels WHERE required = 1").fetchall()
        if channels:
            if not await check_subscription(user_id, context.bot):
                await update.message.reply_text(
                    "📢 Iltimos, quyidagi kanallarga obuna bo'ling o'yin o'ynash uchun:",
                    reply_markup=await get_subscription_keyboard()
                )
                return
        
        # Agar allaqachon o'yin bo'lsa
        if chat_id in games and games[chat_id]["started"]:
            await update.message.reply_text("⚠️ Bu guruhda allaqachon faol o'yin mavjud!")
            return
        
        games[chat_id] = {
            "players": [],
            "started": False,
            "imposters": [],
            "topic": "",
            "fake_topic": "",
            "votes": {},
            "has_voted": set(),
            "message_id": None,
            "chat_title": update.effective_chat.title
        }
        
        keyboard = [
            [InlineKeyboardButton("🎮 Qo'shilish", callback_data="join")],
            [InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")]
        ]
        
        msg = await update.message.reply_text(
            "🎯 **Yangi Imposter o'yini yaratildi!**\n\n"
            "Qo'shilish uchun tugmani bosing:\n"
            "👥 O'yinchilar: 0\n\n"
            "🚀 O'yinni boshlash uchun kamida 4 ta o'yinchi kerak!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        
        games[chat_id]["message_id"] = msg.message_id
    except Exception as e:
        logger.error(f"newgame xatosi: {e}")
        await update.message.reply_text("❌ O'yin yaratishda xato!")

async def check_subscription(user_id, bot):
    """Foydalanuvchi barcha kanallarga obuna bo'lganligini tekshirish"""
    try:
        channels = c.execute("SELECT channel_id FROM channels WHERE required = 1").fetchall()
        
        if not channels:
            return True
        
        for (channel_id,) in channels:
            try:
                member = await bot.get_chat_member(channel_id, user_id)
                if member.status in ['left', 'kicked']:
                    return False
            except Exception as e:
                logger.error(f"Obuna tekshirish xatosi {channel_id}: {e}")
                continue
        
        return True
    except Exception as e:
        logger.error(f"check_subscription xatosi: {e}")
        return True

async def get_subscription_keyboard():
    """Obuna kanallari tugmalari"""
    try:
        channels = c.execute("SELECT channel_id, channel_name FROM channels WHERE required = 1").fetchall()
        keyboard = []
        
        for channel_id, channel_name in channels:
            keyboard.append([InlineKeyboardButton(f"📢 {channel_name}", url=f"https://t.me/{channel_id[1:]}")])
        
        keyboard.append([InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")])
        return InlineKeyboardMarkup(keyboard)
    except Exception as e:
        logger.error(f"get_subscription_keyboard xatosi: {e}")
        return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Tekshirish", callback_data="check_subscription")]])

# ─────────────────── O'YINCHI QO'SHISH ───────────────────
async def join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        user = q.from_user
        chat_id = q.message.chat_id
        
        if chat_id not in games:
            await q.answer("❌ O'yin topilmadi!", show_alert=True)
            return
            
        game = games[chat_id]
        
        if game["started"]:
            await q.answer("❌ O'yin allaqachon boshlandi!", show_alert=True)
            return
        
        # O'yinchi allaqachon qo'shilganmi?
        if any(p["id"] == user.id for p in game["players"]):
            await q.answer("❌ Siz allaqachon qo'shilgansiz!", show_alert=True)
            return
        
        # O'yinchini qo'shish
        game["players"].append({
            "id": user.id, 
            "name": user.first_name or f"User{user.id}",
            "username": user.username
        })
        
        # Bazada foydalanuvchi mavjudligini tekshirish
        c.execute("INSERT OR IGNORE INTO users (user_id, name, username) VALUES (?, ?, ?)", 
                  (user.id, user.first_name or "User", user.username))
        conn.commit()
        
        # O'yinchilar ro'yxatini yangilash
        plist = "\n".join(f"👤 {p['name']}" for p in game["players"])
        
        keyboard = [[InlineKeyboardButton("🎮 Qo'shilish", callback_data="join")]]
        
        if len(game["players"]) >= 4:
            keyboard.append([InlineKeyboardButton("🚀 O'yinni boshlash", callback_data="start")])
        
        keyboard.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="cancel")])
        
        await q.edit_message_text(
            f"🎯 **Imposter O'yini**\n\n"
            f"👥 O'yinchilar ({len(game['players'])}):\n{plist}\n\n"
            f"✅ O'yinni boshlash uchun '🚀 O'yinni boshlash' tugmasini bosing!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"join xatosi: {e}")
        await q.answer("❌ Xato!", show_alert=True)

# ─────────────────── O'YIN BOSHLASH ───────────────────
async def start_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        chat_id = q.message.chat_id
        
        if chat_id not in games:
            await q.answer("❌ O'yin topilmadi!", show_alert=True)
            return
            
        game = games[chat_id]
        
        if len(game["players"]) < 4:
            await q.answer("❌ Kamida 4 ta o'yinchi kerak!", show_alert=True)
            return
        
        if game["started"]:
            await q.answer("❌ O'yin allaqachon boshlandi!", show_alert=True)
            return
        
        game["started"] = True

        # AI orqali mavzular olish
        real_topic, fake_topic = await AITopicService.get_ai_topic()
        game["topic"] = real_topic
        game["fake_topic"] = fake_topic

        # Imposterlarni tanlash
        imp_count = 1 if len(game["players"]) <= 6 else 2
        imposters = random.sample(game["players"], imp_count)
        game["imposters"] = [p["id"] for p in imposters]

        # Rol xabarlarini SHAXSIY CHATDA yuborish
        successful_messages = 0
        for p in game["players"]:
            role = "IMPOSTER 🎭" if p["id"] in game["imposters"] else "CREWMATE 👨‍🚀"
            secret = game["fake_topic"] if p["id"] in game["imposters"] else game["topic"]
            
            try:
                await context.bot.send_message(
                    p["id"],
                    f"🎮 **Sizning rolingiz: {role}**\n\n"
                    f"📖 Mavzu: **{secret}**\n\n"
                    f"💡 **Qoida:** Guruhda faqat shu mavzuga oid gapiring!\n"
                    f"🎭 **Imposterlar** yolg'on mavzuga oid gapirishadi!\n"
                    f"⏰ Muhokama vaqti: 70 soniya\n\n"
                    f"🏷️ Guruh: {game['chat_title']}"
                )
                successful_messages += 1
            except Exception as e:
                logger.error(f"Xabar yuborishda xato: {e}")

        if successful_messages < 3:
            await q.edit_message_text("❌ Ko'pchilik o'yinchilar bot bilan chat boshmagan! O'yin bekor qilindi.")
            del games[chat_id]
            return

        await q.edit_message_text(
            f"🚀 **O'YIN BOSHLANDI!**\n\n"
            f"🎭 Imposterlar: {imp_count} ta\n"
            f"⏰ 70 soniya muhokama qiling...\n\n"
            f"💬 Faqat mavzu haqida gapiring!"
        )

        # Muhokama vaqti
        await asyncio.sleep(70)

        # Ovoz berish bosqichi - SHAXSIY CHATDA
        await context.bot.send_message(
            chat_id, 
            "🗳️ **OVOZ BERISH VAQTI!**\n\n"
            "Hamma @ImposterWordBot bilan SHAXSIY CHATDA ovoz beradi!\n"
            "Ovozingiz sir saqlanadi!"
        )

        # Har bir o'yinchiga SHAXSIY CHATDA ovoz berish tugmalari
        for player in game["players"]:
            kb = []
            for p in game["players"]:
                kb.append([InlineKeyboardButton(f"🗳️ {p['name']}", callback_data=f"vote_{chat_id}_{p['id']}")])
            kb.append([InlineKeyboardButton("❌ Hech kim", callback_data=f"vote_{chat_id}_none")])
            
            try:
                await context.bot.send_message(
                    player["id"],
                    f"🎭 **Kim impostor deb o'ylaysiz?**\n\n"
                    f"Guruh: {game['chat_title']}\n"
                    f"Ovozingiz sir saqlanadi!",
                    reply_markup=InlineKeyboardMarkup(kb)
                )
            except Exception as e:
                logger.error(f"Ovoz xabarini yuborishda xato: {e}")
    except Exception as e:
        logger.error(f"start_game xatosi: {e}")
        await q.answer("❌ Xato!", show_alert=True)

# ─────────────────── OVOZ BERISH TIZIMI ───────────────────
async def private_vote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        user_id = q.from_user.id
        data = q.data.split("_")

        if len(data) < 3:
            await q.answer("❌ Xato!", show_alert=True)
            return
            
        chat_id = int(data[1])
        voted = data[2]

        if chat_id not in games:
            await q.edit_message_text("❌ O'yin topilmadi yoki tugagan!")
            return
            
        game = games[chat_id]
        
        if user_id not in [p["id"] for p in game["players"]]:
            await q.edit_message_text("❌ Siz bu o'yinda emassiz!")
            return
            
        if user_id in game["has_voted"]:
            await q.answer("❌ Siz allaqachon ovoz bergansiz!", show_alert=True)
            return

        voted_id = None if voted == "none" else int(voted)
        game["votes"][user_id] = voted_id
        game["has_voted"].add(user_id)

        await q.edit_message_text("✅ **Ovozingiz qabul qilindi!**")

        progress = len(game['has_voted'])
        total = len(game['players'])
        
        if progress == total:
            await finish_game(chat_id, context.bot, game)
    except Exception as e:
        logger.error(f"private_vote xatosi: {e}")
        await q.answer("❌ Xato!", show_alert=True)

async def finish_game(chat_id, bot, game):
    try:
        votes = [v for v in game["votes"].values() if v is not None]
        
        if not votes:
            result_text = "❌ Hech kim ovoz bermadi!\nO'yin durang bilan tugadi."
            winner = "none"
        else:
            count = Counter(votes)
            ejected_id, votes_received = count.most_common(1)[0]
            
            max_votes = votes_received
            candidates = [pid for pid, v in count.items() if v == max_votes]
            
            if len(candidates) > 1:
                ejected_id = random.choice(candidates)
            
            ejected_player = next(p for p in game["players"] if p["id"] == ejected_id)
            is_imposter = ejected_id in game["imposters"]

            if is_imposter:
                result_text = (
                    f"🎉 **CREWMATE G'ALABA!** 🎉\n\n"
                    f"🎭 {ejected_player['name']} HAQIQIY IMPOSTER EDI! ✅\n"
                    f"🗳️ Uni {votes_received} ta ovoz bilan chiqardilar!\n\n"
                    f"👨‍🚀 Crewmatelar g'alaba qozondi!"
                )
                winner = "crew"
            else:
                result_text = (
                    f"💀 **IMPOSTER G'ALABA!** 💀\n\n"
                    f"👨‍🚀 {ejected_player['name']} HAQSIZ CREWMATE EDI! ❌\n"
                    f"🗳️ Uni {votes_received} ta ovoz bilan chiqardilar!\n\n"
                    f"🎭 Imposterlar g'alaba qozondi!"
                )
                winner = "imp"

            result_text += (
                f"\n\n📖 **Haqiqiy mavzu:** {game['topic']}\n"
                f"🤥 **Yolg'on mavzu:** {game['fake_topic']}\n"
                f"🎭 **Imposterlar:** {', '.join(p['name'] for p in game['players'] if p['id'] in game['imposters'])}"
            )

        await bot.send_message(chat_id, f"🏁 **O'YIN TUGADI!**\n\n{result_text}")

        await update_statistics(game, winner)

        if chat_id in games:
            del games[chat_id]
    except Exception as e:
        logger.error(f"finish_game xatosi: {e}")

async def update_statistics(game, winner):
    try:
        for p in game["players"]:
            c.execute("UPDATE users SET games = games + 1 WHERE user_id=?", (p["id"],))
            
            if winner == "crew":
                if p["id"] not in game["imposters"]:
                    c.execute("UPDATE users SET wins = wins + 1, crew_wins = crew_wins + 1, rating = rating + 25 WHERE user_id=?", (p["id"],))
                else:
                    c.execute("UPDATE users SET rating = rating - 20 WHERE user_id=?", (p["id"],))
            elif winner == "imp":
                if p["id"] in game["imposters"]:
                    c.execute("UPDATE users SET wins = wins + 1, imp_wins = imp_wins + 1, rating = rating + 30 WHERE user_id=?", (p["id"],))
                else:
                    c.execute("UPDATE users SET rating = rating - 15 WHERE user_id=?", (p["id"],))
        
        conn.commit()
    except Exception as e:
        logger.error(f"update_statistics xatosi: {e}")

# ─────────────────── STATISTIKA ───────────────────
async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        row = c.execute("SELECT games, wins, imp_wins, crew_wins, rating FROM users WHERE user_id=?", (user_id,)).fetchone()
        
        if not row:
            await update.message.reply_text("📊 Siz hali o'ynamagansiz!")
            return
            
        g, w, iw, cw, r = row
        win_rate = (w / g * 100) if g > 0 else 0
        
        await update.message.reply_text(
            f"📊 **Statistikangiz**\n\n"
            f"🎮 O'yinlar: {g}\n"
            f"🏆 G'alabalar: {w}\n"
            f"📈 G'alaba foizi: {win_rate:.1f}%\n\n"
            f"🎭 Imposter g'alaba: {iw}\n"
            f"👨‍🚀 Crewmate g'alaba: {cw}\n"
            f"⭐ Rating: {r}"
        )
    except Exception as e:
        logger.error(f"stats xatosi: {e}")
        await update.message.reply_text("❌ Statistika olishda xato!")

async def top(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        rows = c.execute("SELECT name, rating, wins FROM users ORDER BY rating DESC LIMIT 10").fetchall()
        
        text = "🏆 **Global Top-10** 🏆\n\n"
        for i, (n, r, w) in enumerate(rows, 1):
            text += f"{i}. {n} — {r} ⭐ | {w} 🏆\n"
        
        await update.message.reply_text(text or "📊 Hali reyting yo'q")
    except Exception as e:
        logger.error(f"top xatosi: {e}")
        await update.message.reply_text("❌ Reyting olishda xato!")

# ─────────────────── BOSHQA FUNKSIYALAR ───────────────────
async def cancel_game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        chat_id = q.message.chat_id
        
        if chat_id in games:
            del games[chat_id]
        
        await q.edit_message_text("❌ O'yin bekor qilindi!")
    except Exception as e:
        logger.error(f"cancel_game xatosi: {e}")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Founded by @DarkPixelGames\n"
        "🎮 Imposter Botga xush kelibsiz!\n\n"
        "O'yinni boshlash uchun botni guruhda admin qiling va /newgame buyrug'ini bering\n"
        
        "📊Statistika: /stats\n"
        "🏆Reyting: /top\n"
    )

async def check_subscription_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        q = update.callback_query
        user_id = q.from_user.id
        
        if await check_subscription(user_id, context.bot):
            await q.edit_message_text("✅ Siz barcha kanallarga obuna bo'lgansiz! Endi o'yin o'ynashingiz mumkin.")
        else:
            await q.answer("❌ Hali barcha kanallarga obuna bo'lmagansiz!", show_alert=True)
    except Exception as e:
        logger.error(f"check_subscription_callback xatosi: {e}")

# ─────────────────── MAIN FUNKSIYA ───────────────────
def main():
    try:
        app = Application.builder().token(TOKEN).build()

        # Komanda handlerlari
        app.add_handler(CommandHandler("newgame", newgame))
        app.add_handler(CommandHandler("stats", stats))
        app.add_handler(CommandHandler("top", top))
        app.add_handler(CommandHandler("admin", AdminPanel.admin_panel))
        app.add_handler(CommandHandler("start", start_command))

        # Xabar handlerlari
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, AdminPanel.handle_channel_input))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, AdminPanel.handle_broadcast))

        # Callback handlerlari
        app.add_handler(CallbackQueryHandler(join, pattern="^join$"))
        app.add_handler(CallbackQueryHandler(start_game, pattern="^start$"))
        app.add_handler(CallbackQueryHandler(private_vote, pattern="^vote_"))
        app.add_handler(CallbackQueryHandler(cancel_game, pattern="^cancel$"))
        app.add_handler(CallbackQueryHandler(check_subscription_callback, pattern="^check_subscription$"))
        
        # Admin callback handlerlari
        app.add_handler(CallbackQueryHandler(AdminPanel.admin_stats, pattern="^admin_stats$"))
        app.add_handler(CallbackQueryHandler(AdminPanel.broadcast_message, pattern="^admin_broadcast$"))
        app.add_handler(CallbackQueryHandler(AdminPanel.add_channel, pattern="^admin_add_channel$"))
        app.add_handler(CallbackQueryHandler(AdminPanel.remove_channel, pattern="^admin_remove_channel$"))
        app.add_handler(CallbackQueryHandler(AdminPanel.list_channels, pattern="^admin_list_channels$"))
        app.add_handler(CallbackQueryHandler(AdminPanel.handle_remove_channel, pattern="^remove_"))

        print("🤖 Bot muvaffaqiyatli ishga tushdi!")
        print("🎯 500+ soz bilan to'liq tayyor!")
        print("📊 Barcha xususiyatlar ishga tushdi")
        
        app.run_polling()
    except Exception as e:
        logger.error(f"main xatosi: {e}")

if __name__ == "__main__":
    main()
