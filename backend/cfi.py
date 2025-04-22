#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import hashlib
import sys
import pandas as pd
import numpy as np
import joblib
from fuzzywuzzy import process, fuzz
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from pathlib import Path
import warnings
import os
import jieba

# 环境配置
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'  # 禁用TensorFlow日志
warnings.filterwarnings("ignore")
pd.set_option('display.unicode.ambiguous_as_wide', True)
pd.set_option('display.unicode.east_asian_width', True)


# ======================== 配置区域 ========================
class Config:
    # 缓存配置
    CACHE_DIR = Path("cache")
    TFIDF_CACHE = CACHE_DIR / "tfidf_model.pkl"
    DATA_CACHE = CACHE_DIR / "medical_data.feather"

    DATA_22_PATH = './data/22.csv'

    # 性能配置
    MAX_RESULTS = 10  # 最大返回结果数
    MIN_QUERY_LEN = 2  # 最小查询长度


# ======================== 核心功能 ========================
def _tokenize_zh(text):
    """中文分词优化"""
    if text is None:
        return []
    return [word for word in jieba.cut(text) if word.strip()]


class cfi22:
    def __init__(self):
        self.config = Config()
        self._init_cache()
        self.data = self._load_data()
        self._init_models()
        self.ex_kv = self.build_ex_kv()

    def _init_cache(self):
        """初始化缓存目录"""
        self.config.CACHE_DIR.mkdir(exist_ok=True)

    def _load_data(self):
        """智能加载数据（优先使用缓存）"""
        try:
            if self.config.DATA_CACHE.exists():
                print("🔄 从缓存加载数据...", end="")
                df = pd.read_feather(self.config.DATA_CACHE)
                print("\r✅ 缓存数据加载完成（{}条记录）".format(len(df)))
            else:
                print("🔄 从本地CSV文件加载数据...", end="")
                df = pd.read_csv(self.config.DATA_22_PATH)
                df.to_feather(self.config.DATA_CACHE)  # 保存为高性能feather格式
                print("\r✅ 本地CSV文件加载完成（{}条记录）".format(len(df)))

            # **防止 None 值**
            df['sku_ex'] = df['sku_ex'].fillna('').astype(str)
            df['use_to'] = df['use_to'].fillna('').astype(str)
            df['index-complex'] = df['sku_ex'] + df['use_to']
            return df

        except Exception as e:
            print(f"\n❌ 数据加载失败: {str(e)}")
            print("⚠️ 使用内置示例数据运行")
            return self._get_sample_data()

    def _get_sample_data(self):
        """应急示例数据"""
        return pd.DataFrame({
            'name': ['血糖检测仪', '引流导管', '超声诊断仪', '心脏支架', '医用口罩'],
            'code': ['IVD-001', 'DEV-002', 'DEV-003', 'IMP-004', 'PRO-005'],
            'level': [3, 2, 3, 3, 1],
            'sku_ex': [
                '用于血糖水平检测',
                '用于术后引流',
                '用于医学影像诊断',
                '用于心血管手术',
                '用于个人防护'
            ]
        })

    def _init_models(self):
        """初始化模型（带缓存）"""
        try:
            if self.config.TFIDF_CACHE.exists():
                print("🔄 加载缓存模型...", end="")
                if self.config.TFIDF_CACHE.is_file():
                    self.tfidf = joblib.load(self.config.TFIDF_CACHE)
                    print("\r✅ 缓存模型加载完成")
                else:
                    raise FileNotFoundError(f"{self.config.TFIDF_CACHE} 不是一个有效的文件")
            else:
                print("🔄 训练TF-IDF模型...", end="")
                # 初始化并拟合 TF-IDF 模型
                self.tfidf = TfidfVectorizer(
                    tokenizer=_tokenize_zh,
                    ngram_range=(1, 2)
                )
                self.tfidf.fit(self.data['index-complex'])
                joblib.dump(self.tfidf, self.config.TFIDF_CACHE)
                print("\r✅ 模型训练并缓存完成")

            # 预计算矩阵
            self.tfidf_matrix = self.tfidf.transform(self.data['index-complex'])
            print("\r✅ 模型初始化完成")

        except Exception as e:
            print(f"\n❌ 模型初始化失败: {str(e)}")
            sys.exit(1)

    def build_ex_kv(self):
        ex_kv = {}
        for index, row in self.data.iterrows():
            ex_kv[hashlib.md5(
                (row['sku_ex'] + row['use_to']).encode(
                    encoding='UTF-8')).hexdigest()] = row
        return ex_kv

    def fuzzy_search(self, query, top_n=5):
        """优化模糊搜索"""
        sku_ex = self.data['index-complex'].tolist()
        matches = process.extract(query, sku_ex, scorer=fuzz.token_set_ratio, limit=top_n)

        results = []
        for name, score in matches:
            md5 = hashlib.md5(name.encode(encoding='UTF-8')).hexdigest()
            row = self.ex_kv[md5]

            results.append({
                'name': row['name'],
                'code': row['code'],
                'level': row['level'],
                'score': score / 100,  # 归一化到0-1
                'exp': row.get('sku_ex', ''),
                'description': row.get('use_to', '')
            })
        return results

    def semantic_search(self, query, top_n=5):
        """语义相似度搜索"""
        query_vec = self.tfidf.transform([query])
        cos_sim = cosine_similarity(query_vec, self.tfidf_matrix).flatten()
        top_indices = np.argsort(cos_sim)[-top_n:][::-1]

        results = []
        for idx in top_indices:
            row = self.data.iloc[idx]
            results.append({
                'name': row['name'],
                'code': row['code'],
                'level': row['level'],
                'score': float(cos_sim[idx]),
                'exp': row.get('sku_ex', ''),
                'description': row.get('use_to', '')
            })
        return results
