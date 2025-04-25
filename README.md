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

7.**ข้อมูลในโฟลเดอร์ ffmpeg สามารถโหลดได้ที่**
   - เปิดเบราว์เซอร์ไปที่ [https://ffmpeg.org/download.html]
   - หรือถ้าใช้ Windows โหลดได้ที่ [https://drive.google.com/drive/folders/1KbMz2HjQOXPOHzRQMM7JsJkn8BA9c-OU?usp=sharing]

## วิธีรับข้อมูลจาก API `/chat` แบบสตรีม

API `/chat` รองรับการส่งผลลัพธ์แบบสตรีม (stream) เมื่อส่ง `stream: true` ใน payload  
ตัวอย่างการใช้งานฝั่ง client (JavaScript) เพื่อรับข้อความทีละส่วน:

```js
const payload = {
    text: "ข้อความที่ต้องการถาม",
    image_base64: undefined, // หรือ base64 string ถ้ามีรูป
    use_agent: true,
    stream: true
};

const response = await fetch('https://llm.pmnd.online/api/chat/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
});

const reader = response.body.getReader();
const decoder = new TextDecoder();

while (true) {
    const { value, done } = await reader.read();
    if (done) break;
    const chunk = decoder.decode(value);
    // chunk จะมีรูปแบบ "data: ...\n\n"
    const lines = chunk.split('\n').filter(line => line.trim());
    for (const line of lines) {
        if (line.startsWith('data: ')) {
            const content = line.slice(6); // ตัด "data: "
            // นำ content ไปแสดงผลต่อผู้ใช้
            console.log(content);
        }
    }
}
```

**หมายเหตุ**
- ถ้าไม่ต้องการสตรีม ให้ส่ง `stream: false` หรือไม่ระบุ field นี้ จะได้ response แบบ JSON ปกติ
- ตัวอย่างนี้ใช้ fetch API และอ่าน stream ทีละ chunk
- สามารถนำไปประยุกต์ใช้กับ React, Vue, หรือ JS อื่น ๆ ได้