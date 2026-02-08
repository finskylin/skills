---
name: agent_deploy_search
display_name: Agent 部署项目搜索
description: |
  【功能】搜索 GitHub 上适合 Agent 部署的开源项目
  【数据源】GitHub REST API
  【输出数据】项目名称、描述、星标数、克隆地址、部署提示（Docker/K8s/CI/CD）、Agent 相关性评分
  【耗时】~5-15秒
  【适用场景】用户问"搜索Agent项目"、"找部署框架"、"GitHub Agent搜索"时使用
category: composite
priority: 75
skill_type: workflow
intents:
  - search
  - deploy
  - agent
  - open_source
keywords:
  - Agent
  - 部署
  - GitHub
  - 开源
  - FastAPI
  - LangChain
  - LlamaIndex
  - 框架
  - 微服务
ui_components:
  - component: summary_card
    condition: default
    priority: 1
    title: 搜索概览
    fields:
      - key: total_found
        label: 找到项目
        format: number
      - key: agent_relevant_count
        label: Agent 相关
        format: number
      - key: query
        label: 搜索关键词
      - key: avg_stars
        label: 平均 Stars
        format: number

  - component: table
    condition: default
    priority: 2
    title: Agent 部署项目推荐
    data_key: projects
    columns:
      - key: name
        label: 项目名称
        highlight: true
      - key: description
        label: 描述
        width: 300
      - key: stars
        label: Stars
        format: number
        width: 80
      - key: relevance_score
        label: 相关性
        format: badge
        width: 100
      - key: language
        label: 语言
        width: 80
      - key: deployment
        label: 部署方式
        format: tags
        width: 150
      - key: clone_url
        label: 克隆地址
        format: link
        width: 200

  - component: markdown
    condition: get_details=true
    priority: 3
    title: 部署指南
    data_key: deployment_guide

dynamic: true
user_id: "{{ user_id }}"
is_shared: true
license: MIT
time_estimates:
  default:
    min: 5
    max: 15
    desc: "GitHub Agent 项目搜索"
---

# Agent 部署项目搜索技能

## 概述

本技能专门用于搜索适合 Agent 部署的开源项目，重点关注：

1. **Agent 框架**: LangChain、LlamaIndex、AutoGPT、BabyAGI 等
2. **后端框架**: FastAPI、Flask、Django 等
3. **微服务架构**: Kubernetes、Docker Compose 配置
4. **LLM 工具**: OpenAI SDK、Anthropic SDK、HuggingFace 等

## 核心功能

### 1. 智能 Agent 项目搜索

根据关键词搜索，并自动过滤和评分与 Agent 部署相关的项目：

- **Agent 框架类**: LangChain、LlamaIndex、CrewAI、AgentGPT
- **API 服务类**: FastAPI、Flask、Tornado、Sanic
- **向量数据库**: ChromaDB、Pinecone、Weaviate、Qdrant
- **LLM 集成**: OpenAI、Anthropic、 Cohere、本地 LLM

### 2. 部署方式识别

自动检测项目是否包含：

- `Dockerfile` - Docker 容器化部署
- `docker-compose.yml` - 本地开发环境
- `Kubernetes` manifests - 生产环境部署
- `GitHub Actions` / `GitLab CI` - CI/CD 流水线
- `requirements.txt` / `poetry.lock` / `Pipfile` - Python 依赖管理

### 3. 相关性评分

根据以下维度计算 Agent 相关性评分 (0-100)：

| 维度 | 权重 | 说明 |
|-----|------|-----|
| 关键词匹配 | 30% | 名称/描述包含 agent、llm、ai 等关键词 |
| 部署就绪度 | 25% | 包含 Docker/K8s 等部署配置 |
| 活跃度 | 20% | 最近更新时间、星标增长 |
| 文档完整度 | 15% | README、部署文档 |
| 技术栈匹配 | 10% | Python/FastAPI 等主流技术 |

## 工作流程

```mermaid
flowchart LR
    A[接收搜索关键词] --> B[调用 GitHub API]
    B --> C[获取项目列表]
    C --> D[过滤 Agent 相关项目]
    D --> E[计算相关性评分]
    E --> F[检测部署配置]
    F --> G[生成部署指南]
    G --> H[返回结果]
```

## 使用示例

### 1. 搜索 LangChain 项目

```json
{
  "tool": "execute_skill_with_ui",
  "usage": {
    "skill_name": "agent_deploy_search",
    "params": {
      "query": "langchain",
      "max_results": 10
    }
  }
}
```

### 2. 搜索 FastAPI Agent 框架

```json
{
  "tool": "execute_skill_with_ui",
  "usage": {
    "skill_name": "agent_deploy_search",
    "params": {
      "query": "fastapi agent",
      "language": "Python",
      "max_results": 15,
      "get_details": true
    }
  }
}
```

### 3. 搜索向量数据库

