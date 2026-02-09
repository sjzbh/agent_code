import json
import os
import hashlib
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path

from config.settings import settings


class MemoryItem:
    def __init__(self, content: str, metadata: Optional[Dict[str, Any]] = None):
        self.content = content
        self.metadata = metadata or {}
        self.id = self._generate_id(content)
        self.created_at = datetime.now().isoformat()
        self.embedding: Optional[List[float]] = None
    
    def _generate_id(self, content: str) -> str:
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "created_at": self.created_at,
            "embedding": self.embedding
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MemoryItem":
        item = cls(data["content"], data.get("metadata"))
        item.id = data["id"]
        item.created_at = data.get("created_at", datetime.now().isoformat())
        item.embedding = data.get("embedding")
        return item


class SimpleVectorStore:
    def __init__(self, dimension: int = 1536):
        self.dimension = dimension
        self.vectors: List[List[float]] = []
        self.items: List[MemoryItem] = []
    
    def add(self, item: MemoryItem, embedding: List[float]):
        if len(embedding) != self.dimension:
            raise ValueError(f"Embedding dimension mismatch: expected {self.dimension}, got {len(embedding)}")
        
        item.embedding = embedding
        self.vectors.append(embedding)
        self.items.append(item)
    
    def search(self, query_embedding: List[float], k: int = 5, 
               threshold: float = 0.0) -> List[tuple]:
        if not self.vectors:
            return []
        
        similarities = []
        for i, vec in enumerate(self.vectors):
            sim = self._cosine_similarity(query_embedding, vec)
            if sim >= threshold:
                similarities.append((self.items[i], sim))
        
        similarities.sort(key=lambda x: x[1], reverse=True)
        return similarities[:k]
    
    def _cosine_similarity(self, a: List[float], b: List[float]) -> float:
        dot_product = sum(x * y for x, y in zip(a, b))
        norm_a = sum(x * x for x in a) ** 0.5
        norm_b = sum(x * x for x in b) ** 0.5
        
        if norm_a == 0 or norm_b == 0:
            return 0.0
        
        return dot_product / (norm_a * norm_b)
    
    def save(self, path: str):
        data = {
            "dimension": self.dimension,
            "items": [item.to_dict() for item in self.items]
        }
        
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load(self, path: str):
        if not os.path.exists(path):
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        self.dimension = data.get("dimension", 1536)
        self.items = [MemoryItem.from_dict(item) for item in data.get("items", [])]
        self.vectors = [item.embedding for item in self.items if item.embedding]


class Memory:
    def __init__(self, storage_path: Optional[str] = None):
        self.storage_path = storage_path or settings.memory.vector_db_path
        self.similarity_threshold = settings.memory.similarity_threshold
        self.max_items = settings.memory.max_memory_items
        
        self.store = SimpleVectorStore()
        self._embedding_client = None
        self._load()
    
    def _get_embedding_client(self):
        if self._embedding_client is not None:
            return self._embedding_client
        
        try:
            from openai import OpenAI
            self._embedding_client = OpenAI(
                api_key=settings.llm.api_key,
                base_url=settings.llm.base_url
            )
            return self._embedding_client
        except Exception:
            return None
    
    def _get_embedding(self, text: str) -> List[float]:
        client = self._get_embedding_client()
        
        if client is None:
            return self._simple_embedding(text)
        
        try:
            response = client.embeddings.create(
                model=settings.memory.embedding_model,
                input=text[:8000]
            )
            return response.data[0].embedding
        except Exception:
            return self._simple_embedding(text)
    
    def _simple_embedding(self, text: str) -> List[float]:
        hash_values = []
        for i in range(0, min(len(text), 1536)):
            char_hash = hash(text[i:i+1]) % 1000 / 1000
            hash_values.append(char_hash)
        
        while len(hash_values) < 1536:
            hash_values.append(0.0)
        
        return hash_values[:1536]
    
    def add(self, content: str, metadata: Optional[Dict[str, Any]] = None) -> str:
        item = MemoryItem(content, metadata)
        embedding = self._get_embedding(content)
        
        self.store.add(item, embedding)
        
        if len(self.store.items) > self.max_items:
            self.store.items = self.store.items[-self.max_items:]
            self.store.vectors = self.store.vectors[-self.max_items:]
        
        self._save()
        
        return item.id
    
    def search(self, query: str, k: int = 5) -> List[Dict[str, Any]]:
        query_embedding = self._get_embedding(query)
        
        results = self.store.search(
            query_embedding, 
            k=k, 
            threshold=self.similarity_threshold
        )
        
        return [
            {
                "content": item.content,
                "metadata": item.metadata,
                "similarity": score,
                "id": item.id
            }
            for item, score in results
        ]
    
    def add_experience(self, task: str, result: str, success: bool):
        content = f"Task: {task}\nResult: {result}\nSuccess: {success}"
        metadata = {
            "type": "experience",
            "task": task,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.add(content, metadata)
    
    def add_knowledge(self, topic: str, content: str, source: str = "user"):
        metadata = {
            "type": "knowledge",
            "topic": topic,
            "source": source,
            "timestamp": datetime.now().isoformat()
        }
        
        return self.add(content, metadata)
    
    def get_relevant_experiences(self, task: str, k: int = 3) -> List[str]:
        results = self.search(task, k=k)
        
        experiences = []
        for r in results:
            if r.get("metadata", {}).get("type") == "experience":
                experiences.append(r["content"])
        
        return experiences
    
    def _save(self):
        if self.storage_path:
            self.store.save(self.storage_path)
    
    def _load(self):
        if self.storage_path and os.path.exists(self.storage_path):
            self.store.load(self.storage_path)
    
    def clear(self):
        self.store = SimpleVectorStore()
        self._save()
    
    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_items": len(self.store.items),
            "dimension": self.store.dimension,
            "storage_path": self.storage_path
        }


memory = Memory()
