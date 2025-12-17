from typing import List, Dict
import json
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

    def get_chain_as_json(self):
        """
        รวบรวมข้อมูลทั้ง Blockchain และแปลงเป็น JSON string
        """
        blockchain_json = []
        for block in self.blockchain.chain:
            blockchain_json.append({
                "index": block.index,
                "timestamp": block.timestamp,
                "data": block.data,
                "previous_hash": block.previous_hash,
                "hash": block.hash
            })
        return json.dumps(blockchain_json, indent=4)

    def distribute_rewards(self, winner: Node, correct_voters: List[Node]):
        """
        แจกรางวัล Token ให้กับโหนดที่ทำงานสำเร็จ
        """
        print("\n5. การแจกรางวัล (Incentive):")
        # ให้รางวัลผู้ชนะ
        winner.tokens += 10
        print(f"   - ผู้ชนะ [{winner.name}] ได้รับ 10 tokens")

        # ให้รางวัลผู้ที่โหวตถูกต้อง
        for voter in correct_voters:
            voter.tokens += 1
            print(f"   - ผู้โหวต [{voter.name}] ได้รับ 1 token")

    def show_token_balances(self):
        """
        แสดงจำนวน Token คงเหลือของทุกโหนด
        """
        print("\n--- ยอด Token คงเหลือ ---")
        for node in self.nodes:
            print(f"  - [{node.name}]: {node.tokens} tokens")
        print("------------------------")


    def start_verification_race(self, input_vector: List[float]):
        """
        เริ่มกระบวนการทั้งหมด: รับ vector, แข่งขัน, โหวต, แจกรางวัล และแสดงผลลัพธ์
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
        winner_result = min(race_results, key=lambda x: x['time_taken'])
        winner_node = next(n for n in self.nodes if n.name == winner_result['node_name'])
        print(f"\n2. ผู้ชนะการแข่งขัน: [{winner_node.name}] (ใช้เวลา {winner_result['time_taken']:.4f} วินาที)")
        
        winner_answer = winner_result['result_data']
        if winner_answer:
            print(f"   คำตอบของผู้ชนะ: พบข้อมูล -> รูป '{winner_answer['image_name']}'")
        else:
            print(f"   คำตอบของผู้ชนะ: ไม่พบข้อมูล")

        # 4. Voting: Other nodes verify the winner's answer
        print("\n3. เริ่มการโหวตเพื่อยืนยันคำตอบ:")
        votes_yes = 0
        correct_voters: List[Node] = []
        for voter_node in self.nodes:
            if voter_node.name == winner_node.name:
                continue

            verification_result = voter_node.search_for_hash(input_hash)
            
            if verification_result == winner_answer:
                votes_yes += 1
                correct_voters.append(voter_node)
                print(f"   - [{voter_node.name}] ยืนยันตรงกัน -> โหวต YES")
            else:
                print(f"   - [{voter_node.name}] ยืนยันไม่ตรงกัน -> โหวต NO")

        # 5. Final Result & Rewards
        total_voters = len(self.nodes) - 1
        print(f"\n4. สรุปผลการโหวต: {votes_yes} YES / {total_voters} เสียง")

        if total_voters == 0 or votes_yes / total_voters > 0.5:
            print("\n>>> ผลลัพธ์สุดท้าย (ผ่านการรับรองจากเครือข่าย):")
            if winner_answer:
                print(f"    ตรงกัน! คือรูป: '{winner_answer['image_name']}' ของศิลปิน: {winner_answer['owner']}")
            else:
                print("    ไม่พบข้อมูลรูปภาพนี้ใน Blockchain")
            
            # แจกรางวัลให้ผู้ชนะและผู้โหวตที่ถูกต้อง
            self.distribute_rewards(winner=winner_node, correct_voters=correct_voters)
        else:
            print("\n>>> ผลลัพธ์สุดท้าย: เครือข่ายไม่สามารถยืนยันคำตอบของผู้ชนะได้! (ไม่มีการแจกรางวัล)")

        # แสดง Token คงเหลือของทุกคน
        self.show_token_balances()

        return winner_answer
