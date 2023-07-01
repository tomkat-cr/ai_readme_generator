#!/bin/bash
ERROR_MSG=""

if [ "${ERROR_MSG}" = "" ]; then
    export SCRIPTS_DIR="$(dirname "$0")";
    cd "${SCRIPTS_DIR}"
    export SCRIPTS_DIR="$(pwd)";
    cd "${SCRIPTS_DIR}/.."
    export BASE_DIR="$(pwd)";
    if [ -f "${BASE_DIR}/.env" ]; then
        set -o allexport; . "${BASE_DIR}/.env" ; set +o allexport ;
    fi
fi

if [ "${PYTHON_VERSION}" == "" ]; then
    PYTHON_VERSION="3.9.17"
fi

BASH_PROFILE="${HOME}/.bash_profile"
BASH_SOURCE1="bash"
if [ -f "${HOME}/.zshrc" ]; then
    BASH_PROFILE="${HOME}/.zshrc"
    BASH_SOURCE1="zsh"
fi

PYENV_INSTALL_PREFIX=""
MACHINE_ARCHITECTURE=$(arch)
if [ "${MACHINE_ARCHITECTURE}" = "arm64" ]; then
    PYENV_INSTALL_PREFIX="arch -x86_64"
fi

if [ "${ERROR_MSG}" = "" ]; then
    if ! pyenv --version
    then
        # install pyenv
        echo ""
        echo "Install pyenv"
        echo ""
        curl https://pyenv.run | bash
        if ! pyenv --version
        then
            ERROR_MSG="ERROR: pyenv could not be installed."
        fi
    fi
fi

if [ "${ERROR_MSG}" = "" ]; then
    if ! grep -q 'eval "$(pyenv init --path)"' ${BASH_PROFILE}; then
        # add pyenv to the PATH and enable shims and autocompletion
        echo ""
        echo "Add pyenv to the PATH and enable shims and autocompletion"
        echo ""

        echo "" >> ${BASH_PROFILE}
        echo "# `date`" >> ${BASH_PROFILE}
        echo "# Add pyenv to the PATH and enable shims and autocompletion" >> ${BASH_PROFILE}
        echo "" >> ${BASH_PROFILE}
        echo 'export PYENV_ROOT="${HOME}/.pyenv"' >> ${BASH_PROFILE}
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ${BASH_PROFILE}
        echo 'eval "$(pyenv init --path)"' >> ${BASH_PROFILE}
        echo 'eval "$(pyenv init -)"' >> ${BASH_PROFILE}
        # echo 'eval "$(pyenv virtualenv-init -)"' >> ${BASH_PROFILE}
    fi
fi

if [ "${ERROR_MSG}" = "" ]; then
    if [ ! -d "${HOME}/.pyenv/versions/${PYTHON_VERSION}" ]; then
        # install python version using pyenv
        echo ""
        echo "Install python with: pyenv install ${PYTHON_VERSION}"
        echo ""
        if ! ${PYENV_INSTALL_PREFIX} pyenv install ${PYTHON_VERSION}
        then
            ERROR_MSG="ERROR: running pyenv install ${PYTHON_VERSION}"
        fi
    fi
fi

if [ "${ERROR_MSG}" = "" ]; then
    echo ""
    echo "Changing python version: pyenv local ${PYTHON_VERSION}"
    echo ""
    if ! pyenv local ${PYTHON_VERSION}
    then
        ERROR_MSG="ERROR: running pyenv local ${PYTHON_VERSION}"
    fi
fi

if [ "${ERROR_MSG}" = "" ]; then
    if ! pipenv --version
    then
        # install pipenv
        echo ""
        echo "Install pipenv"
        echo ""
        if ! pip install --user pipenv
        then
            ERROR_MSG="ERROR: pipenv could not be installed."
        else
            # add pipenv to the bash profile
            ADD_CMD_TO_PROFILE="eval \"$(_PIPENV_COMPLETE=${BASH_SOURCE1}_source pipenv)\""
            if ! grep -q "${ADD_CMD_TO_PROFILE}" ${BASH_PROFILE}; then
                echo ""
                echo "Add pipenv to the ${BASH_SOURCE1} profile"
                echo ""

                echo "" >> ${BASH_PROFILE}
                echo "# `date`" >> ${BASH_PROFILE}
                echo "# Add pipenv init" >> ${BASH_PROFILE}
                echo "" >> ${BASH_PROFILE}
                echo "${ADD_CMD_TO_PROFILE}" >> ${BASH_PROFILE}
            fi
        fi
    fi
fi

if [ "${ERROR_MSG}" = "" ]; then
    if ! make --version
    then
        # install make
        echo ""
        echo "Install make"
        echo ""

        if [[ "$OSTYPE" == "darwin"* ]]; then
            brew install make
        else
            if ! apt -y install make
            then
                if ! yum -y install make
                then
                    if ! apk add make
                    then
                        ERROR_MSG="ERROR: make could not be installed in linux (debian/rhel/alpine)"
                    fi
                fi
            fi  
        fi
        if ! make --version
        then
            ERROR_MSG="ERROR: make could not be installed"
        fi
    fi
fi

if [ "${ERROR_MSG}" = "" ]; then
    if ! aws --version
    then
        sh ${SCRIPTS_DIR}/install_aws_cli.sh
        if ! aws --version
        then
            ERROR_MSG="ERROR: aws-cli could not be installed"
        fi
    fi
fi

if [ "${ERROR_MSG}" = "" ]; then
    echo ""
    echo "Reload the shell"
    echo ""
    exec "$SHELL"
fi

echo ""
if [ "${ERROR_MSG}" = "" ]; then
    echo "Done!"
else
    echo "${ERROR_MSG}" ;
fi
echo ""
