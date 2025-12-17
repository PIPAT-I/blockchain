import json
from core.blockchain import Blockchain
from core.hashing import generate_hash
from core.network import Network

# 1. สร้าง Blockchain และ Seed ข้อมูลทั้งหมดให้ครบถ้วน
# ==================================================
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


# 2. สร้างเครือข่ายและโหนด โดยให้ทุกโหนดมีข้อมูล Blockchain ชุดเดียวกัน
# =================================================================
NUMBER_OF_NODES = 5  # กำหนดจำนวนโหนดในเครือข่าย
network = Network(num_nodes=NUMBER_OF_NODES, initial_blockchain=master_blockchain)


# 3. เริ่มส่วน Interactive สำหรับให้ผู้ใช้ป้อนข้อมูลเพื่อตรวจสอบ
# =================================================================
print("\n\n--- ระบบตรวจสอบรูปภาพบนเครือข่าย Blockchain ---")
print("คำสั่งที่ใช้ได้: 'showchain', 'balances', 'exit'")
print("ตัวอย่าง Vector ของ 'The Kiss': [0.99, 0.88, 0.77, 0.66, 0.55]")
print("ตัวอย่าง Vector ที่ไม่มีในระบบ: [1, 2, 3]")

while True:
    user_input = input("\nป้อนค่า Vector หรือคำสั่ง: ")
    command = user_input.lower()

    if command == 'exit':
        break
    
    elif command == 'showchain':
        print("\n--- แสดงข้อมูลทั้งหมดใน Blockchain ---")
        print(network.get_chain_as_json())
        print("------------------------------------")

    elif command == 'balances':
        network.show_token_balances()

    else:
        try:
            # Convert the input string to a Python list
            input_vector = json.loads(user_input)
            
            # เริ่มกระบวนการทั้งหมดผ่าน Network
            network.start_verification_race(input_vector)

        except json.JSONDecodeError:
            print("\n[Error] รูปแบบ Vector หรือคำสั่งไม่ถูกต้อง กรุณาใส่ในรูปแบบ JSON array หรือใช้คำสั่ง 'showchain', 'balances', 'exit'")
        except Exception as e:
            print(f"\n[Error] เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}")