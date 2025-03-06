#!/bin/bash
#
# script to manage versions and comments used for `git tag`, `build.yml` file
# for Github Actions, `pyproject.toml` file used by `poetry` for the current
# project.
#
#
# YAML_FILE='.github/workflows/build.yml'
PYPROJECT_TOML=$(realpath 'pyproject.toml')
VERSION_COMICPY=$(realpath 'comicpy/version.py')
STATUS=0


check_version_input () {
  # check version tag
  res=$(echo $NEW_VERSION_TAG | grep -E '[0-9]+\.[0-9]+\.[0-9]+')
  if [[ ! -z $res ]]; then
    STATUS=0
  else
    STATUS=1
    echo "Enter correct version. Syntax: [0-9].[0-9].[0-9]."
    echo -e "Example: $0 0.1.0\n"
  fi
}

change_version_pyproject () {
  # change version of TOML file
  status_check_code

  echo "File:  $PYPROJECT_TOML"
  sed s"/version = \"[0-9]\+\.[0-9]\+\.[0-9]\+\"/version = \"$1\"/" "$PYPROJECT_TOML" -i "$PYPROJECT_TOML"

  echo "File:  $VERSION_COMICPY"
  sed s"/VERSION = \"[0-9]\+\.[0-9]\+\.[0-9]\+\"/VERSION = \"$1\"/" "$VERSION_COMICPY" -i "$VERSION_COMICPY"

  status_get_exit_code
}

build_requirements () {
  # generates requirements.txt
  status_check_code

  echo "Get related Python packages, requirements.txt".
  poetry export --without-hashes --format=requirements.txt --output requirements.txt

  status_get_exit_code
}

git_new_tag () {
  # git create tag and push
  status_check_code

  CURRENT_TAG="v$1"
  MESSAGE="$CURRENT_TAG $(date +"%D %H:%M:%S.%N")"

  echo "Creating new tag - $CURRENT_TAG"

  git tag -a $CURRENT_TAG -m "$MESSAGE"

  git push origin $CURRENT_TAG

  status_get_exit_code
}

git_push_changes_repository () {
  # adds, commits and push changes
  status_check_code

  echo "git_push_changes_repository - $NEW_VERSION_TAG"
  if [[ -z "$1" ]]; then
    COMMENT="v$NEW_VERSION_TAG"
  else
    COMMENT="$1"
  fi

  git add .
  git commit -m "$COMMENT"
  git push origin main --force

  status_get_exit_code
}

status_get_exit_code () {
  # checks status code of last command and
  # sets status for this scripts.
  if [ $? == 0 ]; then
    STATUS=0
  else
    STATUS=1
  fi
}

status_check_code () {
  # checks STATUS of script and sets exit code
  if [ $STATUS == 1 ]; then
    exit 1
  fi
}


#
# main code
#
if [ $# -eq 1 ] || [ $# -eq 2 ]; then

  NEW_VERSION_TAG="$1"
  COMMIT_PUSH="$2"

  check_version_input

  if [ $STATUS == 0 ]; then

    echo -e "\nTag: $NEW_VERSION_TAG, Commit: $COMMIT_PUSH\n"

    change_version_pyproject $NEW_VERSION_TAG

    build_requirements

    git_push_changes_repository "$COMMIT_PUSH"

    git_new_tag $NEW_VERSION_TAG

    exit 0

  else

    exit 1

  fi

else
  echo 'Need only 1 or 2 arguments: 1 = Version, 2 = Comment Commit Git Push'
  echo
fi
