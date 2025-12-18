from core.blockchain import Blockchain

class Node:
    def __init__(self, name: str, listen_host: str, public_host: str, port: int):
        self.name = name
        self.listen_host = listen_host
        self.public_host = public_host
        self.port = port
        self.blockchain = Blockchain()
        self.peers = set()
        self.tokens = 100
        
        # State management for the voting process
        self.state = "IDLE"  # Can be IDLE, SEARCHING, VOTING, AWAITING_VOTES
        self.current_winner_info = None
        self.votes = {} # To store votes for the current round, e.g., {'node_url': 'YES'}

    def add_peer(self, peer_address):
        self.peers.add(peer_address)

    def get_address(self):
        return f"http://{self.public_host}:{self.port}"