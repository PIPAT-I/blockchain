from core.blockchain import Blockchain

# 1. สร้าง Blockchain และเพิ่มข้อมูลเข้าไป 3 บล็อก
print("--- 1. สร้าง Blockchain และเพิ่มข้อมูล ---")
my_chain = Blockchain()
my_chain.add_block({"sender": "Alice", "receiver": "Bob", "amount": 50})
my_chain.add_block({"sender": "Bob", "receiver": "Charlie", "amount": 25})
my_chain.add_block({"sender": "Charlie", "receiver": "Alice", "amount": 10})

print("สร้าง Blockchain ที่มี 4 บล็อก (รวม Genesis Block) สำเร็จ")
print("ตรวจสอบความถูกต้องครั้งแรก (ก่อนแก้ไข):")
print(f">> Chain valid: {my_chain.is_chain_valid()}\n")


# 2. จำลองการแก้ไขข้อมูล (Tampering)
print("--- 2. จำลองการแก้ไขข้อมูลในบล็อกที่ 2 ---")
# สมมติแฮกเกอร์เข้ามาแก้ข้อมูลในบล็อกที่ 2 (index=2) จาก 25 เป็น 2500
tampered_block = my_chain.chain[2]
print(f"ข้อมูลเดิม: {tampered_block.data}")
tampered_block.data = {"sender": "Bob", "receiver": "Charlie", "amount": 2500}
print(f"ข้อมูลใหม่: {tampered_block.data}")

print("\nตรวจสอบความถูกต้องครั้งที่ 2 (หลังจากแก้ไขข้อมูล):")
# การตรวจสอบนี้จะล้มเหลว เพราะ hash ของบล็อกที่ 2 ไม่ตรงกับข้อมูลข้างในแล้ว
print(f">> Chain valid: {my_chain.is_chain_valid()}\n")


# 3. จำลองการแก้ไขข้อมูลที่ซับซ้อนขึ้น
print("--- 3. แฮกเกอร์พยายามคำนวณ Hash ใหม่เพื่อหลอกระบบ ---")
print("แฮกเกอร์คำนวณ Hash ของบล็อกที่ 2 ใหม่จากข้อมูลที่ถูกแก้ไข")
original_hash = tampered_block.hash
tampered_block.hash = tampered_block.calculate_hash()
print(f"Hash เดิม: {original_hash}")
print(f"Hash ใหม่: {tampered_block.hash}")
print("ตอนนี้ Hash ของบล็อกที่ 2 ถูกต้องกับข้อมูลที่แก้ไขแล้ว แต่...")

print("\nตรวจสอบความถูกต้องครั้งที่ 3 (หลังจากคำนวณแฮชใหม่):")
# การตรวจสอบนี้จะยังคงล้มเหลว เพราะ hash ของบล็อกที่ 2 ไม่ตรงกับ previous_hash ของบล็อกที่ 3 อีกต่อไป
print(f">> Chain valid: {my_chain.is_chain_valid()}\n")

print("สรุป: การแก้ไขข้อมูลใน Blockchain แม้เพียงเล็กน้อย จะถูกตรวจจับได้เสมอ")
