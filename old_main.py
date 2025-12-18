import json
import threading
import http.server
import socketserver
from core.blockchain import Blockchain
from core.hashing import generate_hash
from core.network import Network

# --- ส่วนของ API Server ---
def make_api_handler(network_instance: Network):
    """
    Factory function to create a request handler class that has access to the network instance.
    """
    class ApiRequestHandler(http.server.BaseHTTPRequestHandler):
        def __init__(self, *args, **kwargs):
            self.network = network_instance
            super().__init__(*args, **kwargs)

        def do_GET(self):
            if self.path == '/blockchain':
                try:
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.send_header('Access-Control-Allow-Origin', '*') # Allow cross-origin requests
                    self.end_headers()
                    
                    json_data = self.network.get_chain_as_json()
                    self.wfile.write(json_data.encode('utf-8'))
                except Exception as e:
                    self.send_error(500, f"Server error: {e}")
            else:
                self.send_error(404, "Not Found: Please use the /blockchain endpoint")

    return ApiRequestHandler

def run_api_server(httpd: socketserver.TCPServer):
    """Function to run the server's forever loop."""
    print("API server is running...")
    httpd.serve_forever()

# --- ส่วนหลักของโปรแกรม ---
if __name__ == "__main__":
    # 1. สร้าง Blockchain และ Seed ข้อมูล
    print("กำลังเตรียมข้อมูลต้นฉบับใน Blockchain...")
    master_blockchain = Blockchain()
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
        master_blockchain.add_block({
            "image_name": artist['image_name'],
            "owner": artist['owner'],
            "vector": artist['vector'],
            "vector_hash": vector_hash
        })
    print("Blockchain พร้อมใช้งาน\n")

    # 2. สร้าง Network และ Nodes
    NUMBER_OF_NODES = 5
    network = Network(num_nodes=NUMBER_OF_NODES, initial_blockchain=master_blockchain)

    # 3. ตั้งค่าและรัน API Server ใน Background Thread
    HOST, PORT = "0.0.0.0", 5000
    ApiHandler = make_api_handler(network)
    httpd = socketserver.TCPServer((HOST, PORT), ApiHandler)
    
    server_thread = threading.Thread(target=run_api_server, args=(httpd,))
    server_thread.daemon = True  # ตั้งเป็น Daemonเพื่อให้ Thread ปิดตัวเมื่อโปรแกรมหลักจบ
    server_thread.start()
    
    # 4. เริ่มส่วน Interactive CLI
    print("\n\n--- ระบบตรวจสอบรูปภาพบนเครือข่าย Blockchain ---")
    print(f"API Server กำลังทำงานที่ http://localhost:{PORT}/blockchain")
    print("คำสั่งที่ใช้ได้: 'showchain', 'balances', 'exit'")
    print("ตัวอย่าง Vector ของ 'The Kiss': [0.99, 0.88, 0.77, 0.66, 0.55]")

    while True:
        user_input = input("\nป้อนค่า Vector หรือคำสั่ง: ")
        command = user_input.lower()

        if command == 'exit':
            print("กำลังปิดเซิร์ฟเวอร์และออกจากโปรแกรม...")
            httpd.shutdown() # สั่งปิด http server
            break
        
        elif command == 'showchain':
            print("\n--- แสดงข้อมูลทั้งหมดใน Blockchain ---")
            print(network.get_chain_as_json())
            print("------------------------------------")

        elif command == 'balances':
            network.show_token_balances()

        else:
            try:
                input_vector = json.loads(user_input)
                network.start_verification_race(input_vector)
            except json.JSONDecodeError:
                print("\n[Error] รูปแบบ Vector หรือคำสั่งไม่ถูกต้อง")
            except Exception as e:
                print(f"\n[Error] เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")