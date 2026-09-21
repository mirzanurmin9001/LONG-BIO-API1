#!/usr/bin/env python3
"""
Free Fire Auto Spinner — Telegram Bot (Premium UI + Bilingual)
"""

import asyncio
try:
    asyncio.get_event_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

import os
import sys
import re
import json
import time
import traceback
import tempfile
import shutil
from datetime import datetime

# ==================== DEBUG INFO ====================
print("=" * 60)
print(f"[DEBUG] Python: {sys.version}")
print(f"[DEBUG] CWD: {os.getcwd()}")
print(f"[DEBUG] Files: {os.listdir('.')}")
print("=" * 60)

from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, InputFile
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters
)
from telegram.constants import ParseMode

import aiohttp
import blackboxprotobuf
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad

# ==================== PROTOBUF IMPORT (DEBUG) ====================
try:
    import google.protobuf
    print(f"[DEBUG] protobuf version: {google.protobuf.__version__}")
except Exception as e:
    print(f"[DEBUG] protobuf check failed: {e}")

try:
    import my_pb2
    print("[DEBUG] my_pb2 imported OK")
except Exception as e:
    print(f"[DEBUG] my_pb2 IMPORT FAILED:")
    traceback.print_exc()
    raise SystemExit(f"[!] my_pb2 import failed: {type(e).__name__}: {e}")

try:
    import output_pb2
    print("[DEBUG] output_pb2 imported OK")
except Exception as e:
    print(f"[DEBUG] output_pb2 IMPORT FAILED:")
    traceback.print_exc()
    raise SystemExit(f"[!] output_pb2 import failed: {type(e).__name__}: {e}")

print("[DEBUG] All imports OK — starting bot...")
print("=" * 60)


# ==================== CONFIG ====================
BOT_TOKEN = "8913853842:AAHWQyNY-SisDL7X84h7AzDDKkFuF-0fDDw"

AES_KEY = bytes([89, 103, 38, 116, 99, 37, 68, 69, 117, 104, 54, 37, 90, 99, 94, 56])
AES_IV  = bytes([54, 111, 121, 90, 68, 114, 50, 50, 69, 51, 121, 99, 104, 106, 77, 37])

SERVERS = {
    "bd":  {"name": "Bangladesh 🇧🇩", "url": "https://clientbp.ggpolarbear.com"},
    "ind": {"name": "India 🇮🇳",      "url": "https://client.ind.freefiremobile.com"},
}

EXTERNAL_JWT_API = "https://jwt-fmhy.vercel.app/token"
RELEASE_VERSION  = "OB55"
DEFAULT_SPIN_HEX = "7DF7F8996CD696356CD01BCBD2B3CDE8"

RARE_ITEMS_DB = {
    710047022: "NARUTO BUNDLE",
    801055004: "NARUTO TOKEN",
    820981015: "BLUE NINJA VOUCHER",
    903047008: "Loot Box - Body Substitution",
    904047008: "Backpack - Ninja's Scroll",
    907104746: "Gloo Wall - Hokage Rock",
    909047015: "Rasengan",
}
ULTRA_RARE_IDS = {710047022}

# ==================== STATE ====================
user_sessions = {}
user_tasks = {}
user_stats = {}
user_lang = {}


