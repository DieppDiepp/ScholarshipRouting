from transformers import AutoTokenizer, AutoModel
import torch
from typing import List
import numpy as np
from langchain.embeddings.base import Embeddings

class CustomVietnameseEmbeddings(Embeddings):
    """
    Lớp wrapper tùy chỉnh cho 'intfloat/multilingual-e5-large'
    dựa trên code của bạn.
    """
    def __init__(self, model_name: str, max_length: int):
        self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        print(f"Initializing CustomMultiEmbeddings on device: {self.device}")
        
        # Khởi tạo model và tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        self.max_length = max_length
        self.model.eval() # Chuyển sang chế độ inference

    def _get_embedding(self, text: str) -> np.ndarray:
        """
        Hàm lấy embedding (sử dụng mean pooling) cho một chuỗi text.
        """
        inputs = self.tokenizer(
            text, 
            return_tensors="pt", 
            padding=True, 
            truncation=True, 
            max_length=self.max_length
        ).to(self.device)
        
        with torch.no_grad():
            outputs = self.model(**inputs)
        
        # Mean pooling (giống code của bạn)
        token_embeddings = outputs.last_hidden_state
        attention_mask = inputs["attention_mask"]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        embedding = torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
        
        return embedding.squeeze().cpu().numpy()

    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embeds a list of documents."""
        # Có thể tối ưu bằng cách batching, nhưng hiện tại chạy từng cái cho ổn định
        embeddings = []
        for text in texts:
            emb = self._get_embedding(text)
            embeddings.append(emb.tolist())
        return embeddings

    def embed_query(self, text: str) -> List[float]:
        """Embeds a single query."""
        return self.embed_documents([text])[0]