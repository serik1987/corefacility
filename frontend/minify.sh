#!/bin/bash

echo Creating common CSS...
minify css/corefacility/main.css > ../corefacility/core/static/common.min.css

for app_name in `ls css`
do
	if [ "$app_name" != "corefacility" ]
	then
		echo Creating CSS for $app_name...
		minify css/$app_name/main.css > ../corefacility/$app_name/static/$app_name/main.min.css
	fi
done

for app_name in `ls js`
do
  if [ "$app_name" != "corefacility" ]
  then
    echo Creating JS for $app_name...
    cd js/$app_name
    npm run build
    cd ../..
  fi
done