"""
Authentication service for Google OAuth verification.
Simple authentication layer - ready for future multi-tenant expansion.
"""
from google.auth.transport import requests
from google.oauth2 import id_token
from app.core.config import settings
import logging
import httpx

logger = logging.getLogger(__name__)


class AuthService:
    """Simple authentication service using Google OAuth."""
    
    # Google OAuth Client IDs (add to .env)
    GOOGLE_CLIENT_IDS = [
        # Add your Google OAuth Client ID here
        # For now, we'll verify any Google token (for CV demo)
    ]
    
    @staticmethod
    def verify_google_token(token: str) -> dict:
        """
        Verify Google OAuth token and extract user info.
        Handles both ID tokens and access tokens.
        
        Returns:
            dict: User info with 'email', 'name', 'user_id'
        
        Raises:
            ValueError: If token is invalid
        """
        try:
            # Try to verify as ID token first
            try:
                idinfo = id_token.verify_oauth2_token(
                    token,
                    requests.Request(),
                    None  # Accept any Google client ID for demo
                )
                
                # Extract user info from ID token
                email = idinfo.get('email')
                name = idinfo.get('name', 'User')
                picture = idinfo.get('picture', '')
                
                if not email:
                    raise ValueError("Email not found in token")
                
            except (ValueError, Exception) as e:
                # If ID token verification fails, try as access token
                # Fetch user info from Google's userinfo endpoint
                logger.info("Token is not ID token, trying as access token...")
                
                response = httpx.get(
                    'https://www.googleapis.com/oauth2/v2/userinfo',
                    headers={'Authorization': f'Bearer {token}'},
                    timeout=10.0
                )
                
                if response.status_code != 200:
                    raise ValueError(f"Failed to fetch user info: {response.status_code}")
                
                user_data = response.json()
                email = user_data.get('email')
                name = user_data.get('name', 'User')
                picture = user_data.get('picture', '')
                
                if not email:
                    raise ValueError("Email not found in user data")
            
            # Use email as user_id (future: can map to tenant_id)
            user_id = email.split('@')[0]  # Simple: use email prefix as user_id
            
            return {
                'email': email,
                'name': name,
                'user_id': user_id,
                'picture': picture,
            }
            
        except ValueError as e:
            logger.error(f"Token verification failed: {str(e)}")
            raise ValueError(f"Invalid Google token: {str(e)}")
        except Exception as e:
            logger.error(f"Auth error: {str(e)}")
            raise ValueError(f"Authentication failed: {str(e)}")
    
    @staticmethod
    def get_user_id_from_token(token: str) -> str:
        """
        Quick method to get user_id from token.
        Returns 'default' if token is invalid (for backward compatibility).
        """
        try:
            user_info = AuthService.verify_google_token(token)
            return user_info['user_id']
        except:
            # Fallback to default for backward compatibility
            return 'default'
