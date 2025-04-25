# vector_db.py
import faiss
import numpy as np
import os
import pickle
from sentence_transformers import SentenceTransformer
import uuid
from pythainlp import word_tokenize
from typing import List, Dict
from Model.document import Document

class VectorDB:
    def __init__(self, model_name='nomic-ai/nomic-embed-text-v1', db_file='vector_db.pkl'):
        self.encoder = SentenceTransformer(model_name,trust_remote_code=True)
        self.dimension = 768  # ขนาดเวกเตอร์ของโมเดล nomic-embed-text-v1
        self.index = faiss.IndexFlatL2(self.dimension)
        self.texts = []
        self.db_file = db_file
        self.ids = []
        self.documents = []
        self.load_db()

    def add_text(self, text: str):
        vector = self.encoder.encode([text])[0]
        self.index.add(np.array([vector]).astype('float32'))
        self.texts.append(text)
        self.ids.append(str(uuid.uuid4()))  # สร้าง UUID ใหม่
        self.save_db()

    def add_document(self, document: Document):
        vector = self.encoder.encode([document.page_content])[0]
        self.index.add(np.array([vector]).astype('float32'))
        self.documents.append(document)
        self.ids.append(str(uuid.uuid4()))
        self.save_db()

    def search_for_rag(self, query: str, k=3) -> List[Dict]:
        """ค้นหาข้อความสำหรับ RAG"""
        query_vector = self.encoder.encode([query])[0]
        D, I = self.index.search(np.array([query_vector]).astype('float32'), k)
        
        results = []
        for i, idx in enumerate(I[0]):
            if idx != -1 and idx < len(self.documents):
                doc = self.documents[idx]
                results.append({
                    'id': self.ids[idx],
                    'text': doc.page_content,
                    'metadata': doc.metadata,
                    'score': float(D[0][i]),
                    'relevance': float(1/(1+D[0][i]))
                })
        return results
    
    def chunk_and_add_text(self, text: str, chunk_size=200):
        """แบ่งข้อความและเพิ่มลง vector store"""
        chunks = self._create_chunks(text, chunk_size)
        for chunk in chunks:
            self.add_text(chunk)

    def _create_chunks(self, text: str, chunk_size: int) -> List[str]:
        """สร้าง chunks จากข้อความ"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size):
            chunk = words[i:i + chunk_size]
            chunks.append(' '.join(chunk))
        return chunks

    def save_db(self):
        with open(self.db_file, 'wb') as f:
            pickle.dump({
                'texts': [doc.page_content for doc in self.documents],
                'documents': self.documents,
                'index': faiss.serialize_index(self.index),
                'ids': self.ids
            }, f)

    def load_db(self):
        if os.path.exists(self.db_file):
            try:
                with open(self.db_file, 'rb') as f:
                    data = pickle.load(f)
                    self.documents = data.get('documents', [])
                    self.texts = [doc.page_content for doc in self.documents]
                    self.index = faiss.deserialize_index(data['index'])
                    self.ids = data.get('ids', [str(uuid.uuid4()) for _ in self.texts])
                    print(f"✅ โหลดฐานข้อมูลแล้ว ({len(self.texts)} เอกสาร)")
            except Exception as e:
                print("❌ โหลดฐานข้อมูลไม่สำเร็จ:", e)

    def delete_document(self, doc_id: str) -> bool:
        """ลบเอกสารด้วย ID"""
        try:
            idx = self.ids.index(doc_id)
            # ลบข้อมูลจากทุกรายการ
            self.ids.pop(idx)
            self.documents.pop(idx)
            
            # สร้าง index ใหม่
            new_index = faiss.IndexFlatL2(self.dimension)
            vectors = [self.encoder.encode([doc.page_content])[0] for doc in self.documents]
            if vectors:  # ถ้ามีเวกเตอร์เหลืออยู่
                new_index.add(np.array(vectors).astype('float32'))
            self.index = new_index
            
            self.save_db()
            return True
        except ValueError:
            return False

    def update_document(self, doc_id: str, new_content: str, new_metadata: Dict = None) -> bool:
        """อัพเดตเอกสารด้วย ID"""
        try:
            idx = self.ids.index(doc_id)
            # อัพเดตเนื้อหาและ metadata
            current_doc = self.documents[idx]
            if new_metadata:
                current_doc.metadata.update(new_metadata)
            current_doc.page_content = new_content
            
            # อัพเดต vector
            vector = self.encoder.encode([new_content])[0]
            new_index = faiss.IndexFlatL2(self.dimension)
            vectors = [self.encoder.encode([doc.page_content])[0] for doc in self.documents]
            new_index.add(np.array(vectors).astype('float32'))
            self.index = new_index
            
            self.save_db()
            return True
        except ValueError:
            return False

    def get_document(self, doc_id: str) -> Dict:
        """ดึงข้อมูลเอกสารด้วย ID"""
        try:
            idx = self.ids.index(doc_id)
            doc = self.documents[idx]
            return {
                'id': doc_id,
                'content': doc.page_content,
                'metadata': doc.metadata
            }
        except ValueError:
            return None

    def list_documents(self, skip: int = 0, limit: int = 10) -> List[Dict]:
        """แสดงรายการเอกสารทั้งหมดแบบแบ่งหน้า"""
        docs = []
        end_idx = min(skip + limit, len(self.documents))
        for i in range(skip, end_idx):
            docs.append({
                'id': self.ids[i],
                'content': self.documents[i].page_content,
                'metadata': self.documents[i].metadata
            })
        return docs
