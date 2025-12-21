# 1. ใช้ Python 3.12-slim เป็น Base Image
FROM python:3.12-slim

# 2. ตั้งค่า Working Directory ภายใน Container
WORKDIR /app

# 3. คัดลอกไฟล์ requirements.txt เข้าไปใน Container
COPY requirements.txt .

# 4. ติดตั้ง Dependencies
RUN pip install --no-cache-dir -r requirements.txt

# 5. คัดลอกโค้ดโปรเจคทั้งหมดเข้าไปใน Container
COPY . .

# 6. เปิด Port 5000-5010 เผื่อไว้สำหรับการทดลอง
# (ขั้นตอนนี้ไม่จำเป็น แต่เป็น Best Practice)
EXPOSE 5000-5010

# Default command (จะถูก override ใน docker-compose.yml)
CMD ["python", "node_server.py"]
