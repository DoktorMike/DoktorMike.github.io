#!/bin/bash
#echo "${BASH_SOURCE[0]}"
#echo "$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
Rscript -e "source('$DIR/rmarkdown.R'); convertRMarkdown(images.dir='$DIR/images')"
mv *.md ../_posts
