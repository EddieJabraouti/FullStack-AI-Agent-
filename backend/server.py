import os
from livekit import api
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from flask_cors import CORS
from livekit.api import LiveKitAPI, ListRoomsRequest
import uuid
import asyncio

load_dotenv()  # Load environment variables from .env file
app = Flask(__name__)  # Create a Flask application instance
CORS(app, resources={r"/*": {"origins": "*"}})  # Enable Cross-Origin Resource Sharing (CORS) for the app

async def generate_room_name():
    name = "room-" + str(uuid.uuid4())[:8]  # Generate a unique room name using UUID
    try:
        rooms = await get_rooms()
        while name in rooms:
            name = "room-" + str(uuid.uuid4())[:8]
    except Exception as e:
        print(f"Error getting rooms: {e}")
        # If we can't get rooms, just use the generated name
    return name

async def get_rooms():
    lk_api = LiveKitAPI()
    try:
        rooms = await lk_api.room.list_rooms(ListRoomsRequest())
        return [room.name for room in rooms.rooms]  # Return a list of room names from the API response
    finally:
        await lk_api.aclose()  # Use aclose() for async

@app.route("/getToken", methods=['GET'])
async def get_token():
    try:
        print(f"Received request: {request.args}")  # Debug logging
        
        name = request.args.get("name", "my name")  # Get the participant's name from the query parameters
        room = request.args.get("room", None)
        
        if not room:
            room = await generate_room_name()
        
        # Check if environment variables are set
        api_key = os.getenv("LIVEKIT_API_KEY")
        api_secret = os.getenv("LIVEKIT_API_SECRET")
        
        if not api_key or not api_secret:
            return jsonify({"error": "LiveKit API credentials not configured"}), 500
        
        print(f"Generating token for name: {name}, room: {room}")  # Debug logging
        
        token = api.AccessToken(api_key, api_secret)\
            .with_identity(name)\
            .with_name(name)\
            .with_grants(api.VideoGrants(
                room_join=True,
                room=room
            ))
        
        jwt_token = token.to_jwt()
        
        print(f"Generated JWT token: {jwt_token[:50]}...")  # Debug logging (partial token)
        
        # Return just the JWT token as plain text - this is what LiveKit expects
        return jwt_token, 200, {'Content-Type': 'text/plain'}
        
    except Exception as e:
        print(f"Error generating token: {e}")  # Debug logging
        return jsonify({"error": str(e)}), 500

@app.route("/", methods=['GET'])
def health_check():
    return jsonify({"status": "healthy", "service": "livekit-token-server"})

@app.route("/rooms", methods=['GET'])
async def list_rooms():
    try:
        rooms = await get_rooms()
        return jsonify({"rooms": rooms})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    print("Starting Flask server...")
    print(f"LIVEKIT_API_KEY set: {'Yes' if os.getenv('LIVEKIT_API_KEY') else 'No'}")
    print(f"LIVEKIT_API_SECRET set: {'Yes' if os.getenv('LIVEKIT_API_SECRET') else 'No'}")
    app.run(host="0.0.0.0", port=5001, debug=True)