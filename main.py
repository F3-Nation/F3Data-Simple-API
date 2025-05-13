import os
import sys
import logging
from flask import Flask, jsonify
from sqlalchemy.exc import SQLAlchemyError
from models import db, Org, Event
from config import Config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
app.config.from_object(Config)

# Log configuration details (excluding sensitive info)
logger.info(f"Starting application in environment: {os.getenv('ENVIRONMENT', 'development')}")
logger.info(f"Database host: {app.config['SQLALCHEMY_DATABASE_URI'].split('@')[1].split('/')[0]}")

db.init_app(app)

# Verify database connection
def verify_db_connection():
    if not app.config['SQLALCHEMY_DATABASE_URI']:
        logger.error("Database URI is not configured")
        return False
    
    try:
        with app.app_context():
            db.session.execute('SELECT 1')
            db.session.commit()
            logger.info("Database connection successful")
            return True
    except SQLAlchemyError as e:
        logger.error(f"Database connection failed: {str(e)}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during database connection check: {str(e)}")
        return False
    finally:
        db.session.remove()

# Error handler for 500 errors
@app.errorhandler(500)
def handle_500_error(e):
    logger.error(f"Internal Server Error: {str(e)}")
    return jsonify(error="Internal Server Error", message=str(e)), 500

# Error handler for SQLAlchemy errors
@app.errorhandler(SQLAlchemyError)
def handle_db_error(e):
    logger.error(f"Database error: {str(e)}")
    return jsonify(error="Database Error", message="A database error occurred"), 500

@app.route('/', methods=['GET'])
def index():
    try:
        return jsonify(
            message="Welcome to the VERY simple F3 Data API!",
            status="healthy",
            database_connected=verify_db_connection()
        )
    except Exception as e:
        logger.error(f"Error in index route: {str(e)}")
        return jsonify(error="Error checking API health", message=str(e)), 500

@app.route('/regions/count', methods=['GET'])
def count_regions():
    try:
        with db.session.begin():
            count = db.session.query(Org).filter_by(org_type='region').count()
            logger.info(f"Retrieved region count: {count}")
            return jsonify(count=count)
    except SQLAlchemyError as e:
        logger.error(f"Database error in count_regions: {str(e)}")
        return jsonify(error="Database Error", message="Failed to retrieve region count"), 500
    except Exception as e:
        logger.error(f"Unexpected error in count_regions: {str(e)}")
        return jsonify(error="Unexpected Error", message=str(e)), 500
    finally:
        db.session.remove()

@app.route('/weeklyworkouts/count', methods=['GET'])
def count_weekly_workouts():
    try:
        with db.session.begin():
            count = db.session.query(Event).count()
            logger.info(f"Retrieved weekly workouts count: {count}")
            return jsonify(count=count)
    except SQLAlchemyError as e:
        logger.error(f"Database error in count_weekly_workouts: {str(e)}")
        return jsonify(error="Database Error", message="Failed to retrieve workout count"), 500
    except Exception as e:
        logger.error(f"Unexpected error in count_weekly_workouts: {str(e)}")
        return jsonify(error="Unexpected Error", message=str(e)), 500
    finally:
        db.session.remove()

def create_app():
    # Initialize extensions
    db.init_app(app)
    
    # Verify database connection on startup
    if not verify_db_connection():
        logger.error("Failed to connect to database on startup")
        return None
    
    return app

if __name__ == '__main__':
    application = create_app()
    if application is None:
        sys.exit(1)
    
    # Gunicorn configuration
    options = {
        'bind': f"0.0.0.0:{int(os.environ.get('PORT', 8080))}",
        'worker_class': 'gthread',
        'workers': 1,  # Single worker for Cloud Run
        'threads': 8,  # Increased threads per worker
        'timeout': 0,  # Disable timeout for Cloud Run
        'graceful_timeout': 30,  # Grace period for workers to finish
        'keepalive': 65,  # Keepalive timeout
        'max_requests': 1000,  # Restart workers after this many requests
        'max_requests_jitter': 50  # Add jitter to prevent all workers restarting at once
    }
    
    logger.info(f"Starting server on port {options['bind']} with timeout {options['timeout']}s")
    
    import gunicorn.app.base
    
    class StandaloneApplication(gunicorn.app.base.BaseApplication):
        def __init__(self, app, options=None):
            self.options = options or {}
            self.application = app
            super().__init__()

        def load_config(self):
            config = {key: value for key, value in self.options.items()
                     if key in self.cfg.settings and value is not None}
            for key, value in config.items():
                self.cfg.set(key.lower(), value)

        def load(self):
            return self.application
    
    StandaloneApplication(application, options).run()
