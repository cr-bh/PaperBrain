"""
RAG 检索服务
实现论文的向量化存储和检索问答
"""
import chromadb
from chromadb.config import Settings
import config
from services.llm_service import llm_service
from utils.prompts import RAG_QA_PROMPT, format_prompt
from typing import List
import google.generativeai as genai


class RAGService:
    """RAG 检索服务"""

    def __init__(self):
        self.llm = llm_service
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(path=config.CHROMA_DB_PATH)
        self.collection = self.client.get_or_create_collection(name="papers")

    def add_paper_to_vector_db(self, paper_id: int, paper_text: str):
        """
        将论文文本向量化并存储到 ChromaDB

        Args:
            paper_id: 论文 ID
            paper_text: 论文全文文本
        """
        # 分块
        chunks = self._chunk_text(paper_text)

        # 为每个块生成 ID
        ids = [f"paper_{paper_id}_chunk_{i}" for i in range(len(chunks))]

        # 添加到向量数据库（ChromaDB 会自动生成 embeddings）
        self.collection.add(
            documents=chunks,
            ids=ids,
            metadatas=[{"paper_id": paper_id, "chunk_index": i} for i in range(len(chunks))]
        )

    def _chunk_text(self, text: str) -> List[str]:
        """
        将文本分块

        Args:
            text: 原始文本

        Returns:
            文本块列表
        """
        # 简单的分块策略：按段落分割，每块约 1000 字符
        paragraphs = text.split('\n\n')
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            if len(current_chunk) + len(para) < config.CHUNK_SIZE:
                current_chunk += para + "\n\n"
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = para + "\n\n"

        if current_chunk:
            chunks.append(current_chunk.strip())

        return chunks

    def delete_paper_vectors(self, paper_id: int):
        """
        从向量数据库中删除论文的所有向量

        Args:
            paper_id: 论文 ID
        """
        try:
            # 查询该论文的所有向量 ID
            results = self.collection.get(
                where={"paper_id": paper_id}
            )

            if results and results['ids']:
                # 删除所有相关向量
                self.collection.delete(ids=results['ids'])
                print(f"✓ 已从向量数据库删除论文 {paper_id} 的 {len(results['ids'])} 个向量")
        except Exception as e:
            print(f"警告: 删除向量失败: {str(e)}")

    def query_paper(self, paper_id: int, question: str) -> str:
        """
        对论文进行问答

        Args:
            paper_id: 论文 ID
            question: 用户问题

        Returns:
            回答
        """
        # 检索相关文本块
        results = self.collection.query(
            query_texts=[question],
            n_results=config.TOP_K_RESULTS,
            where={"paper_id": paper_id}
        )

        if not results['documents'] or not results['documents'][0]:
            return "抱歉，在论文中没有找到相关信息。"

        # 获取检索到的文本块
        retrieved_chunks = "\n\n---\n\n".join(results['documents'][0])

        # 格式化 Prompt
        prompt = format_prompt(
            RAG_QA_PROMPT,
            retrieved_chunks=retrieved_chunks,
            user_question=question
        )

        # 调用 LLM 生成回答
        answer = self.llm.generate_text(prompt, temperature=0.3)

        return answer


    def query_all_papers(self, question: str) -> str:
        """
        对所有论文进行问答

        Args:
            question: 用户问题

        Returns:
            回答（包含来源论文信息）
        """
        # 检索相关文本块（不限制 paper_id）
        results = self.collection.query(
            query_texts=[question],
            n_results=config.TOP_K_RESULTS
        )

        if not results['documents'] or not results['documents'][0]:
            return "抱歉，在论文库中没有找到相关信息。"

        # 获取检索到的文本块和元数据
        retrieved_chunks = results['documents'][0]
        metadatas = results['metadatas'][0] if results['metadatas'] else []

        # 构建带来源的文本块
        chunks_with_source = []
        paper_ids = set()
        for i, chunk in enumerate(retrieved_chunks):
            if i < len(metadatas):
                paper_id = metadatas[i].get('paper_id', 'unknown')
                paper_ids.add(paper_id)
                chunks_with_source.append(f"[来源: 论文ID {paper_id}]\n{chunk}")
            else:
                chunks_with_source.append(chunk)

        retrieved_text = "\n\n---\n\n".join(chunks_with_source)

        # 格式化 Prompt
        prompt = format_prompt(
            RAG_QA_PROMPT,
            retrieved_chunks=retrieved_text,
            user_question=question
        )

        # 调用 LLM 生成回答
        answer = self.llm.generate_text(prompt, temperature=0.3)

        # 添加来源论文信息
        if paper_ids:
            from database.db_manager import db_manager
            source_papers = []
            for pid in paper_ids:
                if pid != 'unknown':
                    paper = db_manager.get_paper_by_id(int(pid))
                    if paper:
                        source_papers.append(f"- {paper.title}")

            if source_papers:
                answer += "\n\n**参考论文:**\n" + "\n".join(source_papers[:3])

        return answer

    def query_multiple_papers(self, paper_ids: List[int], question: str) -> str:
        """
        查询多篇论文并生成回答

        Args:
            paper_ids: 论文 ID 列表
            question: 用户问题

        Returns:
            生成的回答
        """
        if not paper_ids:
            return self.query_all_papers(question)

        from database.db_manager import db_manager

        # 优先使用结构化总结，补充向量检索
        chunks_with_source = []
        paper_ids_found = set()

        for paper_id in paper_ids:
            paper = db_manager.get_paper_by_id(paper_id)
            if paper and paper.content_summary:
                # 添加结构化总结的关键部分
                summary = paper.content_summary
                paper_ids_found.add(paper_id)

                # 提取核心内容
                if 'methodology' in summary:
                    chunks_with_source.append(f"[来源: 论文ID {paper_id} - 方法论]\n{summary['methodology'][:1500]}")
                if 'contribution' in summary:
                    chunks_with_source.append(f"[来源: 论文ID {paper_id} - 核心贡献]\n{summary['contribution'][:1000]}")
                if 'problem_definition' in summary:
                    chunks_with_source.append(f"[来源: 论文ID {paper_id} - 问题定义]\n{summary['problem_definition'][:800]}")

            # 补充向量检索结果
            results = self.collection.query(
                query_texts=[question],
                n_results=2,
                where={"paper_id": paper_id}
            )

            if results['documents'] and results['documents'][0]:
                for chunk in results['documents'][0][:2]:
                    chunks_with_source.append(f"[来源: 论文ID {paper_id} - 原文片段]\n{chunk}")

        if not chunks_with_source:
            return "抱歉，在指定的论文中没有找到相关信息。"

        retrieved_text = "\n\n---\n\n".join(chunks_with_source)

        # 格式化 Prompt
        prompt = format_prompt(
            RAG_QA_PROMPT,
            retrieved_chunks=retrieved_text,
            user_question=question
        )

        # 调用 LLM 生成回答
        answer = self.llm.generate_text(prompt, temperature=0.3)

        # 添加来源论文信息
        if paper_ids_found:
            from database.db_manager import db_manager
            source_papers = []
            for pid in paper_ids_found:
                paper = db_manager.get_paper_by_id(pid)
                if paper:
                    source_papers.append(f"- {paper.title}")

            if source_papers:
                answer += "\n\n**参考论文:**\n" + "\n".join(source_papers[:5])

        return answer

    def parse_mention(self, question: str):
        """
        解析问题中的 @mention，支持多个论文和模糊匹配

        Args:
            question: 用户问题

        Returns:
            (paper_ids, cleaned_question) - paper_ids 是列表，可能为空
        """
        import re

        # 匹配所有 @mention
        # 1. @"论文标题" - 引号包裹的完整标题
        # 2. @论文标题 - 匹配到下一个@、中文标点、或常见问句词
        pattern = r'@"([^"]+)"|@([^@\n]+?)(?=\s+@|\s*[，。？！、]|\s+[这那它有是的吗呢]|$)'
        matches = re.findall(pattern, question)

        paper_ids = []

        if matches:
            from database.db_manager import db_manager

            for match in matches:
                # 提取论文标题或关键词
                keyword = (match[0] if match[0] else match[1]).strip()

                # 首先尝试精确匹配
                paper = db_manager.get_paper_by_title(keyword)

                # 如果精确匹配失败，尝试模糊搜索
                if not paper:
                    papers = db_manager.search_papers(keyword)
                    if papers:
                        # 使用第一个匹配的论文
                        paper = papers[0]

                if paper:
                    paper_ids.append(paper.id)

            # 移除所有 @mention 部分
            cleaned_question = re.sub(pattern, '', question).strip()
            return paper_ids, cleaned_question

        return [], question


# 创建全局 RAG 服务实例
rag_service = RAGService()