# ==================== TRANSLATIONS ====================
T = {
    "en": {
        "welcome_title": "👋 *Welcome, {name}!*",
        "welcome_sub": "🎁 *FREE FIRE AUTO SPINNER BOT*",
        "welcome_tag": "⚡ Fast • Secure • Multi-Server",
        "how_to": "📌 *How to use:*",
        "step1": "1️⃣ Tap 🚀 New Spin",
        "step2": "2️⃣ Select server (BD/IND)",
        "step3": "3️⃣ Upload accounts file (.json/.txt)",
        "step4": "4️⃣ Select concurrency",
        "step5": "5️⃣ Get results!",
        "use_buttons": "👇 Use the buttons below:",
        "btn_spin": "🚀 New Spin",
        "btn_stats": "📊 My Stats",
        "btn_profile": "👤 Profile",
        "btn_lang": "🌐 Language",
        "btn_cancel": "🛑 Cancel",
        "select_server": "🌐 *SELECT SERVER*\n\nChoose your target server:",
        "select_conc": "⚙️ *SELECT CONCURRENCY:*",
        "server": "🌐 *Server:* {srv}",
        "conc_safe": "⚡ 10 (Safe)",
        "conc_bal": "🚀 20 (Balanced)",
        "conc_fast": "🔥 30 (Fast)",
        "conc_max": "💎 50 (Max)",
        "back": "◀ Back",
        "cancel": "❌ Cancel",
        "cancelled": "❌ Cancelled.",
        "ready": "✅ *READY TO START*\n━━━━━━━━━━━━━━━\n\n🌐 Server: {srv}\n⚙️ Concurrency: `{cc}`\n\n📁 *Now upload your accounts file* (.json/.txt)\n👇 Just send it as a document.",
        "already_run": "⏳ Already running. Use 🛑 Cancel first.",
        "nothing_run": "ℹ️ Nothing running.",
        "select_first": "❌ Please tap 🚀 *New Spin* first.",
        "only_json": "❌ Only `.json` or `.txt` files allowed.",
        "downloading": "📥 Downloading file...",
        "dl_fail": "❌ Download failed: {e}",
        "no_valid": "❌ No valid accounts found.",
        "loaded": "✅ *Loaded {n} accounts*\n\n🚀 Starting spin...",
        "spinning": "🚀 *SPINNING...*\n━━━━━━━━━━━━━━━",
        "processed": "`{done}/{total}` processed ({pct}%)",
        "ultra": "👑 Ultra",
        "rare": "🎁 Rare",
        "items": "📦 Items",
        "failed": "❌ Failed",
        "done": "✅ *SPIN COMPLETED!*",
        "accounts": "👥 *Accounts:* `{n}`",
        "sending_files": "📁 Sending result files...",
        "back_menu": "🏠 *Back to main menu*",
        "cancel_done": "🛑 *Task Cancelled*\n\nProcess stopped successfully.",
        "stats_title": "📊 *MY STATISTICS*",
        "total_spins": "🎰 *Total Spins:*",
        "ultra_rare": "👑 *Ultra Rare:*",
        "rare_items": "🎁 *Rare Items:*",
        "joined": "📅 *Joined:*",
        "keep_spin": "🎯 Keep spinning to get more!",
        "profile_title": "👤 *MY PROFILE*",
        "user_id": "🆔 *User ID:*",
        "name": "📛 *Name:*",
        "username": "🔗 *Username:*",
        "language": "🌍 *Language:*",
        "lang_select": "🌐 *SELECT LANGUAGE*\n\nChoose your preferred language:",
        "lang_changed": "✅ Language changed to *English*",
        "lang_bn": "🇧🇩 বাংলা",
        "lang_en": "🇬🇧 English",
        "not_found": "❌ N/A",
    },
    "bn": {
        "welcome_title": "👋 *স্বাগতম, {name}!*",
        "welcome_sub": "🎁 *ফ্রি ফায়ার অটো স্পিনার বট*",
        "welcome_tag": "⚡ দ্রুত • নিরাপদ • মাল্টি-সার্ভার",
        "how_to": "📌 *ব্যবহারের নিয়ম:*",
        "step1": "1️⃣ 🚀 New Spin চাপুন",
        "step2": "2️⃣ সার্ভার সিলেক্ট করুন (BD/IND)",
        "step3": "3️⃣ অ্যাকাউন্ট ফাইল পাঠান (.json/.txt)",
        "step4": "4️⃣ কনকারেন্সি সিলেক্ট করুন",
        "step5": "5️⃣ রেজাল্ট পেয়ে যান!",
        "use_buttons": "👇 নিচের বাটনগুলো ব্যবহার করুন:",
        "btn_spin": "🚀 নতুন স্পিন",
        "btn_stats": "📊 আমার স্ট্যাটস",
        "btn_profile": "👤 প্রোফাইল",
        "btn_lang": "🌐 ভাষা",
        "btn_cancel": "🛑 বাতিল",
        "select_server": "🌐 *সার্ভার সিলেক্ট করুন*\n\nআপনার টার্গেট সার্ভার বেছে নিন:",
        "select_conc": "⚙️ *কনকারেন্সি সিলেক্ট করুন:*",
        "server": "🌐 *সার্ভার:* {srv}",
        "conc_safe": "⚡ 10 (নিরাপদ)",
        "conc_bal": "🚀 20 (ব্যালেন্সড)",
        "conc_fast": "🔥 30 (দ্রুত)",
        "conc_max": "💎 50 (সর্বোচ্চ)",
        "back": "◀ পিছনে",
        "cancel": "❌ বাতিল",
        "cancelled": "❌ বাতিল হয়েছে।",
        "ready": "✅ *শুরু করার জন্য প্রস্তুত*\n━━━━━━━━━━━━━━━\n\n🌐 সার্ভার: {srv}\n⚙️ কনকারেন্সি: `{cc}`\n\n📁 *এখন আপনার অ্যাকাউন্ট ফাইল পাঠান* (.json/.txt)\n👇 শুধু ডকুমেন্ট হিসেবে পাঠান।",
        "already_run": "⏳ ইতিমধ্যে চলছে। 🛑 বাতিল চাপুন।",
        "nothing_run": "ℹ️ কিছুই চলছে না।",
        "select_first": "❌ আগে 🚀 *নতুন স্পিন* চাপুন।",
        "only_json": "❌ শুধু `.json` বা `.txt` ফাইল পাঠান।",
        "downloading": "📥 ফাইল ডাউনলোড হচ্ছে...",
        "dl_fail": "❌ ডাউনলোড ব্যর্থ: {e}",
        "no_valid": "❌ কোনো বৈধ অ্যাকাউন্ট পাওয়া যায়নি।",
        "loaded": "✅ *{n} টি অ্যাকাউন্ট লোড হয়েছে*\n\n🚀 স্পিন শুরু হচ্ছে...",
        "spinning": "🚀 *স্পিন চলছে...*\n━━━━━━━━━━━━━━━",
        "processed": "`{done}/{total}` প্রসেসড ({pct}%)",
        "ultra": "👑 আল্ট্রা",
        "rare": "🎁 রেয়ার",
        "items": "📦 আইটেম",
        "failed": "❌ ফেইল",
        "done": "✅ *স্পিন সম্পন্ন!*",
        "accounts": "👥 *অ্যাকাউন্ট:* `{n}`",
        "sending_files": "📁 রেজাল্ট ফাইল পাঠানো হচ্ছে...",
        "back_menu": "🏠 *মেইন মেনুতে ফিরে যান*",
        "cancel_done": "🛑 *টাস্ক বাতিল*\n\nপ্রসেস সফলভাবে বন্ধ হয়েছে।",
        "stats_title": "📊 *আমার স্ট্যাটিসটিক্স*",
        "total_spins": "🎰 *মোট স্পিন:*",
        "ultra_rare": "👑 *আল্ট্রা রেয়ার:*",
        "rare_items": "🎁 *রেয়ার আইটেম:*",
        "joined": "📅 *জয়েন:*",
        "keep_spin": "🎯 আরো পেতে স্পিন চালিয়ে যান!",
        "profile_title": "👤 *আমার প্রোফাইল*",
        "user_id": "🆔 *ইউজার আইডি:*",
        "name": "📛 *নাম:*",
        "username": "🔗 *ইউজারনেম:*",
        "language": "🌍 *ভাষা:*",
        "lang_select": "🌐 *ভাষা সিলেক্ট করুন*\n\nআপনার পছন্দের ভাষা বেছে নিন:",
        "lang_changed": "✅ ভাষা পরিবর্তন হয়েছে *বাংলা*",
        "lang_bn": "🇧🇩 বাংলা",
        "lang_en": "🇬🇧 English",
        "not_found": "❌ নেই",
    }
}


