import google.generativeai as genai
from google.generativeai.types import content_types
from dotenv import load_dotenv
import os
import json
import base64
import re
from Model.Model_Vector_DB import VectorDB

load_dotenv()

class Gemini:
    def __init__(self):
        self.systemagent = "คุณเป็นผู้เชี่ยวชาญด้านโรคพืชและการดูแลพืช สามารถให้ข้อมูลเกี่ยวกับโรคพืช, อาการ, สาเหตุ, วิธีการรักษา และการป้องกันโรคพืชต่างๆ รวมถึงแนะนำการดูแลพืช เช่น การรดน้ำ, แสงแดด, และการจัดการกับศัตรูพืชให้พืชมีสุขภาพดี"
        genai.configure(api_key=os.getenv("APIKEY"))
        self.model = genai.GenerativeModel(os.getenv("MODEL"))
        self.vector_db = VectorDB()

    def _get_relevant_context(self, text: str, k: int = 3) -> str:
        """Get relevant context from vector DB"""
        results = self.vector_db.search_for_rag(text, k)
        if not results:
            return ""
            
        context_parts = []
        for i, result in enumerate(results, 1):
            source = result['metadata'].get('source', 'ไม่ระบุแหล่งที่มา')
            context = f"ข้อมูลอ้างอิงที่ {i} (จาก {source}):\n{result['text']}\n"
            context_parts.append(context)
            
        return "\n".join(context_parts)

    def _validate_base64(self, image_data: str) -> bool:
        """Validate base64 image data"""
        try:
            if not image_data:
                return False
                
            # Remove header if exists
            if 'base64,' in image_data:
                image_data = image_data.split('base64,')[1]
                
            # Try to decode
            decoded = base64.b64decode(image_data)
            return len(decoded) > 0
        except Exception:
            return False

    def grminichat(self, text: str = None, image: str = None, agent: bool = False):
        try:
            # Handle empty inputs
            if not text and not image:
                return "กรุณาระบุข้อความหรือรูปภาพ"

            # Set default text for image-only requests
            if not text and image:
                text = "ช่วยวิเคราะห์รูปภาพนี้"

            if agent:
                # Get relevant context from vector DB
                context = self._get_relevant_context(text if text else "โรคพืช")
                
                # Build enhanced prompt with context
                if context:
                    enhanced_prompt = f"""ใช้ข้อมูลต่อไปนี้ในการตอบคำถาม:

{context}

คำถามหรือข้อความ: {text if text else 'ช่วยวิเคราะห์รูปภาพนี้'}

{self.systemagent}

โปรดตอบโดยอ้างอิงข้อมูลที่ให้มาด้วย"""
                    self.prompt = enhanced_prompt
                else:
                    self.prompt = f"{self.systemagent} {text if text else 'ช่วยวิเคราะห์รูปภาพนี้'}"
            else:
                self.prompt = text if text else "ช่วยวิเคราะห์รูปภาพนี้"

            print(f"Prompt: {self.prompt}")
            # Process request based on inputs
            if image:
                try:
                    # Validate base64 data
                    if not self._validate_base64(image):
                        return "รูปแบบข้อมูลรูปภาพไม่ถูกต้อง กรุณาตรวจสอบ base64 string"

                    # Clean and format image data
                    if not image.startswith('data:image/'):
                        image = 'data:image/jpeg;base64,' + image
                    
                    image_data = image.split('base64,')[1]
                    image_data = re.sub(r'\s+', '', image_data)

                    # Create content parts for the model
                    contents = [
                        {
                            "parts": [
                                {"text": self.prompt},
                                {
                                    "inline_data": {
                                        "mime_type": "image/jpeg",
                                        "data": image_data
                                    }
                                }
                            ]
                        }
                    ]

                    response = self.model.generate_content(contents)
                    return response.text

                except Exception as img_error:
                    print(f"Image processing error: {str(img_error)}")
                    return "เกิดข้อผิดพลาดในการประมวลผลรูปภาพ: " + str(img_error)
            else:
                # For text-only request
                response = self.model.generate_content(self.prompt)
                return response.text

        except Exception as e:
            print(f"Error: {str(e)}")
            return f"เกิดข้อผิดพลาด: {str(e)}"