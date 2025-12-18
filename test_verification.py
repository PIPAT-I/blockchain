#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
ไฟล์ทดสอบการตรวจสอบความสมบูรณ์ของ Blockchain
แสดงวิธีใช้ระบบตรวจสอบการแก้ไขข้อมูล
"""

from core.blockchain import Blockchain
import json


def test_blockchain_verification():
    print("=" * 60)
    print("ทดสอบระบบตรวจสอบ Blockchain")
    print("=" * 60)
    
    # สร้าง blockchain ใหม่
    blockchain = Blockchain()
    
    # เพิ่มข้อมูลบางส่วน
    print("\n1. เพิ่มข้อมูลลงใน blockchain...")
    blockchain.add_block({"type": "transaction", "from": "Alice", "to": "Bob", "amount": 50})
    blockchain.add_block({"type": "transaction", "from": "Bob", "to": "Charlie", "amount": 30})
    blockchain.add_block({"type": "transaction", "from": "Charlie", "to": "Alice", "amount": 20})
    print(f"✓ เพิ่มข้อมูลเสร็จ ({len(blockchain.chain)} blocks)")
    
    # ทดสอบ 1: ตรวจสอบ blockchain ที่ปลอดภัย
    print("\n" + "=" * 60)
    print("ทดสอบ 1: ตรวจสอบ blockchain ที่ไม่มีการแก้ไข")
    print("=" * 60)
    
    result = blockchain.is_chain_valid()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    if result["is_valid"]:
        print("✓ Blockchain ปลอดภัย - ไม่มีการแก้ไขข้อมูล")
    
    # ทดสอบ 2: ตรวจสอบ block เดียว
    print("\n" + "=" * 60)
    print("ทดสอบ 2: ตรวจสอบความสมบูรณ์ของ block เดียว")
    print("=" * 60)
    
    for i in range(len(blockchain.chain)):
        integrity = blockchain.verify_block_integrity(i)
        status = "✓" if integrity["valid"] else "✗"
        print(f"{status} Block {i}: {integrity['message']}")
    
    # ทดสอบ 3: จำลองการแก้ไขข้อมูล
    print("\n" + "=" * 60)
    print("ทดสอบ 3: จำลองการแก้ไขข้อมูลในระบบ")
    print("=" * 60)
    
    print("⚠️  ทำการแก้ไขข้อมูลใน Block 1...")
    original_data = blockchain.chain[1].data.copy()
    blockchain.chain[1].data = {"type": "fake", "from": "Hacker", "to": "Attacker", "amount": 9999}
    print(f"   ข้อมูลเดิม: {original_data}")
    print(f"   ข้อมูลใหม่: {blockchain.chain[1].data}")
    
    # ตรวจสอบหลังจากการแก้ไข
    print("\nตรวจสอบ blockchain หลังการแก้ไข:")
    result = blockchain.is_chain_valid()
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    # ทดสอบ 4: ตรวจหาการแก้ไขทั้งหมด
    print("\n" + "=" * 60)
    print("ทดสอบ 4: รายงานการแก้ไขทั้งหมด")
    print("=" * 60)
    
    tampering = blockchain.detect_tampering()
    print(json.dumps(tampering, indent=2, ensure_ascii=False))
    
    if tampering["is_tampered"]:
        print(f"\n⚠️  ตรวจพบการแก้ไขใน {len(tampering['tampered_blocks'])} block(s)")
        for tampered in tampering["tampered_blocks"]:
            print(f"\n   Block #{tampered['index']}:")
            print(f"   - Hash ที่เก็บไว้: {tampered['stored_hash'][:16]}...")
            print(f"   - Hash ที่คาดหวัง: {tampered['expected_hash'][:16]}...")
    
    # ทดสอบ 5: ตรวจสอบ block ที่ถูกแก้ไข
    print("\n" + "=" * 60)
    print("ทดสอบ 5: ตรวจสอบ block ที่ถูกแก้ไข")
    print("=" * 60)
    
    integrity = blockchain.verify_block_integrity(1)
    print(json.dumps(integrity, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    test_blockchain_verification()
