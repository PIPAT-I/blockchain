import json
import sys
import os
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
VOTING_TIMEOUT = 30 # Voting timeout in seconds

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
        if 'vector_hash' in block.data and block.data.get('vector_hash') == vector_hash_to_find:
            return block.data
        if isinstance(block.data, dict):
            result_data = block.data.get("result", {})
            if isinstance(result_data, dict) and result_data.get('vector_hash') == vector_hash_to_find:
                return result_data
    return None

# --- PoS & Timeout Logic ---

def tally_votes():
    """
    Calculates the consensus result based on stake-weighted votes.
    This function should only be called after acquiring the winner_lock.
    """
    # Prevent double-tallying if called by both timeout and full vote completion
    if node.state != "AWAITING_VOTES":
        return

    print("Tallying results based on stake...")
    
    balances = node.blockchain.get_balances()
    
    total_voting_stake = sum(balances.get(voter_addr, 0) for voter_addr in node.votes.keys())
    yes_stake = sum(balances.get(voter_addr, 0) for voter_addr, vote_cast in node.votes.items() if vote_cast == 'YES')
    
    print(f"Tally: YES stake = {yes_stake}, Total voting stake = {total_voting_stake}")

    all_nodes = node.peers.copy()
    all_nodes.add(node.get_address())

    # Consensus is reached if more than 50% of the stake that voted agrees
    if total_voting_stake > 0 and (yes_stake / total_voting_stake) > 0.5:
        print(">>> CONSENSUS REACHED: Vote passes! <<<")
        
        verified_data = node.current_winner_info['result_data']
        
        rewards = {node.get_address(): 10}
        for voter_addr, vote_cast in node.votes.items():
            if vote_cast == 'YES':
                rewards[voter_addr] = rewards.get(voter_addr, 0) + 1
        
        print(f"Distributing rewards: {rewards}")

        new_block_data = {
            "type": "CONSENSUS_RESULT",
            "result": verified_data,
            "rewards": rewards
        }
        node.blockchain.add_block(new_block_data)
        
        sync_payload = {"chain": [b.__dict__ for b in node.blockchain.chain]}
        broadcast_to_peers(all_nodes, '/sync-chain', sync_payload)
    else:
        print(">>> CONSENSUS FAILED: Vote does not pass or no votes received. <<<")
        broadcast_to_peers(all_nodes, '/round-over', {"status": "failed"})

def vote_timeout_manager(round_id_for_timeout):
    time.sleep(VOTING_TIMEOUT)
    with winner_lock:
        # Check if the round has already ended or we are no longer the winner
        if node.round_id != round_id_for_timeout or node.state != "AWAITING_VOTES":
            print(f"[TimeoutThread] Round {round_id_for_timeout} already concluded or state changed. Exiting.")
            return

        print(f"\n!!! Voting for round {round_id_for_timeout} has timed out after {VOTING_TIMEOUT} seconds. Tallying results now... !!!\n")
        tally_votes()

def perform_search_task(vector_hash: str):
    global winner_found_for_current_search
    print(f"[{node.name}] has started searching for hash: {vector_hash[:10]}...")

    balances = node.blockchain.get_balances()
    my_stake = balances.get(node.get_address(), 1)

    base_work_time = random.uniform(1.0, 5.0)
    simulated_work_time = base_work_time / (my_stake / 10 if my_stake > 0 else 1)
    
    print(f"[{node.name}] My stake is {my_stake}. My work time is {simulated_work_time:.2f}s.")

    start_time = time.time()
    time.sleep(simulated_work_time)
    
    found_data = search_for_hash(node.blockchain, vector_hash)
    time_taken = time.time() - start_time

    with winner_lock:
        if winner_found_for_current_search or node.state != "SEARCHING":
            print(f"[{node.name}] finished searching, but a winner has already been determined. Standing down.")
            return

        winner_found_for_current_search = True
        print(f"\n!!! [{node.name}] is the WINNER! Found data in {time_taken:.4f}s !!!\n")

        winner_data = {
            "winner_name": node.name,
            "winner_address": node.get_address(),
            "time_taken": time_taken,
            "result_data": found_data,
        }

        node.state = "AWAITING_VOTES"
        node.current_winner_info = winner_data
        
        # Start the voting timer
        print(f"[{node.name}] Starting {VOTING_TIMEOUT}s voting timer for round {node.round_id}...")
        timer_thread = threading.Thread(target=vote_timeout_manager, args=(node.round_id,))
        timer_thread.daemon = True
        timer_thread.start()

        broadcast_to_peers(node.peers, '/announce-winner', winner_data)

