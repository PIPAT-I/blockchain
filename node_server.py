import json
import sys
import requests
import threading
import time
import random
from flask import Flask, request, jsonify
from core.blockchain import Blockchain
from core.block import Block
from core.hashing import generate_hash
from core.node import Node
from core.network import broadcast_to_peers

# --- Basic App Setup ---
app = Flask(__name__)
winner_lock = threading.Lock()
winner_found_for_current_search = False

# --- Blockchain Initialization & Node Setup ---
def seed_blockchain(blockchain: Blockchain):
    """Adds the initial art data to the blockchain."""
    print("Seeding the blockchain with initial data...")
    artists_data = [
        {"owner": "Da Vinci", "image_name": "Mona Lisa", "vector": [0.12, 0.23, 0.45, 0.67, 0.89]},
        {"owner": "Van Gogh", "image_name": "Starry Night", "vector": [0.88, 0.11, 0.34, 0.76]},
        {"owner": "Rembrandt", "image_name": "The Night Watch", "vector": [0.55, 0.66, 0.77, 0.88]},
        {"owner": "Johannes Vermeer", "image_name": "Girl with a Pearl Earring", "vector": [0.1, 0.2, 0.3, 0.4, 0.5]},
        {"owner": "Salvador Dalí", "image_name": "The Persistence of Memory", "vector": [0.91, 0.82, 0.73, 0.64]},
        {"owner": "Pablo Picasso", "image_name": "Guernica", "vector": [0.22, 0.33, 0.44, 0.55, 0.66]},
        {"owner": "Claude Monet", "image_name": "Impression, Sunrise", "vector": [0.78, 0.89, 0.10, 0.21]},
        {"owner": "Edvard Munch", "image_name": "The Scream", "vector": [0.5, 0.5, 0.5, 0.5]},
        {"owner": "Gustav Klimt", "image_name": "The Kiss", "vector": [0.99, 0.88, 0.77, 0.66, 0.55]},
        {"owner": "Sandro Botticelli", "image_name": "The Birth of Venus", "vector": [0.15, 0.25, 0.35, 0.45]}
    ]
    for artist in artists_data:
        vector_hash = generate_hash(artist['vector'])
        blockchain.add_block({
            "image_name": artist['image_name'],
            "owner": artist['owner'],
            "vector": artist['vector'],
            "vector_hash": vector_hash
        })
    print("Blockchain is ready.")

def search_for_hash(blockchain: Blockchain, vector_hash_to_find: str):
    for block in blockchain.chain[1:]:
        if 'vector_hash' in block.data and block.data['vector_hash'] == vector_hash_to_find:
            return block.data
    return None

def perform_search_task(vector_hash: str):
    global winner_found_for_current_search
    print(f"[{node.name}] has started searching for hash: {vector_hash[:10]}...")
    
    start_time = time.time()
    simulated_work_time = random.uniform(0.1, 1.0)
    time.sleep(simulated_work_time)
    
    found_data = search_for_hash(node.blockchain, vector_hash)
    time_taken = time.time() - start_time

    with winner_lock:
        if not winner_found_for_current_search:
            winner_found_for_current_search = True
            print(f"\n!!! [{node.name}] is the WINNER! Found data in {time_taken:.4f}s !!!\n")

            winner_data = {
                "winner_name": node.name,
                "winner_address": node.get_address(),
                "time_taken": time_taken,
                "result_data": found_data,
            }
            all_peers = node.peers.copy()
            all_peers.add(node.get_address())
            broadcast_to_peers(all_peers, '/announce-winner', winner_data)

# --- API Endpoints ---
@app.route('/info', methods=['GET'])
def get_node_info():
    return jsonify({
        "name": node.name,
        "peers": list(node.peers),
        "tokens": node.tokens,
        "state": node.state,
        "current_winner_info": node.current_winner_info,
    })

@app.route('/blockchain', methods=['GET'])
def get_blockchain():
    chain_data = [b.__dict__ for b in node.blockchain.chain]
    return jsonify({"chain": chain_data, "length": len(chain_data)})

@app.route('/add_peer', methods=['POST'])
def add_peer():
    data = request.get_json()
    if not data or 'peer_address' not in data:
        return jsonify({"error": "Invalid data"}), 400
    node.add_peer(data['peer_address'])
    return jsonify({"message": "Peer added", "peers": list(node.peers)})

@app.route('/start-search', methods=['POST'])
def start_search():
    data = request.get_json()
    try:
        vector = json.loads(data['vector'])
        vector_hash = generate_hash(vector)
    except (json.JSONDecodeError, TypeError):
        return jsonify({"error": "Invalid vector format."}), 400

    all_nodes = node.peers.copy()
    all_nodes.add(node.get_address())
    broadcast_to_peers(all_nodes, '/reset', {})
    
    search_payload = {"vector_hash": vector_hash}
    broadcast_to_peers(all_nodes, '/perform-local-search', search_payload)

    return jsonify({"message": "Search initiated across the network."})

