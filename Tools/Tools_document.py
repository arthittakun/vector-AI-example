from dataclasses import dataclass, asdict
from typing import Dict, Any

@dataclass
class Document:
    page_content: str
    metadata: Dict[str, Any]
    
    def to_dict(self):
        return {
            'content': self.page_content,
            'metadata': self.metadata
        }
    
    @classmethod
    def from_dict(cls, data: Dict):
        return cls(
            page_content=data['content'],
            metadata=data['metadata']
        )