# --- API Endpoints ---
@app.route('/info', methods=['GET'])
def get_node_info():
    balances = node.blockchain.get_balances()
    node.tokens = balances.get(node.get_address(), 0)
    return jsonify({
        "name": node.name,
        "peers": list(node.peers),
        "tokens": node.tokens,
        "state": node.state,
        "round_id": node.round_id,
        "current_winner_info": node.current_winner_info,
        "all_balances": balances
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
        if node.state == "SEARCHING":
            print(f"[{node.name}] received winner announcement from {data.get('winner_name')}. Stopping search.")
            node.state = "VOTING"
            node.current_winner_info = data
        else:
            print(f"[{node.name}] ignored a winner announcement from {data.get('winner_name')} because its state is already '{node.state}'.")
    return jsonify({"message": "Announcement processed."})

@app.route('/cast-vote', methods=['POST'])
def cast_vote():
    if node.state != "VOTING" or not node.current_winner_info:
        return jsonify({"error": "Node is not in a VOTING state or no winner is known.", "state": node.state}), 409

    data = request.get_json()
    if 'vote' not in data or data['vote'] not in ['YES', 'NO']:
        return jsonify({"error": "Invalid vote. It must be 'YES' or 'NO'."}), 400

    vote_payload = {"voter_address": node.get_address(), "vote": data['vote']}
    
    winner_address = node.current_winner_info.get('winner_address')
    if not winner_address:
        return jsonify({"error": "Could not determine winner's address."}), 500

    try:
        requests.post(f"{winner_address}/receive-vote", json=vote_payload, timeout=3)
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to send vote to winner: {e}"}), 502

    node.state = "VOTED"
    return jsonify({"message": "Vote cast successfully."})

@app.route('/receive-vote', methods=['POST'])
def receive_vote():
    with winner_lock:
        if node.current_winner_info and node.get_address() == node.current_winner_info.get('winner_address'):
            data = request.get_json()
            voter = data['voter_address']
            vote = data['vote']
            node.votes[voter] = vote
            print(f"[{node.name}] collected vote '{vote}' from {voter}")

            # If all expected votes are in, tally immediately without waiting for timeout.
            total_voters = len(node.peers)
            if len(node.votes) >= total_voters:
                print("All votes received before timeout. Tallying now.")
                tally_votes()
    return jsonify({"message": "Vote received."})

@app.route('/sync-chain', methods=['POST'])
def sync_chain():
    data = request.get_json()
    new_chain_data = data.get('chain', [])

    if len(new_chain_data) > len(node.blockchain.chain):
        potential_new_chain = Blockchain()
        potential_new_chain.chain = [Block(**b) for b in new_chain_data]

        if potential_new_chain.is_chain_valid():
             node.blockchain.chain = potential_new_chain.chain
             new_balances = node.blockchain.get_balances()
             node.tokens = new_balances.get(node.get_address(), 0)
             print(f"[{node.name}] successfully synced blockchain. New length: {len(node.blockchain.chain)}. My new balance: {node.tokens}")
             reset_state()
        else:
             print(f"[{node.name}] received an invalid chain. Discarding.")
             return jsonify({"error": "Invalid chain received"}), 400
    
    return jsonify({"message": "Chain synced."})

@app.route('/round-over', methods=['POST'])
def round_over():
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
        node.round_id += 1 # Increment round ID for the next round
    print(f"[{node.name}] has been reset to IDLE state for round {node.round_id}.")

# --- Main Execution ---
if __name__ == '__main__':
    port = 5000
    if '--port' in sys.argv:
        port_index = sys.argv.index('--port') + 1
        if port_index < len(sys.argv):
            port = int(sys.argv[port_index])

    node_name = f"Node-{port}"

    listen_host = '0.0.0.0'
    public_host = os.environ.get('NODE_HOST', '127.0.0.1')
    
    node = Node(
        name=node_name,
        listen_host=listen_host,
        public_host=public_host,
        port=port
    )

    seed_blockchain(node.blockchain)

    if '--peers' in sys.argv:
        peers_index = sys.argv.index('--peers') + 1
        if peers_index < len(sys.argv):
            peers = sys.argv[peers_index].split(',')
            for peer in peers:
                node.add_peer(peer.strip())
    
    print(f"Starting {node.name} at {node.get_address()}")
    print(f"Listening on {listen_host}:{port}")
    print(f"Known peers: {node.peers}")

    app.run(host=listen_host, port=port, debug=False, threaded=True)
