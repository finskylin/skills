---
name: github_project_search
display_name: GitHub 开源项目搜索
description: |
  【功能】搜索 GitHub 上的开源项目，获取项目信息、克隆地址、部署说明等
  【数据源】GitHub REST API
  【输出数据】项目名称、描述、星标数、克隆地址、README 内容、部署提示（Docker/K8s/CI/CD）
  【耗时】~5-15秒
  【适用场景】用户问"搜索开源项目"、"找XX项目"、"GitHub搜索"时使用
category: data_collection
priority: 70
ui_components:
  - component: table
    condition: default
    priority: 1
    data_hints:
      - has_projects_array
    title: 搜索结果
    data_key: projects
    columns:
      - key: full_name
        label: 项目名称
      - key: description
        label: 描述
      - key: stars
        label: Stars
        format: number
      - key: language
        label: 语言
      - key: url
        label: 链接
        format: link
  - component: markdown
    condition: get_details=true
    priority: 2
    title: 项目详情
    data_key: project_details
intents:
  - search
  - github
  - open_source
keywords:
  - GitHub
  - 开源
  - 项目
  - 搜索
  - 克隆
  - 部署
  - Docker
  - 部署
license: MIT
time_estimates:
  default:
    min: 5
    max: 15
    desc: "GitHub 项目搜索"
---

# GitHub 开源项目搜索技能

## 概述

本技能提供 GitHub 开源项目搜索功能，支持：

1. 按关键词搜索 GitHub 项目
2. 按编程语言过滤
3. 获取项目详细信息（README、部署文件）
4. 识别部署相关配置（Docker、Kubernetes、CI/CD）

## 核心功能

### 1. 项目搜索

根据关键词和编程语言搜索 GitHub 项目，支持按 stars/forks/updated 排序。

### 2. 项目详情

获取项目的详细信息：
- 基本信息（名称、描述、星标数、语言）
- README 内容
- 部署文件检测（Dockerfile、docker-compose、Kubernetes）
- CI/CD 配置检测

### 3. 部署提示

自动识别项目是否包含：
- Dockerfile
- docker-compose.yml
- Kubernetes 配置
- GitHub Actions / GitLab CI

## 使用示例

### 1. 基础搜索

```json
{
  "tool": "execute_skill_with_ui",
  "usage": {
    "skill_name": "github_project_search",
    "params": {
      "query": "fastapi agent",
      "language": "Python",
      "max_results": 10
    }
  }
}
```

### 2. 获取详细部署信息

```json
{
  "tool": "execute_skill_with_ui",
  "usage": {
    "skill_name": "github_project_search",
    "params": {
      "query": "telegram bot",
      "language": "Python",
      "sort_by": "stars",
      "max_results": 5,
      "get_details": true
    }
  }
}
```

### 3. 按更新时间搜索

```json
{
  "tool": "execute_skill_with_ui",
  "usage": {
    "skill_name": "github_project_search",
    "params": {
      "query": "react dashboard",
      "sort_by": "updated",
      "max_results": 10
    }
  }
}
```

## 输入参数

| 参数        | 类型   | 必填 | 描述                                    |
| ----------- | ------ | ---- | --------------------------------------- |
| query       | string | 是   | 搜索关键词，如 "fastapi agent"          |
| language    | string | 否   | 编程语言过滤，如 "Python", "JavaScript" |
| sort_by     | string | 否   | 排序方式: stars(默认)/forks/updated     |
| max_results | int    | 否   | 返回结果数量，默认 10                   |
| get_details | bool   | 否   | 是否获取详细部署信息，默认 false        |

## 输出字段

### 项目列表字段

| 字段        | 类型   | 描述                   |
| ----------- | ------ | ---------------------- |
| name        | string | 项目名称               |
| full_name   | string | 完整名称 (owner/repo)  |
| description | string | 项目描述               |
| url         | string | 项目地址               |
| clone_url   | string | HTTPS 克隆地址         |
| ssh_url     | string | SSH 克隆地址           |
| stars       | int    | 星标数                 |
| forks       | int    | Fork 数                |
| language    | string | 主要编程语言           |
| license     | string | 开源协议               |
| updated_at  | string | 最后更新时间           |

### 详情字段（get_details=true）

| 字段             | 类型   | 描述                     |
| ---------------- | ------ | ------------------------ |
| readme           | string | README 内容              |
| deployment_hints | object | 部署提示                 |
| has_dockerfile   | bool   | 是否包含 Dockerfile      |
| has_docker_compose | bool | 是否包含 docker-compose  |
| has_kubernetes   | bool   | 是否包含 K8s 配置        |
| has_ci_cd        | bool   | 是否包含 CI/CD 配置      |

## 错误处理

- GitHub API 限流时返回友好提示
- 无搜索结果时返回空列表
- 网络异常时返回错误信息

## 数据源

- GitHub REST API (https://api.github.com)

## 环境变量

- `GITHUB_TOKEN`: GitHub Personal Access Token（可选，提高 API 限流）
