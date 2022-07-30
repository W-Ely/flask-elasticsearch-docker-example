from flask_script import Manager

from api import create_app
from config import CONFIG

app = create_app(CONFIG)
manager = Manager(app)

if __name__ == "__main__":
    manager.run()
