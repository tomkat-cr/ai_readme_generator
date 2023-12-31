import os

from dotenv import load_dotenv
from pprint import pprint

from git import Repo
import openai
from langchain.document_loaders import GitLoader

from langchain.chat_models import ChatOpenAI
from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain
from langchain.indexes import VectorstoreIndexCreator

from ai_readme_generator.init_parser import init_parser


class AiReadmeGenerator():
    def __init__(self):
        parser = init_parser()
        args = parser.parse_args()
        self.repo_url = args.repo_url
        self.branch = args.branch
        self.file_ext_filter = args.file_ext_filter
        self.model = args.model
        self.temperature = args.temperature
        self.debug = args.debug == '1'
        self.prompt_type = args.prompt_type
        self.processing_method = "model_input"
        # self.processing_method = "embeddings"

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

        if not self.repo_url:
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
                self.prompt_type = str(input(
                    "Prompt type (readme|test): "
                ))
            except KeyboardInterrupt:
                return "Keyboard interrupt"
            except Exception as err:
                return str(err)

        if not self.temperature:
            self.temperature = 0.7
        else:
            self.temperature = float(self.temperature)
        if not self.model:
            self.model = "gpt-3.5-turbo-16k"
        if not self.prompt_type:
            self.prompt_type = "readme"
        elif self.prompt_type not in ["readme", "test"]:
            return "ERROR: Invalid Prompt type."

        return ""

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
                local_temp_repo_path = self.repo_url
                repo = Repo(local_temp_repo_path)
            except Exception as err:
                if self.debug:
                    raise
                response["error"] = True
                response["error_msg"] = f"ERROR: {str(err)}"
                return response
        if not self.branch:
            try:
                self.branch = repo.head.reference
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
                branch=self.branch
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

    def get_prompt(self, pcode):
        if pcode == "readme":
            prompt = \
                """Write a readme.md file for this repository content.
                """
        if pcode == "test":
            prompt = \
                """Give me a pytest file for this repository content.
                """
        return prompt

    def std_response(self):
        response = {
            "error": False,
            "content": "",
        }
        return response

    def model_input_method(self):
        response = self.std_response()
        text = ""
        for doc_obj in self.repo_data:
            if self.file_ext_filter and \
               not doc_obj.metadata["file_type"] \
               in self.file_extensions_allowed:
                continue
            text += doc_obj.page_content
            text += str(doc_obj.metadata)
            if self.debug:
                print(doc_obj.metadata["source"])

        # https://platform.openai.com/docs/api-reference/completions/create
        # https://github.com/openai/openai-cookbook/blob/main/examples/Question_answering_using_embeddings.ipynb

        openai.api_key = self.openai_api_key
        prompt = self.get_prompt(self.prompt_type)
        messages = [
            {
                "role": "system",
                "content": prompt
            },
            {"role": "user", "content": text},
        ]

        print("Model Input processing start...")

        try:
            ai_response = openai.ChatCompletion.create(
                model=self.model,
                temperature=self.temperature,
                messages=messages,
            )
        except Exception as err:
            if self.debug:
                raise
            response["error"] = True
            response["content"] = f"ERROR: {str(err)}"

        print("Model Input processing done!")

        if not response["error"]:
            try:
                response["content"] = \
                    ai_response["choices"][0]["message"]["content"]
            except Exception as err:
                response["error"] = True
                response["content"] = f"ERROR: {str(err)}"

        return response

    def embeddings_method(self):
        response = self.std_response()
        prompt = self.get_prompt(self.prompt_type)

        print("Embedding processing start...")

        index = VectorstoreIndexCreator().from_documents(
            self.repo_data
        )
        llm = ChatOpenAI(
            model=self.model,
            temperature=self.temperature,
        )
        memory = ConversationBufferMemory(
            memory_key='chat_history', return_messages=True
        )
        conversation_chain = ConversationalRetrievalChain.from_llm(
            llm=llm,
            retriever=index.vectorstore.as_retriever(),
            memory=memory
        )

        print("LLM processing...")

        ai_response = conversation_chain({'question': prompt})
        chat_history = ai_response['chat_history']

        response["content"] = ""
        for i, message in enumerate(chat_history):
            if i % 2 == 0:
                continue
            else:
                response["content"] += message.content

        print("Embedding processing done!")

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
        self.repo_data = repo_response["data"]

        self.file_extensions_allowed = None
        if self.file_ext_filter:
            self.file_extensions_allowed = \
                [f".{v}" for v in self.file_ext_filter.split(",")]
            print(f"File extensions allowed: {self.file_extensions_allowed}")
            if self.debug:
                print()
                print("Files to be included in the context:")

        if self.processing_method == "embeddings":
            response = self.embeddings_method()
        else:
            response = self.model_input_method()

        if self.debug:
            print("The response is:")
            pprint(response)
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
            print(f"The suggested {self.prompt_type} is:")
        print()
        print(readme_suggestion["content"])


if __name__ == "__main__":
    airg = AiReadmeGenerator()
    airg.main()
