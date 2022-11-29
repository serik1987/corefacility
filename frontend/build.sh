#!/bin/bash

echo Creating common CSS...
minify css/corefacility/main.css > ../corefacility/core/static/common.min.css

for dir_name in `ls js`
do
  if [[ "dir_name" != "corefacility" ]] && ([[ "$dir_name" == "$1" ]] || [[ "$1" == "" ]])
  then
    app_name=`awk -F "-" '{print $1}' <<< "$dir_name"`
    frame_name=`awk -F "-" '{print $2}' <<< "$dir_name"`
    if [[ "$frame_name" == "" ]]
    then
      frame_name="main"
    fi
    echo Creating CSS and JS for $app_name, frame = $frame_name...
    cd js/$dir_name
    npm run build
    cd ../..

    # for output_file in `ls js/$dir_name/build/static/js`
    # do
    #  new_output_file=`sed -e "s/main/${frame_name}/" <<< "$output_file"`
    #  mv -v js/$dir_name/build/static/js/$output_file js/$dir_name/build/static/js/$new_output_file
    # done

    django_app_name=$app_name

    # looking for core pseudomodules
    if [[ `awk -F "." '{print $1}' <<< $app_name` == "core" ]]
    then
      django_app_name="core"
    fi

    rm -rvf ../corefacility/$django_app_name/static/$app_name/$frame_name.*.js
    rm -rvf ../corefacility/$django_app_name/static/$app_name/$frame_name.*.js.map
    rm -rvf ../corefacility/$django_app_name/static/$app_name/$frame_name.*.css
    rm -rvf ../corefacility/$django_app_name/static/$app_name/$frame_name.*.css.map
    cp -v js/$dir_name/build/static/js/$frame_name.*.js ../corefacility/$django_app_name/static/$app_name
    cp -v js/$dir_name/build/static/js/$frame_name.*.js.map ../corefacility/$django_app_name/static/$app_name
    cp -v js/$dir_name/build/static/css/$frame_name.*.css ../corefacility/$django_app_name/static/$app_name
    if (( $? != 0  ))
    then
      touch ../corefacility/$django_app_name/static/$app_name/$frame_name.min.css
    fi
    cp -v js/$dir_name/build/static/css/$frame_name.*.css.map ../corefacility/$django_app_name/static/$app_name
    cp -v js/$dir_name/build/static/$app_name/* ../corefacility/$django_app_name/static/$app_name
  fi
done