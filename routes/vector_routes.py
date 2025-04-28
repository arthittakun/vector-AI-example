from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from typing import Optional, List, Dict
from pydantic import BaseModel
from Model.Model_Vector_DB import VectorDB
from Tools.Tools_readfile import Tools_readfile
import base64
import io

router = APIRouter(
    prefix="/vector",
    tags=["Vector DB"],
    responses={
        500: {"description": "เกิดข้อผิดพลาดภายในเซิร์ฟเวอร์"},
        404: {"description": "ไม่พบข้อมูล"},
        400: {"description": "คำขอไม่ถูกต้อง"}
    }
)

vector_db = VectorDB()
tools = Tools_readfile()

class DocumentMetadata(BaseModel):
    source: Optional[str] = None
    chunk_id: Optional[int] = None
    type: Optional[str] = None

class DocumentUpdate(BaseModel):
    content: str
    metadata: Optional[DocumentMetadata] = None

class SearchQuery(BaseModel):
    query: str
    k: int = 3
    
@router.post(
    "/upload/file",
    summary="อัปโหลดไฟล์เข้าระบบ Vector DB",
    description="""
    # การอัปโหลดไฟล์เข้าระบบ Vector Database

    ## ประเภทไฟล์ที่รองรับ

    ### 1. ไฟล์เอกสาร
    - **TXT** (ไม่เกิน 5MB): ไฟล์ข้อความทั่วไป
    - **PDF** (ไม่เกิน 10MB): เอกสาร PDF
    - **DOC/DOCX** (ไม่เกิน 8MB): เอกสาร Microsoft Word
    
    ### 2. ไฟล์ข้อมูล
    - **CSV** (ไม่เกิน 5MB): ไฟล์ข้อมูลตาราง
    - **XLSX/XLS** (ไม่เกิน 8MB): ไฟล์ Excel
    - **JSON** (ไม่เกิน 5MB): ไฟล์ข้อมูลโครงสร้าง
    
    ### 3. ไฟล์เว็บและอีเมล
    - **HTML** (ไม่เกิน 5MB): ไฟล์เว็บเพจ
    - **MD** (ไม่เกิน 5MB): ไฟล์ Markdown
    - **EML** (ไม่เกิน 5MB): ไฟล์อีเมล
    
    ### 4. ไฟล์สื่อ
    - **MP3/WAV** (ไม่เกิน 10MB): ไฟล์เสียง
    - **MP4** (ไม่เกิน 10MB): ไฟล์วิดีโอ
    **หมายเหตุ**: ถ้ามากก่วา 10Mb จะ error 524 Timeout

    ## พารามิเตอร์
    - **file**: ไฟล์ที่ต้องการอัปโหลด (รองรับตามประเภทด้านบน)
    - **chunk_size**: ขนาดการแบ่งข้อความ (ค่าเริ่มต้น: 250 คำ)

    ## หมายเหตุ
    - ไฟล์เสียงและวิดีโอจะถูกแปลงเป็นข้อความด้วย Speech Recognition
    - ไฟล์ PDF จะดึงเฉพาะข้อความ
    - ไฟล์ตารางจะถูกแปลงเป็นข้อความ
    - ระบบจะแบ่งข้อความเป็นส่วนๆ ตาม chunk_size

    ## การประมวลผล
    1. ตรวจสอบประเภทและขนาดไฟล์
    2. แปลงข้อมูลเป็นข้อความ
    3. แบ่งข้อความเป็นส่วนๆ
    4. สร้าง vector embeddings
    5. บันทึกลงฐานข้อมูล

    ## ตัวอย่างการใช้งาน
    ```bash
    curl -X POST "api/vector/upload/file" \\
         -H "Content-Type: multipart/form-data" \\
         -F "file=@document.pdf" \\
         -F "chunk_size=250"
    ```
    """
)
async def upload_file(
    file: UploadFile = File(...),
    chunk_size: Optional[int] = Form(250)
):
    try:
        content = await file.read()
        file_ext = file.filename.split('.')[-1].lower()
        
        if file_ext not in tools.MAX_FILE_SIZES:
            raise HTTPException(status_code=400, detail="Unsupported file type")
        
        if len(content) > tools.MAX_FILE_SIZES[file_ext]:
            raise HTTPException(
                status_code=413,
                detail=f"File too large for type {file_ext}"
            )
        
        success = tools.upload_to_vector(content, file.filename, file_ext)
        
        if success:
            # Reload VectorDB after successful upload
            vector_db.load_db()
            return {"message": f"File {file.filename} uploaded and processed successfully"}
        raise HTTPException(status_code=500, detail="Failed to process file")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/upload/text")
