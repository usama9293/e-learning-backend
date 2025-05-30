from flask import Flask, jsonify
from datetime import timedelta
import os
from flask_cors import CORS
from extensions import db, jwt

def create_app():
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = 'your-secret-key'  # Change this!
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', 'jwt-secret-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=1)
    app.config['JWT_TOKEN_LOCATION'] = ['headers']
    app.config['JWT_HEADER_NAME'] = 'Authorization'
    app.config['JWT_HEADER_TYPE'] = 'Bearer'
    app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    
    # Configure CORS
    CORS(app, 
         resources={r"/*": {
             "origins": ["http://localhost:3000", "http://localhost:3001"],
             "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
             "allow_headers": ["Content-Type", "Authorization"],
             "supports_credentials": True,
             "expose_headers": ["Content-Range", "X-Content-Range"],
             "max_age": 3600
         }},
         supports_credentials=True)

    # Import routes
    from routes.auth import auth_bp
    from routes.api import api_bp
    from routes.admin import admin_bp

    # Register blueprints with correct prefixes
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(api_bp, url_prefix='/')
    app.register_blueprint(admin_bp, url_prefix='/admin')

    return app

app = create_app()

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'message': 'FDMA AI API is running',
        'endpoints': {
            'auth': [
                {'path': '/auth/register', 'method': 'POST', 'description': 'Register new user'},
                {'path': '/auth/login', 'method': 'POST', 'description': 'Login user'},
                {'path': '/auth/profile', 'method': 'GET', 'description': 'Get user profile (requires auth)'}
            ],
            'api': [
                {'path': '/api/upload', 'method': 'POST', 'description': 'Upload financial data (requires auth)'},
                {'path': '/api/data', 'method': 'GET', 'description': 'Get financial data (requires auth)'},
                {'path': '/api/data/<id>', 'method': 'PUT', 'description': 'Update financial data (requires auth)'},
                {'path': '/api/stats', 'method': 'GET', 'description': 'Get statistics (requires auth)'}
            ]
        }
    })

def init_database():
    with app.app_context():
        # Create all tables
        db.create_all()
        
        # Verify tables exist
        from models.financial_data import FinancialData, AuditLog
        from models.user import User
        
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        app.logger.info(f'Database tables: {tables}')
        
        # Verify table structure
        for table in [User, FinancialData, AuditLog]:
            if table.__tablename__ in tables:
                columns = [col['name'] for col in inspector.get_columns(table.__tablename__)]
                app.logger.info(f'Table {table.__tablename__} columns: {columns}')
            else:
                app.logger.error(f'Table {table.__tablename__} does not exist!')

if __name__ == '__main__':
    init_database()
    app.run(debug=True, port=5000)
