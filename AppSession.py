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
        self.user_prof = UserProfile(self.config['creds_file'])
        self.session = self.user_prof.login()

    def end_session(self):
        try:
            self.user_prof.logout()
            self.session = None
        except Exception as e:
            raise e("Error logging out of our user session")

    def activate_session(self):
        pass