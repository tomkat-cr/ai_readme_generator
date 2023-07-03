<h1 align="center" id="title">ai_readme_generator</h1>

<p align="center"><img src="https://socialify.git.ci/tomkat-cr/ai_readme_generator/image?description=0&amp;font=Inter&amp;language=1&amp;name=1&amp;owner=1&amp;pattern=Plus&amp;stargazers=0&amp;theme=Light" alt="project-image"></p>

<p id="description">AI Readme Generator reads a Github repository and suggest a README.md file based on that code using LLM Langchain and OpenAI GPT4.</p>

<h2>🛠️ Installation Steps:</h2>

<p>1. Clone the repo:</p>

```
git clone https://github.com/tomkat-cr/ai_readme_generator
```

<p>2. Change the directory:</p>

```
cd ai_readme_generator
```

<p>3. Start the virtual environment:</p>

```
python3 -m venv venv
source venv/bin/activate
```

<p>5. Install requirements:</p>

```
pip install -r requirements.txt
```

<p>6. Create the .env file:</p>

```
cp .env-example .env
vi .env
```

<p>8. Configure parameters:</p>

```
OPENAI_API_KEY=sk-XXXXXX
DEBUG=0
```

<p>11. Run it (it'll ask for git repo URL/local path and branch):</p>

```
python -m ai_readme_generator.main
```

<p>12. or run it with repo URL/path and branch</p>

```
python -m ai_readme_generator.main https://github.com/tomkat-cr/ai_readme_generator main
```

<h2>🍰 Contribution Guidelines:</h2>

Feel free to submit pull requests create issues or spread the word.

<h2>💻 Built with</h2>

Technologies used in the project:

*   python3
*   openai
*   langchain
*   llm
*   gitpython

<h2>🛡️ License:</h2>

This project is licensed under the GNU 2.0
