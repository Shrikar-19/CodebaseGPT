
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl

from app.services.github_service import (
    get_repository_details,
    get_file_content,
    get_repository_file_tree,
    clean_readme_content,
    get_all_code_contents,
)

from app.services.ollama_service import generate_ai_response

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
        # Get repository URL
        repo_url = str(request.repo_url)

        # Fetch repository details
        repository_details = get_repository_details(repo_url)

        # Fetch README
        readme = get_file_content(
            repo_url,
            "README.md"
        )

        # Clean README content
        cleaned_readme = clean_readme_content(
            readme["content"]
        )

        # Fetch repository file tree
        file_tree = get_repository_file_tree(repo_url)

        # Fetch code files
        code_contents = get_all_code_contents(
            repo_url,
            max_files=10
        )

        # Prepare code context for AI
        code_context = ""

        for file in code_contents[:5]:
            file_path = file.get(
                "path",
                file.get("name", "Unknown")
            )

            file_content = file.get(
                "content",
                ""
            )

            code_context += f"""
File: {file_path}

{file_content[:3000]}

"""

        # Create AI analysis prompt
        analysis_prompt = f"""
You are a senior software engineer and code reviewer.

Analyze the following GitHub repository.

Repository name:
{repository_details.get("name", "Not available")}

Repository description:
{repository_details.get("description", "Not available")}

Programming language:
{repository_details.get("language", "Not available")}

README:
{cleaned_readme[:2000]}

Source code:
{code_context}

Provide the following:

1. Project overview
2. Main functionality
3. Important files and their purpose
4. Technologies used
5. Potential issues or improvements
6. Suggestions for future development

Use clear headings and bullet points.

Base your analysis only on the provided information.
If information is missing, mention that instead of guessing.
"""

        # Generate AI analysis using Ollama
        ai_analysis = generate_ai_response(
            analysis_prompt
        )

        # Return complete response
        return {
            "message": "Repository analyzed successfully",
            "status": "success",

            "repository": repository_details,

            "file_tree": file_tree,

            "code_files": code_contents,

            "readme": {
                "name": readme["name"],
                "path": readme["path"],
                "content": cleaned_readme[:2000]
            },

            "ai_analysis": ai_analysis
        }

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception as error:
        print("Repository analysis error:", error)

        raise HTTPException(
            status_code=500,
            detail="Unable to analyze repository"
        )
