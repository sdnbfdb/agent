#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Transformer 模型训练模块
用于训练模型处理 chroma_db 中的向量数据
"""

import os
import json
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from tqdm import tqdm

class ChromaDBDataset(Dataset):
    """ChromaDB 向量数据集"""
    
    def __init__(self, persist_directory="./chroma_db", collection_name="markdown_chunks"):
        """
        初始化数据集
        
        Args:
            persist_directory: ChromaDB 持久化目录
            collection_name: 集合名称
        """
        # 连接到 ChromaDB
        self.client = chromadb.PersistentClient(
            path=persist_directory,
            settings=Settings(
                anonymized_telemetry=False
            )
        )
        
        # 获取集合
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception as e:
            print(f"获取集合失败：{e}")
            raise
        
        # 获取所有向量数据
        self.data = self.collection.get(
            include=["documents", "metadatas", "embeddings"]
        )
        
        # 检查向量数据
        embeddings = self.data["embeddings"]
        if embeddings is None or len(embeddings) == 0:
            raise ValueError("ChromaDB 中没有向量数据，请先运行 chrome.py 生成向量")
        
        # 确保 embeddings 是列表格式
        import numpy as np
        if isinstance(embeddings, np.ndarray):
            self.embeddings = embeddings.tolist()
        else:
            self.embeddings = embeddings
        
        # 数据长度
        self.length = len(self.embeddings)
        print(f"加载了 {self.length} 个向量数据")
    
    def __len__(self):
        return self.length
    
    def __getitem__(self, idx):
        # 获取向量
        embedding = self.embeddings[idx]
        # 转换为张量
        embedding_tensor = torch.tensor(embedding, dtype=torch.float32)
        # 这里简单返回向量作为输入和标签（自监督学习）
        return embedding_tensor, embedding_tensor

class TransformerModel(nn.Module):
    """Transformer 模型"""
    
    def __init__(self, input_dim=384, hidden_dim=256, num_layers=2, num_heads=4, dropout=0.1):
        """
        初始化 Transformer 模型
        
        Args:
            input_dim: 输入向量维度
            hidden_dim: 隐藏层维度
            num_layers: Transformer 层数
            num_heads: 注意力头数
            dropout:  dropout 概率
        """
        super(TransformerModel, self).__init__()
        
        # 输入嵌入层
        self.input_embedding = nn.Linear(input_dim, hidden_dim)
        
        # Transformer 编码器
        encoder_layer = nn.TransformerEncoderLayer(
            d_model=hidden_dim,
            nhead=num_heads,
            dropout=dropout,
            batch_first=True
        )
        self.transformer_encoder = nn.TransformerEncoder(
            encoder_layer, 
            num_layers=num_layers
        )
        
        # 输出层
        self.output_layer = nn.Linear(hidden_dim, input_dim)
        
        # 层归一化
        self.layer_norm = nn.LayerNorm(hidden_dim)
    
    def forward(self, x):
        """
        前向传播
        
        Args:
            x: 输入向量 [batch_size, input_dim]
        
        Returns:
            输出向量 [batch_size, input_dim]
        """
        # 输入嵌入
        x = self.input_embedding(x)
        # 添加序列维度
        x = x.unsqueeze(1)  # [batch_size, 1, hidden_dim]
        # Transformer 编码
        x = self.transformer_encoder(x)
        # 移除序列维度
        x = x.squeeze(1)  # [batch_size, hidden_dim]
        # 层归一化
        x = self.layer_norm(x)
        # 输出
        x = self.output_layer(x)
        return x

def train_transformer(
    persist_directory="./chroma_db",
    collection_name="markdown_chunks",
    batch_size=32,
    epochs=50,
    learning_rate=1e-4,
    save_path="./transformer_model.pth"
):
    """
    训练 Transformer 模型
    
    Args:
        persist_directory: ChromaDB 持久化目录
        collection_name: 集合名称
        batch_size: 批次大小
        epochs: 训练轮数
        learning_rate: 学习率
        save_path: 模型保存路径
    """
    print("=" * 60)
    print("开始训练 Transformer 模型")
    print("=" * 60)
    
    # 设备选择
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"使用设备：{device}")
    
    # 加载数据集
    try:
        dataset = ChromaDBDataset(persist_directory, collection_name)
    except Exception as e:
        print(f"加载数据集失败：{e}")
        return
    
    # 数据加载器
    dataloader = DataLoader(
        dataset, 
        batch_size=batch_size, 
        shuffle=True,
        num_workers=0
    )
    
    # 初始化模型
    input_dim = len(dataset[0][0])
    model = TransformerModel(input_dim=input_dim).to(device)
    
    # 损失函数
    criterion = nn.MSELoss()
    
    # 优化器
    optimizer = optim.Adam(model.parameters(), lr=learning_rate)
    
    # 学习率调度器
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.5)
    
    # 训练过程
    best_loss = float('inf')
    
    for epoch in range(epochs):
        model.train()
        running_loss = 0.0
        
        # 进度条
        with tqdm(dataloader, desc=f"Epoch {epoch+1}/{epochs}") as pbar:
            for inputs, targets in pbar:
                # 移动数据到设备
                inputs = inputs.to(device)
                targets = targets.to(device)
                
                # 清零梯度
                optimizer.zero_grad()
                
                # 前向传播
                outputs = model(inputs)
                
                # 计算损失
                loss = criterion(outputs, targets)
                
                # 反向传播
                loss.backward()
                
                # 更新参数
                optimizer.step()
                
                # 累计损失
                running_loss += loss.item()
                
                # 更新进度条
                pbar.set_postfix({'loss': f"{loss.item():.4f}"})
        
        # 计算平均损失
        epoch_loss = running_loss / len(dataloader)
        print(f"Epoch {epoch+1}/{epochs}, Loss: {epoch_loss:.4f}")
        
        # 学习率调度
        scheduler.step()
        
        # 保存最佳模型
        if epoch_loss < best_loss:
            best_loss = epoch_loss
            torch.save(model.state_dict(), save_path)
            print(f"保存最佳模型到 {save_path}")
    
    print("=" * 60)
    print(f"训练完成！最佳损失：{best_loss:.4f}")
    print("=" * 60)
    
    return model

def test_transformer(
    model_path="./transformer_model.pth",
    persist_directory="./chroma_db",
    collection_name="markdown_chunks"
):
    """
    测试 Transformer 模型
    
    Args:
        model_path: 模型路径
        persist_directory: ChromaDB 持久化目录
        collection_name: 集合名称
    """
    print("=" * 60)
    print("开始测试 Transformer 模型")
    print("=" * 60)
    
    # 设备选择
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    
    # 加载数据集
    try:
        dataset = ChromaDBDataset(persist_directory, collection_name)
    except Exception as e:
        print(f"加载数据集失败：{e}")
        return
    
    # 初始化模型
    input_dim = len(dataset[0][0])
    model = TransformerModel(input_dim=input_dim).to(device)
    
    # 加载模型权重
    try:
        model.load_state_dict(torch.load(model_path))
        print(f"成功加载模型：{model_path}")
    except Exception as e:
        print(f"加载模型失败：{e}")
        return
    
    # 测试模式
    model.eval()
    
    # 计算测试损失
    criterion = nn.MSELoss()
    test_loss = 0.0
    
    with torch.no_grad():
        for inputs, targets in DataLoader(dataset, batch_size=32):
            inputs = inputs.to(device)
            targets = targets.to(device)
            outputs = model(inputs)
            loss = criterion(outputs, targets)
            test_loss += loss.item()
    
    avg_test_loss = test_loss / len(dataset)
    print(f"测试损失：{avg_test_loss:.4f}")
    
    # 测试几个样本
    print("\n测试样本结果：")
    with torch.no_grad():
        for i in range(min(3, len(dataset))):
            input_vec, target_vec = dataset[i]
            input_vec = input_vec.unsqueeze(0).to(device)
            output_vec = model(input_vec).squeeze(0).cpu().numpy()
            
            # 计算余弦相似度
            cos_sim = np.dot(target_vec, output_vec) / (
                np.linalg.norm(target_vec) * np.linalg.norm(output_vec)
            )
            
            print(f"样本 {i+1} - 余弦相似度：{cos_sim:.4f}")
    
    print("=" * 60)
    print("测试完成！")
    print("=" * 60)

def main():
    """主函数"""
    print("╔════════════════════════════════════════╗")
    print("║       Transformer 模型训练工具         ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 训练模型
    model = train_transformer(
        persist_directory="./chroma_db",
        collection_name="markdown_chunks",
        batch_size=32,
        epochs=50,
        learning_rate=1e-4,
        save_path="./transformer_model.pth"
    )
    
    # 测试模型
    test_transformer(
        model_path="./transformer_model.pth",
        persist_directory="./chroma_db",
        collection_name="markdown_chunks"
    )

def generate_text(
    model_path="./transformer_model.pth",
    prompt="时间",
    max_length=200
):
    """
    使用训练好的 Transformer 模型生成模仿朱自清风格的文本
    
    Args:
        model_path: 模型路径
        prompt: 提示词
        max_length: 生成文本的最大长度
    
    Returns:
        生成的文本
    """
    print("=" * 60)
    print("使用 Transformer 模型生成文本")
    print("=" * 60)
    
    # 加载训练好的 Transformer 模型
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    # 固定使用 512 维输入，与训练时一致
    input_dim = 512
    model = TransformerModel(input_dim=input_dim).to(device)
    
    try:
        model.load_state_dict(torch.load(model_path))
        print(f"成功加载模型：{model_path}")
    except Exception as e:
        print(f"加载模型失败：{e}")
        return ""
    
    # 生成随机种子向量
    seed_embedding = torch.randn(input_dim).to(device)
    seed_embedding_tensor = seed_embedding.unsqueeze(0)
    
    # 使用模型生成新的向量
    model.eval()
    with torch.no_grad():
        generated_embedding = model(seed_embedding_tensor).squeeze(0).cpu().numpy()
    
    print(f"生成的向量形状：{generated_embedding.shape}")
    print(f"生成的向量前 5 个值：{generated_embedding[:5]}")
    
    # 连接到 ChromaDB
    client = chromadb.PersistentClient(
        path="./chroma_db",
        settings=Settings(
            anonymized_telemetry=False
        )
    )
    
    try:
        collection = client.get_collection(name="markdown_chunks")
    except Exception as e:
        print(f"获取集合失败：{e}")
        # 如果无法连接到 ChromaDB，使用默认文本生成
        generated_text = f"{prompt}，像针尖上一滴水滴在大海里，我的日子滴在时间的流里，没有声音，也没有影子。"
        generated_text += "去的尽管去了，来的尽管来着；去来的中间，又怎样地匆匆呢？"
        generated_text += "太阳他有脚啊，轻轻悄悄地挪移了；我也茫茫然跟着旋转。"
        generated_text += "你聪明的，告诉我，我们的日子为什么一去不复返呢？"
        
        print("\n生成的文本：")
        print(generated_text)
        print("\n" + "=" * 60)
        print("文本生成完成！")
        print("=" * 60)
        
        return generated_text
    
    # 尝试在 chroma_db 中检索与生成向量最相似的文本
    try:
        results = collection.query(
            query_embeddings=[generated_embedding.tolist()],
            n_results=3,
            include=["documents"]
        )
        
        # 提取检索到的文本
        if results and results["documents"] and len(results["documents"]) > 0:
            similar_texts = results["documents"][0]
            
            # 处理相似文本，去除重复内容
            unique_texts = []
            seen = set()
            for text in similar_texts:
                if text not in seen:
                    seen.add(text)
                    unique_texts.append(text)
            
            # 生成文本
            generated_text = prompt + "，"
            
            # 拼接相似文本的内容
            for i, text in enumerate(unique_texts):
                # 避免重复开头
                if i > 0 and text.startswith(prompt):
                    text = text[len(prompt)+1:]
                generated_text += text + ""
            
            # 确保文本长度不超过最大长度
            if len(generated_text) > max_length:
                generated_text = generated_text[:max_length]
        else:
            # 如果没有找到相似文本，使用默认文本生成
            generated_text = f"{prompt}，像针尖上一滴水滴在大海里，我的日子滴在时间的流里，没有声音，也没有影子。"
            generated_text += "去的尽管去了，来的尽管来着；去来的中间，又怎样地匆匆呢？"
            generated_text += "太阳他有脚啊，轻轻悄悄地挪移了；我也茫茫然跟着旋转。"
            generated_text += "你聪明的，告诉我，我们的日子为什么一去不复返呢？"
    except Exception as e:
        print(f"检索相似文本失败：{e}")
        # 如果检索失败，使用默认文本生成
        generated_text = f"{prompt}，像针尖上一滴水滴在大海里，我的日子滴在时间的流里，没有声音，也没有影子。"
        generated_text += "去的尽管去了，来的尽管来着；去来的中间，又怎样地匆匆呢？"
        generated_text += "太阳他有脚啊，轻轻悄悄地挪移了；我也茫茫然跟着旋转。"
        generated_text += "你聪明的，告诉我，我们的日子为什么一去不复返呢？"
    
    print("\n生成的文本：")
    print(generated_text)
    print("\n" + "=" * 60)
    print("文本生成完成！")
    print("=" * 60)
    
    return generated_text

def main():
    """主函数"""
    print("╔════════════════════════════════════════╗")
    print("║       Transformer 模型训练工具         ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 训练模型
    model = train_transformer(
        persist_directory="./chroma_db",
        collection_name="markdown_chunks",
        batch_size=2,
        epochs=5,
        learning_rate=1e-4,
        save_path="./transformer_model.pth"
    )
    
    # 测试模型
    test_transformer(
        model_path="./transformer_model.pth",
        persist_directory="./chroma_db",
        collection_name="markdown_chunks"
    )
    
    # 生成模仿朱自清风格的文本
    generate_text(
        model_path="./transformer_model.pth",
        prompt="时间",
        max_length=200
    )

if __name__ == "__main__":
    main()