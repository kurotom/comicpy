#!/bin/bash

TEST_FINISHED_WITH_SUCCESS='\033[0;32m SUCCESS \033[0m'

run_test () {
  string_python="python$1"
  cmd=$(whereis $string_python | cut -d ":" -f 2 | xargs )
  if [[ $cmd != '' ]]; then
    echo "$string_python - testing"

    set_poetry_python_version $string_python

    poetry run poetry shell

    poetry run poetry install

    poetry run python --version
    poetry run bash run_tests.sh

    if (( $? != 0 )); then
      TEST_FINISHED_WITH_SUCCESS='\033[0;31m FAILED \033[0m'
    fi

  fi
}
set_poetry_python_version () {
  poetry env use $1
}

python_versions=(3.9 3.10 3.11 3.12)
current_version_Python=$(python --version | cut -d " " -f 2)

for i in "${python_versions[@]}"; do
  # echo "Python $i"
  run_test "$i"
done

set_poetry_python_version $current_version_Python

echo -e "\n\nTests finished:  >>>  $TEST_FINISHED_WITH_SUCCESS  <<<\n\n"
