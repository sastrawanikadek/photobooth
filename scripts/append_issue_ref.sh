#! /usr/bin/env bash

COMMIT_MSG=$(cat $1)
CURRENT_BRANCH=$(git branch --show-current)

if [[ ! $CURRENT_BRANCH =~ ^(feature|bugfix|hotfix)/[0-9]+$ ]]; then
  exit 0
elif [[ $COMMIT_MSG =~ \(#[0-9]+\)$ ]]; then
  exit 0
fi

ISSUE_REF=$(echo $CURRENT_BRANCH | sed -E 's/(feature|bugfix|hotfix)\/([0-9]+)/(#\2)/g')

echo "$COMMIT_MSG $ISSUE_REF" > $1
