from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from LLM_Model.Model_llm_gemini import Gemini

router = APIRouter()
gemini = Gemini()

class ChatRequest(BaseModel):
    text: Optional[str] = None
    image_base64: Optional[str] = None
    use_agent: bool = False

    class Config:
        schema_extra = {
            "example": {
                "text": "ช่วยดูว่าต้นไม้นี้เป็นโรคอะไร",
                "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
                "use_agent": True
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
        "use_agent": true
    }
    ```

    ### ส่งเฉพาะข้อความ:
    ```json
    {
        "text": "วิธีการดูแลต้นกล้วย",
        "use_agent": true
    }
    ```

    ### ส่งเฉพาะรูปภาพ:
    ```json
    {
        "image_base64": "data:image/jpeg;base64,/9j/4AAQSkZJRg...",
        "use_agent": false
    }
    ```
    """
)
async def chat(request: ChatRequest):
    response = gemini.grminichat(
        text=request.text,
        image=request.image_base64,
        agent=request.use_agent
    )
    return {"response": response}
