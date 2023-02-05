from  dataclasses import dataclass

@dataclass
class UserProfile:
    _profile: dict

    @property
    def user_profile(self) -> dict:
        return self._profile

    @user_profile.setter
    def user_profile(self, updated_profile: dict) -> None:
        self._profile = updated_profile

    @property
    def user_cash(self) -> str:
        return self._profile['cash']