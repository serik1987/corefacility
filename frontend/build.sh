#!/bin/bash

current_dir=$(pwd)
frontend_files=( *.*.js *.*.js.map *.*.css *.*.css.map )

echo "build.sh: Create CSS files for all applications"
cd common_styles || exit
minify index.css > ../../corefacility/core/static/common.min.css || exit
cd ..

for dir_name in ./apps/*
do
  app_name=$(basename "$dir_name")
  echo "build.sh: Create CSS and JS files for the application $app_name"
  rm -rf "$dir_name/src/corefacility-base"
  if ! cp -R common_components "$dir_name/src/corefacility-base"
  then
    echo "build.sh: Application frontend doesn't have src folder. Probably, you need to launch create-react-app"
    continue
  fi
  cd "$dir_name" || exit
  if ! npm run build
  then
    echo "build.sh: Frontend compilation failed."
    continue
  fi
  cd "$current_dir" || exit
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.css
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.css.map
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.js
  rm -f "../corefacility/$app_name/static/$app_name/"*.*.js.map
  cp "apps/$app_name/build/static/css/"*.*.css "../corefacility/$app_name/static/$app_name"
  cp "apps/$app_name/build/static/css/"*.*.css.map "../corefacility/$app_name/static/$app_name"
  cp "apps/$app_name/build/static/js/"*.*.js "../corefacility/$app_name/static/$app_name"
  cp "apps/$app_name/build/static/js/"*.*.js.map "../corefacility/$app_name/static/"$app_name
done