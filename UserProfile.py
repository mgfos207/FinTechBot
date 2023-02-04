import robin_stocks.robinhood as rh
import pyotp

class UserProfile:
    def __init__(self, creds_file):
        self.creds_life = creds_file
        self.profile = None

    def login(self):
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

    def load_user_info(self):
        self.profile = rh.load_account_profile()
        print(self.profile)

    def logout(self):
        rh.logout()