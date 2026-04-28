"""
Google OAuth2 Authentication Backend for Django.
Verifies Google ID tokens (from Google Identity Services) and links to Django users by email.
"""
import logging
import requests

from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

GOOGLE_CLIENT_ID = '704532942244-f8ki61utsulo3gv0sdu4gegvc4pu48jt.apps.googleusercontent.com'


class FirebaseAuthBackend(BaseBackend):
    """
    Custom auth backend that verifies Google OAuth2 ID tokens.
    Links Google users to Django users by email.
    """

    def authenticate(self, request, google_credential=None, **kwargs):
        if google_credential is None:
            return None

        try:
            # Verify the Google ID token using Google's TokenInfo API (Removes need for google-auth library)
            verify_url = f"https://oauth2.googleapis.com/tokeninfo?id_token={google_credential}"
            response = requests.get(verify_url)
            
            if response.status_code != 200:
                raise ValueError(f"Invalid token: {response.text}")
                
            decoded_token = response.json()
            
            # Verify audience
            if decoded_token.get('aud') != GOOGLE_CLIENT_ID:
                raise ValueError("Token audience mismatch")

            # Verify issuer
            issuer = decoded_token.get('iss', '')
            if issuer not in ('accounts.google.com', 'https://accounts.google.com'):
                logger.error(f"Invalid token issuer: {issuer}")
                return None

            email = decoded_token.get('email')
            name = decoded_token.get('name', '')
            picture = decoded_token.get('picture', '')

            logger.info(f"Google auth: email={email}, name={name}")
            print(f"[Google Auth] Verified: email={email}, name={name}")

            if not email:
                logger.warning("Google token has no email claim")
                return None

            # Try to find existing Django user by email
            try:
                user = User.objects.get(email=email)
                logger.info(f"Found existing user: {user.username}")
                print(f"[Google Auth] Found existing user: {user.username}")
                return user
            except User.DoesNotExist:
                pass

            # No user with that email — create a new one
            base_username = email.split('@')[0]
            username = base_username
            counter = 1
            while User.objects.filter(username=username).exists():
                username = f"{base_username}{counter}"
                counter += 1

            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=name.split(' ')[0] if name else '',
                last_name=' '.join(name.split(' ')[1:]) if name and ' ' in name else '',
            )
            user.set_unusable_password()
            user.save()

            logger.info(f"Created new user: {user.username} ({email})")
            print(f"[Google Auth] Created new user: {user.username} ({email})")
            return user

        except ValueError as e:
            logger.error(f"Google token verification failed: {e}")
            print(f"[Google Auth] FAILED: {e}")
            if request:
                request.session['auth_error'] = f"ValueError: {str(e)}"
            return None
        except Exception as e:
            logger.error(f"Google auth error: {e}")
            print(f"[Google Auth] EXCEPTION: {e}")
            import traceback
            traceback.print_exc()
            if request:
                request.session['auth_error'] = f"Exception: {str(e)}"
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None


