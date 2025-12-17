from core.blockchain import Blockchain
from core.hashing import generate_hash

print("TEST")

art_chain = Blockchain()

# --- Block 1 Data ---
vector_mona_lisa = [0.12,0.23,0.45,0.67,0.89]
vector_hash_1 = generate_hash(vector_mona_lisa)

# --- Block 2 & 3 Data ---
vector_starry_night = [0.88, 0.11, 0.34, 0.76]
vector_hash_2 = generate_hash(vector_starry_night)


print("Adding Block 1 (Mona Lisa)...")
art_chain.add_block({
    "image_name": "Mona Lisa",
    "owner": "Da Vinci",
    "vector": vector_mona_lisa,
    "vector_hash": vector_hash_1
})

print("Adding Block 2 (Starry Night)...")
art_chain.add_block({
    "image_name": "Starry Night",
    "owner": "Van Gogh",
    "vector": vector_starry_night,
    "vector_hash": vector_hash_2
})

print("Adding Block 3 (Starry Night)...")
art_chain.add_block({
    "image_name": "Starry Night",
    "owner": "Van Gogh",
    "vector": vector_starry_night,
    "vector_hash": vector_hash_2
})


print("\n--- Blockchain Status ---")
for block in art_chain.chain:
    print(f"Block #{block.index}")
    print(f"Hash: {block.hash}")
    print(f"Prev: {block.previous_hash}")
    print(f"Data: {block.data}")
    print("-" * 20)

# 5. ตรวจสอบความถูกต้อง
print(f"\nIs Chain Valid? {art_chain.is_chain_valid()}")


print("\n[!!!] Hacker is modifying Block 1...")
art_chain.chain[1].data['vector'] = [0.00, 0.00, 0.00, 0.00] # เปลี่ยนค่า Vector

# ตรวจสอบอีกรอบ
print(f"Is Chain Valid after hack? {art_chain.is_chain_valid()}")