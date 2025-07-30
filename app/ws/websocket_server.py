import json
import websockets
import asyncio

from app.auth.jwt_handler import verify_jwt
from app.db.db_handler import insert_sample_data, get_channels_for_client
from app.utils.logger import log

connected_clients = set()

# ✅ Moving average filter for filtered_signal
def moving_average(signal, window_size=3):
    if len(signal) < window_size:
        return signal
    return [
        sum(signal[i:i+window_size]) / window_size
        for i in range(len(signal) - window_size + 1)
    ]

async def handle_client(websocket):
    client_id = None
    try:
        while True:
            try:
                message = await websocket.recv()
                data = json.loads(message)
                action = data.get("action")

                if action == "data":
                    token = data.get("token")
                    if not verify_jwt(token):
                        await websocket.send(json.dumps({"error": "unauthorized"}))
                        log("Unauthorized connection attempt", level="ERROR")
                        continue

                    client_id = data.get("client_id", "unknown")
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
                        features_dict = extract_features(decoded_signal)

                        features = [
                            features_dict["I-L1_SigStat-MW"],
                            features_dict["I-L1_StatSig-qMW"],
                            features_dict["I-L1_Stat-StdAW"],
                            features_dict["I-L1_Stat-Var"],
                            features_dict["I-L1_Stat-Wb"],
                            features_dict["I-L1_Stat-N6M"],
                            features_dict["I-L1_Sig-QWM"],
                            features_dict["I-L1_Sig-GRW"],
                            features_dict["I-L1_Sig-FF"]
                        ]

                        classification = classify_sample(features)

                        # ✅ Apply real filtering instead of copying raw
                        filtered_signal = moving_average(decoded_signal)

                        await insert_sample_data(
                            client_id,
                            channel_id,
                            decoded_signal,
                            filtered_signal,
                            features_dict,
                            classification
                        )

                        await websocket.send(json.dumps({
                            "status": "success",
                            "classification": int(classification)
                        }))
                        log(f"[{client_id}] → Class {classification}")

                    except Exception as e:
                        log(f"[WS] Data submission error: {e}", level="ERROR")
                        await websocket.send(json.dumps({
                            "error": "data_submission_failed",
                            "message": str(e)
                        }))

                elif action == "list_channels":
                    token = data.get("token")
                    if not verify_jwt(token):
                        await websocket.send(json.dumps({"error": "unauthorized"}))
                        log("Unauthorized channel list attempt", level="ERROR")
                        return

                    client_id = data.get("client_id")
                    if not client_id:
                        await websocket.send(json.dumps({"error": "No client_id provided"}))
                        return

                    try:
                        channels = get_channels_for_client(client_id)  # ✅ Synchronous function
                        await websocket.send(json.dumps({"channels": channels}))
                    except Exception as e:
                        log(f"[WS] Channel list error: {e}", level="ERROR")
                        await websocket.send(json.dumps({
                            "error": "channel_fetch_failed",
                            "message": str(e)
                        }))

                else:
                    await websocket.send(json.dumps({"error": "Unknown action"}))

            except websockets.exceptions.ConnectionClosed:
                log(f"[Disconnected] Client '{client_id}'")
                break

            except Exception as e:
                log(f"[WS] Unexpected error: {e}", level="ERROR")
                await websocket.send(json.dumps({
                    "error": "server_error",
                    "message": str(e)
                }))

    except Exception as e:
        log(f"Connection error: {e}", level="ERROR")

    finally:
        if websocket in connected_clients:
            connected_clients.remove(websocket)

async def start_server():
    log("Starting WebSocket server on ws://0.0.0.0:8765")
    async with websockets.serve(handle_client, "0.0.0.0", 8765):
        await asyncio.Future()  # Run forever