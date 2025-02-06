# cms_backend.py
from flask import Flask, request, jsonify
from pymongo import MongoClient
from bson import ObjectId
from flask_cors import CORS  # Import CORS

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes (for development)

# MongoDB Configuration
MONGO_URI = "mongodb://localhost:27017/"  # Replace with your MongoDB connection string
DB_NAME = "cms_db"
COLLECTION_NAME = "content"

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db[COLLECTION_NAME]


# Helper function to convert ObjectId to string for JSON serialization
def serialize_doc(doc):
    if "_id" in doc:
        doc["_id"] = str(doc["_id"])
    return doc


# API Endpoints
@app.route("/api/paragraphs", methods=["GET", "POST"])
def paragraphs():
    if request.method == "GET":
        paragraphs = []
        for doc in collection.find({"type": "paragraph"}):
            paragraphs.append(serialize_doc(doc))
        return jsonify(paragraphs)
    elif request.method == "POST":
        data = request.get_json()
        if not data or "content" not in data:
            return jsonify({"error": "Missing 'content' field"}), 400
        new_paragraph = {"type": "paragraph", "content": data["content"]}
        result = collection.insert_one(new_paragraph)
        return jsonify(
            {"_id": str(result.inserted_id), "message": "Paragraph created"}
        ), 201


@app.route("/api/textareas", methods=["GET", "POST"])
def textareas():
    if request.method == "GET":
        textareas = []
        for doc in collection.find({"type": "textarea"}):
            textareas.append(serialize_doc(doc))
        return jsonify(textareas)
    elif request.method == "POST":
        data = request.get_json()
        if not data or "content" not in data:
            return jsonify({"error": "Missing 'content' field"}), 400
        new_textarea = {"type": "textarea", "content": data["content"]}
        result = collection.insert_one(new_textarea)
        return jsonify(
            {"_id": str(result.inserted_id), "message": "Textarea created"}
        ), 201


@app.route("/api/headings", methods=["GET", "POST"])
def headings():
    if request.method == "GET":
        headings = []
        for doc in collection.find({"type": "heading"}):
            headings.append(serialize_doc(doc))
        return jsonify(headings)
    elif request.method == "POST":
        data = request.get_json()
        if not data or "content" not in data or "level" not in data:
            return jsonify(
                {"error": "Missing 'content' or 'level' field"}
            ), 400  # Add level validation
        new_heading = {
            "type": "heading",
            "content": data["content"],
            "level": data["level"],
        }
        result = collection.insert_one(new_heading)
        return jsonify(
            {"_id": str(result.inserted_id), "message": "Heading created"}
        ), 201


@app.route("/api/lists", methods=["GET", "POST"])
def lists():
    if request.method == "GET":
        lists = []
        for doc in collection.find({"type": "list"}):
            lists.append(serialize_doc(doc))
        return jsonify(lists)
    elif request.method == "POST":
        data = request.get_json()
        if not data or "items" not in data:
            return jsonify({"error": "Missing 'items' field"}), 400
        new_list = {"type": "list", "items": data["items"]}  # items should be a list
        result = collection.insert_one(new_list)
        return jsonify(
            {"_id": str(result.inserted_id), "message": "List created"}
        ), 201


@app.route("/api/images", methods=["GET", "POST"])
def images():
    if request.method == "GET":
        images = []
        for doc in collection.find({"type": "image"}):
            images.append(serialize_doc(doc))
        return jsonify(images)
    elif request.method == "POST":
        data = request.get_json()
        if not data or "url" not in data or "alt" not in data:
            return jsonify({"error": "Missing 'url' or 'alt' field"}), 400
        new_image = {"type": "image", "url": data["url"], "alt": data["alt"]}
        result = collection.insert_one(new_image)
        return jsonify(
            {"_id": str(result.inserted_id), "message": "Image created"}
        ), 201


@app.route("/api/content/<content_id>", methods=["GET", "PUT", "DELETE"])
def content_item(content_id):
    try:
        object_id = ObjectId(content_id)
    except:
        return jsonify({"error": "Invalid content ID"}), 400

    if request.method == "GET":
        item = collection.find_one({"_id": object_id})
        if item:
            return jsonify(serialize_doc(item))
        else:
            return jsonify({"message": "Content not found"}), 404
    elif request.method == "PUT":
        data = request.get_json()
        if not data:
            return jsonify({"error": "Missing request body"}), 400

        result = collection.update_one({"_id": object_id}, {"$set": data})
        if result.modified_count > 0:
            return jsonify({"message": "Content updated"})
        else:
            return jsonify({"message": "Content not found"}), 404
    elif request.method == "DELETE":
        result = collection.delete_one({"_id": object_id})
        if result.deleted_count > 0:
            return jsonify({"message": "Content deleted"})
        else:
            return jsonify({"message": "Content not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
