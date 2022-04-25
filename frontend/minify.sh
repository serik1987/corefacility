#!/bin/bash

for app_name in `ls css`
do
	echo Creating CSS for $app_name...
	minify css/$app_name/main.css > ../corefacility/$app_name/static/$app_name/main.min.css
done