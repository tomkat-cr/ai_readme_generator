# ai_readme_generator

<p align="center"><img src="https://socialify.git.ci/tomkat-cr/ai_readme_generator/image?description=0&amp;font=Inter&amp;language=1&amp;name=1&amp;owner=1&amp;pattern=Plus&amp;stargazers=0&amp;theme=Light" alt="project-image"></p>

AI Readme Generator reads a Github repository and suggest a README.md file based on that code using Langchain and OpenAI's GPT4.

Main functionalities of this project are listed below:

1. The script clones a given repo from its url or local path, and fetches file content and metadata.
2. The content and metadata fetched are then passed to GPT-4 model to generate the README suggestion.
3. It can filter out files based on their extensions.
4. The script can also work in debug mode. In debug mode, the script provides more detailed output logs.

## Usage

Please note, in order to use this script, you will need the `OPENAI_API_KEY`.

To use the script from command line, please use the following template and fill in the relevant details:

```bash
pipenv run python -m ai_readme_generator.main -h
```

```bash
usage: main.py [-h] [-u REPO_URL] [-b BRANCH] [-e FILE_EXT_FILTER] [-m {gpt-3.5-turbo,gpt-3.5-turbo-16k,gpt-4,gpt-4-32k}]
               [-t TEMPERATURE] [-D DEBUG]

AI README Generator

options:
  -h, --help            show this help message and exit
  -u REPO_URL, --repo_url REPO_URL
                        Git repository URL or local path
  -b BRANCH, --branch BRANCH
                        Repository branch name. Default: main
  -e FILE_EXT_FILTER, --file_ext_filter FILE_EXT_FILTER
                        Filter the files based on their extensions. For instance: 'py,md', 'js,jsx' or 'php'
  -m {gpt-3.5-turbo,gpt-3.5-turbo-16k,gpt-4,gpt-4-32k}, --model {gpt-3.5-turbo,gpt-3.5-turbo-16k,gpt-4,gpt-4-32k}
                        GPT model. Default: gpt-3.5-turbo-16k
  -t TEMPERATURE, --temperature TEMPERATURE
                        Temperature for the GPT model. Default: 0.7
  -D DEBUG, --debug DEBUG
                        Show debug information
```

- `REPO_URL`: repository URL for which you want to generate README. It is a mandatory parameter. This can be also a local path, so repo won't be cloned in the `/tmp` directory.

- `BRANCH`: It is the branch of the repo from which you want to generate README. This is an optional parameter, the `main` branch will be used by default if no branch is specified.

- `FILE_EXT_FILTER`: It is to filter the files based on their extensions. For instance: `py,md`, `js,jsx` or `php`. This is an optional parameter, all files will be used if no filter is given.

For instance,

```bash
pipenv run python -m ai_readme_generator.main -u https://github.com/bard/ai-assistant -b main -e py,md
```

## Dependencies

Following Python libraries are required:
- git (Repo)
- langchain.document_loaders (GitLoader)
- openai
- os, sys
- dotenv (load_dotenv)
- pprint

## Installation Steps

1. Clone the repo:

```
git clone https://github.com/tomkat-cr/ai_readme_generator
```

2. Change the directory:

```
cd ai_readme_generator
```

3. Start the virtual environment:

```
python3 -m venv venv
source venv/bin/activate
```

4. Install requirements:

```
pip install -r requirements.txt
```

5. Create the .env file:

```
cp .env-example .env
vi .env
```

6. Configure parameters:

```
OPENAI_API_KEY=sk-XXXXXX
DEBUG=0
```

7. Run it (it'll ask for git repo URL/local path and branch):

```
pipenv run python -m ai_readme_generator.main
```

8. or run it with repo URL/path and branch

```
pipenv run python -m ai_readme_generator.main -u https://github.com/tomkat-cr/ai_readme_generator -b main
```

## Note

Please be aware that script will not attempt to delete or modify any files or directories outside of its designated working area.

Enjoy exploring the project!

## Contributions

Feel free to submit pull requests create issues or spread the word.

## Built with

Technologies used in the project:

- python3
- openai
- langchain
- gitpython
- pipenv
- make

## License

This project is licensed under the GNU 2.0
