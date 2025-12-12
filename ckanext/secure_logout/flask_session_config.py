from flask_session import Session
import redis
import logging

log = logging.getLogger(__name__)

_redis_client = None

def init_flask_session(app):
    """Configure Flask-Session with Redis"""
    global _redis_client
    try:
        redis_url = app.config.get('ckan.redis.url', 'redis://localhost:6379/1')

        _redis_client = redis.from_url(redis_url)
        
        app.config['SESSION_TYPE'] = 'redis'
        app.config['SESSION_REDIS'] = _redis_client
        app.config['SESSION_PERMANENT'] = True
        app.config['SESSION_USE_SIGNER'] = True
        app.config['SESSION_KEY_PREFIX'] = 'ckan_session:'
        app.config['PERMANENT_SESSION_LIFETIME'] = 3600 # 1 hour
        app.config['SESSION_REFRESH_EACH_REQUEST'] = True
        
        # Apply the configuration
        Session(app)
        
        log.info("Flask-Session configured with Redis")
        
    except Exception as e:
        log.error(f"Failed to configure Flask-Session: {e}")
        raise

def get_redis_client():
    """Provide the configured Redis client"""
    if not _redis_client:
        log.error("Redis client requested before initialization.")
        raise Exception("Redis client not initialized.")
    return _redis_client