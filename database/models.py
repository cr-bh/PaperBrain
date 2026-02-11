from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, ForeignKey, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime

Base = declarative_base()


class Paper(Base):
    """论文主表"""
    __tablename__ = 'papers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(500), nullable=False)
    authors = Column(JSON)  # 存储作者列表
    file_path = Column(String(500), nullable=False)  # PDF文件路径
    upload_date = Column(DateTime, default=datetime.now)
    content_summary = Column(JSON)  # 存储结构化总结
    mindmap_code = Column(Text)  # 存储Mermaid代码
    embedding_status = Column(Boolean, default=False)  # 是否已完成向量化

    # 关系
    tags = relationship('PaperTag', back_populates='paper', cascade='all, delete-orphan')
    images = relationship('PaperImage', back_populates='paper', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Paper(id={self.id}, title='{self.title}')>"


class Tag(Base):
    """标签表"""
    __tablename__ = 'tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), unique=True, nullable=False)
    category = Column(String(50))  # Domain, Methodology, Task
    parent_id = Column(Integer, ForeignKey('tags.id'), nullable=True)  # 支持层级结构
    color = Column(String(20), default='#3B82F6')  # 标签颜色

    # 关系
    papers = relationship('PaperTag', back_populates='tag')
    parent = relationship('Tag', remote_side=[id], backref='children')

    def __repr__(self):
        return f"<Tag(id={self.id}, name='{self.name}', category='{self.category}')>"


class PaperTag(Base):
    """论文-标签关联表"""
    __tablename__ = 'paper_tags'

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    tag_id = Column(Integer, ForeignKey('tags.id'), nullable=False)

    # 关系
    paper = relationship('Paper', back_populates='tags')
    tag = relationship('Tag', back_populates='papers')

    def __repr__(self):
        return f"<PaperTag(paper_id={self.paper_id}, tag_id={self.tag_id})>"


class PaperImage(Base):
    """论文图片表"""
    __tablename__ = 'paper_images'

    id = Column(Integer, primary_key=True, autoincrement=True)
    paper_id = Column(Integer, ForeignKey('papers.id'), nullable=False)
    image_path = Column(String(500), nullable=False)  # 图片文件路径
    caption = Column(Text)  # 图片标题/说明
    page_number = Column(Integer)  # 图片所在页码
    image_type = Column(String(50))  # 图片类型：architecture, performance, etc.

    # 关系
    paper = relationship('Paper', back_populates='images')

    def __repr__(self):
        return f"<PaperImage(id={self.id}, paper_id={self.paper_id}, caption='{self.caption}')>"


class ArxivPaper(Base):
    """Arxiv论文表（Auto-Scholar功能）"""
    __tablename__ = 'arxiv_papers'

    id = Column(Integer, primary_key=True, autoincrement=True)
    arxiv_id = Column(String(50), unique=True, nullable=False)  # 如 2401.12345
    title = Column(String(500), nullable=False)
    authors = Column(JSON)  # 作者列表
    abstract = Column(Text)  # 摘要
    categories = Column(JSON)  # ['cs.AI', 'cs.LG']
    published_date = Column(DateTime)  # 发布日期

    # 评分相关
    score = Column(Float)  # 1-10 分
    score_reason = Column(Text)  # 打分理由
    title_zh = Column(String(500))  # 中文标题
    abstract_zh = Column(Text)  # 中文摘要
    tags = Column(JSON)  # 自动生成的标签

    # 状态
    fetch_date = Column(DateTime, default=datetime.now)  # 抓取日期
    is_imported = Column(Boolean, default=False)  # 是否已导入到 Paper 表
    imported_paper_id = Column(Integer, ForeignKey('papers.id'), nullable=True)

    def __repr__(self):
        return f"<ArxivPaper(id={self.id}, arxiv_id='{self.arxiv_id}', score={self.score})>"


class KeywordConfig(Base):
    """关键词配置表（Auto-Scholar功能）"""
    __tablename__ = 'keyword_configs'

    id = Column(Integer, primary_key=True, autoincrement=True)
    keyword = Column(String(200), nullable=False)
    category = Column(String(50))  # 'core' 或 'frontier'
    created_date = Column(DateTime, default=datetime.now)

    def __repr__(self):
        return f"<KeywordConfig(id={self.id}, keyword='{self.keyword}', category='{self.category}')>"
