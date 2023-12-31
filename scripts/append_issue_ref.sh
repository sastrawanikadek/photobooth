#! /usr/bin/env bash

COMMIT_MSG=$(cat $1)
COMMIT_MSG_FIRST_LINE=$(echo "$COMMIT_MSG" | head -1)
CURRENT_BRANCH=$(git branch --show-current)

if [[ ! $CURRENT_BRANCH =~ ^(feature|bugfix|hotfix)/[0-9]+$ ]]; then
  exit 0
elif [[ $COMMIT_MSG_FIRST_LINE =~ \(#[0-9]+\)$ ]]; then
  exit 0
fi

ISSUE_REF=$(echo $CURRENT_BRANCH | sed -E 's/(feature|bugfix|hotfix)\/([0-9]+)/(#\2)/g')

MODIFIED_COMMIT_MSG=$(echo "$COMMIT_MSG" | sed -E "1s/$/ $ISSUE_REF/")
echo "$MODIFIED_COMMIT_MSG" > $1
