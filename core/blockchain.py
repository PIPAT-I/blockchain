from datetime import datetime
from core.block import Block


class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        

    def create_genesis_block(self):
        return Block(0, datetime.now(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]
    

    def add_block(self, new_data):

        # 1. หา Block ล่าสุด
        previous_block = self.get_latest_block()

        # 2. สร้าง Block ใหม่
        # - index = ความยาวของ chain
        # - timestamp = วันที่และเวลาที่ block ถูกสร้าง
        # - data = ข้อมูลที่ถูกเก็บใน block
        # - previous_hash = hash ของ block ที่อยู่ก่อนหน้า

        new_block = Block(
            index = len(self.chain),
            timestamp = datetime.now(),
            data = new_data,
            previous_hash = previous_block.hash
        )

        # 3. เพิ่ม block ใหม่เข้าไปใน chain
        self.chain.append(new_block)


    def is_chain_valid(self):
       
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]

            # 1. ตรวจสอบ hash ของ block ปัจจุบัน
            if current_block.hash != current_block.calculate_hash():
                print(f"Block {current_block.index} ข้อมูลถูกปลอมแปลง ")
                return False

            # 2. ตรวจสอบ hash ของ block ที่ก่อนหน้า
            if current_block.previous_hash != previous_block.hash:
                print(f"Block {current_block.index} เชื่อมโยงผิดพลาด ")
                return False

        return True
