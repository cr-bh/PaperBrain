from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from typing import List, Optional
from datetime import datetime, timedelta
import config
from database.models import Base, Paper, Tag, PaperTag, PaperImage, ArxivPaper, KeywordConfig, FavoritePaper


class DatabaseManager:
    """数据库管理器"""

    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = config.DATABASE_PATH

        self.engine = create_engine(f'sqlite:///{db_path}', echo=False)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def create_tables(self):
        """创建所有表"""
        Base.metadata.create_all(self.engine)

    def get_session(self) -> Session:
        """获取数据库会话"""
        return self.SessionLocal()

    # ========== Paper CRUD ==========

    def create_paper(self, title: str, authors: List[str], file_path: str,
                     content_summary: dict = None, mindmap_code: str = None) -> Paper:
        """创建论文记录"""
        session = self.get_session()
        try:
            paper = Paper(
                title=title,
                authors=authors,
                file_path=file_path,
                content_summary=content_summary,
                mindmap_code=mindmap_code,
                upload_date=datetime.now()
            )
            session.add(paper)
            session.commit()
            session.refresh(paper)
            return paper
        finally:
            session.close()

    def get_paper_by_id(self, paper_id: int) -> Optional[Paper]:
        """根据ID获取论文"""
        session = self.get_session()
        try:
            paper = session.query(Paper).filter(Paper.id == paper_id).first()
            if paper:
                # 显式访问属性以触发加载，避免 session 关闭后无法访问
                _ = paper.mindmap_code
                _ = paper.content_summary
                _ = paper.authors
                _ = paper.title
                _ = paper.file_path
            return paper
        finally:
            session.close()

    def get_all_papers(self, limit: int = None) -> List[Paper]:
        """获取所有论文"""
        session = self.get_session()
        try:
            query = session.query(Paper).order_by(Paper.upload_date.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def search_papers(self, keyword: str) -> List[Paper]:
        """
        搜索论文（按标题或作者，支持模糊搜索）

        Args:
            keyword: 搜索关键词

        Returns:
            匹配的论文列表
        """
        session = self.get_session()
        try:
            # 使用 ilike 进行不区分大小写的模糊搜索
            keyword_pattern = f"%{keyword}%"
            return session.query(Paper).filter(
                Paper.title.ilike(keyword_pattern)
            ).all()
        finally:
            session.close()

    def get_paper_by_title(self, title: str) -> Optional[Paper]:
        """根据标题精确查询论文"""
        session = self.get_session()
        try:
            paper = session.query(Paper).filter(Paper.title == title).first()
            if paper:
                # 显式访问属性以触发加载
                _ = paper.mindmap_code
                _ = paper.content_summary
            return paper
        finally:
            session.close()

    def get_paper_by_file_path(self, file_path: str) -> Optional[Paper]:
        """根据文件路径查询论文"""
        session = self.get_session()
        try:
            paper = session.query(Paper).filter(Paper.file_path == file_path).first()
            if paper:
                _ = paper.mindmap_code
                _ = paper.content_summary
            return paper
        finally:
            session.close()

    def update_paper(self, paper_id: int, **kwargs) -> Optional[Paper]:
        """更新论文信息"""
        session = self.get_session()
        try:
            paper = session.query(Paper).filter(Paper.id == paper_id).first()
            if paper:
                for key, value in kwargs.items():
                    if hasattr(paper, key):
                        setattr(paper, key, value)
                session.commit()
                session.refresh(paper)
            return paper
        finally:
            session.close()

    def update_paper_summary(self, paper_id: int, content_summary: dict) -> Optional[Paper]:
        """更新论文的结构化总结"""
        return self.update_paper(paper_id, content_summary=content_summary)

    def delete_paper(self, paper_id: int) -> bool:
        """删除论文及其相关文件"""
        session = self.get_session()
        try:
            paper = session.query(Paper).filter(Paper.id == paper_id).first()
            if paper:
                # 保存文件路径用于删除
                file_path = paper.file_path

                # 删除数据库记录（会级联删除关联的标签和图片记录）
                session.delete(paper)
                session.commit()

                # 删除 PDF 文件
                try:
                    from pathlib import Path
                    pdf_file = Path(file_path)
                    if pdf_file.exists():
                        pdf_file.unlink()
                        print(f"✓ 已删除 PDF 文件: {file_path}")
                except Exception as e:
                    print(f"警告: 删除 PDF 文件失败: {str(e)}")

                # 删除图片文件夹
                try:
                    import shutil
                    import config
                    images_dir = Path(config.IMAGES_DIR) / str(paper_id)
                    if images_dir.exists():
                        shutil.rmtree(images_dir)
                        print(f"✓ 已删除图片文件夹: {images_dir}")
                except Exception as e:
                    print(f"警告: 删除图片文件夹失败: {str(e)}")

                # 清理孤立的标签（没有关联任何论文的标签）
                self.cleanup_orphaned_tags()

                return True
            return False
        finally:
            session.close()

    # ========== Tag CRUD ==========

    def create_tag(self, name: str, category: str = None,
                   parent_id: int = None, color: str = '#3B82F6') -> Tag:
        """创建标签"""
        session = self.get_session()
        try:
            # 检查标签是否已存在
            existing_tag = session.query(Tag).filter(Tag.name == name).first()
            if existing_tag:
                return existing_tag

            tag = Tag(name=name, category=category, parent_id=parent_id, color=color)
            session.add(tag)
            session.commit()
            session.refresh(tag)
            return tag
        finally:
            session.close()

    def get_tag_by_name(self, name: str) -> Optional[Tag]:
        """根据名称获取标签"""
        session = self.get_session()
        try:
            return session.query(Tag).filter(Tag.name == name).first()
        finally:
            session.close()

    def get_tag_by_id(self, tag_id: int) -> Optional[Tag]:
        """根据ID获取标签"""
        session = self.get_session()
        try:
            return session.query(Tag).filter(Tag.id == tag_id).first()
        finally:
            session.close()

    def get_all_tags(self) -> List[Tag]:
        """获取所有标签"""
        session = self.get_session()
        try:
            return session.query(Tag).all()
        finally:
            session.close()

    def get_tags_by_category(self, category: str) -> List[Tag]:
        """根据类别获取标签"""
        session = self.get_session()
        try:
            return session.query(Tag).filter(Tag.category == category).all()
        finally:
            session.close()

    def update_tag(self, tag_id: int, **kwargs) -> Optional[Tag]:
        """更新标签信息"""
        session = self.get_session()
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                for key, value in kwargs.items():
                    if hasattr(tag, key):
                        setattr(tag, key, value)
                session.commit()
                session.refresh(tag)
            return tag
        finally:
            session.close()

    def delete_tag(self, tag_id: int) -> bool:
        """删除标签"""
        session = self.get_session()
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                session.delete(tag)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def cleanup_orphaned_tags(self) -> int:
        """
        清理孤立的标签（没有关联任何论文的标签）

        Returns:
            删除的标签数量
        """
        session = self.get_session()
        try:
            # 查找所有标签
            all_tags = session.query(Tag).all()
            deleted_count = 0

            for tag in all_tags:
                # 检查该标签是否有关联的论文
                paper_count = session.query(PaperTag).filter(
                    PaperTag.tag_id == tag.id
                ).count()

                # 如果没有关联的论文，删除该标签
                if paper_count == 0:
                    session.delete(tag)
                    deleted_count += 1

            session.commit()
            if deleted_count > 0:
                print(f"✓ 已清理 {deleted_count} 个孤立标签")
            return deleted_count
        finally:
            session.close()

    # ========== Paper-Tag Association ==========

    def add_tag_to_paper(self, paper_id: int, tag_id: int) -> PaperTag:
        """为论文添加标签"""
        session = self.get_session()
        try:
            # 检查关联是否已存在
            existing = session.query(PaperTag).filter(
                PaperTag.paper_id == paper_id,
                PaperTag.tag_id == tag_id
            ).first()
            if existing:
                return existing

            paper_tag = PaperTag(paper_id=paper_id, tag_id=tag_id)
            session.add(paper_tag)
            session.commit()
            session.refresh(paper_tag)
            return paper_tag
        finally:
            session.close()

    def remove_tag_from_paper(self, paper_id: int, tag_id: int) -> bool:
        """从论文移除标签"""
        session = self.get_session()
        try:
            paper_tag = session.query(PaperTag).filter(
                PaperTag.paper_id == paper_id,
                PaperTag.tag_id == tag_id
            ).first()
            if paper_tag:
                session.delete(paper_tag)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def get_paper_tags(self, paper_id: int) -> List[Tag]:
        """获取论文的所有标签"""
        session = self.get_session()
        try:
            paper = session.query(Paper).filter(Paper.id == paper_id).first()
            if paper:
                return [pt.tag for pt in paper.tags]
            return []
        finally:
            session.close()

    def get_papers_by_tag(self, tag_id: int) -> List[Paper]:
        """获取具有指定标签的所有论文"""
        session = self.get_session()
        try:
            tag = session.query(Tag).filter(Tag.id == tag_id).first()
            if tag:
                return [pt.paper for pt in tag.papers]
            return []
        finally:
            session.close()

    # ========== Paper Image Management ==========

    def add_image_to_paper(self, paper_id: int, image_path: str,
                          caption: str = None, page_number: int = None,
                          image_type: str = None) -> PaperImage:
        """为论文添加图片"""
        session = self.get_session()
        try:
            image = PaperImage(
                paper_id=paper_id,
                image_path=image_path,
                caption=caption,
                page_number=page_number,
                image_type=image_type
            )
            session.add(image)
            session.commit()
            session.refresh(image)
            return image
        finally:
            session.close()

    def get_paper_images(self, paper_id: int) -> List[PaperImage]:
        """获取论文的所有图片"""
        session = self.get_session()
        try:
            return session.query(PaperImage).filter(
                PaperImage.paper_id == paper_id
            ).all()
        finally:
            session.close()

    def delete_image(self, image_id: int) -> bool:
        """删除图片记录"""
        session = self.get_session()
        try:
            image = session.query(PaperImage).filter(PaperImage.id == image_id).first()
            if image:
                session.delete(image)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def update_image_caption(self, image_id: int, caption: str) -> bool:
        """更新图片说明"""
        session = self.get_session()
        try:
            image = session.query(PaperImage).filter(PaperImage.id == image_id).first()
            if image:
                image.caption = caption
                session.commit()
                return True
            return False
        finally:
            session.close()

    # ========== ArxivPaper CRUD (Auto-Scholar) ==========

    def create_arxiv_paper(self, arxiv_id: str, title: str, authors: List[str],
                          abstract: str, categories: List[str], published_date: datetime,
                          score: float = None, score_reason: str = None,
                          title_zh: str = None, abstract_zh: str = None,
                          tags: List[str] = None, venue: str = None,
                          venue_year: int = None, institutions: List[str] = None) -> ArxivPaper:
        """创建 Arxiv 论文记录"""
        session = self.get_session()
        try:
            arxiv_paper = ArxivPaper(
                arxiv_id=arxiv_id,
                title=title,
                authors=authors,
                abstract=abstract,
                categories=categories,
                published_date=published_date,
                score=score,
                score_reason=score_reason,
                title_zh=title_zh,
                abstract_zh=abstract_zh,
                tags=tags,
                venue=venue,
                venue_year=venue_year,
                institutions=institutions,
                fetch_date=datetime.now()
            )
            session.add(arxiv_paper)
            session.commit()
            session.refresh(arxiv_paper)
            return arxiv_paper
        finally:
            session.close()

    def get_arxiv_paper_by_id(self, arxiv_paper_id: int) -> Optional[ArxivPaper]:
        """根据ID获取 Arxiv 论文"""
        session = self.get_session()
        try:
            return session.query(ArxivPaper).filter(ArxivPaper.id == arxiv_paper_id).first()
        finally:
            session.close()

    def get_arxiv_paper_by_arxiv_id(self, arxiv_id: str) -> Optional[ArxivPaper]:
        """根据 arxiv_id 获取论文（用于去重）"""
        session = self.get_session()
        try:
            return session.query(ArxivPaper).filter(ArxivPaper.arxiv_id == arxiv_id).first()
        finally:
            session.close()

    def get_arxiv_papers_by_date(self, date: datetime, min_score: float = 0.0) -> List[ArxivPaper]:
        """获取指定日期抓取的论文"""
        session = self.get_session()
        try:
            from datetime import timedelta
            start_date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)

            return session.query(ArxivPaper).filter(
                ArxivPaper.fetch_date >= start_date,
                ArxivPaper.fetch_date < end_date,
                ArxivPaper.score >= min_score
            ).order_by(ArxivPaper.score.desc()).all()
        finally:
            session.close()

    def get_arxiv_papers_by_date_range(self, start_date: datetime, end_date: datetime,
                                       min_score: float = 0.0) -> List[ArxivPaper]:
        """获取指定日期范围内抓取的论文"""
        session = self.get_session()
        try:
            return session.query(ArxivPaper).filter(
                ArxivPaper.fetch_date >= start_date,
                ArxivPaper.fetch_date <= end_date,
                ArxivPaper.score >= min_score
            ).order_by(ArxivPaper.score.desc()).all()
        finally:
            session.close()

    def get_all_arxiv_papers(self, limit: int = None, min_score: float = 0.0) -> List[ArxivPaper]:
        """获取所有 Arxiv 论文"""
        session = self.get_session()
        try:
            query = session.query(ArxivPaper).filter(
                ArxivPaper.score >= min_score
            ).order_by(ArxivPaper.score.desc(), ArxivPaper.fetch_date.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def update_arxiv_paper_import_status(self, arxiv_paper_id: int,
                                        imported_paper_id: int) -> bool:
        """更新 Arxiv 论文的导入状态"""
        session = self.get_session()
        try:
            arxiv_paper = session.query(ArxivPaper).filter(
                ArxivPaper.id == arxiv_paper_id
            ).first()
            if arxiv_paper:
                arxiv_paper.is_imported = True
                arxiv_paper.imported_paper_id = imported_paper_id
                session.commit()
                return True
            return False
        finally:
            session.close()

    def delete_all_arxiv_papers(self) -> bool:
        """删除所有 Arxiv 论文"""
        session = self.get_session()
        try:
            session.query(ArxivPaper).delete()
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    # ========== KeywordConfig CRUD (Auto-Scholar) ==========

    def add_keyword(self, keyword: str, category: str = 'core') -> KeywordConfig:
        """添加关键词"""
        session = self.get_session()
        try:
            # 检查是否已存在
            existing = session.query(KeywordConfig).filter(
                KeywordConfig.keyword == keyword
            ).first()
            if existing:
                return existing

            kw = KeywordConfig(keyword=keyword, category=category)
            session.add(kw)
            session.commit()
            session.refresh(kw)
            return kw
        finally:
            session.close()

    def get_all_keywords(self) -> List[KeywordConfig]:
        """获取所有关键词"""
        session = self.get_session()
        try:
            return session.query(KeywordConfig).order_by(
                KeywordConfig.category, KeywordConfig.created_date
            ).all()
        finally:
            session.close()

    def get_keywords_by_category(self, category: str) -> List[KeywordConfig]:
        """根据类别获取关键词"""
        session = self.get_session()
        try:
            return session.query(KeywordConfig).filter(
                KeywordConfig.category == category
            ).all()
        finally:
            session.close()

    def delete_keyword(self, keyword_id: int) -> bool:
        """删除关键词"""
        session = self.get_session()
        try:
            kw = session.query(KeywordConfig).filter(KeywordConfig.id == keyword_id).first()
            if kw:
                session.delete(kw)
                session.commit()
                return True
            return False
        finally:
            session.close()

    # ========== FavoritePaper CRUD ==========

    def favorite_arxiv_paper(self, arxiv_paper_id: int) -> Optional[FavoritePaper]:
        """将 ArxivPaper 收藏为 FavoritePaper"""
        session = self.get_session()
        try:
            arxiv_paper = session.query(ArxivPaper).filter(
                ArxivPaper.id == arxiv_paper_id
            ).first()

            if not arxiv_paper:
                return None

            # 检查是否已收藏
            existing = session.query(FavoritePaper).filter(
                FavoritePaper.arxiv_id == arxiv_paper.arxiv_id
            ).first()
            if existing:
                return existing

            # 简化作者列表（仅保留名字）
            authors_simple = []
            for author in (arxiv_paper.authors or [])[:5]:
                if isinstance(author, dict):
                    authors_simple.append(author.get('name', str(author)))
                else:
                    authors_simple.append(str(author))

            # 创建收藏记录
            favorite = FavoritePaper(
                arxiv_id=arxiv_paper.arxiv_id,
                title=arxiv_paper.title,
                title_zh=arxiv_paper.title_zh,
                authors=authors_simple,
                abstract=arxiv_paper.abstract,
                abstract_zh=arxiv_paper.abstract_zh,
                score=arxiv_paper.score,
                score_reason=arxiv_paper.score_reason,
                tags=arxiv_paper.tags,
                arxiv_url=f"https://arxiv.org/abs/{arxiv_paper.arxiv_id}",
                pdf_url=f"https://arxiv.org/pdf/{arxiv_paper.arxiv_id}.pdf",
                published_date=arxiv_paper.published_date,
                favorited_date=datetime.now()
            )

            session.add(favorite)

            # 标记原记录为已收藏
            arxiv_paper.is_favorited = True

            session.commit()
            session.refresh(favorite)
            return favorite
        finally:
            session.close()

    def get_all_favorites(self, limit: int = None, min_score: float = 0.0) -> List[FavoritePaper]:
        """获取所有收藏的论文"""
        session = self.get_session()
        try:
            query = session.query(FavoritePaper).filter(
                FavoritePaper.score >= min_score
            ).order_by(FavoritePaper.favorited_date.desc())
            if limit:
                query = query.limit(limit)
            return query.all()
        finally:
            session.close()

    def get_favorite_by_arxiv_id(self, arxiv_id: str) -> Optional[FavoritePaper]:
        """根据 arxiv_id 获取收藏"""
        session = self.get_session()
        try:
            return session.query(FavoritePaper).filter(
                FavoritePaper.arxiv_id == arxiv_id
            ).first()
        finally:
            session.close()

    def remove_favorite(self, favorite_id: int) -> bool:
        """取消收藏"""
        session = self.get_session()
        try:
            favorite = session.query(FavoritePaper).filter(
                FavoritePaper.id == favorite_id
            ).first()
            if favorite:
                # 更新对应的 ArxivPaper（如果存在）
                arxiv_paper = session.query(ArxivPaper).filter(
                    ArxivPaper.arxiv_id == favorite.arxiv_id
                ).first()
                if arxiv_paper:
                    arxiv_paper.is_favorited = False

                session.delete(favorite)
                session.commit()
                return True
            return False
        finally:
            session.close()

    def update_favorite_notes(self, favorite_id: int, notes: str) -> bool:
        """更新收藏的用户笔记"""
        session = self.get_session()
        try:
            favorite = session.query(FavoritePaper).filter(
                FavoritePaper.id == favorite_id
            ).first()
            if favorite:
                favorite.user_notes = notes
                session.commit()
                return True
            return False
        finally:
            session.close()

    def cleanup_expired_arxiv_papers(self, days_to_keep: int = 7) -> int:
        """
        清理过期的临时论文数据（保留已收藏和已导入的）

        Args:
            days_to_keep: 保留天数

        Returns:
            删除的论文数量
        """
        session = self.get_session()
        try:
            expire_threshold = datetime.now() - timedelta(days=days_to_keep)

            # 删除未收藏、未导入且超过保留期的论文
            deleted = session.query(ArxivPaper).filter(
                ArxivPaper.is_favorited == False,
                ArxivPaper.is_imported == False,
                ArxivPaper.fetch_date < expire_threshold
            ).delete()

            session.commit()
            if deleted > 0:
                print(f"✓ 已清理 {deleted} 篇过期论文")
            return deleted
        finally:
            session.close()

    def get_storage_stats(self) -> dict:
        """获取存储统计信息"""
        session = self.get_session()
        try:
            arxiv_count = session.query(ArxivPaper).count()
            favorite_count = session.query(FavoritePaper).count()
            imported_count = session.query(ArxivPaper).filter(
                ArxivPaper.is_imported == True
            ).count()
            favorited_count = session.query(ArxivPaper).filter(
                ArxivPaper.is_favorited == True
            ).count()

            return {
                'arxiv_papers': arxiv_count,
                'favorites': favorite_count,
                'imported': imported_count,
                'favorited': favorited_count,
                'can_cleanup': arxiv_count - favorited_count - imported_count
            }
        finally:
            session.close()


# 创建全局数据库管理器实例
db_manager = DatabaseManager()
