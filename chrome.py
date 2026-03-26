#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
使用 sentence-transformers 生成文本向量
并存储到 ChromaDB 向量数据库
"""

from typing import List, Dict, Any, Optional
from pathlib import Path
import sys

# 导入分片处理器
from markdown_chunker import process_markdown_file, TextChunker

# 导入sentence-transformers
try:
    from sentence_transformers import SentenceTransformer
except ImportError:
    print("❌ 未安装 sentence-transformers")
    print("请运行：pip install sentence-transformers")
    sys.exit(1)

# 导入 chromadb
try:
    import chromadb
    from chromadb.config import Settings
except ImportError:
    print("❌ 未安装 chromadb")
    print("请运行：pip install chromadb")
    sys.exit(1)


class TextEmbedder:
    """文本向量化处理类"""
    
    def __init__(self, model_name: str = 'BAAI/bge-small-zh-v1.5'):
        """
        初始化向量化器
        
        Args:
            model_name: sentence-transformers 模型名称（默认使用中文模型）
        """
        self.model_name: str = model_name
        self.model: Optional[SentenceTransformer] = None
        self.client: Optional[chromadb.Client] = None
        self.collection: Optional[chromadb.api.models.Collection.Collection] = None
        
    def load_model(self) -> bool:
        """
        加载预训练模型
        
        Returns:
            是否加载成功
        """
        try:
            print(f"🤖 正在加载模型：{self.model_name}...")
            print("💡 首次使用需要下载模型，请保持网络连接")
            print("   如果网络不好，可以预先下载模型到本地")
            
            # 设置信任远程代码
            import os
            os.environ['TRANSFORMERS_NO_ADVISORY_WARNINGS'] = '1'
            
            self.model = SentenceTransformer(
                self.model_name,
                trust_remote_code=True
            )
            
            print(f"✅ 模型加载成功")
            return True
        except Exception as e:
            print(f"❌ 模型加载失败：{e}")
            print("\n💡 建议:")
            print("   1. 检查网络连接")
            print("   2. 使用镜像站点：export HF_ENDPOINT=https://hf-mirror.com")
            print("   3. 或改用本地模型路径")
            return False
    
    def generate_embeddings(self, texts: List[str]) -> Optional[List[List[float]]]:
        """
        生成文本向量
        
        Args:
            texts: 文本列表
            
        Returns:
            向量列表，失败返回 None
        """
        if not self.model or not texts:
            return None
        
        try:
            print(f"✏️ 正在生成 {len(texts)} 个文本的向量...")
            embeddings = self.model.encode(texts, convert_to_numpy=True, show_progress_bar=True)
            print(f"✅ 向量生成成功，维度：{embeddings.shape}")
            return embeddings.tolist()
        except Exception as e:
            print(f"❌ 向量生成失败：{e}")
            return None
    
    def setup_chromadb(self, persist_directory: str = "./chroma_db") -> bool:
        """
        设置 ChromaDB
        
        Args:
            persist_directory: 数据持久化目录
            
        Returns:
            是否设置成功
        """
        try:
            print(f"💾 正在初始化 ChromaDB，存储路径：{persist_directory}")
            
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(path=persist_directory)
            
            # 创建或获取集合
            self.collection = self.client.get_or_create_collection(
                name="markdown_chunks",
                metadata={"description": "Markdown 分片向量存储"}
            )
            
            print(f"✅ ChromaDB 初始化成功")
            return True
            
        except Exception as e:
            print(f"❌ ChromaDB 初始化失败：{e}")
            return False
    
    def store_embeddings(
        self,
        chunks: List[str],
        embeddings: List[List[float]],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        存储向量到 ChromaDB
        
        Args:
            chunks: 原始文本分片
            embeddings: 向量列表
            metadata_list: 元数据列表（可选）
            
        Returns:
            是否存储成功
        """
        if not self.collection or not chunks or not embeddings:
            return False
        
        try:
            # 生成 ID 列表
            ids: List[str] = [f"chunk_{i}" for i in range(len(chunks))]
            
            # 如果没有提供元数据，创建默认元数据
            if not metadata_list:
                metadata_list = [{"chunk_index": i, "text_length": len(chunk)} 
                                for i, chunk in enumerate(chunks)]
            
            print(f"💾 正在存储 {len(chunks)} 个向量到 ChromaDB...")
            
            # 添加到集合
            self.collection.add(
                embeddings=embeddings,
                documents=chunks,
                metadatas=metadata_list,
                ids=ids
            )
            
            print(f"✅ 成功存储 {len(chunks)} 个向量")
            return True
            
        except Exception as e:
            print(f"❌ 向量存储失败：{e}")
            return False
    
    def query_similar(
        self,
        query_text: str,
        n_results: int = 3
    ) -> Optional[Dict[str, Any]]:
        """
        查询相似文本
        
        Args:
            query_text: 查询文本
            n_results: 返回结果数量
            
        Returns:
            查询结果字典
        """
        if not self.collection or not self.model:
            return None
        
        try:
            # 生成查询向量
            query_embedding: List[List[float]] = self.model.encode(
                [query_text], 
                convert_to_numpy=True
            ).tolist()
            
            # 查询相似向量
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results,
                include=["documents", "metadatas", "distances"]
            )
            
            return results
            
        except Exception as e:
            print(f"❌ 查询失败：{e}")
            return None


