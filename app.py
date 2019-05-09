from flask import Flask, jsonify, request, Response
from time import time
from collections import defaultdict
from typing import List

app = Flask(__name__)


class Message:
    def __init__(self, text: str, sender_id: str) -> None:
        self.text = text
        self.sender_id = sender_id
        self.created_at = time()
        self.id = hash(self.text + str(self.created_at) + self.sender_id)

    def __str__(self) -> str:
        return f"{self.sender_id}: {self.text} ({self.created_at})"

    def to_dict(self) -> dict:
        retval = dict()
        for key in ["text", "sender_id", "created_at", "id"]:
            retval[key] = self.__getattribute__(key)
        return retval


class Channel:
    def __init__(self, id: str, messages: List[Message] = []) -> None:
        self.messages = messages
        self.id = id

    def add_message(self, message: Message) -> bool:
        self.messages.append(message)
        return True

    def to_dict(self, ts: float = None) -> dict:
        retval = {"channel_id": self.id, "messages": self.get_messages(ts)}

        return retval

    def get_messages(self, ts: float = None) -> List[Message]:
        start_idx = 0
        if ts is not None:
            while ts > self.messages[start_idx].created_at:
                start_idx += 1

        return [msg.to_dict() for msg in self.messages[start_idx:]]


# texts = ["Hi", "Hello", "How are you?", "I'm great, thanks!"]
# senders = ["Bob", "Alice"] * (len(texts) // 2)
# messages = [Message(t, s) for t, s in zip(texts, senders)]

channels = dict()
# channels["foo"] = Channel("foo", messages)


@app.route("/get_messages/<channel_id>", methods=["GET"])
def get_messages(channel_id: str) -> Response:
    ts = request.args.get("ts")
    try:
        channel = channels[channel_id]
    except:
        return Response(response=f"channel_id: {channel_id} not found!", status=404)

    return jsonify(channel.to_dict(ts))


@app.route("/create_message/<channel_id>", methods=["POST"])
def create_message(channel_id: str) -> Response:
    # Get channel
    try:
        channel = channels[channel_id]
    except:
        channel = Channel(channel_id)
        channels[channel_id] = channel

    # Create message
    body = request.get_json()
    text, sender_id = body["message"], body["sender_id"]
    message = Message(text, sender_id)

    # Add message to correct channel
    channel.add_message(message)

    return jsonify({"response_text": "Success!!"})


@app.route("/")
def hello():
    return "Hello, World!"
