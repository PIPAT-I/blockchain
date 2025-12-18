from core.blockchain import Blockchain
import random

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
    
    def select_random_validators(self, num_validators=None):
        """
        เลือก validators แบบสุ่ม เพื่อป้องกัน 51% Attack
        
        ถ้า node เดียวกันที่ propose ทุกครั้ง 
        มันสามารถ 51% attack ได้ เพราะว่า
        มัน propose + vote ให้ตัวเองได้
        
        วิธีแก้: เลือก validators แบบสุ่มจากทั้งหมด
        
        Args:
            num_validators: จำนวน validators ที่ต้องการ
                          ถ้า None ใช้ทั้งหมด
        
        Returns:
            set ของ validator addresses
        """
        all_nodes = self.peers.copy()
        all_nodes.add(self.get_address())
        
        if num_validators is None:
            num_validators = len(all_nodes)
        
        # ถ้าขอ validators มากกว่าจำนวนที่มี ให้ใช้ทั้งหมด
        num_validators = min(num_validators, len(all_nodes))
        
        selected = set(random.sample(list(all_nodes), num_validators))
        return selected