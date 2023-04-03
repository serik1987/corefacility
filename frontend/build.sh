#!/bin/bash

current_dir=$(pwd)

function build(){
  app_name=$(basename "$1")
  echo "build.sh: Create CSS and JS files for the application $app_name"
  rm -rf "$1/src/corefacility-base"
  if ! cp -R common_components "$1/src/corefacility-base"
  then
    echo "build.sh: Application frontend doesn't have src folder. Probably, you need to launch create-react-app"
    return 1
  fi
  cd "$1" || exit
  if ! npm run build
  then
    echo "build.sh: Frontend compilation failed."
    cd "$current_dir" || exit
    return 2
  fi
  echo "build.sh: Frontend compilation succeed."
  cd "$current_dir" || exit
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.css
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.css.map
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.js
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.js.map
  cp "apps/$app_name/build/static/css/"*.*.css "../corefacility/$app_name/static/$app_name"
  cp "apps/$app_name/build/static/css/"*.*.css.map "../corefacility/$app_name/static/$app_name"
  cp "apps/$app_name/build/static/js/"*.*.js "../corefacility/$app_name/static/$app_name"
  cp "apps/$app_name/build/static/js/"*.*.js.map "../corefacility/$app_name/static/"$app_name
}

if [ -z "$1" ]
then
  echo "build.sh: Create CSS files for all applications"
  cd common_styles || exit
  minify index.css > ../../corefacility/core/static/common.min.css || exit
  cd ..

  for dir_name in ./apps/*
  do
    build "$dir_name"
  done
else
  build "$1"
fi