@app.route('/perform-local-search', methods=['POST'])
def perform_local_search():
    data = request.get_json()
    vector_hash = data['vector_hash']
    node.state = "SEARCHING"
    thread = threading.Thread(target=perform_search_task, args=(vector_hash,))
    thread.start()
    return jsonify({"message": "Search started."})

@app.route('/announce-winner', methods=['POST'])
def announce_winner():
    data = request.get_json()
    with winner_lock:
        if node.state != "VOTING":
            print(f"[{node.name}] received winner announcement from {data.get('winner_name')}")
            node.state = "VOTING"
            node.current_winner_info = data
    return jsonify({"message": "Announcement received."})

@app.route('/cast-vote', methods=['POST'])
def cast_vote():
    data = request.get_json()
    vote_payload = {"voter_address": node.get_address(), "vote": data['vote']}
    
    winner_address = node.current_winner_info.get('winner_address')
    requests.post(f"{winner_address}/receive-vote", json=vote_payload)

    node.state = "VOTED"
    return jsonify({"message": "Vote cast."})

@app.route('/receive-vote', methods=['POST'])
def receive_vote():
    data = request.get_json()
    # Only the winner should process votes
    if node.current_winner_info and node.get_address() == node.current_winner_info.get('winner_address'):
        voter = data['voter_address']
        vote = data['vote']
        node.votes[voter] = vote
        print(f"[{node.name}] collected vote '{vote}' from {voter}")

        total_voters = len(node.peers)
        if len(node.votes) >= total_voters:
            print("All votes are in! Tallying results...")
            votes_yes = sum(1 for v in node.votes.values() if v == 'YES')
            
            all_nodes = node.peers.copy()
            all_nodes.add(node.get_address())

            if total_voters == 0 or (votes_yes / total_voters) > 0.5:
                print(">>> CONSENSUS REACHED: Vote passes! <<<")
                verified_data = node.current_winner_info['result_data']
                node.blockchain.add_block(verified_data)
                
                # Calculate rewards
                rewards = {node.get_address(): 10} # Winner's reward
                for voter_addr, vote_cast in node.votes.items():
                    if vote_cast == 'YES':
                        rewards[voter_addr] = rewards.get(voter_addr, 0) + 1
                
                print(f"Distributing rewards: {rewards}")
                
                # Sync the updated chain and rewards with all peers
                sync_payload = {
                    "chain": [b.__dict__ for b in node.blockchain.chain],
                    "rewards": rewards
                }
                broadcast_to_peers(all_nodes, '/sync-chain', sync_payload)
            else:
                print(">>> CONSENSUS FAILED: Vote does not pass. <<<")
                broadcast_to_peers(all_nodes, '/round-over', {"status": "failed"})
    return jsonify({"message": "Vote received."})

@app.route('/sync-chain', methods=['POST'])
def sync_chain():
    data = request.get_json()
    new_chain_data = data['chain']
    rewards = data.get('rewards', {})

    # Update tokens based on rewards
    my_reward = rewards.get(node.get_address())
    if my_reward:
        node.tokens += my_reward
        print(f"[{node.name}] received {my_reward} tokens! New balance: {node.tokens}")

    # Sync chain
    if len(new_chain_data) > len(node.blockchain.chain):
        node.blockchain.chain = [Block(**b) for b in new_chain_data]
        print(f"[{node.name}] successfully synced blockchain. New length: {len(node.blockchain.chain)}")
    
    reset_state()
    return jsonify({"message": "Chain synced."})

@app.route('/round-over', methods=['POST'])
def round_over():
    """Endpoint to signify a round has ended (e.g., consensus failed)."""
    print(f"[{node.name}] received round-over signal.")
    reset_state()
    return jsonify({"message": "Round over."})

@app.route('/reset', methods=['POST'])
def reset_state_endpoint():
    reset_state()
    return jsonify({"message": "Node state has been reset."})

def reset_state():
    global winner_found_for_current_search
    with winner_lock:
        winner_found_for_current_search = False
        node.state = "IDLE"
        node.current_winner_info = None
        node.votes = {}
    print(f"[{node.name}] has been reset to IDLE state.")

# --- Main Execution ---
if __name__ == '__main__':
    port = 5000
    if '--port' in sys.argv:
        port_index = sys.argv.index('--port') + 1
        if port_index < len(sys.argv):
            port = int(sys.argv[port_index])

    node_name = f"Node-{port}"
    node = Node(name=node_name, host='0.0.0.0', port=port)

    seed_blockchain(node.blockchain)

    if '--peers' in sys.argv:
        peers_index = sys.argv.index('--peers') + 1
        if peers_index < len(sys.argv):
            peers = sys.argv[peers_index].split(',')
            for peer in peers:
                node.add_peer(peer.strip())
    
    print(f"Starting {node.name} at http://{node.host}:{node.port}")
    print(f"Known peers: {node.peers}")

    app.run(host=node.host, port=port, debug=False, threaded=True)
