from typing import Any, List, Optional, Dict
from pydantic import BaseModel, Field
import pandas as pd
from datetime import datetime


class DataDocument(BaseModel):
    """
    单个数据文档，可以是表格或文本
    这种格式可用于存储好document这个变量所需要的各项元数据
    """
    id: str = Field(description="文档唯一标识")
    title: str = Field(description="文档标题")
    content_type: str = Field(description="内容类型：table/text")
    data: Dict[str, Any] = Field(description="实际数据，对于表格是DataFrame的字典表示，对于文本是文本内容")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    source: Optional[str] = Field(default=None, description="数据来源")
    created_at: datetime = Field(default_factory=datetime.now)


class Dossier(BaseModel):
    """
    辩论信息载体，专注于存储和检索数据证明。
    Agent在辩论过程中可以引用dossier中的数据作为论据。
    
    stock_pool: 能够从某个特定的股票集来做为agents的检索挑选范围，比如从akshare的api接口接入固定股票池的数据，后面也能够agent有足够的数据来进行股票的挑选
    """

    # 任务基本信息（上下文）
    mission: str = Field(description="本次选股目的")
    stock_pool: List[str] = Field(description="股票池，股票代码列表")

    # 数据存储
    numerical_documents: List[DataDocument] = Field(default_factory=list, description="数值型文档集合")
    textual_documents: List[DataDocument] = Field(default_factory=list, description="文本型文档集合")

    # 原始数据源引用（方便重新加载）
    data_sources: List[str] = Field(default_factory=list, description="原始数据源路径或URL列表")

    # 索引（用于快速检索）
    stock_data_index: Dict[str, List[str]] = Field(default_factory=dict, description="股票数据索引：股票代码->文档ID列表")
    topic_index: Dict[str, List[str]] = Field(default_factory=dict, description="主题索引：关键词->文档ID列表")

    def add_numerical_document(self, title: str, data: pd.DataFrame,
                              metadata: Optional[Dict[str, Any]] = None,
                              source: Optional[str] = None) -> str:
        """
        添加数值型文档（表格数据）
        将则这个document装到这个dossier的documents里面，且带有元数据可供查询
        """
        doc_id = f"num_{len(self.numerical_documents) + 1:04d}"
        # ── 关键修复在这里 ────────────────────────────────
        if not isinstance(data, pd.DataFrame):
            raise ValueError("data 参数必须是 pandas.DataFrame")

        # 安全处理 index（尤其是 DatetimeIndex）
        df_for_storage = data.copy()
        if isinstance(df_for_storage.index, pd.DatetimeIndex):
            df_for_storage.index = df_for_storage.index.strftime('%Y-%m-%d')

        # 转成 dict（orient="index" 最常用）
        dict_data = df_for_storage.to_dict(orient="index")
        # ───────────────────────────────────────────────────

        doc = DataDocument(
            id=doc_id,
            title=title,
            content_type="table",
            data=dict_data,               # ← 这里一定是 dict，不能是 DataFrame
            metadata=metadata or {},
            source=source
        )
        self.numerical_documents.append(doc)
        self._update_indices(doc)
        return doc_id

    def add_textual_document(self, title: str, text: str,
                            metadata: Optional[Dict[str, Any]] = None,
                            source: Optional[str] = None) -> str:
        """添加文本型文档"""
        doc_id = f"text_{len(self.textual_documents) + 1:04d}"
        doc = DataDocument(
            id=doc_id,
            title=title,
            content_type="text",
            data={"text": text},
            metadata=metadata or {},
            source=source
        )
        self.textual_documents.append(doc)
        self._update_indices(doc)
        return doc_id

    def add_data_source(self, source: str):
        """添加数据源"""
        if source not in self.data_sources:
            self.data_sources.append(source)

    def _update_indices(self, doc: DataDocument):
        """更新索引"""
        # 更新股票索引
        if doc.content_type == "table":
            # 假设表格数据包含股票代码信息
            data = doc.data
            if isinstance(data, dict):
                for key in data.keys():
                    if isinstance(key, str) and key.upper() in self.stock_pool:
                        if key not in self.stock_data_index:
                            self.stock_data_index[key] = []
                        if doc.id not in self.stock_data_index[key]:
                            self.stock_data_index[key].append(doc.id)

        # 更新主题索引（简单基于标题和元数据）
        title_words = doc.title.lower().split()
        for word in title_words:
            if len(word) > 3:  # 忽略短词
                if word not in self.topic_index:
                    self.topic_index[word] = []
                if doc.id not in self.topic_index[word]:
                    self.topic_index[word].append(doc.id)

    def get_document(self, doc_id: str) -> Optional[DataDocument]:
        """根据所有document带的元数据里面的id来获取文档"""
        all_docs = self.numerical_documents + self.textual_documents
        for doc in all_docs:
            if doc.id == doc_id:  
                return doc
        return None

    def get_stock_documents(self, symbol: str) -> List[DataDocument]:
        """获取与特定股票相关的所有文档"""
        doc_ids = self.stock_data_index.get(symbol.upper(), [])
        return [self.get_document(doc_id) for doc_id in doc_ids if self.get_document(doc_id) is not None]

    def search_documents(self, query: str, limit: int = 10) -> List[DataDocument]:
        """搜索文档（简单关键词匹配）"""
        query_words = query.lower().split()
        scored_docs = {}

        for doc in self.numerical_documents + self.textual_documents:
            score = 0
            content_str = str(doc.data).lower() + " " + doc.title.lower()

            for word in query_words:
                if word in content_str:
                    score += 1

            if score > 0:
                scored_docs[doc.id] = (score, doc)

        # 按分数排序
        sorted_docs = sorted(scored_docs.values(), key=lambda x: x[0], reverse=True)
        return [doc for _, doc in sorted_docs[:limit]]

    def get_numerical_data_as_dataframe(self, doc_id: str) -> Optional[pd.DataFrame]:
        """将数值型文档转换为DataFrame"""
        doc = self.get_document(doc_id)
        if doc and doc.content_type == "table":
            try:
                return pd.DataFrame.from_dict(doc.data, orient='index')
            except:
                return None
        return None

    def to_summary(self) -> Dict[str, Any]:
        """生成摘要信息"""
        return {
            "mission": self.mission,
            "stock_pool_size": len(self.stock_pool),
            "numerical_docs_count": len(self.numerical_documents),
            "textual_docs_count": len(self.textual_documents),
            "data_sources_count": len(self.data_sources)
        }