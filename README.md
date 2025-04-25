# vector-AI-example

## วิธีติดตั้งและรันโปรเจกต์

1. **โคลนโปรเจกต์**
   ```bash
   git clone https://github.com/arthittakun/vector-AI-example.git
   
   cd vector-AI-example
   ```

2. **สร้าง virtual environment (แนะนำ)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # สำหรับ macOS/Linux
   venv\Scripts\activate     # สำหรับ Windows
   ```

3. **ติดตั้ง dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **ตั้งค่าไฟล์ .env**
   - สร้างไฟล์ `.env` (หากยังไม่มี) และกำหนดค่า APIKEY, MODEL ตามตัวอย่างใน repo

5. **รันเซิร์ฟเวอร์**
   ```bash
   python app.py
   ```

6. **เข้าใช้งาน API Docs**
   - เปิดเบราว์เซอร์ไปที่ [http://localhost:8000/docs](http://localhost:8000/docs)