#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ChromaDB 向量数据库管理
导入、查询和管理文本向量数据
"""

from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import sys

# 导入chromadb
try:
    import chromadb
    # print(f"OK chromadb 版本：{chromadb.__version__}")
except ImportError as e:
    print(f"Error: 导入chromadb 失败：{e}")
    print("请运行：pip install chromadb")
    sys.exit(1)


class ChromaDBManager:
    """ChromaDB 向量数据库管理类"""
    
    def __init__(self, persist_directory: str = "./chroma_db"):
        """
        初始化 ChromaDB
        
        Args:
            persist_directory: 数据持久化目录
        """
        self.persist_directory: str = persist_directory
        self.client: Optional[chromadb.Client] = None
        self.collection = None  # type: Optional[Any]
        self.collection_name: str = "markdown_chunks"
        
    def connect(self) -> bool:
        """
        连接到 ChromaDB（加载已存在的数据）
        
        Returns:
            是否连接成功
        """
        try:
            print(f"💾 正在连接到 ChromaDB，路径：{self.persist_directory}")
            
            # 创建持久化客户端
            self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            # 获取现有的集合
            try:
                self.collection = self.client.get_collection(self.collection_name)
                count = self.collection.count()
                print(f"✅ 成功连接到集合：{self.collection_name}")
                print(f"   当前向量数量：{count}")
                return True
            except Exception as e:
                print(f"⚠️  集合不存在：{e}")
                print("   请先运行 chrome.py 生成向量数据")
                return False
                
        except Exception as e:
            print(f"❌ 连接失败：{e}")
            return False
    
    def create_collection(self, collection_name: Optional[str] = None) -> bool:
        """
        创建新的集合
        
        Args:
            collection_name: 集合名称
            
        Returns:
            是否创建成功
        """
        try:
            if not self.client:
                self.client = chromadb.PersistentClient(path=self.persist_directory)
            
            name = collection_name or self.collection_name
            
            print(f"📦 正在创建集合：{name}")
            self.collection = self.client.create_collection(
                name=name,
                metadata={"description": "Markdown 分片向量存储"}
            )
            
            print(f"✅ 集合创建成功")
            return True
            
        except Exception as e:
            print(f"❌ 创建集合失败：{e}")
            return False
    
    def add_vectors(
        self,
        embeddings: List[List[float]],
        documents: List[str],
        ids: Optional[List[str]] = None,
        metadatas: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """
        添加向量到数据库
        
        Args:
            embeddings: 向量列表
            documents: 原始文本列表
            ids: ID 列表
            metadatas: 元数据列表
            
        Returns:
            是否添加成功
        """
        if not self.collection:
            print("❌ 未连接到集合")
            return False
        
        if not ids:
            ids = [f"vector_{i}" for i in range(len(embeddings))]
        
        if not metadatas:
            metadatas = [{"index": i, "length": len(doc)} 
                        for i, doc in enumerate(documents)]
        
        try:
            print(f"💾 正在添加 {len(embeddings)} 个向量...")
            
            self.collection.add(
                embeddings=embeddings,
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            
            print(f"✅ 成功添加 {len(embeddings)} 个向量")
            return True
            
        except Exception as e:
            print(f"❌ 添加向量失败：{e}")
            return False
    
    def query(
        self,
        query_embeddings: Optional[List[List[float]]] = None,
        query_texts: Optional[List[str]] = None,
        n_results: int = 3,
        where: Optional[Dict[str, Any]] = None,
        model_name: str = 'BAAI/bge-small-zh-v1.5'
    ) -> Optional[Dict[str, Any]]:
        """
        查询相似向量
        
        Args:
            query_embeddings: 查询向量列表
            query_texts: 查询文本列表（需要模型转换为向量）
            n_results: 返回结果数量
            where: 过滤条件
            model_name: 用于生成查询向量的模型名称
            
        Returns:
            查询结果字典
        """
        if not self.collection:
            print("❌ 未连接到集合")
            return None
        
        try:
            # 如果提供的是文本而不是向量，需要先生成向量
            if query_texts and not query_embeddings:
                try:
                    from sentence_transformers import SentenceTransformer
                    model = SentenceTransformer(model_name, trust_remote_code=True)
                    query_embeddings = model.encode(query_texts, convert_to_numpy=True).tolist()
                except Exception as e:
                    print(f"❌ 生成查询向量失败：{e}")
                    return None
            
            results = self.collection.query(
                query_embeddings=query_embeddings,
                n_results=n_results,
                where=where,
                include=["documents", "metadatas", "distances"]
            )
            
            return results
            
        except Exception as e:
            print(f"❌ 查询失败：{e}")
            return None
    
    def get_all(self) -> Optional[Dict[str, Any]]:
        """
        获取所有向量数据
        
        Returns:
            所有数据字典
        """
        if not self.collection:
            print("❌ 未连接到集合")
            return None
        
        try:
            print(f"📊 正在获取所有向量数据...")
            
            all_data = self.collection.get(
                include=["documents", "metadatas", "embeddings"]
            )
            
            count = len(all_data['ids']) if all_data['ids'] else 0
            print(f"✅ 共获取 {count} 个向量")
            
            return all_data
            
        except Exception as e:
            print(f"❌ 获取数据失败：{e}")
            return None
    
    def delete_by_ids(self, ids: List[str]) -> bool:
        """
        根据 ID 删除向量
        
        Args:
            ids: 要删除的 ID 列表
            
        Returns:
            是否删除成功
        """
        if not self.collection:
            print("❌ 未连接到集合")
            return False
        
        try:
            print(f"🗑️  正在删除 {len(ids)} 个向量...")
            
            self.collection.delete(ids=ids)
            
            print(f"✅ 成功删除 {len(ids)} 个向量")
            return True
            
        except Exception as e:
            print(f"❌ 删除失败：{e}")
            return False
    
    def update_vector(
        self,
        vector_id: str,
        embedding: Optional[List[List[float]]] = None,
        document: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        更新向量数据
        
        Args:
            vector_id: 向量 ID
            embedding: 新向量
            document: 新文本
            metadata: 新元数据
            
        Returns:
            是否更新成功
        """
        if not self.collection:
            print("❌ 未连接到集合")
            return False
        
        try:
            print(f"🔄 正在更新向量：{vector_id}")
            
            self.collection.update(
                ids=[vector_id],
                embeddings=embedding,
                documents=document,
                metadatas=metadata
            )
            
            print(f"✅ 更新成功")
            return True
            
        except Exception as e:
            print(f"❌ 更新失败：{e}")
            return False
    
    def display_stats(self) -> None:
        """显示数据库统计信息"""
        if not self.collection:
            print("❌ 未连接到集合")
            return
        
        try:
            count = self.collection.count()
            
            print("\n" + "=" * 60)
            print("📊 ChromaDB 统计信息")
            print("=" * 60)
            print(f"集合名称：{self.collection_name}")
            print(f"向量总数：{count}")
            print(f"存储路径：{Path(self.persist_directory).absolute()}")
            print("=" * 60)
            
        except Exception as e:
            print(f"❌ 获取统计信息失败：{e}")


