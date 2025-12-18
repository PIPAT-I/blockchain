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

    def get_balances(self):
        """
        คำนวณยอด token ของแต่ละ node
        โดยนำมาจาก rewards ใน block และการ slashing
        """
        # Initial distribution
        balances = {
            'http://node1:5001': 100,
            'http://node2:5002': 100,
            'http://node3:5003': 100,
            'http://node4:5004': 100,
        }

        # อัปเดตตามการ reward และ slashing
        for block in self.chain[1:]: # Skip genesis block
            if isinstance(block.data, dict) and block.data.get("type") == "CONSENSUS_RESULT":
                # เพิ่ม rewards
                rewards = block.data.get("rewards", {})
                for address, reward in rewards.items():
                    balances[address] = balances.get(address, 0) + reward
                
                # ลด slashing สำหรับ invalid votes
                slashing = block.data.get("slashing", {})
                for address, penalty in slashing.items():
                    balances[address] = max(0, balances.get(address, 0) - penalty)
        
        return balances

    def is_chain_valid(self):
        """
        ตรวจสอบความถูกต้องของ blockchain ทั้งหมด
        ตรวจสอบว่ามีการแก้ไขข้อมูลหรือไม่
        """
        validation_report = {
            "is_valid": True,
            "errors": [],
            "blocks_checked": 0
        }
       
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            validation_report["blocks_checked"] += 1

            # 1. ตรวจสอบ hash ของ block ปัจจุบัน
            calculated_hash = current_block.calculate_hash()
            if current_block.hash != calculated_hash:
                error_msg = f"Block {current_block.index}: ข้อมูลถูกแก้ไข! Hash ไม่ตรงกัน (เก็บไว้: {current_block.hash}, คำนวณได้: {calculated_hash})"
                print(error_msg)
                validation_report["errors"].append(error_msg)
                validation_report["is_valid"] = False
                return validation_report

            # 2. ตรวจสอบ hash ของ block ที่ก่อนหน้า (ตรวจสอบห่วงโซ่)
            if current_block.previous_hash != previous_block.hash:
                error_msg = f"Block {current_block.index}: การเชื่อมโยงห่วงโซ่ผิดพลาด! (คาดหวัง: {previous_block.hash}, ได้รับ: {current_block.previous_hash})"
                print(error_msg)
                validation_report["errors"].append(error_msg)
                validation_report["is_valid"] = False
                return validation_report

        return validation_report

    def verify_block_integrity(self, block_index):
        """
        ตรวจสอบความสมบูรณ์ของ block เดียว
        """
        if block_index < 0 or block_index >= len(self.chain):
            return {"valid": False, "message": f"Block {block_index} ไม่มีอยู่"}

        block = self.chain[block_index]
        calculated_hash = block.calculate_hash()
        
        integrity_report = {
            "block_index": block_index,
            "valid": block.hash == calculated_hash,
            "stored_hash": block.hash,
            "calculated_hash": calculated_hash,
            "data": block.data,
            "message": ""
        }

        if integrity_report["valid"]:
            integrity_report["message"] = f"Block {block_index} ปลอดภัย - ข้อมูลไม่ถูกแก้ไข"
        else:
            integrity_report["message"] = f"Block {block_index} ตรวจพบการแก้ไขข้อมูล!"

        return integrity_report

    def detect_tampering(self):
        """
        ตรวจหาการแก้ไขข้อมูลทั้งใน blockchain
        คืนรายชื่อ block ที่ถูกแก้ไข
        """
        tampering_report = {
            "is_tampered": False,
            "tampered_blocks": [],
            "total_blocks": len(self.chain)
        }

        for i, block in enumerate(self.chain):
            calculated_hash = block.calculate_hash()
            if block.hash != calculated_hash:
                tampering_report["is_tampered"] = True
                tampering_report["tampered_blocks"].append({
                    "index": i,
                    "stored_hash": block.hash,
                    "expected_hash": calculated_hash,
                    "data": block.data
                })

        return tampering_report

    def calculate_slashing_penalty(self, votes, yes_count, total_voters):
        """
        คำนวณการ slashing สำหรับ node ที่ vote ผิด
        
        Slashing Rules:
        - ถ้า vote ไป NO แต่ consensus ผ่าน → slashing 2 tokens
        - ถ้า vote ไป YES แต่ consensus ไม่ผ่าน → slashing 1 token
        
        Args:
            votes: dict {voter_address: 'YES'/'NO'}
            yes_count: จำนวน YES vote
            total_voters: จำนวน voter ทั้งหมด
            
        Returns:
            dict {address: penalty_amount}
        """
        slashing = {}
        consensus_passed = yes_count > (total_voters / 2) if total_voters > 0 else False
        
        for voter_addr, vote in votes.items():
            if consensus_passed and vote == 'NO':
                # ลงคะแนน NO แต่ consensus ผ่าน → slashing 2 tokens
                slashing[voter_addr] = 2
            elif not consensus_passed and vote == 'YES':
                # ลงคะแนน YES แต่ consensus ไม่ผ่าน → slashing 1 token
                slashing[voter_addr] = 1
        
        return slashing
