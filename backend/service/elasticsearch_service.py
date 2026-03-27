"""
Elasticsearch 服务模块 - 提供文献全文检索功能

本模块基于官方 elasticsearch-py (Async) 客户端实现，主要功能包括：
1. 索引管理：创建、删除、重建索引（包含 Mapping 定义）。
2. 文档操作：单条索引、批量索引、删除文档。
3. 搜索服务：支持多字段模糊搜索、过滤、分页、高亮显示。
4. 数据同步：提供从 PostgreSQL 同步数据到 Elasticsearch 的功能。

依赖：
- elasticsearch>=8.0.0
- IK Analysis Plugin (推荐安装在 Elasticsearch服务端以支持中文分词)
"""
import asyncio
from typing import List, Dict, Any, Optional, Union
from datetime import datetime

from elasticsearch import AsyncElasticsearch, helpers
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.config import config
from core.service_manager import BaseManagedService
from utils.log import global_logger
from database.orm.models.manuscript import Manuscript


class ElasticsearchService(BaseManagedService):
    """Elasticsearch 服务管理器 (异步)"""

    def __init__(self):
        # 初始化父类，注册服务名为 'elasticsearch'
        super().__init__("elasticsearch")
        self.client: Optional[AsyncElasticsearch] = None
        
        # 加载配置
        # 配置文件: backend/configs/elasticsearch.toml
        # 访问格式: 配置文件名.表名.键名
        env = config.get("global.global.env", "dev")
        host_key = f"elasticsearch.elasticsearch.elasticsearch_host_{env}"
        self.host = config.get(host_key, "localhost")
        self.port = config.get("elasticsearch.elasticsearch.elasticsearch_port", 9200)
        self.scheme = config.get("elasticsearch.elasticsearch.elasticsearch_scheme", "http")
        self.username = config.get("elasticsearch.elasticsearch.elasticsearch_username", "")
        self.password = config.get("elasticsearch.elasticsearch.elasticsearch_password", "")
        
        self.index_name = config.get("elasticsearch.elasticsearch.elasticsearch_index", "journals")
        self.shards = config.get("elasticsearch.elasticsearch.elasticsearch_shards", 1)
        self.replicas = config.get("elasticsearch.elasticsearch.elasticsearch_replicas", 0)

    async def start(self):
        """
        启动 Elasticsearch 服务（实现 BaseManagedService 接口）
        
        初始化 Elasticsearch 客户端连接
        """
        if self._initialized:
            return

        hosts = [f"{self.scheme}://{self.host}:{self.port}"]
        http_auth = (self.username, self.password) if self.username and self.password else None
        
        try:
            global_logger.info("Elasticsearch", f"正在连接 Elasticsearch: {hosts}")
            self.client = AsyncElasticsearch(
                hosts=hosts,
                basic_auth=http_auth,
                verify_certs=False,  # 开发环境通常关闭证书验证，生产环境建议开启
                request_timeout=30
            )
            
            # 验证连接
            if await self.client.ping():
                info = await self.client.info()
                version = info['version']['number']
                global_logger.info("Elasticsearch", f"连接成功，版本: {version}")
                self._initialized = True
                
                # 检查索引是否存在，不存在则创建
                await self.create_index_if_not_exists()
            else:
                global_logger.error("Elasticsearch", "无法连接到 Elasticsearch 服务")
                
        except Exception as e:
            global_logger.exception("Elasticsearch", f"初始化失败: {e}")
            self.client = None

    async def stop(self):
        """
        停止 Elasticsearch 服务（实现 BaseManagedService 接口）
        
        关闭连接
        """
        if self.client:
            await self.client.close()
            self.client = None
            self._initialized = False
            global_logger.info("Elasticsearch", "连接已关闭")

    async def create_index_if_not_exists(self):
        """如果索引不存在则创建"""
        if not self.client:
            return

        if not await self.client.indices.exists(index=self.index_name):
            await self.create_index()

    async def create_index(self):
        """创建索引 (定义 Mapping)"""
        if not self.client:
            return

        # 定义 Mapping
        # 注意：这里默认使用了 ik_max_word 和 ik_smart 分词器
        # 如果 ES 服务端未安装 IK 插件，创建索引会失败
        mapping = {
            "settings": {
                "number_of_shards": self.shards,
                "number_of_replicas": self.replicas,
                "analysis": {
                    "analyzer": {
                        "default": {
                            "type": "ik_max_word"
                        },
                        "default_search": {
                            "type": "ik_smart"
                        }
                    }
                }
            },
            "mappings": {
                "properties": {
                    "manuscript_id": {"type": "long"},
                    "title": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart",
                        "fields": {"keyword": {"type": "keyword", "ignore_above": 256}}
                    },
                    "authors": {
                        "type": "text",
                        "analyzer": "ik_max_word",  # 作者名也可能包含中文
                        "search_analyzer": "ik_smart"
                    },
                    "abstract": {
                        "type": "text",
                        "analyzer": "ik_max_word",
                        "search_analyzer": "ik_smart"
                    },
                    "subject": {"type": "keyword"},  # 学科作为过滤条件
                    "stage": {"type": "keyword"},  # 流转阶段
                    "status": {"type": "keyword"},
                    "create_time": {"type": "keyword"},  # ISO 字符串格式
                    "update_time": {"type": "keyword"}   # ISO 字符串格式
                }
            }
        }

        try:
            # 尝试创建带 IK 分词器的索引
            await self.client.indices.create(index=self.index_name, body=mapping)
            global_logger.info("Elasticsearch", f"索引 {self.index_name} 创建成功 (使用 IK 分词器)")
        except Exception as e:
            error_msg = str(e)
            if "unknown analysis" in error_msg or "analyzer [ik_max_word] not found" in error_msg:
                global_logger.warning("Elasticsearch", "创建索引失败，未检测到 IK 分词器，尝试使用标准分词器回退...")
                # 回退方案：移除 analysis 设置，使用默认 standard 分词器
                fallback_mapping = mapping.copy()
                del fallback_mapping["settings"]["analysis"]
                # 移除字段中的 analyzer 指定
                props = fallback_mapping["mappings"]["properties"]
                for field in ["title", "authors", "abstract"]:
                    if field in props and "analyzer" in props[field]:
                        del props[field]["analyzer"]
                    if field in props and "search_analyzer" in props[field]:
                        del props[field]["search_analyzer"]
                
                try:
                    await self.client.indices.create(index=self.index_name, body=fallback_mapping)
                    global_logger.info("Elasticsearch", f"索引 {self.index_name} 创建成功 (使用 Standard 分词器)")
                except Exception as e2:
                    global_logger.error("Elasticsearch", f"回退创建索引失败: {e2}")
            else:
                global_logger.error("Elasticsearch", f"创建索引失败: {e}")

    async def delete_index(self):
        """删除索引"""
        if not self.client:
            return
        try:
            if await self.client.indices.exists(index=self.index_name):
                await self.client.indices.delete(index=self.index_name)
                global_logger.info("Elasticsearch", f"索引 {self.index_name} 已删除")
        except Exception as e:
            global_logger.error("Elasticsearch", f"删除索引失败: {e}")

    def _model_to_doc(self, manuscript: Manuscript) -> Dict[str, Any]:
        """
        将 Manuscript ORM 模型转换为 ES 文档
        
        Args:
            manuscript: 稿件模型实例
            
        Returns:
            ES 文档字典
        """
        doc = {
            "manuscript_id": manuscript.manuscript_id,
            "title": manuscript.title,
            "authors": manuscript.authors,
            "subject": manuscript.subject,
            "abstract": manuscript.abstract,
            "stage": manuscript.stage,
            "status": manuscript.status,
            "create_time": manuscript.create_time,
            "update_time": manuscript.update_time
        }
        return doc

    async def index_manuscript(self, manuscript: Manuscript):
        """
        索引单个稿件
        
        Args:
            manuscript: 稿件模型实例
        """
        if not self.client or not self._initialized:
            # 尝试惰性初始化，防止服务未启动
            if not self._initialized:
                await self.start()
            if not self.client:
                return

        try:
            doc = self._model_to_doc(manuscript)
            await self.client.index(index=self.index_name, id=str(manuscript.manuscript_id), document=doc)
            global_logger.debug("Elasticsearch", f"稿件已索引: {manuscript.manuscript_id}")
        except Exception as e:
            global_logger.error("Elasticsearch", f"索引稿件失败 {manuscript.manuscript_id}: {e}")

    async def delete_manuscript(self, manuscript_id: int):
        """
        删除单个稿件文档
        
        Args:
            manuscript_id: 稿件 ID
        """
        if not self.client:
            return
        try:
            await self.client.delete(index=self.index_name, id=str(manuscript_id), ignore=[404])
            global_logger.info("Elasticsearch", f"稿件索引已删除: {manuscript_id}")
        except Exception as e:
            global_logger.error("Elasticsearch", f"删除文档失败 {manuscript_id}: {e}")

    async def search(self, 
                     query: str, 
                     page: int = 1, 
                     size: int = 10, 
                     filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        搜索文献
        :param query: 搜索关键词
        :param page: 页码 (从1开始)
        :param size: 每页数量
        :param filters: 过滤条件字典 (例如 {"status": "published", "subject": "计算机"})
        :return: 搜索结果字典
        """
        if not self.client:
            return {"total": 0, "items": [], "error": "Elasticsearch service not available"}

        # 构建查询 DSL
        dsl: Dict[str, Any] = {
            "from": (page - 1) * size,
            "size": size,
            "query": {
                "bool": {
                    "must": [],
                    "filter": []
                }
            },
            "highlight": {
                "fields": {
                    "title": {},
                    "abstract": {},
                    "keywords": {}
                },
                "pre_tags": ["<em>"],
                "post_tags": ["</em>"]
            }
        }

        # 1. 关键词全文检索
        if query:
            dsl["query"]["bool"]["must"].append({
                "multi_match": {
                    "query": query,
                    "fields": ["title^3", "keywords^2", "abstract", "authors"],
                    "type": "best_fields",
                    "operator": "or" # 提高召回率，若需精确可改 "and"
                }
            })
        else:
            dsl["query"]["bool"]["must"].append({"match_all": {}})

        # 2. 过滤条件
        if filters:
            for k, v in filters.items():
                if v is not None and v != "":
                    if isinstance(v, list):
                        dsl["query"]["bool"]["filter"].append({"terms": {k: v}})
                    else:
                        dsl["query"]["bool"]["filter"].append({"term": {k: v}})

        # 默认只搜已发布的（除非 filters 显式指定了 status）
        if not filters or "status" not in filters:
             dsl["query"]["bool"]["filter"].append({"term": {"status": "published"}})

        try:
            resp = await self.client.search(index=self.index_name, body=dsl)
            
            total = resp["hits"]["total"]["value"]
            hits = resp["hits"]["hits"]
            
            items = []
            for hit in hits:
                source = hit["_source"]
                # 处理高亮
                highlight = hit.get("highlight", {})
                if "title" in highlight:
                    source["title_highlight"] = highlight["title"][0]
                if "abstract" in highlight:
                    source["abstract_highlight"] = highlight["abstract"][0]
                    
                items.append(source)
                
            return {
                "total": total,
                "page": page,
                "size": size,
                "items": items
            }
            
        except Exception as e:
            global_logger.error("Elasticsearch", f"搜索失败: {e}")
            return {"total": 0, "items": [], "error": str(e)}

    async def sync_all_data(self, session: AsyncSession):
        """
        全量同步 PostgreSQL 稿件数据到 Elasticsearch
        
        Args:
            session: SQLAlchemy AsyncSession
        """
        if not self.client:
            await self.start()
            if not self.client:
                global_logger.error("Elasticsearch", "服务未就绪，无法同步")
                return

        global_logger.info("Elasticsearch", "开始全量同步稿件数据...")
        start_time = datetime.now()
        
        try:
            # 查询所有已发布的稿件
            # 注意：如果数据量巨大，应使用 stream 或分页查询
            stmt = (
                select(Manuscript)
                .where(Manuscript.status == "published")
                .where(Manuscript.is_deleted == False)
            )
            
            result = await session.execute(stmt)
            manuscripts = result.scalars().all()
            
            actions = []
            for manuscript in manuscripts:
                doc = self._model_to_doc(manuscript)
                action = {
                    "_index": self.index_name,
                    "_id": str(manuscript.manuscript_id),
                    "_source": doc
                }
                actions.append(action)
                
            if actions:
                # 使用 bulk 批量写入
                success, failed = await helpers.async_bulk(self.client, actions, stats_only=True)
                global_logger.info("Elasticsearch", f"同步完成。成功: {success}, 失败: {failed}")
            else:
                global_logger.info("Elasticsearch", "没有需要同步的数据")
                
            duration = (datetime.now() - start_time).total_seconds()
            global_logger.info("Elasticsearch", f"同步耗时: {duration:.2f}秒")
            
        except Exception as e:
            global_logger.exception("Elasticsearch", f"全量同步失败: {e}")

# 全局单例
elasticsearch_service = ElasticsearchService()
