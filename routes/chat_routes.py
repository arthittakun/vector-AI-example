from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from LLM_Model.Model_llm_gemini import Gemini
import asyncio

router = APIRouter()
gemini = Gemini()

class ChatRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None
    use_agent: bool = False
    stream: bool = False  # เพิ่มพารามิเตอร์สำหรับสตรีม

    class Config:
        schema_extra = {
            "example": {
                "text": "ช่วยดูว่าต้นไม้นี้เป็นโรคอะไร",
                "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                "use_agent": True,
                "stream": False
            }
        }

@router.post(
    "/chat",
    summary="แชทกับ AI",
    description="""
    # API สำหรับแชทกับ AI

    ## พารามิเตอร์
    - **text** (string, optional): ข้อความที่ต้องการส่งให้ AI
    - **image_base64** (string, optional): รูปภาพในรูปแบบ Base64 string
    - **use_agent** (boolean): เลือกใช้ agent (true) หรือไม่ใช้ (false)
    - **stream** (boolean): ส่งผลลัพธ์แบบสตรีมหรือไม่ (default: false)

    ## หมายเหตุ
    - สามารถส่ง text หรือ image_base64 อย่างใดอย่างหนึ่ง หรือส่งทั้งคู่พร้อมกันได้
    - รูปภาพต้องแปลงเป็น Base64 string ก่อนส่ง
    - รูปแบบ Base64 ควรเริ่มต้นด้วย "data:image/jpeg;base64,"

    ## ตัวอย่าง Request

    ### ส่งทั้งข้อความและรูปภาพ:
    ```json
    {
        "text": "ช่วยดูว่าต้นไม้นี้เป็นโรคอะไร",
        "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
        "use_agent": true,
        "stream": false
    }
    ```

    ### ส่งเฉพาะข้อความ:
    ```json
    {
        "text": "วิธีการดูแลต้นกล้วย",
        "use_agent": true,
        "stream": true
    }
    ```

    ### ส่งเฉพาะรูปภาพ:
    ```json
    {
        "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
        "use_agent": false,
        "stream": false
    }
    ```

    ## วิธีรับข้อมูลแบบสตรีม (stream) ฝั่ง client

    เมื่อส่ง `stream: true` ใน payload จะได้รับผลลัพธ์แบบสตรีม (Server-Sent Events)  
    ตัวอย่างการอ่านผลลัพธ์ทีละ chunk ด้วย JavaScript fetch:

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
        // chunk จะมีรูปแบบ "data: ...\\n\\n"
        const lines = chunk.split('\\n').filter(line => line.trim());
        for (const line of lines) {
            if (line.startsWith('data: ')) {
                const content = line.slice(6); // ตัด "data: "
                // นำ content ไปแสดงผลต่อผู้ใช้
                console.log(content);
            }
        }
    }
    ```

    - ถ้าไม่ต้องการสตรีม ให้ส่ง `stream: false` หรือไม่ระบุ field นี้ จะได้ response แบบ JSON ปกติ
    - สามารถนำไปประยุกต์ใช้กับ React, Vue, หรือ JS อื่น ๆ ได้
    """
)
async def chat(request: ChatRequest):
    response = gemini.grminichat(
        text=request.text,
        image=request.image_base64,
        agent=request.use_agent
    )
    if request.stream:
        async def chunk_text(text, size=50, delay=0.1):
            for i in range(0, len(text), size):
                chunk = text[i:i+size]
                yield f"data: {chunk}\n\n"
                await asyncio.sleep(delay)
        return StreamingResponse(chunk_text(response), media_type="text/event-stream")
    return {"response": response}