async def upload_text(text: str, chunk_size: int = 250):
    try:
        chunks = tools.chunk_text(text, chunk_size)
        for chunk in chunks:
            tools.upload_to_vector(chunk, "direct_input", "text")
        
        # Reload VectorDB after successful upload
        vector_db.load_db()
        return {"message": "Text uploaded and processed successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/documents",
    summary="ดูรายการเอกสารทั้งหมด",
    description="""
    ## แสดงรายการเอกสารแบบแบ่งหน้า
    
    ### พารามิเตอร์:
    - **skip**: ข้ามข้อมูล n รายการแรก
    - **limit**: จำนวนข้อมูลต่อหน้า (สูงสุด 100)
    
    ### ผลลัพธ์:
    ```json
    {
        "total": "จำนวนเอกสารทั้งหมด",
        "documents": [
            {
                "id": "รหัสเอกสาร",
                "content": "เนื้อหา",
                "metadata": {}
            }
        ]
    }
    ```
    """
)
async def list_documents(skip: int = 0, limit: int = 10):
    try:
        docs = vector_db.list_documents(skip, limit)
        return {
            "total": len(vector_db.documents),
            "documents": docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get(
    "/documents/{doc_id}",
    summary="ดูข้อมูลเอกสาร",
    description="""
    ## ดูข้อมูลเอกสารตาม ID
    
    ### พารามิเตอร์:
    - **doc_id**: รหัสเอกสารที่ต้องการดู
    
    ### ผลลัพธ์:
    ```json
    {
        "id": "รหัสเอกสาร",
        "content": "เนื้อหา",
        "metadata": {}
    }
    ```
    """
)
async def get_document(doc_id: str):
    doc = vector_db.get_document(doc_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.put(
    "/documents/{doc_id}",
    summary="แก้ไขเอกสาร",
    description="""
    ## แก้ไขข้อมูลเอกสาร
    
    ### พารามิเตอร์:
    - **doc_id**: รหัสเอกสารที่ต้องการแก้ไข
    - **content**: เนื้อหาใหม่
    - **metadata**: ข้อมูลเพิ่มเติม (ไม่บังคับ)
    
    ### ตัวอย่าง Request:
    ```json
    {
        "content": "เนื้อหาที่แก้ไขใหม่",
        "metadata": {
            "source": "แหล่งที่มา",
            "type": "ประเภทเอกสาร"
        }
    }
    ```
    """
)
async def update_document(doc_id: str, update: DocumentUpdate):
    success = vector_db.update_document(doc_id, update.content, update.metadata.dict() if update.metadata else None)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document updated successfully"}

@router.delete(
    "/documents/{doc_id}",
    summary="ลบเอกสาร",
    description="""
    ## ลบเอกสารออกจากระบบ
    
    ### พารามิเตอร์:
    - **doc_id**: รหัสเอกสารที่ต้องการลบ
    
    ### การทำงาน:
    1. ลบข้อมูลเอกสาร
    2. ลบ vector ที่เกี่ยวข้อง
    3. อัพเดตฐานข้อมูล
    """
)
async def delete_document(doc_id: str):
    success = vector_db.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

@router.post(
    "/search",
    summary="ค้นหาเอกสาร",
    description="""
    ## ค้นหาเอกสารด้วย Semantic Search
    
    ### พารามิเตอร์:
    - **query**: ข้อความที่ต้องการค้นหา
    - **k**: จำนวนผลลัพธ์ที่ต้องการ (ค่าเริ่มต้น: 3)
    
    ### ตัวอย่าง Request:
    ```json
    {
        "query": "วิธีการดูแลต้นไม้",
        "k": 5
    }
    ```
    
    ### ผลลัพธ์:
    ```json
    {
        "results": [
            {
                "id": "รหัสเอกสาร",
                "text": "เนื้อหา",
                "metadata": {},
                "score": "คะแนนความเกี่ยวข้อง",
                "relevance": "ค่าความเกี่ยวข้อง"
            }
        ]
    }
    ```
    """
)
async def search_documents(query: SearchQuery):
    results = vector_db.search_for_rag(query.query, query.k)
    return {"results": results}