```json
{
  "tool": "execute_skill_with_ui",
  "usage": {
    "skill_name": "agent_deploy_search",
    "params": {
      "query": "vector database",
      "language": "Python",
      "sort_by": "stars",
      "max_results": 10
    }
  }
}
```

### 4. 搜索 LLM 代理项目

```json
{
  "tool": "execute_skill_with_ui",
  "usage": {
    "skill_name": "agent_deploy_search",
    "params": {
      "query": "autonomous agent",
      "max_results": 20,
      "get_details": true
    }
  }
}
```

## 输入参数

| 参数         | 类型    | 必填 | 描述                                      | 默认值    |
| ------------ | ------- | ---- | ----------------------------------------- | --------- |
| query        | string  | 是   | 搜索关键词，如 "fastapi agent"            | -         |
| language     | string  | 否   | 编程语言过滤                              | Python    |
| sort_by      | string  | 否   | 排序: stars/forks/updated                 | stars     |
| max_results  | int     | 否   | 返回结果数量                              | 10        |
| get_details  | boolean | 否   | 是否获取详细部署信息                      | false     |
| min_stars    | int     | 否   | 最小星标数过滤                            | 0         |
| deployment_ready | boolean | 否   | 只返回包含部署配置的项目                  | false     |

## 输出字段

### 概览字段 (summary_card)

| 字段                 | 类型   | 描述                     |
| -------------------- | ------ | ------------------------ |
| total_found          | int    | 搜索结果总数             |
| agent_relevant_count | int    | Agent 相关项目数         |
| query                | string | 搜索关键词               |
| avg_stars            | int    | 平均星标数               |

### 项目列表字段 (table)

| 字段            | 类型   | 描述                     |
| --------------- | ------ | ------------------------ |
| name            | string | 项目名称                 |
| description     | string | 项目描述                 |
| stars           | int    | 星标数                   |
| relevance_score | int    | Agent 相关性评分 (0-100) |
| language        | string | 主要编程语言             |
| deployment      | string | 部署方式标签             |
| clone_url       | string | Git 克隆地址             |

### 部署指南字段 (get_details=true)

| 字段            | 类型   | 描述                     |
| --------------- | ------ | ------------------------ |
| has_dockerfile  | bool   | 是否包含 Dockerfile      |
| has_docker_compose | bool | 是否包含 docker-compose  |
| has_kubernetes  | bool   | 是否包含 K8s 配置        |
| has_ci_cd       | bool   | 是否包含 CI/CD 配置      |
| readme          | string | README 内容              |
| quick_start     | string | 快速开始命令             |

## 相关性评分算法

```python
def calculate_relevance_score(project):
    score = 0

    # 关键词匹配 (30%)
    keywords = ['agent', 'llm', 'ai', 'langchain', 'llamaindex',
                'autonomous', 'gpt', 'openai', 'anthropic']
    text = (project.name + ' ' + project.description).lower()
    keyword_matches = sum(1 for kw in keywords if kw in text)
    score += (keyword_matches / len(keywords)) * 30

    # 部署就绪度 (25%)
    deployment_score = 0
    if project.has_dockerfile:
        deployment_score += 10
    if project.has_docker_compose:
        deployment_score += 8
    if project.has_kubernetes:
        deployment_score += 5
    if project.has_ci_cd:
        deployment_score += 2
    score += deployment_score

    # 活跃度 (20%)
    days_since_update = (now - project.updated_at).days
    if days_since_update < 30:
        score += 20
    elif days_since_update < 90:
        score += 15
    elif days_since_update < 180:
        score += 10

    # 文档完整度 (15%)
    if project.readme:
        score += 10
    if project.has_wiki or project.has_website:
        score += 5

    # 技术栈匹配 (10%)
    if project.language in ['Python', 'TypeScript', 'JavaScript']:
        score += 10

    return min(int(score), 100)
```

## 推荐搜索关键词

### Agent 框架
- `langchain`
- `llamaindex`
- `autogpt`
- `agentgpt`
- `crewai`
- `semantic kernel`

### 后端框架
- `fastapi agent`
- `flask agent`
- `django llm`

### 向量数据库
- `vector database`
- `chromadb`
- `pinecone`
- `weaviate`
- `qdrant`

### LLM 工具
- `openai api`
- `anthropic sdk`
- `huggingface`
- `local llm`

## 错误处理

- GitHub API 限流时返回友好提示和重试建议
- 无搜索结果时返回空列表并建议调整关键词
- 网络异常时返回错误信息和降级方案

## 数据源

- GitHub REST API (https://api.github.com/search/repositories)
- GitHub Contents API (获取部署文件)

## 环境变量

- `GITHUB_TOKEN`: GitHub Personal Access Token（推荐，提高 API 限流）

## 依赖技能

- `github_project_search` - 基础 GitHub 项目搜索功能
