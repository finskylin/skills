"""
GitHub Project Search Skill
搜索 GitHub 开源项目并获取部署相关信息
"""
import os
from typing import Dict, Any, List, Optional
from datetime import datetime
import requests

from ...base import Skill, SkillContext, SkillResult, SkillStatus
from ...registry import register_skill


class GitHubProjectSearcher:
    """GitHub 开源项目搜索器"""

    def __init__(self, token: str):
        self.token = token
        self.api_base = "https://api.github.com"
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def search_projects(
        self,
        query: str,
        language: Optional[str] = None,
        sort: str = "stars",
        order: str = "desc",
        per_page: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索 GitHub 项目

        Args:
            query: 搜索关键词
            language: 编程语言过滤 (如 Python, JavaScript)
            sort: 排序方式 (stars, forks, updated)
            order: 排序顺序 (desc, asc)
            per_page: 返回结果数量
        """
        search_query = query
        if language:
            search_query += f" language:{language}"

        url = f"{self.api_base}/search/repositories"
        params = {
            "q": search_query,
            "sort": sort,
            "order": order,
            "per_page": per_page
        }

        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            projects = []

            for item in data.get("items", []):
                project = {
                    "name": item["name"],
                    "full_name": item["full_name"],
                    "description": item.get("description", "无描述"),
                    "url": item["html_url"],
                    "clone_url": item["clone_url"],
                    "ssh_url": item["ssh_url"],
                    "stars": item["stargazers_count"],
                    "forks": item["forks_count"],
                    "language": item.get("language", "未知"),
                    "updated_at": item["updated_at"],
                    "license": item.get("license", {}).get("name", "无许可证") if item.get("license") else "无许可证",
                    "topics": item.get("topics", []),
                    "is_fork": item["fork"],
                    "has_wiki": item["has_wiki"],
                    "has_pages": item["has_pages"]
                }
                projects.append(project)

            return projects

        except requests.exceptions.RequestException as e:
            return {"error": f"API 请求失败: {str(e)}"}

    def get_project_details(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        获取项目详细信息

        Args:
            owner: 仓库所有者
            repo: 仓库名称
        """
        url = f"{self.api_base}/repos/{owner}/{repo}"

        try:
            # 获取基本信息
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            repo_data = response.json()

            # 获取 README 内容
            readme_url = f"{self.api_base}/repos/{owner}/{repo}/readme"
            readme_response = requests.get(readme_url, headers=self.headers, timeout=10)

            readme_content = ""
            if readme_response.status_code == 200:
                readme_data = readme_response.json()
                # README 内容是 base64 编码的
                import base64
                readme_content = base64.b64decode(readme_data["content"]).decode("utf-8")

            # 获取最新 release 信息
            releases_url = f"{self.api_base}/repos/{owner}/{repo}/releases/latest"
            releases_response = requests.get(releases_url, headers=self.headers, timeout=10)

            release_info = None
            if releases_response.status_code == 200:
                release_data = releases_response.json()
                release_info = {
                    "tag_name": release_data.get("tag_name"),
                    "name": release_data.get("name"),
                    "published_at": release_data.get("published_at"),
                    "download_url": release_data.get("html_url")
                }

            return {
                "basic_info": {
                    "name": repo_data["name"],
                    "full_name": repo_data["full_name"],
                    "description": repo_data.get("description", "无描述"),
                    "url": repo_data["html_url"],
                    "clone_url": repo_data["clone_url"],
                    "ssh_url": repo_data["ssh_url"],
                    "stars": repo_data["stargazers_count"],
                    "forks": repo_data["forks_count"],
                    "watchers": repo_data["subscribers_count"],
                    "open_issues": repo_data["open_issues_count"],
                    "language": repo_data.get("language", "未知"),
                    "created_at": repo_data["created_at"],
                    "updated_at": repo_data["updated_at"],
                    "pushed_at": repo_data["pushed_at"],
                    "size_kb": repo_data["size"],
                    "license": repo_data.get("license", {}).get("name", "无许可证") if repo_data.get("license") else "无许可证",
                    "default_branch": repo_data.get("default_branch", "main"),
                    "is_archived": repo_data["archived"],
                    "homepage": repo_data.get("homepage", ""),
                    "topics": repo_data.get("topics", [])
                },
                "readme": readme_content,
                "latest_release": release_info,
                "deployment_hints": self._extract_deployment_info(readme_content)
            }

        except requests.exceptions.RequestException as e:
            return {"error": f"获取项目详情失败: {str(e)}"}

    def _extract_deployment_info(self, readme: str) -> Dict[str, Any]:
        """从 README 中提取部署相关信息"""
        hints = {
            "has_dockerfile": "Dockerfile" in readme or "docker" in readme.lower(),
            "has_docker_compose": "docker-compose" in readme.lower(),
            "has_kubernetes": "kubernetes" in readme.lower() or "k8s" in readme.lower(),
            "has_ci_cd": any(keyword in readme.lower() for keyword in ["github actions", "gitlab ci", "jenkins", "workflow"]),
            "deployment_keywords": [],
            "env_vars": []
        }

        # 查找常见的部署关键词
        deploy_keywords = ["deploy", "deployment", "production", "staging", "docker", "kubernetes", "helm", "terraform"]
        for keyword in deploy_keywords:
            if keyword in readme.lower():
                hints["deployment_keywords"].append(keyword)

        # 简单的环境变量检测（查找 .env 例子）
        if ".env" in readme or "environment variable" in readme.lower():
            hints["env_vars"] = ["检测到环境变量配置说明"]

        return hints


@register_skill
class GitHubProjectSearchSkill(Skill):
    """
    GitHub 开源项目搜索技能
    搜索 GitHub 项目并获取部署相关信息
    """

    @property
    def name(self) -> str:
        return "github_project_search"

    @property
    def description(self) -> str:
        return "搜索 GitHub 开源项目，获取项目信息、克隆地址、部署说明等"

    @property
    def category(self) -> str:
        return "data_collection"

    @property
    def dependencies(self) -> List[str]:
        return []

    @property
    def input_schema(self) -> Dict[str, Any]:
        return {
            "query": {"type": "string", "description": "搜索关键词，如 'fastapi agent'"},
            "language": {"type": "string", "description": "编程语言过滤，如 'Python', 'JavaScript'"},
            "sort_by": {"type": "string", "description": "排序方式: stars/forks/updated", "default": "stars"},
            "max_results": {"type": "integer", "description": "返回结果数量，默认 10", "default": 10},
            "get_details": {"type": "boolean", "description": "是否获取详细信息（包括 README 和部署信息）", "default": False}
        }

    @property
    def output_schema(self) -> Dict[str, Any]:
        return {
            "query": "string",
            "total_count": "integer",
            "projects": [
                {
                    "name": "string",
                    "full_name": "string",
                    "description": "string",
                    "url": "string",
                    "clone_url": "string",
                    "ssh_url": "string",
                    "stars": "integer",
                    "forks": "integer",
                    "language": "string",
                    "updated_at": "string",
                    "license": "string"
                }
            ],
            "generated_at": "string"
        }

    async def execute(self, context: SkillContext) -> SkillResult:
        """
        执行 GitHub 项目搜索

        Args:
            context: 包含以下参数的上下文
                - query: 搜索关键词（必填）
                - language: 编程语言（可选）
                - sort_by: 排序方式（可选，默认 stars）
                - max_results: 返回结果数量（可选，默认 10）
                - get_details: 是否获取详情（可选，默认 False）

        Returns:
            SkillResult: 包含搜索结果
        """
        start_time = datetime.now()

        try:
            # 获取参数
            query = context.params.get("query")
            if not query:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    error="缺少必填参数: query（搜索关键词）"
                )

            language = context.params.get("language")
            sort_by = context.params.get("sort_by", "stars")
            max_results = context.params.get("max_results", 10)
            get_details = context.params.get("get_details", False)

            # 获取 GitHub token (从环境变量)
            token = context.params.get("github_token") or os.environ.get(
                "GITHUB_TOKEN", ""
            )

            searcher = GitHubProjectSearcher(token)

            # 搜索项目
            projects = searcher.search_projects(
                query=query,
                language=language,
                sort=sort_by,
                per_page=max_results
            )

            if isinstance(projects, dict) and "error" in projects:
                return SkillResult(
                    status=SkillStatus.ERROR,
                    error=projects["error"]
                )

            # 构建结果
            result = {
                "query": query,
                "total_count": len(projects),
                "projects": projects,
                "generated_at": datetime.now().isoformat()
            }

            # 如果需要详细信息，获取前3个项目的详情
            if get_details and projects:
                detailed_projects = []
                for project in projects[:3]:
                    owner, repo = project["full_name"].split("/")
                    details = searcher.get_project_details(owner, repo)
                    if "error" not in details:
                        project["details"] = details
                    detailed_projects.append(project)

                result["projects"] = detailed_projects

            # 计算执行时间
            execution_time = (datetime.now() - start_time).total_seconds() * 1000

            return SkillResult(
                status=SkillStatus.SUCCESS,
                data=result,
                message=f"成功找到 {len(projects)} 个项目",
                execution_time_ms=execution_time,
                metadata={
                    "query": query,
                    "language": language,
                    "sort_by": sort_by,
                    "has_details": get_details
                }
            )

        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds() * 1000
            return SkillResult(
                status=SkillStatus.ERROR,
                error=str(e),
                execution_time_ms=execution_time
            )
