gitpull() {
  if git pull; then
    return 0
  else
    return 1
  fi
}

#echo "Setting SSH Agent"
#eval "$(ssh-agent -s)"
#echo "Readding SSH Key"
#ssh-add ~/.ssh/scamguardapi.pub
#echo "Checking Git Readability"
#ssh -T git@github.com
cd ..
echo "Updating directory"
if gitpull; then
  echo "Deploy success"
else
  echo "Stashing changes!"
  git stash
  echo "Resyncing..."
  gitpull
  echo "Remember to handle the unstashing later"
fi