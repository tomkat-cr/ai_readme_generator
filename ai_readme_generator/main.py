import os

from dotenv import load_dotenv
from git import Repo
from langchain.document_loaders import GitLoader
import openai
from pprint import pprint

from ai_readme_generator.init_parser import init_parser


class AiReadmeGenerator():
    def __init__(self):
        parser = init_parser()
        args = parser.parse_args()
        self.repo_url = args.repo_url
        self.branch = args.branch
        self.file_ext_filter = args.file_ext_filter
        self.model = args.model
        self.temperature = float(args.temperature)
        self.debug = args.debug == '1'

    def get_def_values(self):
        load_dotenv()
        try:
            if os.getenv("OPENAI_API_KEY"):
                self.openai_api_key = os.getenv("OPENAI_API_KEY")
            else:
                self.openai_api_key = str(input("Enter OPENAI_API_KEY: "))
        except KeyboardInterrupt:
            return "Keyboard interrupt"
        except Exception as err:
            return str(err)
        if self.repo_url:
            return ""
        try:
            self.repo_url = str(input(
                "Git repository URL: "
            ))
            self.branch = str(input(
                "Branch (default 'main'): "
            ))
            self.file_ext_filter = str(input(
                "file extension filter (default all files): "
            ))
            self.model = str(input(
                "GPT model (gpt-3.5-turbo, gpt-3.5-turbo-16k," +
                " gpt-4 or gpt-4-32k): "
            ))
            self.temperature = str(input(
                "Temperature for the GPT model (default: 0.7): "
            ))
        except KeyboardInterrupt:
            return "Keyboard interrupt"
        except Exception as err:
            return str(err)

    def remove_dir(self, local_temp_path):
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

    def get_repo(self):
        response = {
            "error": False,
            "error_msg": "",
        }
        if self.repo_url[:8] == "https://":
            # https://python.langchain.com/docs/modules/data_connection/document_loaders/integrations/git
            local_temp_repo_path = f"/tmp/{self.repo_url.rsplit('/', 1)[1]}"
            try:
                self.remove_dir(local_temp_repo_path)
            except Exception as err:
                if self.debug:
                    raise
                response["error"] = True
                response["error_msg"] = f"ERROR: {str(err)}"
                return response
            try:
                repo = Repo.clone_from(
                    url=self.repo_url,
                    to_path=local_temp_repo_path
                )
            except Exception as err:
                if self.debug:
                    raise
                response["error"] = True
                response["error_msg"] = f"ERROR: {str(err)}"
                return response
        else:
            try:
                repo = Repo(self.repo_url)
            except Exception as err:
                if self.debug:
                    raise
                response["error"] = True
                response["error_msg"] = f"ERROR: {str(err)}"
                return response
        if not self.branch:
            try:
                branch = repo.head.reference
            except Exception as err:
                if self.debug:
                    raise
                response["error"] = True
                response["error_msg"] = f"ERROR: {str(err)}"
                return response
        print()
        print(f"Github repository URL: {self.repo_url}")
        print(f"Branch (default 'main'): {self.branch}")
        try:
            loader = GitLoader(
                repo_path=f"{local_temp_repo_path}/",
                branch=branch
            )
        except Exception as err:
            if self.debug:
                raise
            response["error"] = True
            response["error_msg"] = f"ERROR: {str(err)}"
            return response
        response["data"] = loader.load()
        if self.debug:
            print(f"Repo: {self.repo_url}")
            print(f"Branch: {self.branch}")
            print("Data:")
            pprint(response["data"])
        return response

    def get_readme_suggestion(self):
        """Gets a readme.md file suggestion from the given
           GitHub repository URL or local path.
        """
        response = {
            "error": False,
            "content": "",
        }
        repo_response = self.get_repo()
        if repo_response["error"]:
            response["error"] = True
            response["content"] = repo_response["error_msg"]
            return response
        repo_data = repo_response["data"]

        text = ""
        file_extensions_allowed = None
        if self.file_ext_filter:
            file_extensions_allowed = \
                [f".{v}" for v in self.file_ext_filter.split(",")]
            print(f"File extensions allowed: {file_extensions_allowed}")
            if self.debug:
                print()
                print("Files to be included in the context:")

        for doc_obj in repo_data:
            if self.file_ext_filter and \
               not doc_obj.metadata["file_type"] in file_extensions_allowed:
                continue
            text += doc_obj.page_content
            text += str(doc_obj.metadata)
            if self.debug:
                print(doc_obj.metadata["source"])

        # https://platform.openai.com/docs/api-reference/completions/create
        # https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb

        openai.api_key = self.openai_api_key
        messages = [
            {
                "role": "system",
                "content": "Write a readme.md file for this repository" +
                           " content."
            },
            {"role": "user", "content": text},
        ]
        print("Processing...")
        if not self.temperature:
            self.temperature = 0.7
        if not self.model:
            self.model = "gpt-3.5-turbo-16k"
        try:
            response = openai.ChatCompletion.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
            )
        except Exception as err:
            if self.debug:
                raise
            response["error"] = True
            response["content"] = f"ERROR: {str(err)}"
            return response
        print("Processing done!")
        if self.debug:
            print("The response is:")
            pprint(response)
        try:
            return response["choices"][0]["message"]["content"]
        except Exception as err:
            response["error"] = True
            response["content"] = f"ERROR: {str(err)}"
            return response

    def main(self):
        print()
        print("AI README.md file generator")
        error_msg = self.get_def_values()
        if error_msg:
            print()
            print(error_msg)
            return
        readme_suggestion = self.get_readme_suggestion()
        print()
        if readme_suggestion["error"]:
            print("Could not generate the suggested README.md:")
        else:
            print("The suggested README.md is:")
        print()
        print(readme_suggestion["content"])


if __name__ == "__main__":
    airg = AiReadmeGenerator()
    airg.main()
