---
name: jd-homepage-query
display_name: Jd Homepage Query
description: 创建一个名为'jd-homepage-query'的技能，功能是抓取京东首页(www.jd.com)的内容和商品信息。使用web_search或toolbox_execute的playwright功能来抓取页面内容，返回首页的热门商品、促销活动、商品价格等信息。技能描述：查询京东首页商品和活动信息
category: dynamic
priority: 50
dynamic: true
skill_type: workflow
created_at: "2026-02-08T15:53:25.114597Z"
---
# Jd Homepage Query

## 概述
创建一个名为'jd-homepage-query'的技能，功能是抓取京东首页(www.jd.com)的内容和商品信息。使用web_search或toolbox_execute的playwright功能来抓取页面内容，返回首页的热门商品、促销活动、商品价格等信息。技能描述：查询京东首页商品和活动信息

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
