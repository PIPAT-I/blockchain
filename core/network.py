import requests
import json

def broadcast_to_peers(peers: set, endpoint: str, data: dict):
    """
    Sends a POST request with JSON data to a specific endpoint on all peers.

    :param peers: A set of peer addresses (e.g., {'http://localhost:5001'}).
    :param endpoint: The endpoint to hit (e.g., '/announce-winner').
    :param data: The dictionary to send as JSON.
    """
    for peer_address in peers:
        try:
            url = f"{peer_address}{endpoint}"
            requests.post(url, json=data, timeout=3)
            print(f"Successfully sent data to {url}")
        except requests.exceptions.RequestException as e:
            print(f"Could not connect to peer {peer_address}. Error: {e}")

