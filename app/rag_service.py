import os
import pandas as pd
from typing import List, Optional, Any
from qdrant_client import QdrantClient
from qdrant_client.models import VectorParams, Distance
from sentence_transformers import SentenceTransformer, CrossEncoder
from .CRUD import CRUD
from qdrant_client.models import Filter, FieldCondition, Range


# 数据库配置
DB_PATH = "data/medical_categories.db"
COL = "MBS"
DEVICE = "cuda" if os.environ.get("CUDA_VISIBLE_DEVICES", "") != "" else "cpu"

class RAGService:
    def __init__(
        self,
        qdrant_url: str = "http://localhost:6333",
        collection: str = COL,
        emb_model_name: str = "BAAI/bge-m3",
        reranker_name: str = "BAAI/bge-reranker-large",
        db_path: str = DB_PATH,
    ):
        self.collection = collection
        self.db_path = db_path
        self.crud = CRUD(db_path)
        # 1) Embedding
        self.emb_model = SentenceTransformer(emb_model_name, device=DEVICE)
        self.emb_model.max_seq_length = 512
        self.vdim = self.emb_model.get_sentence_embedding_dimension()

        # 2) Reranker
        self.reranker = CrossEncoder(reranker_name, device=DEVICE)

        # 3) Qdrant - 尝试连接，如果失败则标记为不可用
        self.qdrant_available = False
        try:
            self.client = QdrantClient(url=qdrant_url)
            self._ensure_collection()
            self.qdrant_available = True
            print(f"✅ Qdrant连接成功: {qdrant_url}")
        except Exception as e:
            print(f"⚠️  Qdrant连接失败: {e}")
            print("RAG搜索功能将不可用，但其他API功能正常")
            self.qdrant_available = False

    # ---------- data ----------
    def build_doc(self, row: pd.Series) -> str:
        return (
            f"{row['service_summary']}"
        )

    def load_corpus(self, category_id: str = "1"):
        """
        从SQLite数据库加载语料库数据
        默认加载category_1的数据
        """
        try:
            # 使用CRUD从数据库获取数据
            df = self.crud.get_category_dataframe(category_id)
            
            if df.empty:
                raise Exception(f"分类 {category_id} 没有数据")
            
            # 处理缺失值
            df.fillna("", inplace=True)
            
            # 生成文本和元数据
            texts = df.apply(self.build_doc, axis=1).tolist()
            metas = df.to_dict(orient="records")
            
            print(f"✅ 成功加载分类 {category_id} 的数据，共 {len(metas)} 条记录")
            return texts, metas
            
        except Exception as e:
            print(f"⚠️  加载语料库失败: {e}")
            # 返回空数据
            return [], []

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

    def search(self, query: str, k=50, age=None, operator=None, duration=None,location=None, top_n=10):
        if not self.qdrant_available:
            return {"error": "Qdrant不可用，搜索被跳过"}
        print(f"🔎 查询语句：{query},")
        qvec = self.encode_query(query)
        # 构造 filter
        conditions = []
        if age is not None:
            conditions.append(FieldCondition(
                key="start_age",
                range=Range(lte=age)
            ))
            conditions.append(FieldCondition(
                key="end_age",
                range=Range(gte=age)
            ))
        if operator:
            conditions.append(FieldCondition(
                key="service_provider",
                match={"text": operator}
            ))
        if duration is not None:
            conditions.append(FieldCondition(
                key="start_time",
                range=Range(lte=duration)
            ))
            conditions.append(FieldCondition(
                key="end_time",
                range=Range(gte=duration)
            ))
        if location is not None:
            conditions.append(FieldCondition(
                key="location",
                match={"text": location}
            ))

        search_filter = Filter(must=conditions) if conditions else None
        hits = self.client.search(
            collection_name=self.collection,
            query_vector=qvec,
            limit=k,
            with_payload=True,
            query_filter=search_filter 
        )
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
    def buildVectorDb(self, category_id: str = "1"):
        """
        构建向量数据库
        支持指定分类ID，默认使用category_1
        """
        if not self.qdrant_available:
            return {"error": "Qdrant服务不可用，无法构建向量数据库"}
        
        try:
            print(f"🔄 开始构建分类 {category_id} 的向量数据库...")
            
            # 加载指定分类的数据
            texts, metas = self.load_corpus(category_id)
            
            if not texts or not metas:
                return {"error": f"分类 {category_id} 没有数据可处理"}
        
            # 编码文本为向量
            vecs = self.encode_corpus(texts)
            
            print(f"🔢 向量编码完成，开始上传到Qdrant...")
            
            # 上传到Qdrant
            self.upsert(vecs, metas)
            
            print(f"✅ 向量数据库构建完成！共处理 {len(metas)} 条记录")
            return {
                "success": True,
                "category_id": category_id,
                "indexed": len(metas),
                "message": f"成功构建分类 {category_id} 的向量数据库"
            }
            
        except Exception as e:
            error_msg = f"构建向量数据库失败: {str(e)}"
            print(f"❌ {error_msg}")
            return {"error": error_msg}
