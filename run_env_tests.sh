#!/bin/bash

TEST_FINISHED_WITH_SUCCESS='\033[1;32m SUCCESS \033[0m'
TEST_FINISHED_WITH_FAILED='\033[1;31m FAILED \033[0m'
ALL_TESTS_PASSED=0

check_poetry_shell_plugin () {
  result=$(pip list | grep poetry-plugin-shell)
  if [[ -z "$result" ]]; then
    pip install poetry-plugin-shell
  fi
}

run_test () {
  string_python="python$1"
  # cmd=$(whereis $string_python | cut -d ":" -f 2 | xargs )
  cmd=$(command -v "$string_python")
  if [[ -n $cmd ]]; then

    echo -e "\n\n>>>\033[1;34m $string_python - testing \033[0m\n\n"

    set_poetry_python_version "$string_python"

    check_poetry_shell_plugin

    poetry run poetry install

    poetry run python --version
    poetry run bash run_tests.sh

    if (( $? != 0 )); then
      ALL_TESTS_PASSED=1
    fi

  fi
}
set_poetry_python_version () {
  poetry env use "$1"
}

python_versions=(3.9 3.10 3.11 3.12)
current_version_Python=$(python --version | cut -d " " -f 2)


for i in "${python_versions[@]}"; do
  # echo "Python $i"
  run_test "$i"
done

set_poetry_python_version "$current_version_Python"

if [[ "$ALL_TESTS_PASSED" -eq 0 ]]; then
  echo -e "\n\nTests finished:  >>>  $TEST_FINISHED_WITH_SUCCESS  <<<\n\n"
else
  echo -e "\n\nTests finished:  >>>  $TEST_FINISHED_WITH_FAILED  <<<\n\n"
fi

exit $ALL_TESTS_PASSED
