#!/bin/bash

git pull

make save

split -b 30M sso-validator.tar sso-validator.tar.part_

for f in sso-validator.tar.part_*; do
  echo "上傳 $f..."
  curl -F "file=@$f" https://keyman.intellicore-service.net/setup/
done

rm sso-validator.tar*