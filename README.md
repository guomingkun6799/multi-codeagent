# MyCodeAgent

轻量级多Agent代码开发平台 - 基于 CraftAI 理念的现代化实现

## 特性

- 多Agent协作系统
- 简洁的4阶段工作流
- 统一LLM客户端
- 实体驱动的项目管理

## 快速开始

```bash
# 安装
pip install -e ".[dev]"

# 运行
mycodeagent --help
```

## 项目结构

```
mycodeagent/
├── src/mycodeagent/    # 核心代码
│   ├── agents/         # Agent实现
│   ├── core/          # 核心引擎
│   ├── infrastructure/ # 基础设施
│   ├── skills/         # 技能模块
│   └── cli/           # CLI入口
├── tests/             # 测试代码
└── docs/              # 文档
```

## License

MIT
