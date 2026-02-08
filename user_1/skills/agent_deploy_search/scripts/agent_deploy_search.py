"""
Agent Deploy Search Skill
搜索 GitHub 上适合 Agent 部署的开源项目，带有相关性评分
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
import requests

from ...base import Skill, SkillContext, SkillResult, SkillStatus
from ...registry import register_skill


class AgentDeploySearcher:
    """Agent 部署项目搜索器"""

    # Agent 相关关键词
    AGENT_KEYWORDS = [
        'agent', 'llm', 'ai', 'langchain', 'llamaindex',
        'autonomous', 'gpt', 'openai', 'anthropic', 'claude',
        'crewai', 'auto-gpt', 'babyagi', 'semantic kernel',
        'chainlit', 'streamlit', 'gradio', 'fastapi',
        'vector', 'embedding', 'rag', 'retrieval'
    ]

    def __init__(self, token: str):
        self.token = token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def search_agent_projects(
        self,
        query: str,
        language: Optional[str] = "Python",
        sort: str = "stars",
        per_page: int = 10,
        min_stars: int = 0,
        deployment_ready: bool = False
    ) -> Dict[str, Any]:
        """
        搜索 Agent 相关项目

        Args:
            query: 搜索关键词
            language: 编程语言
            sort: 排序方式
            per_page: 返回数量
            min_stars: 最小星标数
            deployment_ready: 只返回部署就绪的项目
        """
        search_query = query
        if language:
            search_query += f" language:{language}"
        if min_stars > 0:
            search_query += f" stars:>={min_stars}"

        url = f"{self.api_base}/search/repositories"
        params = {
            "q": search_query,
            "sort": sort,
            "order": "desc",
            "per_page": per_page * 2  # 多搜索一些，便于过滤
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=15)
            response.raise_for_status()

            data = response.json()
            projects = []

            for item in data.get("items", []):
                project = self._parse_project(item)

                # 计算 Agent 相关性评分
                project["relevance_score"] = self._calculate_relevance_score(project)

                # 获取部署信息
                deployment_hints = self._check_deployment_files(
                    item["full_name"],
                    item.get("default_branch", "main")
                )
                project["deployment_hints"] = deployment_hints
                project["deployment"] = self._get_deployment_tags(deployment_hints)

                # 部署就绪过滤
                if deployment_ready:
                    if not any([
                        deployment_hints.get("has_dockerfile"),
                        deployment_hints.get("has_docker_compose"),
                        deployment_hints.get("has_kubernetes")
                    ]):
                        continue

                projects.append(project)

            # 按相关性排序
            projects.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)

            # 计算统计信息
            agent_relevant = [p for p in projects if p.get("relevance_score", 0) > 50]
            avg_stars = sum(p.get("stars", 0) for p in projects) // max(len(projects), 1)

            return {
                "projects": projects[:per_page],
                "total_found": data.get("total_count", 0),
                "agent_relevant_count": len(agent_relevant),
                "query": query,
                "avg_stars": avg_stars
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"API 请求失败: {str(e)}", "projects": []}

    def _parse_project(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """解析项目信息"""
        return {
            "name": item["name"],
            "full_name": item["full_name"],
            "description": item.get("description") or "无描述",
            "url": item["html_url"],
            "clone_url": item["clone_url"],
            "ssh_url": item["ssh_url"],
            "stars": item["stargazers_count"],
            "forks": item["forks_count"],
            "language": item.get("language") or "未知",
            "updated_at": item["updated_at"],
            "license": item.get("license", {}).get("name", "无许可证") if item.get("license") else "无许可证",
            "topics": item.get("topics", []),
            "default_branch": item.get("default_branch", "main")
        }

    def _calculate_relevance_score(self, project: Dict[str, Any]) -> int:
        """计算 Agent 相关性评分 (0-100)"""
        score = 0
        text = (
            project.get("name", "") + " " +
            project.get("description", "") + " " +
            " ".join(project.get("topics", []))
        ).lower()

        # 1. 关键词匹配 (30%)
        keyword_matches = sum(1 for kw in self.AGENT_KEYWORDS if kw in text)
        score += min((keyword_matches / len(self.AGENT_KEYWORDS)) * 30, 30)

        # 2. 活跃度 (25%)
        updated_at = project.get("updated_at")
        if updated_at:
            try:
                update_date = datetime.fromisoformat(updated_at.replace("Z", "+00:00"))
                now = datetime.now(timezone.utc)
                days_since = (now - update_date).days
                if days_since < 30:
                    score += 25
                elif days_since < 90:
                    score += 20
                elif days_since < 180:
                    score += 15
                elif days_since < 365:
                    score += 8
            except:
                pass

        # 3. 星标分数 (25%)
        stars = project.get("stars", 0)
        if stars >= 10000:
            score += 25
        elif stars >= 5000:
            score += 20
        elif stars >= 1000:
            score += 15
        elif stars >= 500:
            score += 10
        elif stars >= 100:
            score += 5

        # 4. 技术栈匹配 (20%)
        language = project.get("language", "")
        mainstream_languages = ["Python", "TypeScript", "JavaScript", "Go", "Rust"]
        if language in mainstream_languages:
            score += 20

        return min(int(score), 100)

    def _check_deployment_files(self, full_name: str, branch: str) -> Dict[str, bool]:
        """检查项目是否包含部署相关文件"""
        hints = {
            "has_dockerfile": False,
            "has_docker_compose": False,
            "has_kubernetes": False,
            "has_ci_cd": False
        }

        try:
            # 获取仓库根目录文件列表
            url = f"{self.api_base}/repos/{full_name}/contents"
            response = requests.get(url, headers=self.headers, timeout=5)

            if response.status_code == 200:
                files = response.json()
                file_names = [f.get("name", "").lower() for f in files if isinstance(f, dict)]

                hints["has_dockerfile"] = any("dockerfile" in name for name in file_names)
                hints["has_docker_compose"] = any("docker-compose" in name or "compose.y" in name for name in file_names)
                hints["has_kubernetes"] = any(name in ["k8s", "kubernetes", "helm", "charts"] for name in file_names)
                hints["has_ci_cd"] = ".github" in file_names or ".gitlab-ci.yml" in file_names

        except:
            pass

        return hints

    def _get_deployment_tags(self, hints: Dict[str, bool]) -> List[str]:
        """获取部署标签"""
        tags = []
        if hints.get("has_dockerfile"):
            tags.append("Docker")
        if hints.get("has_docker_compose"):
            tags.append("Compose")
        if hints.get("has_kubernetes"):
            tags.append("K8s")
        if hints.get("has_ci_cd"):
            tags.append("CI/CD")
        return tags if tags else ["Clone"]

    def generate_deployment_guide(self, projects: List[Dict[str, Any]]) -> str:
        """生成部署指南"""
        if not projects:
            return ""

        top = projects[0]
        guide = f"""## 🚀 推荐项目部署指南

