import os
import pandas as pd
from typing import List, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer, CrossEncoder

CSV = "data/category_1_final.csv"
COL = "MBS"
DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES", "") != "" else "cpu"

class RAGService:
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection: str = COL,
        emb_model_name: str = "BAAI/bge-m3",
        reranker_name: str = "BAAI/bge-reranker-large",
    ):
        self.collection = collection
        # 1) Embedding
        self.emb_model = SentenceTransformer(emb_model_name, device=DEVICE)
        self.emb_model.max_seq_length = 512
        self.vdim = self.emb_model.get_sentence_embedding_dimension()

        # 2) Reranker
        self.reranker = CrossEncoder(reranker_name, device=DEVICE)

        # 3) Qdrant
        self.client = QdrantClient(url=qdrant_url)
        self._ensure_collection()

    # ---------- data ----------
    def build_doc(self, row: pd.Series) -> str:
        return (
            f"{row['service_summary']}"
        )

    def load_corpus(self):
        df = pd.read_csv(CSV)
        df.fillna("", inplace=True)
        texts = df.apply(self.build_doc, axis=1).tolist()
        metas = df.to_dict(orient="records")
        return texts, metas

    # ---------- Qdrant ----------
    def _ensure_collection(self):
        try:
            self.client.get_collection(self.collection)
        except Exception:
            self.client.create_collection(
                collection_name=self.collection,
                vectors_config=VectorParams(size=self.vdim, distance=Distance.COSINE)
            )

    def upsert(self, vectors, metas):
        self.client.upsert(
            collection_name=self.collection,
            points=[
                {"id": metas[i]["item_number"], "vector": vec, "payload": metas[i]}
                for i, vec in enumerate(vectors)
            ],
        )

    # ---------- encode/filter/search ----------
    def encode_corpus(self, texts: List[str]):
        return self.emb_model.encode(texts, batch_size=64, normalize_embeddings=True)

    def encode_query(self, q: str):
        q = "Represent this sentence for searching relevant passages: " + q
        return self.emb_model.encode([q], normalize_embeddings=True)[0]

    def prefilter(self, meta, age=None, operator=None, duration=None):
        filter = True
        if age is not None:
            filter &= (meta.get("start_age", 0) <= age <= meta.get("end_age", 200))
        if operator:
            filter &= (operator.lower() in str(meta.get("service_provider","")).lower())
        if duration is not None:
            filter &= (meta.get("start_time", 0) <= duration <= meta.get("end_time", 10000))
        return filter

    def query_text(self, age, operator, duration):
        parts = []
        if operator: parts.append(operator)
        if age is not None: parts.append(f"age {age}")
        if duration is not None: parts.append(f"{duration} minutes")
        return " ".join(parts) if parts else "medical consultation"

    def doc_from_meta(self, m):
        return self.build_doc(m)

    def search(self, query: str, k=50, age=None, operator=None, duration=None, top_n=10):
        qvec = self.encode_query(query)
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=qvec,
            limit=k,
            with_payload=True
        )
        hits = [h for h in hits if self.prefilter(h.payload, age, operator, duration)]
        if not hits:
            return []

        pairs = [(self.query_text(age, operator, duration), self.doc_from_meta(h.payload)) for h in hits]
        scores = self.reranker.predict(pairs).tolist()
        ranked = sorted(zip(hits, scores), key=lambda x: x[1], reverse=True)[:top_n]

        return [
            {"item_number": h.payload["item_number"], "score": round(s, 3), "payload": h.payload}
            for h, s in ranked
        ]

    # ---------- upload data----------
    def buildVectorDb(self):
        texts, metas = self.load_corpus()
        vecs = self.encode_corpus(texts)
        self.upsert(vecs, metas)
        return {"indexed": len(metas)}
