# Minimal health server that runs your bot and serves /health
# Adjust `start_bot()` to call whatever starts your existing bot or main loop.

import os
import threading
import time
from flask import Flask, jsonify

app = Flask(__name__)

# ---- Replace this with how your bot is started ----
def start_bot():
    # Example: if your bot is started by running bot.py: import bot and call main/start
    try:
        import bot  # adjust if your bot filename or API differs
        # If bot has a start() or main() function that blocks, run it here.
        if hasattr(bot, "main"):
            bot.main()
        elif hasattr(bot, "start"):
            bot.start()
        else:
            # If bot.py just runs when imported, importing above may be enough.
            pass
    except Exception as e:
        # Log the error so it appears in container logs
        print("Failed to start bot:", e)
# --------------------------------------------------

@app.route("/health", methods=["GET"])
def health():
    # A simple health response. You can expand to check internal components.
    return jsonify({"status": "ok"}), 200

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    # Bind to 0.0.0.0 so Railway can reach it
    app.run(host="0.0.0.0", port=port)

if __name__ == "__main__":
    # Start the bot in a background thread so the Flask server can run in foreground
    bot_thread = threading.Thread(target=start_bot, daemon=True)
    bot_thread.start()

    # Optional: Wait briefly to let the bot initialize before accepting health checks
    time.sleep(1)

    # Start the HTTP server (this is the foreground process)
    run_flask()