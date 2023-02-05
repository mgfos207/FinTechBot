import robin_stocks.robinhood as rh
import pyotp

from UserProfile import UserProfile

class AppSession:
    def __init__(self, config):
        try:
            with open(config) as config_file:
                self.config = config_file
                self.scheduled_session = config_file['scheduled_orders']
            self.user_prof = None
            self.session = None
        except FileNotFoundError as e:
            raise FileNotFoundError(f"Couldn't find the following config file: {config}")
    
    def start_session(self):
        self.session = self.__login()
        profile_info = self.__load_user_info()
        self.user_prof = UserProfile(profile_info)

    def end_session(self):
        self.__logout()
        self.session = None

    def __login(self):
        try: # try getting token and using it otherwise do login
            lines = open(self.creds).read().splitlines()
            KEY = lines[0]
            EMAIL = lines[1]
            PASSWD = lines[2]
            CODE = pyotp.TOTP(KEY).now()
            session = rh.login(EMAIL, PASSWD, mfa_code=CODE)
        except Exception as e:
            raise Exception(f"Got the following error {e}")
        finally:
            self.load_user_info()
            return session

    def __load_user_info(self):
        try:
            profile = rh.load_account_profile()
            return profile
        except Exception as e:
            raise Exception(f"Got the following error when attempting to load the user info: {e}")

    def __logout(self):
        try:
            rh.logout()
        except Exception as e:
            raise Exception(f"Got the following error after attempting to logout the user session: {e}")

    def validate_session(self, func):
        """
        Wrapper function that validates user session before invoking robin stocks API
        """
        def wrapper(*args, **kwargs):
            try:
                rh.load_basic_profile()
                func(*args, **kwargs)
            except Exception as e:
                self.start_session()
                func(*args, **kwargs)

        return wrapper
    
    @validate_session
    def activate_session(self):
        pass
    