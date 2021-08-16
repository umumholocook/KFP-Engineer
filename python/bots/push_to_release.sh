#!/bin/bash -e

echo "----- Pushing code to release, do not use git now!!! -----"
echo "----- If encounter conflict, please fix it yourself! -----"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "----- Copying file to release branch, do not use git now!!! -----"
git checkout release
git merge $CURRENT_BRANCH
git push
echo "----- Pushing code to release success!!! -----"
git checkout $CURRENT_BRANCH
