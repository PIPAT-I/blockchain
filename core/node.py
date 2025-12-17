import time
import random
from core.blockchain import Blockchain


class Node:
    def __init__(self, name: str, blockchain_instance: Blockchain):
        """
        สร้างโหนด 1 ตัว

        :param name: ชื่อของโหนด (เช่น "Node-A")
        :param blockchain_instance: อ็อบเจกต์ของ Blockchain ที่ทุกโหนดจะใช้ร่วมกัน
        """
        self.name = name
        self.blockchain = blockchain_instance
        self.tokens = 100  # โหนดทุกตัวมี 100 โทเคนเมื่อเริ่มต้น

    def search_for_hash(self, vector_hash_to_find: str):
        """
        ตรรกะการค้นหา hash ใน blockchain ของโหนด - ไม่มีการหน่วงเวลา
        """
        # เริ่มค้นหาจากบล็อกที่ 1 (ข้าม Genesis block)
        for block in self.blockchain.chain[1:]:
            if 'vector_hash' in block.data and block.data['vector_hash'] == vector_hash_to_find:
                return block.data  # คืนค่า data ของบล็อกที่เจอ
        return None  # คืนค่า None ถ้าไม่เจอ

    def perform_search_task(self, vector_hash_to_find: str):
        """
        จำลองการ "แข่งขัน" ค้นหาข้อมูล มีการหน่วงเวลาแบบสุ่มเพื่อจำลองการทำงาน
        """
        print(f"    - [{self.name}] เริ่มการค้นหา...")
        start_time = time.time()

        # การทำงานค้นหาจริงๆ
        found_data = self.search_for_hash(vector_hash_to_find)

        # จำลองความยากง่าย/ความเร็วของแต่ละโหนดด้วยการ sleep แบบสุ่ม
        simulated_work_time = random.uniform(0.1, 0.5)  # หน่วงเวลา 0.1 - 0.5 วินาที
        time.sleep(simulated_work_time)

        end_time = time.time()
        time_taken = end_time - start_time

        result_text = "พบข้อมูล" if found_data else "ไม่พบข้อมูล"
        print(f"    - [{self.name}] ค้นหาเสร็จสิ้นใน {time_taken:.4f} วินาที. ผลลัพธ์: {result_text}")

        return {
            "result_data": found_data,
            "time_taken": time_taken,
            "node_name": self.name
        }
