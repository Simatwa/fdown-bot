#!/usr/bin/bash
DIR="fdown-bot"

if [[ -d "$DIR" ]]; then
   rm $DIR -rf
fi

git clone https://github.com/Simatwa/fdown-bot.git
cp .env $DIR/
cd $DIR
pip install -U pip
pip install -r requirements.txt
python bot.py
