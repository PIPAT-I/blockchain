import hashlib
import json

def generate_hash(data_to_hash):
    """
    สร้างค่าแฮช SHA-256 จากข้อมูลใดๆ (เช่น list, dict)
    โดยการแปลงข้อมูลเป็น JSON string ก่อน
    """
    # 1. แปลงข้อมูลเป็น JSON string
    data_string = json.dumps(data_to_hash, sort_keys=True)
    
    # 2. นำ string ไปเข้ารหัส (encode) และ hash
    return hashlib.sha256(data_string.encode()).hexdigest()
