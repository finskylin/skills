---
name: baidu-homepage-query
display_name: Baidu Homepage Query
description: 创建一个名为'baidu-homepage-query'的技能，功能是抓取百度首页(www.baidu.com)的内容和热搜新闻。使用web_search或toolbox_execute的playwright功能来抓取页面内容，返回首页的热搜榜单、新闻标题和链接。技能描述：查询百度首页热搜和新闻
category: dynamic
priority: 50
dynamic: true
skill_type: workflow
created_at: "2026-02-08T15:14:54.486586Z"
---
# Baidu Homepage Query

## 概述
创建一个名为'baidu-homepage-query'的技能，功能是抓取百度首页(www.baidu.com)的内容和热搜新闻。使用web_search或toolbox_execute的playwright功能来抓取页面内容，返回首页的热搜榜单、新闻标题和链接。技能描述：查询百度首页热搜和新闻

## 执行流程
```yaml
steps:
  - name: 步骤1_信息搜索
    skill: web_search
    params:
      query: "{{input.query}}"
      mode: intelligent
  - name: 步骤2_结果汇总
    action: llm_summarize
    prompt: |
      请根据以下数据生成分析报告：
      {{steps.步骤1_信息搜索.results}}
```