# ==================== HELPERS ====================
def get_lang(uid):
    return user_lang.get(uid, "en")


def t(uid, key, **kwargs):
    lang = get_lang(uid)
    txt = T.get(lang, T["en"]).get(key, T["en"].get(key, key))
    return txt.format(**kwargs) if kwargs else txt


def get_or_create_stats(uid):
    if uid not in user_stats:
        user_stats[uid] = {
            "total_spins": 0, "ultra": 0, "rare": 0,
            "joined": datetime.now().strftime("%Y-%m-%d")
        }
    return user_stats[uid]


def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ==================== REPLY KEYBOARD ====================
def main_menu_keyboard(uid):
    kb = [
        [KeyboardButton(t(uid, "btn_spin")),    KeyboardButton(t(uid, "btn_stats"))],
        [KeyboardButton(t(uid, "btn_profile")), KeyboardButton(t(uid, "btn_lang"))],
        [KeyboardButton(t(uid, "btn_cancel"))],
    ]
    return ReplyKeyboardMarkup(kb, resize_keyboard=True, is_persistent=True)


# ==================== CRYPTO ====================
def encrypt_plaintext(plaintext):
    cipher = AES.new(AES_KEY, AES.MODE_CBC, AES_IV)
    return cipher.encrypt(pad(plaintext, AES.block_size))


