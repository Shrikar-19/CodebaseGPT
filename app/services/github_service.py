
import requests
from urllib.parse import urlparse
from bs4 import BeautifulSoup
import os
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")


def parse_github_url(repo_url: str):
    parsed_url = urlparse(str(repo_url))

    if parsed_url.hostname != "github.com":
        raise ValueError("Please provide a valid GitHub repository URL")

    path_parts = parsed_url.path.strip("/").split("/")

    if len(path_parts) < 2:
        raise ValueError("Invalid GitHub repository URL")

    owner = path_parts[0]
    repo = path_parts[1].removesuffix(".git")

    return {
        "owner": owner,
        "repo": repo
    }


def get_repository_details(repo_url: str):
    repository = parse_github_url(repo_url)

    owner = repository["owner"]
    repo = repository["repo"]

    api_url = f"https://api.github.com/repos/{owner}/{repo}"

    headers = {}

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    headers["Accept"] = "application/vnd.github+json"

    response = requests.get(
        api_url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    return {
        "name": data["name"],
        "full_name": data["full_name"],
        "description": data["description"],
        "html_url": data["html_url"],
        "default_branch": data["default_branch"],
        "language": data["language"],
        "stars": data["stargazers_count"]
    }


def get_repository_contents(repo_url: str, path: str = ""):
    repository = parse_github_url(repo_url)

    owner = repository["owner"]
    repo = repository["repo"]

    api_url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

    response = requests.get(api_url, timeout=10)
    response.raise_for_status()

    return response.json()


def get_repository_file_tree(repo_url: str, path: str = ""):
    repository = parse_github_url(repo_url)

    owner = repository["owner"]
    repo = repository["repo"]

    repository_details = get_repository_details(repo_url)
    branch = repository_details["default_branch"]

    api_url = (
        f"https://api.github.com/repos/{owner}/{repo}"
        f"/git/trees/{branch}?recursive=1"
    )

    headers = {}

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    headers["Accept"] = "application/vnd.github+json"

    response = requests.get(
        api_url,
        headers=headers,
        timeout=30
    )

    response.raise_for_status()

    tree = response.json()["tree"]

    file_tree = []

    for item in tree:
        if path and not item["path"].startswith(path + "/"):
            continue

        file_tree.append({
            "name": item["path"].split("/")[-1],
            "path": item["path"],
            "type": "file" if item["type"] == "blob" else "dir"
        })

    return file_tree

def get_file_content(repo_url: str, file_path: str):
    repository = parse_github_url(repo_url)

    owner = repository["owner"]
    repo = repository["repo"]

    api_url = (
        f"https://api.github.com/repos/{owner}/{repo}"
        f"/contents/{file_path}"
    )

    headers = {}

    if GITHUB_TOKEN:
        headers["Authorization"] = f"Bearer {GITHUB_TOKEN}"

    headers["Accept"] = "application/vnd.github+json"

    response = requests.get(
        api_url,
        headers=headers,
        timeout=10
    )

    response.raise_for_status()

    data = response.json()

    if data.get("type") != "file":
        raise ValueError("The requested path is not a file")

    import base64

    content = base64.b64decode(data["content"]).decode("utf-8")

    return {
        "name": data["name"],
        "path": data["path"],
        "content": content
    }


def clean_readme_content(content: str):
    soup = BeautifulSoup(content, "html.parser")

    # Remove unnecessary HTML elements
    for element in soup(["img", "svg", "style", "script"]):
        element.decompose()

    # Convert HTML to readable text
    clean_content = soup.get_text(separator="\n")

    # Remove Markdown formatting
    import re

    clean_content = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", clean_content)
    clean_content = re.sub(r"!\[([^\]]*)\]\([^)]+\)", "", clean_content)
    clean_content = re.sub(r"\*\*(.*?)\*\*", r"\1", clean_content)
    clean_content = re.sub(r"__(.*?)__", r"\1", clean_content)
    clean_content = re.sub(r"\*(.*?)\*", r"\1", clean_content)
    clean_content = re.sub(r"_(.*?)_", r"\1", clean_content)
    clean_content = re.sub(r"`{1,3}(.*?)`{1,3}", r"\1", clean_content)
    clean_content = re.sub(r"^#{1,6}\s*", "", clean_content, flags=re.MULTILINE)
    clean_content = re.sub(r"^\s*[-*+]\s+", "", clean_content, flags=re.MULTILINE)

    # Remove extra blank lines
    lines = [
        line.strip()
        for line in clean_content.splitlines()
        if line.strip()
    ]

    return "\n".join(lines)



def get_code_files(repo_url: str):
    file_tree = get_repository_file_tree(repo_url)

    supported_extensions = (
        ".py",
        ".js",
        ".jsx",
        ".ts",
        ".tsx",
        ".java",
        ".cpp",
        ".c",
        ".h",
        ".cs",
        ".go",
        ".rs",
        ".php",
        ".rb",
        ".swift",
        ".kt",
    )

    ignored_directories = (
        "docs/",
        "docs_src/",
        "tests/",
        "test/",
        "examples/",
        "node_modules/",
        "vendor/",
        ".github/",
    )

    code_files = [
        file
        for file in file_tree
        if file["type"] == "file"
        and file["name"].lower().endswith(supported_extensions)
        and not any(
            file["path"].startswith(directory)
            for directory in ignored_directories
        )
    ]

    # Prioritize Python application files
    code_files.sort(
        key=lambda file: (
            0 if file["name"].endswith(".py") else 1,
            file["path"]
        )
    )

    return code_files

def get_all_code_contents(repo_url: str, max_files: int = 10):
    code_files = get_code_files(repo_url)

    all_code_contents = []

    for file in code_files[:max_files]:
        try:
            file_content = get_file_content(
                repo_url,
                file["path"]
            )

            all_code_contents.append({
                "name": file["name"],
                "path": file["path"],
                "content": file_content["content"]
            })

        except Exception as error:
            print(f"Error fetching {file['path']}: {error}")

    return all_code_contents




