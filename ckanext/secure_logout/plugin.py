import ckan.plugins as plugins
import ckan.plugins.toolkit as toolkit
from flask import Blueprint, session, make_response
from ckan.common import logout_user, current_user
import logging
from ckan.plugins.interfaces import IConfigurable 
from ckanext.secure_logout.flask_session_config import init_flask_session
from ckanext.secure_logout.flask_session_config import get_redis_client 
import ckan.lib.base as base 

log = logging.getLogger(__name__)


class SecureLogoutPlugin(plugins.SingletonPlugin):
    plugins.implements(plugins.IBlueprint)
    plugins.implements(plugins.IConfigurer)
    plugins.implements(IConfigurable)
    plugins.implements(plugins.IMiddleware)

    def update_config(self, config_):
        """Called in CKAN startup"""
        toolkit.add_template_directory(config_, 'templates')
        
    
    # IBlueprint
    def get_blueprint(self):
        blueprint = Blueprint('secure_logout', self.__module__)
        
        @blueprint.route('/user/_logout', methods=['GET', 'POST'])
        def logout():
            """Secure logout that invalidates server-side session."""
            
            if not current_user.is_authenticated:
                return toolkit.redirect_to('user.login')
            
            user_name = current_user.name

            # Retrieve the session key (SID) - REQUIRES REDIS SESSION
            session_key = session.sid 
            
            # Logout CKAN and clear Flask/Redis session
            logout_user() 
            session.clear()
            session.modified = True
            
            log.info(f"User {user_name} logged out successfully. SID: {session_key}")
            
            try:
                redis_client = get_redis_client()
                
                # Retrieve the session prefix (defined in flask_session_config)
                session_prefix = toolkit.config.get('SESSION_KEY_PREFIX', 'ckan_session:')
                full_redis_key = session_prefix + session_key
                
                deleted_count = redis_client.delete(full_redis_key) 
                
                if deleted_count > 0:
                    log.info(f"Session key {full_redis_key} successfully deleted from Redis.")
                else:
                    log.warning(f"Session key {full_redis_key} not found in Redis (expired/race condition).")
                    
            except Exception as e:
                log.error(f"Failed to delete Redis session key {session_key}: {e}")

            
            # CLIENT-SIDE INVALIDATION (BROWSER COOKIE)
            response = toolkit.redirect_to('home.index') 
            response_obj = make_response(response)
            response_obj.delete_cookie('ckan') # Remove browser cookie
            
            return response_obj
        
        
        return blueprint
    
    # FLASK-SESSION INITIALIZATION METHOD
    def configure(self, config):
        pass
        
    def make_middleware(self, app, config):
        """
        Called by CKAN and get the flask app instance
        """
        from ckanext.secure_logout.flask_session_config import init_flask_session

        init_flask_session(app)
        log.info("Secure session plugin initialized via IMiddleware")

        # Return the modified application
        return app
    
    def make_error_log_middleware(self, app, config):
        """
        Required by IMiddleware interface in newer CKAN versions.
        We just return the app as is because we don't need custom error logging.
        """
        return app