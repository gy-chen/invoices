#coding: utf-8
from . import config
from . import create_app

# TODO disable debug and testing latter
app = create_app(config, debug=True, testing=True)

def main():
    app.run()

if __name__ == '__main__':
    main()
