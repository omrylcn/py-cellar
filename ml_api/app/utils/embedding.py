from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Union
from prometheus_client import Gauge

# Time series metrics for embedding distances
EMBEDDING_DISTANCE_AVG = Gauge('embedding_distance_avg', 'Average distance between current and average embedding')
EMBEDDING_DISTANCE_MAX = Gauge('embedding_distance_max', 'Maximum distance between current and average embedding')
EMBEDDING_DISTANCE_MIN = Gauge('embedding_distance_min', 'Minimum distance between current and average embedding')

class EmbeddingService:
    def __init__(self, model_name: str = 'all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
        self.average_embedding = None
        self.embedding_count = 0
        self.distance_window = []
        self.window_size = 100  # Adjust this value based on your needs

    def generate_embedding(self, text: Union[str, List[str]]) -> np.ndarray:
        return self.model.encode(text)

    def update_average_embedding(self, new_embedding: np.ndarray):
        if self.average_embedding is None:
            self.average_embedding = new_embedding
        else:
            self.average_embedding = (self.average_embedding * self.embedding_count + new_embedding) / (self.embedding_count + 1)
        self.embedding_count += 1

    def calculate_embedding_distance(self, embedding: np.ndarray) -> float:
        if self.average_embedding is None:
            return 0
        return float(np.linalg.norm(embedding - self.average_embedding))

    def update_distance_metrics(self, distance: float):
        self.distance_window.append(distance)
        if len(self.distance_window) > self.window_size:
            self.distance_window.pop(0)
        
        EMBEDDING_DISTANCE_AVG.set(np.mean(self.distance_window))
        EMBEDDING_DISTANCE_MAX.set(np.max(self.distance_window))
        EMBEDDING_DISTANCE_MIN.set(np.min(self.distance_window))

    def process_text(self, text: str) -> float:
        embedding = self.generate_embedding(text)
        self.update_average_embedding(embedding)
        distance = self.calculate_embedding_distance(embedding)
        self.update_distance_metrics(distance)
        return distance