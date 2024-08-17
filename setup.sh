if [ ! -d "venv" ]; then
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    pre-commit install
fi

mkdir -p ~/.config/Code/Dictionaries
cd ~/.config/Code/Dictionaries
wget "https://github.com/titoBouzout/Dictionaries/raw/master/English%20(American).aff"
wget "https://github.com/titoBouzout/Dictionaries/raw/master/English%20(American).dic"
