from flask import Flask, request
import pymongo
import os
from datetime import datetime
from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv()
app = Flask(__name__)
CORS(app)

client = pymongo.MongoClient(os.getenv("MONGO_URI"))
db = client["webhookDB"]
collection = db["events"]

@app.route("/test-mongo")
def test_mongo():
    try:
        db.command("ping")  # quick ping test
        collection.insert_one({"type": "test", "message": "Mongo is connected!"})
        return {"status": "success", "message": "Connected and inserted test document."}, 200
    except Exception as e:
        return {"status": "error", "message": str(e)}, 500


@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    event = request.headers.get('X-GitHub-Event')
    formatted = format_event(data, event)
    if formatted:
        collection.insert_one(formatted)
    return '', 200

@app.route("/events", methods=["GET"])
def get_events():
    logs = list(collection.find({}, {"_id": 0}))
    return logs

def format_event(data, event):
    timestamp = datetime.utcnow().strftime('%d %B %Y - %I:%M %p UTC')
    author = data.get("sender", {}).get("login", "unknown")

    if event == "push":
        branch = data["ref"].split("/")[-1]
        return {
            "type": "push",
            "message": f'{author} pushed to "{branch}" on {timestamp}'
        }

    elif event == "pull_request":
        action = data["action"]
        if action == "opened":
            from_branch = data["pull_request"]["head"]["ref"]
            to_branch = data["pull_request"]["base"]["ref"]
            return {
                "type": "pull_request",
                "message": f'{author} submitted a pull request from "{from_branch}" to "{to_branch}" on {timestamp}'
            }
        elif action == "closed" and data["pull_request"]["merged"]:
            from_branch = data["pull_request"]["head"]["ref"]
            to_branch = data["pull_request"]["base"]["ref"]
            return {
                "type": "merge",
                "message": f'{author} merged branch "{from_branch}" to "{to_branch}" on {timestamp}'
            }
    return None



if __name__ == "__main__":
    app.run(debug=True, port=5000)