# ==================== ACCOUNT PARSING ====================
def load_accounts(path):
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        content = f.read()
    content = re.sub(r',\s*}', '}', content)
    content = re.sub(r',\s*]', ']', content)

    accounts = []
    try:
        data = json.loads(content)
        if isinstance(data, list):
            for item in data:
                acc = _extract_acc(item)
                if acc: accounts.append(acc)
        elif isinstance(data, dict):
            for key in ("accounts", "users", "data", "list"):
                if key in data and isinstance(data[key], list):
                    for item in data[key]:
                        acc = _extract_acc(item)
                        if acc: accounts.append(acc)
                    break
            if not accounts:
                acc = _extract_acc(data)
                if acc: accounts.append(acc)
    except Exception:
        pass

    if not accounts:
        pat = r'["\']?uid["\']?\s*:\s*["\']?(\d+)["\']?.*?["\']?password["\']?\s*:\s*["\']([^"\']+)["\']'
        for uid, pwd in re.findall(pat, content, re.IGNORECASE | re.DOTALL):
            accounts.append({"uid": uid, "password": pwd})
    return accounts


def _extract_acc(obj):
    if not isinstance(obj, dict):
        return None
    uid = pwd = None
    for k in ("uid", "UID", "userId", "user_id", "guestUid", "id"):
        if obj.get(k):
            uid = str(obj[k]); break
    for k in ("password", "pass", "pwd", "guestPass", "Password"):
        if obj.get(k):
            pwd = str(obj[k]); break
    return {"uid": uid, "password": pwd} if (uid and pwd) else None


# ==================== TOKEN + SPIN ====================
async def _token_internal(uid, password, session, retries=2):
    oauth_url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    payload = {
        "uid": uid, "password": password,
        "response_type": "token", "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067",
    }
    headers = {"User-Agent": "GarenaMSDK/4.0.19P9"}
    at, oid = None, None

    async def _try():
        nonlocal at, oid
        try:
            async with session.post(oauth_url, data=payload, headers=headers, timeout=5) as r:
                if r.status == 200:
                    d = await r.json()
                    at = d.get("access_token")
                    oid = d.get("open_id")
        except Exception:
            pass

    await asyncio.gather(*[_try() for _ in range(max(1, retries))])
    if not at or not oid:
        return None

    login_url = "https://loginbp.ggblueshark.com/MajorLogin"
    lh = {
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 9; ASUS_Z01QD Build/PI)",
        "Content-Type": "application/octet-stream",
        "X-Unity-Version": "2018.4.11f1",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASE_VERSION,
    }

    def _body(platform):
        g = my_pb2.GameData()
        g.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        g.game_name = "free fire"
        g.game_version = 1
        g.version_code = "1.111.1"
        g.os_info = "Android OS 9 / API-28"
        g.device_type = "Handheld"
        g.network_provider = "Verizon"
        g.connection_type = "WIFI"
        g.screen_width = 1280
        g.screen_height = 960
        g.dpi = "240"
        g.cpu_info = "ARMv7 VFPv3 NEON VMH | 2400 | 4"
        g.total_ram = 5951
        g.gpu_name = "Adreno (TM) 640"
        g.gpu_version = "OpenGL ES 3.0"
        g.user_id = "Google|74b585a9-0268-4ad3-8f36-ef41d2e53610"
        g.ip_address = "172.190.111.97"
        g.language = "en"
        g.open_id = oid
        g.access_token = at
        g.platform_type = platform
        g.field_99 = str(platform)
        g.field_100 = str(platform)
        return encrypt_plaintext(g.SerializeToString())

    async def _plat(p):
        try:
            async with session.post(login_url, data=_body(p), headers=lh, ssl=False, timeout=6) as r:
                if r.status != 200:
                    return None
                resp = await r.read()
                try:
                    rp = output_pb2.Garena_420()
                    rp.ParseFromString(resp)
                    if rp.token:
                        return rp.token
                except Exception:
                    pass
                text = resp.decode("utf-8", errors="ignore")
                s = text.find("eyJ")
                if s != -1:
                    e = s
                    while e < len(text) and text[e] not in '" \n\r\t\x00':
                        e += 1
                    j = text[s:e]
                    if j.count(".") >= 2:
                        return j
        except Exception:
            return None
        return None

    results = await asyncio.gather(*[_plat(p) for p in (8, 3, 4, 6)], return_exceptions=True)
    for r in results:
        if isinstance(r, str) and r:
            return r
    return None


