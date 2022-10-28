#!/bin/bash

echo Creating common CSS...
minify css/corefacility/main.css > ../corefacility/core/static/common.min.css

for app_name in `ls js`
do
  if [ "$app_name" != "corefacility" ]
  then
    echo Creating CSS and JS for $app_name...
    cd js/$app_name
    npm run build
    cd ../..
    rm -rf ../corefacility/$app_name/static/$app_name/main.*.js
    rm -rf ../corefacility/$app_name/static/$app_name/main.*.js.map
    rm -rf ../corefacility/$app_name/static/$app_name/main.*.css
    rm -rf ../corefacility/$app_name/static/$app_name/main.*.css.map
    cp js/$app_name/build/static/js/main.*.js ../corefacility/$app_name/static/$app_name
    cp js/$app_name/build/static/js/main.*.js.map ../corefacility/$app_name/static/$app_name
    cp js/$app_name/build/static/css/main.*.css ../corefacility/$app_name/static/$app_name
    cp js/$app_name/build/static/css/main.*.css.map ../corefacility/$app_name/static/$app_name
    cp js/$app_name/build/static/$app_name/* ../corefacility/$app_name/static/$app_name
  fi
done