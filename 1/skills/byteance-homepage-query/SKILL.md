---
name: byteance-homepage-query
display_name: Byteance Homepage Query
description: 创建一个名为'byteance-homepage-query'的技能，功能是抓取字节跳动官网(www.bytedance.com)的内容和信息。使用web_search或toolbox_execute的playwright功能来抓取页面内容，返回公司介绍、产品服务、最新动态等内容。技能描述：查询字节跳动官网内容和信息
category: dynamic
priority: 50
dynamic: true
skill_type: workflow
created_at: "2026-02-08T15:22:40.908314Z"
---
# Byteance Homepage Query

## 概述
创建一个名为'byteance-homepage-query'的技能，功能是抓取字节跳动官网(www.bytedance.com)的内容和信息。使用web_search或toolbox_execute的playwright功能来抓取页面内容，返回公司介绍、产品服务、最新动态等内容。技能描述：查询字节跳动官网内容和信息

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
