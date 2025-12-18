# Consensus Mechanism Documentation

## 📌 จุดประสงค์ของ Consensus

**Consensus** ในระบบ Blockchain นี้มีจุดประสงค์เพื่อ:

1. **ยืนยันข้อมูลใหม่** - ก่อนเพิ่ม Block ใหม่เข้า Chain ต้องได้รับการยอมรับจากทุก Node
2. **ป้องกัน Fraud** - หลีกเลี่ยงการเก็บข้อมูลเท็จหรือเสื้อปลอมใน Blockchain
3. **ทำให้ระบบไม่เข้าข้างใครฝ่ายหนึ่ง** - ไม่ให้ Node เดียวควบคุมข้อมูลทั้งหมด
4. **จ่ายผลประโยชน์ให้ผู้มีส่วนร่วม** - Node ที่ช่วย validate ข้อมูลได้ Token

---

## 🔄 ขั้นตอน Consensus Process

### ขั้นตอนที่ 1: Search Phase (ค้นหา)
```
Client → broadcast /start-search → All Nodes
↓
All Nodes: ค้นหาข้อมูลตามเวกเตอร์ (parallel search)
```

**ลักษณะเฉพาะ**:
- ทุก Node ทำงาน **ขนานไปด้วยกัน**
- ผู้ชนะคือ Node ที่หา **เสร็จเร็วที่สุด**
- Stake (Token) ของ Node มีผลต่อความเร็ว:
  ```
  work_time = base_work_time / (my_stake / 10)
  // Node ที่มี stake มากทำงานเร็วกว่า
  ```

**ผ่านหรือไม่**:
- ✓ Node ที่ชนะหา ส่ง `/announce-winner`
- ทุก Node อื่น **ยุติการค้นหา**

---

### ขั้นตอนที่ 2: Voting Phase (โหวต)
```
Winner → broadcast /announce-winner
↓
Other Nodes → /cast-vote → Winner
         (YES or NO)
↓
Winner → collect all votes → tally_votes()
```

**ลักษณะเฉพาะ**:
- **Stake-Weighted Voting**: เสียงของ Node หนัก = Stake มาก
  ```
  yes_stake = sum(stake of YES voters)
  total_stake = sum(stake of all voters)
  
  consensus_passed = (yes_stake / total_stake) > 50%
  ```

- **Timeout Protection**: รอสูงสุด 30 วินาที
  ```python
  voting_timeout = 30  # seconds
  if time > 30s → tally_votes() anyway
  ```

**ผ่านหรือไม่**:
- ✓ YES stake > 50% → Consensus PASSED → Block สร้าง
- ✗ YES stake ≤ 50% → Consensus FAILED → Round ใหม่

---

### ขั้นตอนที่ 3: Reward & Penalty Phase

#### ✅ Consensus PASSED (YES > 50%):
```python
rewards = {
    winner: 10 tokens,           # Node ที่ชนะการค้นหา
    each_yes_voter: +2 tokens,   # Node ที่ vote YES
}

slashing = {
    each_no_voter: -2 tokens     # Node ที่ vote NO (vote ผิด)
}
```

#### ❌ Consensus FAILED (YES ≤ 50%):
```python
slashing = {
    each_yes_voter: -1 tokens    # Node ที่ vote YES (vote ผิด)
    # NO voters ไม่ได้ reward/slashing
}
```

#### 🔗 Block ที่สร้าง:
```json
{
  "type": "CONSENSUS_RESULT",
  "result": verified_data,
  "rewards": {...},
  "slashing": {...}
}
```

---

### ขั้นตอนที่ 4: Chain Sync
```
Winner → broadcast /sync-chain [new_blockchain]
↓
All Nodes: Validate chain
  if valid → accept
  if invalid → reject
↓
Reset state to IDLE
```

---

## 🛡️ ป้องกัน 51% Attack

### ปัญหา: 
ถ้า Node มี 51%+ Stake สามารถ:
1. Propose block เท็จได้เอง
2. Vote ให้ตัวเอง
3. Consensus ผ่านเสมอ

### วิธีแก้ (ที่เพิ่มแล้ว):