async def _token_external(uid, password, session):
    try:
        async with session.get(EXTERNAL_JWT_API, params={"uid": uid, "password": password}, timeout=10) as r:
            if r.status == 200:
                try:
                    d = await r.json()
                    tok = d.get("token") or d.get("jwt")
                    if tok and len(tok) > 50 and tok.count(".") >= 2:
                        return tok
                except Exception:
                    text = await r.text()
                    s = text.find("eyJ")
                    if s != -1:
                        e = s
                        while e < len(text) and text[e] not in '" \n\r\t\x00':
                            e += 1
                        tok = text[s:e]
                        if tok.count(".") >= 2:
                            return tok
    except Exception:
        pass
    return None


async def get_token(uid, password, session, retries=2):
    t1 = asyncio.create_task(_token_external(uid, password, session))
    t2 = asyncio.create_task(_token_internal(uid, password, session, retries))
    try:
        for fut in asyncio.as_completed([t1, t2]):
            try:
                tok = await fut
            except Exception:
                tok = None
            if tok:
                for x in (t1, t2):
                    if not x.done():
                        x.cancel()
                return tok
    finally:
        for x in (t1, t2):
            if not x.done():
                x.cancel()
    return None


async def send_spin(session, url, jwt, payload_hex):
    headers = {
        "Authorization": f"Bearer {jwt}",
        "X-GA": "v1 1",
        "ReleaseVersion": RELEASE_VERSION,
        "Content-Type": "application/octet-stream",
        "User-Agent": "UnityPlayer/2022.3.47f1",
    }
    try:
        async with session.post(url, headers=headers, data=bytes.fromhex(payload_hex), timeout=15, ssl=False) as r:
            return r.status, await r.read()
    except Exception as e:
        return 0, str(e).encode()


def find_item_id(data):
    if isinstance(data, dict):
        if (1 in data or "1" in data):
            sub = data.get(1) or data.get("1")
            if isinstance(sub, dict):
                if 2 in sub: return sub[2]
                if "2" in sub: return sub["2"]
        for v in data.values():
            r = find_item_id(v)
            if r is not None: return r
    elif isinstance(data, list):
        for i in data:
            r = find_item_id(i)
            if r is not None: return r
    return None


# ==================== HANDLERS ====================
async def cmd_start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    get_or_create_stats(uid)
    user = update.effective_user

    text = (
        f"{t(uid, 'welcome_title', name=user.first_name)}\n\n"
        f"{t(uid, 'welcome_sub')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(uid, 'welcome_tag')}\n\n"
        f"{t(uid, 'how_to')}\n"
        f"{t(uid, 'step1')}\n"
        f"{t(uid, 'step2')}\n"
        f"{t(uid, 'step3')}\n"
        f"{t(uid, 'step4')}\n"
        f"{t(uid, 'step5')}\n\n"
        f"{t(uid, 'use_buttons')}"
    )
    await update.message.reply_text(
        text,
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(uid)
    )


