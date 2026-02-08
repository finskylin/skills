---
name: baidu-hotsearch
display_name: 百度热搜查询
description: 抓取百度首页的热搜榜单和新闻内容，返回实时热搜排名、标题和热度
category: dynamic
priority: 50
dynamic: true
skill_type: workflow
created_at: "2026-02-08T15:23:56.262863Z"
---
# 百度热搜查询

## 概述
抓取百度首页的热搜榜单和新闻内容，返回实时热搜排名、标题和热度

## 执行流程
```yaml
steps:
  - name: 抓取热搜
    skill: toolbox_execute
    params:
      action: script
      language: python
      script: |
        import requests
        import json
        from datetime import datetime
        
        url = "https://top.baidu.com/api/board?platform=wise&tab=realtime"
        headers = {"User-Agent": "Mozilla/5.0"}
        
        try:
            resp = requests.get(url, headers=headers, timeout=10)
            data = resp.json()
            cards = data.get("data", {}).get("cards", [])
            
            hotsearch_list = []
            if cards:
                content = cards[0].get("content", [])
                if content and isinstance(content[0], dict) and "content" in content[0]:
                    items = content[0].get("content", [])
                else:
                    items = content
                
                for i, item in enumerate(items[:20], 1):
                    hotsearch_list.append({
                        "rank": i,
                        "title": item.get("word", ""),
                        "url": item.get("url", "")
                    })
            
            result = {
                "status": "success",
                "update_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "total_count": len(hotsearch_list),
                "hotsearch_list": hotsearch_list,
                "summary": f"获取到 {len(hotsearch_list)} 条百度实时热搜"
            }
            print(json.dumps(result, ensure_ascii=False))
        except Exception as e:
            print(json.dumps({"status": "error", "message": str(e)}, ensure_ascii=False))
```
