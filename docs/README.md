# PaperBrain 文档中心

> **欢迎来到 PaperBrain 文档中心！**
>
> 本目录包含项目的所有文档，按功能分类组织。
>
> 📖 **文档管理规范**: [principle.md](principle.md)

---

## 📚 快速导航

### 🎯 新手入门
- [项目 README](../README.md) - 项目概述和快速开始
- [配置指南](guides/CONFIGURATION.md) - 环境配置说明
- [Auto-Scholar 使用指南](guides/AUTO_SCHOLAR_GUIDE.md) - 论文监控功能使用

### 🔧 开发者文档
- [技术文档](technical/TECHNICAL_DOCUMENTATION.md) - 完整技术架构
- [产品需求文档](technical/PRD.md) - 产品设计和需求

### 📝 版本历史
- [主更新日志](CHANGELOG.md) - 所有版本汇总
- [v1.5.0 更新日志](changelogs/v1.5.0/UPDATE_LOG.md) - 最新版本

---

## 📖 用户指南 (guides/)

面向最终用户的使用说明文档

| 文档 | 说明 |
|------|------|
| [Auto-Scholar 使用指南](guides/AUTO_SCHOLAR_GUIDE.md) | 论文监控系统使用说明 |
| [配置指南](guides/CONFIGURATION.md) | 环境变量和系统配置 |

---

## 🔧 技术文档 (technical/)

面向开发者的技术架构和 API 文档

| 文档 | 说明 |
|------|------|
| [技术文档](technical/TECHNICAL_DOCUMENTATION.md) | 完整的系统架构、数据模型、API 接口 |
| [产品需求文档](technical/PRD.md) | 产品功能需求和设计 |

---

## 📝 更新日志 (changelogs/)

记录每个版本的变更历史

### 主日志
- [CHANGELOG.md](CHANGELOG.md) - 所有版本的更新汇总

### 版本详情

#### v1.5.0 (2026-02-28) - 最新版本
- [更新日志](changelogs/v1.5.0/UPDATE_LOG.md) - API 设置页面与多格式 LLM 支持

#### v1.4.0 (2026-02-13)
- [更新日志](changelogs/v1.4.0/UPDATE_LOG.md) - 数据分析与可视化功能
- [已知问题](changelogs/v1.4.0/KNOWN_ISSUES.md) - 当前版本已知问题
- [调试日志](changelogs/v1.4.0/DEBUG_LOG.md) - 开发调试记录

#### v1.3.1 (2026-02-13)
- [更新日志](changelogs/v1.3.1/UPDATE_LOG.md) - PDF 元数据提取修复
- [机构更新说明](changelogs/v1.3.1/INSTITUTION_UPDATE.md) - 机构识别功能优化

#### v1.3.0 (2026-02-12)
- [更新日志](changelogs/v1.3.0/UPDATE_LOG.md) - Venue 和 Institutions 提取功能

---

## 🎯 功能说明 (features/)

详细说明特定功能的设计和实现

| 文档 | 说明 |
|------|------|
| [顶会机构识别](features/VENUE_INSTITUTION.md) | 自动识别顶级会议和知名机构 |
| [论文导入功能](features/IMPORT_FEATURE.md) | 从 Auto-Scholar 导入论文到主库 |
| [API 设置与配置](features/API_SETTINGS.md) | 图形化 API 配置管理 |

---

## 🛠️ 开发文档 (development/)

记录开发过程中的迭代、Bug 修复、计划等

### 迭代日志 (iteration_logs/)
- [2026-02-28](development/iteration_logs/2026-02-28.md) - v1.5.0 API 设置页面
- [2026-02-13](development/iteration_logs/2026-02-13.md) - v1.4.0 开发迭代

### Bug 修复日志 (bugfix_logs/)
- [2026-03-23](development/bugfix_logs/2026-03-23-qwen3-structured-notes.md) - qwen3 结构化笔记全为空（三层根因分析 + Friday One-API 支持）
- [2026-02-28](development/bugfix_logs/2026-02-28.md) - v1.5.1 导入导航 + 总结截断
- [2026-02-12](development/bugfix_logs/2026-02-12.md) - v1.1.1 Bug 修复

### 开发指南
- [双仓库管理指南](development/REPO_MANAGEMENT_GUIDE.md) - 私有/公开仓库管理与推送流程

### 开发计划 (plans/)
- 暂无

---

## 📦 归档文档 (archive/)

过期或废弃的文档

| 文档 | 归档原因 |
|------|---------|
| BUGFIX_SUMMARY.md | 已整合到 CHANGELOG.md |
| FEATURE_SUMMARY.md | 已整合到 CHANGELOG.md |
| IMPLEMENTATION_SUMMARY.md | 已整合到版本更新日志 |
| TASK_VENUE_INSTITUTION.md | 功能已完成，详见 features/VENUE_INSTITUTION.md |

---

## 🖼️ 图片资源 (images/)

文档中使用的图片和截图

- 暂无

---

## 📐 文档规范

所有文档遵循 [文档管理规范](principle.md)，包括：

- 📁 目录结构规范
- 📝 文档分类规则
- 🔄 文档更新流程
- ✍️ Markdown 编写规范
- 🔍 文档审查清单

---

## 🔍 快速查找

### 按主题查找

- **安装配置**: [配置指南](guides/CONFIGURATION.md)
- **功能使用**: [Auto-Scholar 使用指南](guides/AUTO_SCHOLAR_GUIDE.md)
- **技术架构**: [技术文档](technical/TECHNICAL_DOCUMENTATION.md)
- **版本更新**: [CHANGELOG.md](CHANGELOG.md)
- **功能详解**: [features/](features/)
- **开发记录**: [development/](development/)

### 按角色查找

- **用户**: [guides/](guides/) - 使用指南
- **开发者**: [technical/](technical/) - 技术文档
- **维护者**: [development/](development/) - 开发文档

---

## 📞 贡献文档

如需添加或修改文档，请：

1. 阅读 [文档管理规范](principle.md)
2. 按照规范创建或修改文档
3. 更新本索引文件
4. 提交 Pull Request

---

## 📌 注意事项

- 所有文档使用 Markdown 格式
- 遵循文档管理规范
- 保持文档更新和准确
- 及时归档过期文档

---

**最后更新**: 2026-02-28
**维护者**: PaperBrain Team