async def msg_new_spin(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_tasks:
        await update.message.reply_text(t(uid, "already_run"),
                                        reply_markup=main_menu_keyboard(uid))
        return

    kb = [
        [InlineKeyboardButton("🇧🇩 Bangladesh", callback_data="srv|bd"),
         InlineKeyboardButton("🇮🇳 India", callback_data="srv|ind")],
        [InlineKeyboardButton(t(uid, "cancel"), callback_data="cancel")],
    ]
    await update.message.reply_text(
        t(uid, "select_server"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def msg_my_stats(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    st = get_or_create_stats(uid)
    text = (
        f"{t(uid, 'stats_title')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(uid, 'total_spins')} `{st['total_spins']}`\n"
        f"{t(uid, 'ultra_rare')} `{st['ultra']}`\n"
        f"{t(uid, 'rare_items')} `{st['rare']}`\n"
        f"{t(uid, 'joined')} `{st['joined']}`\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"{t(uid, 'keep_spin')}"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=main_menu_keyboard(uid))


async def msg_profile(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    u = update.effective_user
    uid = u.id
    st = get_or_create_stats(uid)
    lang_display = "🇧🇩 বাংলা" if get_lang(uid) == "bn" else "🇬🇧 English"

    text = (
        f"{t(uid, 'profile_title')}\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"{t(uid, 'user_id')} `{u.id}`\n"
        f"{t(uid, 'name')} {u.first_name}\n"
        f"{t(uid, 'username')} @{u.username if u.username else t(uid, 'not_found')}\n"
        f"{t(uid, 'language')} {lang_display}\n\n"
        "━━━━━━━━━━━━━━━━━━━━━━━\n"
        f"🎰 {t(uid, 'total_spins')} `{st['total_spins']}`\n"
        f"👑 {t(uid, 'ultra_rare')} `{st['ultra']}`"
    )
    await update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN,
                                    reply_markup=main_menu_keyboard(uid))


async def msg_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    kb = [
        [InlineKeyboardButton("🇧🇩 বাংলা",    callback_data="lang|bn")],
        [InlineKeyboardButton("🇬🇧 English",  callback_data="lang|en")],
    ]
    await update.message.reply_text(
        t(uid, "lang_select"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(kb)
    )


async def msg_cancel(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    if uid in user_tasks:
        user_tasks[uid].cancel()
        user_tasks.pop(uid, None)
        user_sessions.pop(uid, None)
        await update.message.reply_text(
            t(uid, "cancel_done"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(uid)
        )
    else:
        await update.message.reply_text(t(uid, "nothing_run"),
                                        reply_markup=main_menu_keyboard(uid))


async def handle_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    data = q.data

    if data.startswith("lang|"):
        lang = data.split("|")[1]
        user_lang[uid] = lang
        await q.message.reply_text(
            t(uid, "lang_changed"),
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=main_menu_keyboard(uid)
        )
        await q.message.delete()
        return

    if data == "cancel":
        user_sessions.pop(uid, None)
        await q.edit_message_text(t(uid, "cancelled"))
        return

    if data.startswith("srv|"):
        srv = data.split("|")[1]
        user_sessions[uid] = {"server": srv}
        kb = [
            [InlineKeyboardButton(t(uid, "conc_safe"), callback_data="cc|10")],
            [InlineKeyboardButton(t(uid, "conc_bal"),  callback_data="cc|20")],
            [InlineKeyboardButton(t(uid, "conc_fast"), callback_data="cc|30")],
            [InlineKeyboardButton(t(uid, "conc_max"),  callback_data="cc|50")],
            [InlineKeyboardButton(t(uid, "back"), callback_data="back")],
        ]
        await q.edit_message_text(
            f"{t(uid, 'server', srv=SERVERS[srv]['name'])}\n\n{t(uid, 'select_conc')}",
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data == "back":
        kb = [
            [InlineKeyboardButton("🇧🇩 Bangladesh", callback_data="srv|bd"),
             InlineKeyboardButton("🇮🇳 India", callback_data="srv|ind")],
            [InlineKeyboardButton(t(uid, "cancel"), callback_data="cancel")],
        ]
        await q.edit_message_text(
            t(uid, "select_server"),
            reply_markup=InlineKeyboardMarkup(kb),
            parse_mode=ParseMode.MARKDOWN
        )

    elif data.startswith("cc|"):
        cc = int(data.split("|")[1])
        if uid not in user_sessions:
            await q.edit_message_text("❌ Session expired.")
            return
        if uid in user_tasks:
            await q.edit_message_text(t(uid, "already_run"))
            return

        user_sessions[uid]["concurrency"] = cc
        s = user_sessions[uid]
        await q.edit_message_text(
            t(uid, "ready", srv=SERVERS[s['server']]['name'], cc=cc),
            parse_mode=ParseMode.MARKDOWN
        )


async def handle_document(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    doc = update.message.document

    if uid not in user_sessions or "server" not in user_sessions[uid]:
        await update.message.reply_text(t(uid, "select_first"),
                                        parse_mode=ParseMode.MARKDOWN,
                                        reply_markup=main_menu_keyboard(uid))
        return

    if uid in user_tasks:
        await update.message.reply_text(t(uid, "already_run"))
        return

    if not doc.file_name.lower().endswith((".json", ".txt")):
        await update.message.reply_text(t(uid, "only_json"))
        return

    await update.message.reply_text(t(uid, "downloading"))

    try:
        tg_file = await doc.get_file()
        tmpdir = tempfile.mkdtemp(prefix=f"ffspin_{uid}_")
        fpath = os.path.join(tmpdir, doc.file_name)
        await tg_file.download_to_drive(fpath)
    except Exception as e:
        await update.message.reply_text(t(uid, "dl_fail", e=e))
        return

    accounts = load_accounts(fpath)
    if not accounts:
        shutil.rmtree(tmpdir, ignore_errors=True)
        await update.message.reply_text(t(uid, "no_valid"))
        return

    s = user_sessions[uid]
    s["accounts"] = accounts
    s["tmpdir"] = tmpdir

    await update.message.reply_text(
        t(uid, "loaded", n=len(accounts)),
        parse_mode=ParseMode.MARKDOWN
    )

    task = asyncio.create_task(run_spinner_task(update, uid))
    user_tasks[uid] = task


async def run_spinner_task(update, uid):
    s = user_sessions[uid]
    accounts = s["accounts"]
    server = SERVERS[s["server"]]
    concurrency = s.get("concurrency", 20)
    tmpdir = s["tmpdir"]

    purchase_url = f"{server['url']}/PurchaseGacha"
    total = len(accounts)

    stats = {"done": 0, "items": 0, "rare": 0, "ultra": 0, "failed": 0}
    all_items, ultra_list, other_list, summary = [], [], [], []

    sem = asyncio.Semaphore(concurrency)
    connector = aiohttp.TCPConnector(limit=concurrency * 2, ttl_dns_cache=300, ssl=False)
    timeout = aiohttp.ClientTimeout(total=None, sock_connect=10, sock_read=25)

    progress_msg = await update.message.reply_text(
        f"{t(uid, 'spinning')}\n"
        f"{t(uid, 'processed', done=0, total=total, pct=0)}\n"
        f"▱▱▱▱▱▱▱▱▱▱ 0%",
        parse_mode=ParseMode.MARKDOWN
    )

    async def process_one(acc, http):
        async with sem:
            uid_str = str(acc.get("uid", "?"))
            pwd = acc.get("password", "?")
            try:
                token = await get_token(uid_str, pwd, http, retries=2)
                if not token:
                    stats["failed"] += 1; return

                st, resp = await send_spin(http, purchase_url, token, DEFAULT_SPIN_HEX)
                if st != 200:
                    stats["failed"] += 1; return

                decoded, _ = blackboxprotobuf.decode_message(resp)
                item_id = find_item_id(decoded)
                if item_id is None:
                    stats["failed"] += 1; return

                name = RARE_ITEMS_DB.get(item_id, f"Unknown ({item_id})")
                entry = {"uid": uid_str, "pass": pwd, "item_id": item_id,
                         "item_name": name, "time": now_str()}
                all_items.append(entry)
                stats["items"] += 1

                if item_id in ULTRA_RARE_IDS:
                    stats["ultra"] += 1; stats["rare"] += 1
                    ultra_list.append(entry)
                    summary.append(f"[ULTRA RARE] UID: {uid_str} | Pass: {pwd} | {name}")
                elif item_id in RARE_ITEMS_DB:
                    stats["rare"] += 1
                    other_list.append(entry)
                    summary.append(f"[RARE] UID: {uid_str} | Pass: {pwd} | {name}")
                else:
                    other_list.append(entry)
            except asyncio.CancelledError:
                raise
            except Exception:
                stats["failed"] += 1
            finally:
                stats["done"] += 1

    async def reporter():
        try:
            while stats["done"] < total:
                await asyncio.sleep(5)
                if stats["done"] >= total: break
                pct = int(stats["done"] * 100 / total)
                bar = "▰" * (pct // 5) + "▱" * (20 - pct // 5)
                try:
                    await progress_msg.edit_text(
                        f"{t(uid, 'spinning')}\n"
                        f"{t(uid, 'processed', done=stats['done'], total=total, pct=pct)}\n"
                        f"`{bar}`\n\n"
                        f"{t(uid, 'ultra')}: *{stats['ultra']}*  |  {t(uid, 'rare')}: *{stats['rare']}*\n"
                        f"{t(uid, 'items')}: *{stats['items']}*  |  {t(uid, 'failed')}: *{stats['failed']}*",
                        parse_mode=ParseMode.MARKDOWN
                    )
                except Exception:
                    pass
        except asyncio.CancelledError:
            return

    rep_task = asyncio.create_task(reporter())

    try:
        async with aiohttp.ClientSession(connector=connector, timeout=timeout) as http:
            await asyncio.gather(*[process_one(a, http) for a in accounts])
    except asyncio.CancelledError:
        rep_task.cancel()
        raise
    finally:
        rep_task.cancel()

    st = get_or_create_stats(uid)
    st["total_spins"] += stats["items"]
    st["ultra"] += stats["ultra"]
    st["rare"] += stats["rare"]

    outdir = os.path.join(tmpdir, "results")
    os.makedirs(outdir, exist_ok=True)
    with open(os.path.join(outdir, "all_items.json"), "w", encoding="utf-8") as f:
        json.dump(all_items, f, indent=2, ensure_ascii=False)
    with open(os.path.join(outdir, "ultra_rare.json"), "w", encoding="utf-8") as f:
        json.dump(ultra_list, f, indent=2, ensure_ascii=False)
    with open(os.path.join(outdir, "other_items.json"), "w", encoding="utf-8") as f:
        json.dump(other_list, f, indent=2, ensure_ascii=False)
    with open(os.path.join(outdir, "summary.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(summary) if summary else "No rare items found.")

    try:
        await progress_msg.edit_text(
            f"{t(uid, 'done')}\n"
            "━━━━━━━━━━━━━━━\n\n"
            f"🌐 {t(uid, 'server', srv=server['name']).replace('*', '')}\n"
            f"{t(uid, 'accounts', n=total)}\n\n"
            f"👑 {t(uid, 'ultra')}: `{stats['ultra']}`\n"
            f"🎁 {t(uid, 'rare')}: `{stats['rare']}`\n"
            f"📦 {t(uid, 'items')}: `{stats['items']}`\n"
            f"❌ {t(uid, 'failed')}: `{stats['failed']}`\n\n"
            "━━━━━━━━━━━━━━━\n"
            f"{t(uid, 'sending_files')}",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception:
        pass

    for fname, cap in [
        ("ultra_rare.json",  "👑 Ultra Rare Items"),
        ("all_items.json",   "📄 All Items"),
        ("other_items.json", "📦 Other Items"),
        ("summary.txt",      "📝 Summary"),
    ]:
        fp = os.path.join(outdir, fname)
        if os.path.exists(fp) and os.path.getsize(fp) > 2:
            try:
                with open(fp, "rb") as f:
                    await update.message.reply_document(
                        document=InputFile(f, filename=fname),
                        caption=cap
                    )
            except Exception:
                pass

    await update.message.reply_text(
        t(uid, "back_menu"),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=main_menu_keyboard(uid)
    )

    user_tasks.pop(uid, None)
    user_sessions.pop(uid, None)
    shutil.rmtree(tmpdir, ignore_errors=True)


# ==================== MAIN ====================
def main():
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("[!] BOT_TOKEN set koro age.")
        return

    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", cmd_start))
    app.add_handler(CommandHandler("cancel", msg_cancel))

    spin_labels = ["🚀 New Spin", "🚀 নতুন স্পিন"]
    stats_labels = ["📊 My Stats", "📊 আমার স্ট্যাটস"]
    prof_labels = ["👤 Profile", "👤 প্রোফাইল"]
    lang_labels = ["🌐 Language", "🌐 ভাষা"]
    cancel_labels = ["🛑 Cancel", "🛑 বাতিল"]

    app.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(spin_labels)})$"), msg_new_spin))
    app.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(stats_labels)})$"), msg_my_stats))
    app.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(prof_labels)})$"), msg_profile))
    app.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(lang_labels)})$"), msg_lang))
    app.add_handler(MessageHandler(filters.Regex(f"^({'|'.join(cancel_labels)})$"), msg_cancel))

    app.add_handler(CallbackQueryHandler(handle_callback))
    app.add_handler(MessageHandler(filters.Document.ALL, handle_document))

    print("🤖 Premium Bilingual Spinner Bot is running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
