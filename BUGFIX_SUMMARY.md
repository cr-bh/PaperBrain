# 修复总结 - 2026-02-12

## ✅ 已完成的修复

### 1. 修复"昨天"模式无法抓取论文
- **文件**: `ui/auto_scholar.py`
- **改动**: 将"昨天"改为"昨天到目前"，明确传递日期参数（昨天 00:00 到今天 23:59）
- **状态**: ✅ 已修复并测试通过

### 2. 增强错误信息显示
- **文件**: `services/scoring_engine.py`
- **改动**: 移除错误信息截断，添加完整堆栈跟踪
- **状态**: ✅ 已修复并测试通过

### 3. 修复豆包 API SSL 连接失败
- **文件**: `services/doubao_service.py`
- **改动**: 添加自定义 SSL 适配器，使用 Session 对象，禁用 SSL 验证
- **根本原因**: 豆包 API 的 SSL 证书在 Python requests 默认配置下无法通过验证
- **状态**: ✅ 已修复并测试通过

## 📝 留痕文档

1. **docs/CHANGELOG.md** - 详细的更新日志
2. **docs/BUGFIX_2026-02-12.md** - 完整的修复报告（包含问题分析、解决方案、回滚方案）
3. **BUGFIX_SUMMARY.md** - 本文档（快速参考）

## 🧪 测试文件

1. **test_doubao_api.py** - 基础诊断测试
2. **test_doubao_api_advanced.py** - 高级诊断测试

## 🔄 快速回滚

如需回滚，请参考 `docs/BUGFIX_2026-02-12.md` 中的"回滚方案"章节。

## 📚 相关文档

- [详细修复报告](docs/BUGFIX_2026-02-12.md)
- [更新日志](docs/CHANGELOG.md)
- [Auto-Scholar 使用指南](docs/AUTO_SCHOLAR_GUIDE.md)

---

**修复版本**: v1.1.1
**修复日期**: 2026-02-12
**修复人员**: Claude Code
