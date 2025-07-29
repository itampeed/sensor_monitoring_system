import json
import websockets
import asyncio

from app.auth.jwt_handler import verify_jwt, extract_client_id, create_jwt
from app.db.db_handler import insert_sample_data, create_user, authenticate_user, generate_reset_token
from app.utils.logger import log

connected_clients = set()

async def handle_client(websocket, path):
    client_id = None
    try:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                action = data.get("action")

                if action == "signup":
                    username = data.get("username")
                    password = data.get("password")
                    email = data.get("email")
                    try:
                        success, msg = create_user(username, password, email)
                        await websocket.send(json.dumps({"action": "signup", "success": success, "message": msg}))
                    except Exception as e:
                        log(f"[WS] Signup error: {e}", level="ERROR")
                        await websocket.send(json.dumps({"action": "signup", "success": False, "message": str(e)}))
                elif action == "login":
                    username = data.get("username")
                    password = data.get("password")
                    try:
                        user_id = authenticate_user(username, password)
                        if user_id:
                            token = create_jwt(user_id)
                            await websocket.send(json.dumps({"action": "login", "success": True, "token": token}))
                        else:
                            await websocket.send(json.dumps({"action": "login", "success": False, "message": "Invalid credentials"}))
                    except Exception as e:
                        log(f"[WS] Login error: {e}", level="ERROR")
                        await websocket.send(json.dumps({"action": "login", "success": False, "message": str(e)}))
                elif action == "forgot_password":
                    username = data.get("username")
                    try:
                        token = generate_reset_token(username)
                        if token:
                            await websocket.send(json.dumps({"action": "forgot_password", "success": True, "reset_token": token}))
                        else:
                            await websocket.send(json.dumps({"action": "forgot_password", "success": False, "message": "User not found"}))
                    except Exception as e:
                        log(f"[WS] Forgot password error: {e}", level="ERROR")
                        await websocket.send(json.dumps({"action": "forgot_password", "success": False, "message": str(e)}))
                elif action == "data":
                    token = data.get("token")
                    if not verify_jwt(token):
                        await websocket.send(json.dumps({"error": "unauthorized"}))
                        log("Unauthorized connection attempt", level="ERROR")
                        continue
                    client_id = extract_client_id(token)
                    connected_clients.add(websocket)
                    channel_id = data.get("channel_id", "default")
                    payload = data.get("payload")
                    data_format = data.get("format", "float")
                    if not payload:
                        await websocket.send(json.dumps({"error": "No payload provided"}))
                        continue
                    try:
                        from app.processing.decoder import decode_signal
                        from app.processing.feature_extractor import extract_features
                        from app.ml.model import classify_sample
                        decoded_signal = decode_signal(payload, data_format)
                        features = extract_features(decoded_signal)
                        classification = classify_sample(features)
                        filtered_signal = decoded_signal  # TODO: Replace with actual filter
                        await insert_sample_data(client_id, channel_id, decoded_signal, filtered_signal, features, classification)
                        await websocket.send(json.dumps({
                            "status": "success",
                            "classification": classification
                        }))
                        log(f"[{client_id}] → Class {classification}")
                    except Exception as e:
                        log(f"[WS] Data submission error: {e}", level="ERROR")
                        await websocket.send(json.dumps({"error": "data_submission_failed", "message": str(e)}))
                else:
                    await websocket.send(json.dumps({"error": "Unknown action"}))
            except websockets.exceptions.ConnectionClosed:
                log(f"[Disconnected] Client '{client_id}'")
                break
            except Exception as e:
                log(f"[WS] Unexpected error: {e}", level="ERROR")
                await websocket.send(json.dumps({"error": "server_error", "message": str(e)}))
    except Exception as e:
        log(f"Connection error: {e}", level="ERROR")
    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def start_server():
    log("Starting WebSocket server on ws://0.0.0.0:8765")
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await asyncio.Future()  # run forever
