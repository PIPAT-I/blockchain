import hashlib
import json
from datetime import datetime


class Block: 
    def __init__(self, index ,timestamp , data, previous_hash):

        self.index = index  # ลำดับของ block
        self.timestamp = str(timestamp)  # วันที่และเวลาที่ block ถูกสร้าง
        self.data = data  # ข้อมูลที่ถูกเก็บใน block
        self.previous_hash = previous_hash # hash ของ block ที่อยู่ก่อนหน้า


        self.hash = self.calculate_hash() # ค่า hash ของ block

    def calculate_hash(self):

        data_string = json.dumps(self.data , sort_keys=True)
        # แปลงข้อมูลใน block เป็น string เพื่อการ hash
        payload = str(self.index) + str(self.timestamp) + str(self.data) + str(self.previous_hash)
        return hashlib.sha256(payload.encode()).hexdigest()