def import_from_chrome_py():
    """
    从 chrome.py 导入已生成的向量数据
    
    Returns:
        导入的向量数据
    """
    print("\n" + "=" * 60)
    print("从 chrome.py 导入向量数据")
    print("=" * 60)
    
    # 尝试从 chrome 模块导入
    try:
        import chrome
        
        # 重新处理文件并获取数据
        target_file: str = r"C:\Users\sanjin\Desktop\agent\cc.md"
        
        if not Path(target_file).exists():
            print(f"❌ 文件不存在：{target_file}")
            return None
        
        # 使用 markdown_chunker 分片
        from markdown_chunker import process_markdown_file
        
        chunks = process_markdown_file(
            file_path=target_file,
            chunk_size=300,
            overlap=30,
            mode='size'
        )
        
        if not chunks:
            return None
        
        # 使用 sentence-transformers 生成向量
        embedder = chrome.TextEmbedder(model_name='BAAI/bge-small-zh-v1.5')
        
        if not embedder.load_model():
            return None
        
        embeddings = embedder.generate_embeddings(chunks)
        
        if not embeddings:
            return None
        
        # 准备元数据
        metadatas = [
            {
                "chunk_index": i,
                "text_length": len(chunk),
                "source_file": "cc.md",
                "preview": chunk[:50] + "..."
            }
            for i, chunk in enumerate(chunks)
        ]
        
        print(f"\n✅ 准备好 {len(chunks)} 个向量数据")
        
        return {
            'embeddings': embeddings,
            'documents': chunks,
            'metadatas': metadatas,
            'ids': [f"chunk_{i}" for i in range(len(chunks))]
        }
        
    except Exception as e:
        print(f"❌ 导入失败：{e}")
        return None


