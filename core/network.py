from typing import List, Dict
from core.node import Node
from core.blockchain import Blockchain
from core.hashing import generate_hash

class Network:
    def __init__(self, num_nodes: int, initial_blockchain: Blockchain):
        """
        สร้างเครือข่ายและโหนดทั้งหมด

        :param num_nodes: จำนวนโหนดที่ต้องการสร้างในเครือข่าย
        :param initial_blockchain: Blockchain ที่มีข้อมูลเริ่มต้น ซึ่งจะถูกแชร์ให้ทุกโหนด
        """
        self.nodes: List[Node] = []
        self.blockchain = initial_blockchain
        print(f"กำลังสร้างเครือข่ายที่มี {num_nodes} โหนด...")
        for i in range(num_nodes):
            node_name = f"Node-{chr(65 + i)}" # ตั้งชื่อเป็น Node-A, Node-B, ...
            node = Node(name=node_name, blockchain_instance=self.blockchain)
            self.nodes.append(node)
        print("สร้างโหนดทั้งหมดเรียบร้อยแล้ว")

    def start_verification_race(self, input_vector: List[float]):
        """
        เริ่มกระบวนการทั้งหมด: รับ vector, แข่งขัน, โหวต และแสดงผลลัพธ์สุดท้าย
        """
        print(f"\n--- เริ่มกระบวนการตรวจสอบ Vector ---")
        print(f"Vector ที่รับมา: {input_vector}")

        # 1. Hash the input vector
        input_hash = generate_hash(input_vector)
        print(f"Hash ของ Vector: {input_hash}")

        # 2. Race: All nodes perform the search task
        print("\n1. เริ่มการแข่งขันค้นหา:")
        race_results: List[Dict] = []
        for node in self.nodes:
            result = node.perform_search_task(input_hash)
            race_results.append(result)

        # 3. Find the winner (node with the shortest time)
        winner = min(race_results, key=lambda x: x['time_taken'])
        print(f"\n2. ผู้ชนะการแข่งขัน: [{winner['node_name']}] (ใช้เวลา {winner['time_taken']:.4f} วินาที)")
        
        winner_answer = winner['result_data']
        if winner_answer:
            print(f"   คำตอบของผู้ชนะ: พบข้อมูล -> รูป '{winner_answer['image_name']}'")
        else:
            print(f"   คำตอบของผู้ชนะ: ไม่พบข้อมูล")

        # 4. Voting: Other nodes verify the winner's answer
        print("\n3. เริ่มการโหวตเพื่อยืนยันคำตอบ:")
        votes_yes = 0
        for voter_node in self.nodes:
            # โหนดผู้ชนะไม่ต้องโหวตตัวเอง
            if voter_node.name == winner['node_name']:
                continue

            # โหนดอื่น ๆ ทำการตรวจสอบ (แบบไม่หน่วงเวลา)
            verification_result = voter_node.search_for_hash(input_hash)
            
            # ตรวจสอบว่าผลการค้นหาของโหนดนี้ ตรงกับคำตอบของผู้ชนะหรือไม่
            if verification_result == winner_answer:
                votes_yes += 1
                print(f"   - [{voter_node.name}] ยืนยันตรงกัน -> โหวต YES")
            else:
                print(f"   - [{voter_node.name}] ยืนยันไม่ตรงกัน -> โหวต NO")

        # 5. Final Result: Check if consensus is reached
        total_voters = len(self.nodes) - 1
        print(f"\n4. สรุปผลการโหวต: {votes_yes} YES / {total_voters} เสียง")

        # Consensus is reached if more than 50% of voters agree
        if votes_yes / total_voters > 0.5:
            print("\n>>> ผลลัพธ์สุดท้าย (ผ่านการรับรองจากเครือข่าย):")
            if winner_answer:
                print(f"    ตรงกัน! คือรูป: '{winner_answer['image_name']}' ของศิลปิน: {winner_answer['owner']}")
            else:
                print("    ไม่พบข้อมูลรูปภาพนี้ใน Blockchain")
        else:
            print("\n>>> ผลลัพธ์สุดท้าย: เครือข่ายไม่สามารถยืนยันคำตอบของผู้ชนะได้! อาจมีปัญหาเกิดขึ้น")

        return winner_answer
