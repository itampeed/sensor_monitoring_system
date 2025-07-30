import asyncio
import websockets
import json
import struct
import binascii
import random

# Configuration
SERVER_URI = "ws://localhost:8765"
TOKEN = "mP@9z!rV6q#fY2bL$uX8sK%J3tW0gE"
CHANNEL_IDS = ["channel_1", "channel_2", "channel_3"]
CLIENT_IDS = ["client_1", "client_2", "client_3"]
FORMAT = "float"

def encode_floats_to_hex(float_list):
    binary = b''.join([struct.pack('<f', val) for val in float_list])
    return binascii.hexlify(binary).decode()

def generate_random_floats(n=10):
    return [round(random.uniform(0.0, 1.0), 3) for _ in range(n)]

async def send_client_data(client_id, channel_id, iteration):
    async with websockets.connect(SERVER_URI) as websocket:
        float_data = generate_random_floats()
        hex_payload = encode_floats_to_hex(float_data)

        message = {
            "action": "data",
            "token": TOKEN,
            "client_id": client_id,
            "channel_id": channel_id,
            "payload": hex_payload,
            "format": FORMAT
        }

        await websocket.send(json.dumps(message))
        print(f"[{client_id}] Iteration {iteration}/50 Sent: {float_data}")

        response = await websocket.recv()
        print(f"[{client_id}] Received: {response}")

async def client_loop(client_id, channel_id):
    for i in range(50):  # Send 50 times
        await send_client_data(client_id, channel_id, i+1)
        await asyncio.sleep(0.2)  # 0.2 second delay between sends

async def main_loop():
    # Create tasks for all clients to run concurrently
    tasks = []
    for i in range(3):
        client_id = CLIENT_IDS[i]
        channel_id = CHANNEL_IDS[i]
        tasks.append(client_loop(client_id, channel_id))
    
    # Run all client tasks concurrently
    await asyncio.gather(*tasks)

if __name__ == "__main__":
    asyncio.run(main_loop())