# ============================================================================
# 主程序
# ============================================================================
if __name__ == "__main__":
    print("╔════════════════════════════════════════╗")
    print("║   ChromaDB 向量数据库管理             ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 创建管理器
    db_manager: ChromaDBManager = ChromaDBManager(
        persist_directory="./chroma_db"
    )
    
    # 连接到现有数据库
    if not db_manager.connect():
        print("\n⚠️  无法连接到现有数据库")
        print("选项:")
        print("1. 先运行 chrome.py 生成向量数据")
        print("2. 或者现在创建新集合并导入数据")
        
        choice = input("\n请选择 (1/2): ").strip()
        
        if choice == "2":
            # 创建新集合并导入数据
            if not db_manager.create_collection():
                sys.exit(1)
            
            # 导入数据
            data = import_from_chrome_py()
            
            if data:
                db_manager.add_vectors(
                    embeddings=data['embeddings'],
                    documents=data['documents'],
                    ids=data['ids'],
                    metadatas=data['metadatas']
                )
        else:
            print("\n请先运行：python chrome.py")
            sys.exit(0)
    
    # 显示统计信息
    db_manager.display_stats()
    
    # 获取并展示所有数据
    print("\n" + "=" * 60)
    print("查看所有向量数据")
    print("=" * 60)
    
    all_data = db_manager.get_all()
    
    if all_data and all_data['ids']:
        print(f"\n找到 {len(all_data['ids'])} 个向量:\n")
        
        for i, (doc_id, doc, metadata) in enumerate(
            zip(all_data['ids'], all_data['documents'], all_data['metadatas']), 
            1
        ):
            print(f"【向量 {i}】")
            print(f"  ID: {doc_id}")
            print(f"  长度：{metadata.get('text_length', len(doc))} 字符")
            print(f"  内容：{doc[:80]}...")
            print(f"  元数据：{metadata}")
            print()
    
    # 测试相似度查询
    print("\n" + "=" * 60)
    print("测试相似度查询（使用 query_texts）")
    print("=" * 60)
    
    test_queries: List[str] = [
        "时间过得很快",
        "珍惜生命",
        "回忆过去"
    ]
    
    for query in test_queries:
        print(f"\n🔍 查询：'{query}'")
        results = db_manager.query(query_texts=[query], n_results=2)
        
        if results and results['documents'] and results['documents'][0]:
            for i, (doc, distance, metadata) in enumerate(
                zip(results['documents'][0], 
                    results['distances'][0],
                    results['metadatas'][0]), 
                1
            ):
                print(f"\n  结果 {i} (距离：{distance:.4f}):")
                print(f"  {doc[:100]}...")
        else:
            print("  未找到匹配结果")
    
    # 交互式查询
    print("\n" + "=" * 60)
    print("交互式查询模式")
    print("=" * 60)
    print("提示：输入 'exit' 或 'quit' 退出\n")
    
    while True:
        user_query = input("请输入查询内容：").strip()
        
        if user_query.lower() in ['exit', 'quit']:
            print("\n👋 再见！")
            break
        
        if not user_query:
            continue
        
        results = db_manager.query(query_texts=[user_query], n_results=3)
        
        if results and results['documents'][0]:
            print(f"\n找到 {len(results['documents'][0])} 个相关结果:\n")
            
            for i, (doc, distance) in enumerate(
                zip(results['documents'][0], results['distances'][0]), 
                1
            ):
                print(f"{i}. {doc}\n")
        else:
            print("\n未找到相关结果\n")
    
    print("\n✅ 所有操作完成！")