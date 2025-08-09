# Impor library yang diperlukan
import os
import logging
from serpapi import GoogleSearch
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- KONFIGURASI AMAN ---
# Mengambil token dan key dari Environment Variables yang akan kita atur di Render
# Jangan tulis token/key Anda di sini!
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
SERPAPI_API_KEY = os.environ.get("SERPAPI_API_KEY")

# Mengatur logging untuk melihat error (opsional tapi sangat membantu)
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)


# --- FUNGSI PENCARIAN SERPAPI ---
def jalankan_pencarian_serpapi(kata_kunci: str) -> str:
    """Menjalankan pencarian menggunakan SerpApi dan mengembalikan hasil dalam bentuk string."""
    params = {
        "engine": "google",
        "q": kata_kunci,
        "location": "Indonesia",
        "google_domain": "google.co.id",
        "gl": "id",
        "hl": "id",
        "api_key": SERPAPI_API_KEY # Menggunakan key dari environment variable
    }
    
    try:
        search = GoogleSearch(params)
        results_dict = search.get_dict()

        if "error" in results_dict:
            return f"Maaf, terjadi kesalahan dari SerpApi: {results_dict['error']}"

        if "organic_results" in results_dict:
            hasil_terformat = f"🔍 *Hasil Pencarian untuk: {kata_kunci}*\n\n"
            for result in results_dict["organic_results"][:5]:
                judul = result.get("title", "N/A")
                link = result.get("link", "N/A")
                snippet = result.get("snippet", "N/A")
                hasil_terformat += f"{link}\n"
                hasil_terformat += f"*{judul}*\n"
                hasil_terformat += f"_{snippet}_\n\n"
            return hasil_terformat

        return "Maaf, tidak ada hasil yang ditemukan."

    except Exception as e:
        logger.error(f"Error saat menghubungi SerpApi: {e}")
        return "Terjadi kesalahan internal saat mencoba mencari. Coba lagi nanti."


# --- FUNGSI-FUNGSI UNTUK BOT TELEGRAM ---
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Mengirim pesan sambutan saat command /start dipanggil."""
    user = update.effective_user
    await update.message.reply_html(
        f"Halo {user.mention_html()}!\n\nSaya adalah bot pencari. Kirim saya pesan dengan format:\n`/cari [kata kunci]`"
    )

async def cari_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menjalankan pencarian saat command /cari dipanggil."""
    kata_kunci = " ".join(context.args)
    if not kata_kunci:
        await update.message.reply_text("Tolong berikan kata kunci setelah `/cari`. Contoh: `/cari resep nasi goreng`")
        return

    await update.message.reply_text(f"Oke, sedang mencari informasi tentang '{kata_kunci}'...")
    hasil = jalankan_pencarian_serpapi(kata_kunci)
    await update.message.reply_text(hasil, parse_mode='Markdown', disable_web_page_preview=True)


# --- FUNGSI UTAMA UNTUK MENJALANKAN BOT ---
def main():
    """Fungsi utama untuk menjalankan bot."""
    # Pemeriksaan awal apakah token ada
    if not TELEGRAM_BOT_TOKEN:
        logger.error("Error: TELEGRAM_BOT_TOKEN tidak ditemukan! Atur di Environment Variables.")
        return

    print("Bot sedang berjalan...")
    application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("cari", cari_command))
    application.run_polling()

if __name__ == "__main__":
    main()