### {top.get('full_name')}

**星标**: {top.get('stars', 0)} | **语言**: {top.get('language', 'N/A')} | **相关性**: {top.get('relevance_score', 0)}/100

**描述**: {top.get('description', '无')}

### 克隆项目

```bash
git clone {top.get('clone_url', '')}
cd {top.get('name', 'project')}
```

### 部署方式

"""
        hints = top.get("deployment_hints", {})

        if hints.get("has_dockerfile"):
            guide += """#### Docker 部署

```bash
docker build -t agent-app .
docker run -p 8000:8000 agent-app
```

"""
        if hints.get("has_docker_compose"):
            guide += """#### Docker Compose 部署

```bash
docker-compose up -d
```

"""

        guide += """### 其他推荐项目

"""
        for p in projects[1:4]:
            guide += f"- **{p.get('full_name')}** - {p.get('stars', 0)} ⭐ ({p.get('relevance_score', 0)}/100)\n"

        return guide


@register_skill
class AgentDeploySearchSkill(Skill):
    """
    Agent 部署项目搜索技能
    专门搜索适合 Agent 部署的开源项目，带有相关性评分
    """

    @property
    def name(self) -> str:
        return "agent_deploy_search"

    @property
    def description(self) -> str:
        return "搜索 GitHub 上适合 Agent 部署的开源项目，带有相关性评分和部署指南"

    @property
    def category(self) -> str:
        return "data_collection"

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "query": {"type": "string", "description": "搜索关键词，如 'autonomous agent'"},
            "language": {"type": "string", "description": "编程语言，默认 Python"},
            "sort_by": {"type": "string", "description": "排序: stars/forks/updated", "default": "stars"},
            "max_results": {"type": "integer", "description": "返回数量，默认 10", "default": 10},
            "min_stars": {"type": "integer", "description": "最小星标数", "default": 0},
            "deployment_ready": {"type": "boolean", "description": "只返回部署就绪项目", "default": False},
            "get_details": {"type": "boolean", "description": "是否生成部署指南", "default": False}
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "query": "string",
            "total_found": "integer",
            "agent_relevant_count": "integer",
            "avg_stars": "integer",
            "projects": "array",
            "deployment_guide": "string"
        }

    async def execute(self, context: SkillContext) -> SkillResult:
        """执行 Agent 部署项目搜索"""
        start_time = datetime.now()

        try:
            # 获取参数
            query = context.params.get("query")
            if not query:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    error="缺少必填参数: query（搜索关键词）"
                )

            language = context.params.get("language", "Python")
            sort_by = context.params.get("sort_by", "stars")
            max_results = context.params.get("max_results", 10)
            min_stars = context.params.get("min_stars", 0)
            deployment_ready = context.params.get("deployment_ready", False)
            get_details = context.params.get("get_details", False)

            # 获取 GitHub token
            token = context.params.get("github_token") or os.environ.get(
                "GITHUB_TOKEN",
                ""
            )

            searcher = AgentDeploySearcher(token)

            # 搜索项目
            result = searcher.search_agent_projects(
                query=query,
                language=language,
                sort=sort_by,
                per_page=max_results,
                min_stars=min_stars,
                deployment_ready=deployment_ready
            )

            if "error" in result and not result.get("projects"):
                return SkillResult(
                    status=SkillStatus.ERROR,
                    error=result["error"]
                )

            # 生成部署指南
            if get_details and result.get("projects"):
                result["deployment_guide"] = searcher.generate_deployment_guide(result["projects"])

            result["generated_at"] = datetime.now().isoformat()

            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return SkillResult(
                status=SkillStatus.SUCCESS,
                data=result,
                message=f"找到 {result.get('agent_relevant_count', 0)} 个 Agent 相关项目",
                execution_time_ms=execution_time,
                metadata={
                    "query": query,
                    "language": language,
                    "deployment_ready": deployment_ready
                }
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                execution_time_ms=execution_time
            )