#### 1️⃣ **Slashing System** ✅
- Node ที่ vote ผิด **ลดคะแนน**
- ถ้า Node ที่มี 51% stake vote ผิด → lose 1-2 tokens ต่อรอบ
- ค่อยๆ หมดเหลว (attrition attack prevention)

#### 2️⃣ **Random Validator Selection** ✅
```python
def select_random_validators(num_validators):
    """เลือก validators แบบสุ่ม"""
    all_nodes = peers + self
    return random.sample(all_nodes, num_validators)
```
- ไม่ใช้ validators ทั้งหมดทุกครั้ง
- Node ที่มี 51% stake ไม่ได้เลือกตัวเอง 100%
- ต้องพึ่ง validators อื่นด้วย

#### 3️⃣ **Timeout Mechanism** ✅
- ถ้า node ค้างรอ vote → timeout 30 วินาที
- ป้องกัน single node freeze blockchain

---

## 💰 Incentive System

### Token ที่ได้:

| บทบาท | Condition | Reward |
|------|-----------|--------|
| **Winner** | ชนะการค้นหา | +10 tokens |
| **YES Voter** | vote YES + consensus pass | +2 tokens |
| **YES Voter** | vote YES + consensus fail | -1 token (slashing) |
| **NO Voter** | vote NO + consensus pass | -2 tokens (slashing) |
| **NO Voter** | vote NO + consensus fail | 0 tokens |

### เหตุผล:

1. **Winner Gets Most** - สร้างแรงจูงใจให้ search เร็ว
2. **YES Voters Rewarded** - Honest voting ได้ reward
3. **Slashing on Wrong Vote** - ลดแรงจูงใจในการ vote สุ่ม
4. **Encourages Truthfulness** - ถ้า vote เท็จ → lose token

---

## ⚙️ Configuration

```python
voting_timeout = 30  # วินาที (สามารถปรับได้)
```

การปรับแต่ง:
- ↑ ถ้าเพิ่ม → รอนานขึ้น ต่อให้ node ช้า
- ↓ ถ้าลด → ไม่รอนาน node ที่ช้าอาจขาดเสียง

---

## 📊 ตัวอย่าง Consensus Round

### Scenario: 4 Nodes, 1 Block เสนอ

```
Node1 (100 tokens) - WINNER
Node2 (100 tokens) - YES voter  
Node3 (100 tokens) - YES voter
Node4 (100 tokens) - NO voter

Voting Results:
  YES: 200 tokens (Node2 + Node3)
  NO:  100 tokens (Node4)
  Total: 300 tokens
  
  Pass? 200/300 = 66.6% > 50% ✓ YES

Rewards:
  Node1: +10 tokens (100 → 110)
  Node2: +2 tokens (100 → 102)
  Node3: +2 tokens (100 → 102)
  Node4: -2 tokens (100 → 98) [slashing]

Final Balances:
  Node1: 110
  Node2: 102
  Node3: 102
  Node4: 98
```

---

## 🔍 Validation Rules

Block จะถูกยอมรับเมื่อ:

1. ✅ Block hash ถูกต้อง
2. ✅ Previous block hash ตรงกัน
3. ✅ Consensus passed (YES > 50%)
4. ✅ ไม่มีการแก้ไขข้อมูลหลังจากสร้าง

---

## 📝 State Transitions

```
        ┌──────────────────────────────────┐
        ↓                                  │
     [IDLE] ─── /start-search ──→ [SEARCHING]
        ↑                                  │
        │                             /announce-winner
        │                                  ↓
        │                          [AWAITING_VOTES]
        │                                  │
        │                        (voting_timeout=30s)
        │                                  ↓
        └──── /sync-chain + /round-over ──[tally_votes]
                     (reset)
```

---

## 🎯 การใช้งาน

### ค้นหาข้อมูล:
```bash
POST /start-search
Content-Type: application/json
{
  "vector": "[0.1, 0.2, 0.3, 0.4]"
}
```

### ดูสถานะ Node:
```bash
GET /info
```

### ดู Blockchain:
```bash
GET /blockchain
```

### ดู Balances:
```bash
GET /info → "all_balances"
```

