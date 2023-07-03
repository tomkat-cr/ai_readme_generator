import os
import sys

from dotenv import load_dotenv
from git import Repo
from langchain.document_loaders import GitLoader
import openai

from pprint import pprint


DEBUG = False


def remove_dir(local_temp_path):
    if local_temp_path == '/':
        raise Exception("Cannot use / as a temp path")
    if not os.path.exists(local_temp_path):
        return
    if os.path.isfile(local_temp_path):
        os.remove(local_temp_path)
        return
    for root, dirs, files in os.walk(local_temp_path, topdown=False):
        for name in files:
            os.remove(os.path.join(root, name))
        for name in dirs:
            os.rmdir(os.path.join(root, name))


def get_repo(repo_url, branch):
    response = {
        "error": False,
        "error_msg": "",
    }
    if repo_url[:8] == "https://":
        # https://python.langchain.com/docs/modules/data_connection/document_loaders/integrations/git
        local_temp_repo_path = f"/tmp/{repo_url.rsplit('/', 1)[1]}"
        try:
            remove_dir(local_temp_repo_path)
        except Exception as err:
            if DEBUG:
                raise
            response["error"] = True
            response["error_msg"] = f"ERROR: {str(err)}"
            return response
        try:
            repo = Repo.clone_from(
                url=repo_url,
                to_path=local_temp_repo_path
            )
        except Exception as err:
            if DEBUG:
                raise
            response["error"] = True
            response["error_msg"] = f"ERROR: {str(err)}"
            return response
    else:
        try:
            repo = Repo(repo_url)
        except Exception as err:
            if DEBUG:
                raise
            response["error"] = True
            response["error_msg"] = f"ERROR: {str(err)}"
            return response
    if not branch:
        try:
            branch = repo.head.reference
        except Exception as err:
            if DEBUG:
                raise
            response["error"] = True
            response["error_msg"] = f"ERROR: {str(err)}"
            return response
    print()
    print(f"Github repository URL: {repo_url}")
    print(f"Branch (default 'main'): {branch}")
    try:
        loader = GitLoader(
            repo_path=f"{local_temp_repo_path}/",
            branch=branch
        )
    except Exception as err:
        if DEBUG:
            raise
        response["error"] = True
        response["error_msg"] = f"ERROR: {str(err)}"
        return response
    response["data"] = loader.load()
    if DEBUG:
        print(f"Repo: {repo_url}")
        print(f"Branch: {branch}")
        print("Data:")
        pprint(response["data"])
    return response


def get_readme_suggestion(repo_url, branch, file_ext_filter):
    """Gets a readme.md file suggestion from the given GitHub repository URL."""
    repo_response = get_repo(repo_url, branch)
    if repo_response["error"]:
        return repo_response["error_msg"]
    repo_data = repo_response["data"]

    text = ""
    file_extensions_allowed = None
    if file_ext_filter:
        file_extensions_allowed = [f".{v}" for v in file_ext_filter.split(",")]
        print(f"File extensions allowed: {file_extensions_allowed}")
        if DEBUG:
            print()
            print("Files to be included in the context:")
        
    for doc_obj in repo_data:
        if file_ext_filter and not doc_obj.metadata.file_type in file_extensions_allowed:
            continue
        text += doc_obj.page_content
        text += str(doc_obj.metadata)
        if DEBUG:
            print(doc_obj.metadata.file_name)

    # https://platform.openai.com/docs/api-reference/completions/create
    # https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb

    if os.getenv("OPENAI_API_KEY"):
        openai.api_key = os.getenv("OPENAI_API_KEY")
    else:
        openai.api_key = str(input("Enter OPENAI_API_KEY: "))

    messages = [
        {
            "role": "system",
            "content": "Write a readme.md file for this repository content."
        },
        {"role": "user", "content": text},
    ]
    print("Processing...")
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
        )
    except Exception as err:
        if DEBUG:
            raise
        return f"ERROR: {str(err)}"
    print("Processing done!")
    if DEBUG:
        print("The response is:")
        pprint(response)
    try:
        return response["choices"][0]["message"]["content"]
    except Exception as err:
        return f"ERROR: {str(err)}"


def main():
    global DEBUG
    load_dotenv()
    DEBUG = os.environ.get('DEBUG', '0') == '1'
    branch = None
    file_ext_filter = None
    if len(sys.argv) > 1:
        repo_url = sys.argv[1]
        if len(sys.argv) > 2:
            branch = sys.argv[2]
        if len(sys.argv) > 3:
            branfile_ext_filterch = sys.argv[3]
    else:
        repo_url = str(input("Github repository URL: "))   # example: "https://github.com/bard/ai-assistant"
        branch = str(input("Branch (default 'main'): "))
        file_ext_filter = str(input("file extension filter (default all files): "))
    print()
    print("AI README.md file generator")
    readme_suggestion = get_readme_suggestion(repo_url, branch, file_ext_filter)
    print()
    print("The suggested README.md is:")
    print(readme_suggestion)


if __name__ == "__main__":
    main()
