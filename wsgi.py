from flask import Flask, request
from main import app

flask_app = Flask(__name__)
handler = SlackRequestHandler(app)

@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    return handler.handle(request)


# Start your app
if __name__ == "__main__":
    app.start(port=int(os.environ.get("PORT", 3000)))