def process_file_and_embed(file_path: str) -> Optional[TextEmbedder]:
    """
    处理文件并生成向量
    
    Args:
        file_path: Markdown 文件路径
        
    Returns:
        TextEmbedder 实例
    """
    print("\n" + "=" * 60)
    print("步骤 1: 读取并分片处理 Markdown 文件")
    print("=" * 60)
    
    # 分片处理
    chunks: Optional[List[str]] = process_markdown_file(
        file_path=file_path,
        chunk_size=300,
        overlap=30,
        mode='size'
    )
    
    if not chunks:
        print("❌ 分片处理失败")
        return None
    
    print(f"\n✅ 获得 {len(chunks)} 个文本分片")
    
    # 创建向量化器
    embedder: TextEmbedder = TextEmbedder(
        model_name='BAAI/bge-small-zh-v1.5'  # 中文优化模型
    )
    
    # 加载模型
    print("\n" + "=" * 60)
    print("步骤 2: 加载 sentence-transformers 模型")
    print("=" * 60)
    if not embedder.load_model():
        return None
    
    # 生成向量
    print("\n" + "=" * 60)
    print("步骤 3: 生成文本向量")
    print("=" * 60)
    embeddings: Optional[List[List[float]]] = embedder.generate_embeddings(chunks)
    
    if not embeddings:
        print("❌ 向量生成失败")
        return None
    
    # 设置 ChromaDB
    print("\n" + "=" * 60)
    print("步骤 4: 初始化 ChromaDB 并存储向量")
    print("=" * 60)
    if not embedder.setup_chromadb(persist_directory="./chroma_db"):
        return None
    
    # 存储向量
    if not embedder.store_embeddings(chunks, embeddings):
        return None
    
    print("\n" + "=" * 60)
    print("✅ 全部完成！文件已向量化并存储到 ChromaDB")
    print("=" * 60)
    
    return embedder


# ============================================================================
# 主程序
# ============================================================================
if __name__ == "__main__":
    print("╔════════════════════════════════════════╗")
    print("║   Markdown 向量化处理器               ║")
    print("║   (sentence-transformers + ChromaDB)  ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 目标文件
    target_file: str = r"C:\Users\sanjin\Desktop\agent\cc.md"
    
    # 检查文件是否存在
    if not Path(target_file).exists():
        print(f"❌ 文件不存在：{target_file}")
        sys.exit(1)
    
    # 处理文件并向量化
    embedder: Optional[TextEmbedder] = process_file_and_embed(target_file)
    
    if embedder:
        # 测试查询功能
        print("\n" + "=" * 60)
        print("步骤 5: 测试相似度查询")
        print("=" * 60)
        
        test_queries: List[str] = [
            "时间流逝",
            "日子过去了",
            "生命痕迹"
        ]
        
        for query in test_queries:
            print(f"\n🔍 查询：'{query}'")
            results = embedder.query_similar(query, n_results=2)
            
            if results and results['documents'] and results['documents'][0]:
                for i, (doc, metadata, distance) in enumerate(
                    zip(results['documents'][0], 
                        results['metadatas'][0], 
                        results['distances'][0]), 
                    1
                ):
                    print(f"\n  结果 {i} (距离：{distance:.4f}):")
                    print(f"  {doc[:100]}...")
            else:
                print("  未找到匹配结果")
        
        print("\n" + "=" * 60)
        print("✅ 所有操作完成！")
        print("=" * 60)
    else:
        print("\n❌ 处理失败")