import os

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


def get_repo(repo_url):
    # https://python.langchain.com/docs/modules/data_connection/document_loaders/integrations/git
    local_temp_repo_path = f"/tmp/{repo_url.rsplit('/', 1)[1]}"
    remove_dir(local_temp_repo_path)
    repo = Repo.clone_from(
        url=repo_url,
        to_path=local_temp_repo_path
    )
    branch = repo.head.reference
    loader = GitLoader(
        repo_path=f"{local_temp_repo_path}/",
        branch=branch
    )
    data = loader.load()
    if DEBUG:
        print(f"Repo: {repo_url}")
        print(f"Branch: {branch}")
        print("Data:")
        pprint(data)
    return data


def get_readme_suggestion(repo_url):
    """Gets a readme.md file suggestion from the given GitHub repository URL."""
    repo_data = get_repo(repo_url)
    text = ""
    for doc_obj in repo_data:
        text += doc_obj.page_content
        text += str(doc_obj.metadata)

    # https://platform.openai.com/docs/api-reference/completions/create
    # https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb

    openai.api_key = os.getenv("OPENAI_API_KEY")
    messages = [
        {
            "role": "system",
            "content": "Write a readme.md file for this repository content."
        },
        {"role": "user", "content": text},
    ]
    print("Processing...")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
    )
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
    repo_url = str(input("Github repository URL: "))   # example: "https://github.com/bard/ai-assistant"
    readme_suggestion = get_readme_suggestion(repo_url)
    print("The suggested README.md is:")
    print(readme_suggestion)


if __name__ == "__main__":
    main()