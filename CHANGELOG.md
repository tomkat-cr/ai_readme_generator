# CHANGELOG

All notable changes to this project will be documented in this file.
This project adheres to [Semantic Versioning](http://semver.org/) and [Keep a Changelog](http://keepachangelog.com/).



## Unreleased
---

### New

### Changes

### Fixes

### Breaks


## 0.1.3 (2023-07-05)

### New
Command line parameters changed from positional to named with the argparse.
New model and temperature parameters. Defaults: gpt-3.5-turbo-16k and 0.7.
Converted to the class AiReadmeGenerator.


## 0.1.2 (2023-07-04)

### New
Configurate model and temperature.
named parameters.


## 0.1.1 (2023-07-03)

### New
File extensions filter.
Allows to specify the repo URL, branch and file extesions filter from the command line.
Ask user for branch (default: main) and file extensions filter if no command line parameters are passed.
Ask user for openai api key if the environment variable OPENAI_API_KEY has no value.
Recognize "https://" prefix in repo url to know if it's a local or remote repo.
Program start header to identify repo URL and branch.
Print file extensions filter and files to be included.

### Changes

Update README.md.


## 0.1.0 (2023-07-30)
---

### New
Initial development of the AI Readme Generator. Reads a Github repository and suggest a README.md file based on the repo's code, using OpenAI GPT4.
