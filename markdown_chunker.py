#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown 文件分片处理器
使用 typing 模块进行类型标注
支持将长文本按段落或字符数分片
"""

from typing import List, Tuple, Optional, Dict, Any
from pathlib import Path
import re


class TextChunker:
    """文本分片处理类"""
    
    def __init__(self, file_path: str, chunk_size: int = 500, overlap: int = 50):
        """
        初始化分片处理器
        
        Args:
            file_path: 文件路径
            chunk_size: 每个分片的最大字符数
            overlap: 分片之间的重叠字符数
        """
        self.file_path: Path = Path(file_path)
        self.chunk_size: int = chunk_size
        self.overlap: int = overlap
        self.content: str = ""
        self.chunks: List[str] = []
        self.metadata: Dict[str, Any] = {}
        
    def load_file(self) -> bool:
        """
        加载 Markdown 文件
        
        Returns:
            是否加载成功
        """
        try:
            if not self.file_path.exists():
                print(f"❌ 文件不存在：{self.file_path}")
                return False
            
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.content = f.read()
            
            # 提取元数据
            self.metadata = {
                'file_name': self.file_path.name,
                'file_size': len(self.content),
                'total_lines': len(self.content.splitlines()),
                'paragraphs': len(re.findall(r'\n\s*\n', self.content)) + 1
            }
            
            print(f"✅ 成功加载文件：{self.file_path.name}")
            print(f"   文件大小：{self.metadata['file_size']} 字符")
            print(f"   总行数：{self.metadata['total_lines']}")
            print(f"   段落数：{self.metadata['paragraphs']}")
            
            return True
            
        except Exception as e:
            print(f"❌ 加载文件失败：{e}")
            return False
    
    def chunk_by_paragraph(self) -> List[str]:
        """
        按段落分片
        
        Returns:
            段落列表
        """
        if not self.content:
            return []
        
        # 分割段落（保留空行作为分隔符）
        paragraphs: List[str] = re.split(r'\n\s*\n', self.content)
        self.chunks = [p.strip() for p in paragraphs if p.strip()]
        
        print(f"\n📝 按段落分片完成，共 {len(self.chunks)} 个段落")
        return self.chunks
    
    def chunk_by_size(self) -> List[str]:
        """
        按字符数分片（带重叠）
        
        Returns:
            分片列表
        """
        if not self.content:
            return []
        
        self.chunks = []
        start: int = 0
        content_len: int = len(self.content)
        
        while start < content_len:
            # 计算结束位置
            end: int = min(start + self.chunk_size, content_len)
            
            # 如果不是最后一片，尝试在句子边界处分割
            if end < content_len:
                # 查找最近的句子结束符
                sentence_endings: List[int] = [
                    self.content.rfind('。', start, end),
                    self.content.rfind('！', start, end),
                    self.content.rfind('？', start, end),
                    self.content.rfind('\n', start, end)
                ]
                
                # 过滤掉 -1
                valid_endings: List[int] = [i for i in sentence_endings if i != -1]
                
                if valid_endings:
                    end = max(valid_endings) + 1  # 包含标点符号
            
            # 添加分片
            chunk: str = self.content[start:end].strip()
            if chunk:
                self.chunks.append(chunk)
            
            # 更新起始位置（如果有重叠，减去重叠部分）
            start = end - self.overlap if end < content_len else end
        
        print(f"\n✂️ 按字符数分片完成，共 {len(self.chunks)} 个分片")
        print(f"   每片大小：~{self.chunk_size} 字符")
        print(f"   重叠大小：{self.overlap} 字符")
        
        return self.chunks
    
    def get_chunk_stats(self) -> Dict[str, Any]:
        """
        获取分片统计信息
        
        Returns:
            统计信息字典
        """
        if not self.chunks:
            return {'error': '尚未生成分片'}
        
        chunk_lengths: List[int] = [len(c) for c in self.chunks]
        
        stats: Dict[str, Any] = {
            'total_chunks': len(self.chunks),
            'min_length': min(chunk_lengths),
            'max_length': max(chunk_lengths),
            'avg_length': sum(chunk_lengths) / len(self.chunks),
            'total_characters': sum(chunk_lengths)
        }
        
        return stats
    
    def display_chunks(self, show_all: bool = False) -> None:
        """
        显示分片内容
        
        Args:
            show_all: 是否显示所有内容（默认只显示摘要）
        """
        if not self.chunks:
            print("❌ 没有分片数据")
            return
        
        print("\n" + "=" * 60)
        print("分片预览")
        print("=" * 60)
        
        for i, chunk in enumerate(self.chunks, 1):
            print(f"\n【分片 {i}/{len(self.chunks)}】")
            print(f"长度：{len(chunk)} 字符")
            print("-" * 60)
            
            if show_all:
                print(chunk)
            else:
                # 只显示前 100 个字符
                preview: str = chunk[:100].replace('\n', ' ')
                print(f"{preview}...")
                if len(chunk) > 100:
                    print(f"  （还有 {len(chunk) - 100} 字符未显示）")
        
        print("\n" + "=" * 60)


def process_markdown_file(
    file_path: str,
    chunk_size: int = 500,
    overlap: int = 50,
    mode: str = 'size'
) -> Optional[List[str]]:
    """
    处理 Markdown 文件的便捷函数
    
    Args:
        file_path: 文件路径
        chunk_size: 分片大小
        overlap: 重叠大小
        mode: 分片模式 ('size' 或 'paragraph')
    
    Returns:
        分片列表，如果失败则返回 None
    """
    # 创建处理器实例
    chunker: TextChunker = TextChunker(
        file_path=file_path,
        chunk_size=chunk_size,
        overlap=overlap
    )
    
    # 加载文件
    if not chunker.load_file():
        return None
    
    # 选择分片模式
    if mode == 'paragraph':
        chunks: List[str] = chunker.chunk_by_paragraph()
    else:  # default to 'size'
        chunks: List[str] = chunker.chunk_by_size()
    
    # 显示统计信息
    stats: Dict[str, Any] = chunker.get_chunk_stats()
    print("\n📊 分片统计:")
    for key, value in stats.items():
        if isinstance(value, float):
            print(f"   {key}: {value:.2f}")
        else:
            print(f"   {key}: {value}")
    
    # 显示预览
    chunker.display_chunks(show_all=False)
    
    return chunks


# ============================================================================
# 主程序
# ============================================================================
if __name__ == "__main__":
    print("╔════════════════════════════════════════╗")
    print("║   Markdown 文件分片处理器              ║")
    print("║   (使用 typing 类型标注)               ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 示例：处理 cc.md 文件
    target_file: str = r"C:\Users\sanjin\Desktop\agent\cc.md"
    
    print("📁 处理方式 1: 按字符数分片（推荐）")
    print("-" * 40)
    chunks_by_size: Optional[List[str]] = process_markdown_file(
        file_path=target_file,
        chunk_size=300,
        overlap=30,
        mode='size'
    )
    
    print("\n\n")
    
    print("📁 处理方式 2: 按段落分片")
    print("-" * 40)
    chunks_by_para: Optional[List[str]] = process_markdown_file(
        file_path=target_file,
        mode='paragraph'
    )
    
    # 完整内容展示（可选）
    print("\n\n")
    show_full: str = input("\n是否显示完整分片内容？(y/n): ").strip().lower()
    if show_full == 'y':
        chunker_demo: TextChunker = TextChunker(target_file)
        if chunker_demo.load_file():
            chunker_demo.chunk_by_size()
            chunker_demo.display_chunks(show_all=True)
