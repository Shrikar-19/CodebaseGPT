
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from app.services.github_service import (
    get_repository_details,
    get_file_content,
    get_repository_file_tree,
    clean_readme_content,
    get_all_code_contents,
)

router = APIRouter()


class RepositoryRequest(BaseModel):
    repo_url: HttpUrl


@router.get("/status")
def api_status():
    return {
        "message": "CodebaseGPT API is running",
        "status": "healthy"
    }


@router.post("/analyze")
def analyze_repository(request: RepositoryRequest):
    try:
        repo_url = str(request.repo_url)

        repository_details = get_repository_details(repo_url)

        readme = get_file_content(
            repo_url,
            "README.md"
        )

        cleaned_readme = clean_readme_content(
            readme["content"]
        )

        file_tree = get_repository_file_tree(repo_url)
        code_contents = get_all_code_contents(
    repo_url,
    max_files=10
)

        return {
            "message": "Repository fetched successfully",
            "status": "success",
            "repository": repository_details,
            "file_tree": file_tree,
            "code_files": code_contents,
            "readme": {
                "name": readme["name"],
                "path": readme["path"],
                "content": cleaned_readme[:2000]
            }
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Unable to fetch repository details, file tree, or README"
        )
