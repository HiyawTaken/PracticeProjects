from flask import Flask, request, jsonify
import json
from pathlib import Path
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

contacts_path = Path("contacts.json")
contacts_path.touch(exist_ok=True)

def load_contacts():
    try:
        with contacts_path.open("r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def save_contacts(contacts):
    with contacts_path.open(mode="w") as f:
        json.dump(contacts, f, indent=4)


@app.route('/contacts', methods=['POST'])
def new_contact():

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    contacts = load_contacts()
    contact = request.get_json()

    if contact is None:
        return jsonify({"error": "empty json"}), 400

    if 'name' in contact and 'phone' in contact:
        name = contact["name"]
        phone_number = contact["phone"]

        if phone_number == "" or name == "":
            return jsonify({"error": "Missing required field(name or phone)"}), 400

        # id generation method
        ids = []
        for c in contacts:
            ids.append(c["id"])
        if ids is not None and len(ids) > 0:
            id = max(ids) + 1
        else:
            id = 1

        new_contact = {"id": id, "name": name, "phone": phone_number}

        contacts.append(new_contact)
        save_contacts(contacts)

        return jsonify(new_contact), 201
    else:
        return jsonify({"error": "Missing required field(name or phone)"}), 400

@app.route('/contacts', methods=['GET'])
def read_all():
    contacts = load_contacts()
    print(contacts)
    return jsonify(contacts), 200

@app.route('/contacts/<int:contact_id>', methods=['GET'])
def read_one(contact_id):
    contacts = load_contacts()

    for c in contacts:
        if c["id"] == contact_id:
            return jsonify(c), 200

    return jsonify({"error": "Contact not found"}), 404

@app.route('/contacts/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):

    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 400

    contacts = load_contacts()
    data = request.get_json(silent=True)

    if data is None:
        return jsonify({"error": "Invalid or missing JSON body"}), 400

    allowed = {"name", "phone"}
    unknown = set(data.keys()) - allowed
    if unknown:
        return jsonify({"error": "Unknown fields not allowed"}), 400

    for c in contacts:
        if c["id"] == contact_id:
            for field in allowed:
                if field in data:
                    c[field] = data[field]

            save_contacts(contacts)
            return jsonify(c), 200

    return jsonify({"error": "Contact not found"}), 404


@app.route('/contacts/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    contacts = load_contacts()

    for c in contacts:
        if c["id"] == contact_id:
            contacts.remove(c)
            save_contacts(contacts)
            return jsonify({"success": True}), 200

    return jsonify({"error": "Contact not found"}), 404

if __name__ == "__main__":
    app.run(debug=True)
