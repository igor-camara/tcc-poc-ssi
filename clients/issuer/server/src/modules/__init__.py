# Import settings and app factory
from modules.config.settings import settings
from modules.config.app import create_app
from modules.user.schema import User

# Create app instance
app = create_app()

# Initialize database
User.init_db()