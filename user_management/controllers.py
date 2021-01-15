from django.contrib.auth import get_user_model
from management_portal.general import Status

User = get_user_model()

class UserController:
    """
    The 'UserController' manages the django user model.
    This includes things like changing profile information and passwords.
    """

    @staticmethod
    def change_profile(id: int, username: str, email: str, first_name: str, last_name: str):
        """
        Updates the profile data with the given data if all data is valid.
        It returns a status object.

        Parameters:
        id (int)        : user id
        username (str)  : the user's unique username
        email (str)     : email address
        first_name (str): the user's first name
        last_name (str) : the user's last name

        Returns:
        Status: update status
        """
        status = Status()
        status = UserController.__check_profile_validity(
            id          = id,
            username    = username,
            email       = email,
            first_name  = first_name,
            last_name   = last_name,
        )
        if status.status:
            try:
                user            = User.objects.get(id = id)
                user.username   = username
                user.email      = email
                user.first_name = first_name
                user.last_name  = last_name
                user.save()
                status.message  = 'Profil erfolgreich aktualisiert.'
            except:
                status.status  = False
                status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'

        return status

    @staticmethod
    def change_password(id: int, old_password: str, new_password_1: str, new_password_2: str):
        """
        Updates the password if all data is valid.
        It returns a status object.

        Parameters:
        id (int)            : user id
        old_password (str)  : old password
        new_password_1 (str): new password
        new_password_2 (str): new password again

        Returns:
        Status: update status
        """
        status = Status()
        status = UserController.__check_password_validity(
            id              = id,
            old_password    = old_password,
            new_password_1  = new_password_1,
            new_password_2  = new_password_2,
        )
        if status.status:
            try:
                user            = User.objects.get(id = id)
                status.status   = user.check_password(old_password)
                if status.status:
                    user.set_password(new_password_1)
                    user.save()
                    status.message  = 'Passwort erfolgreich aktualisiert.'
                else:
                    status.message = 'Falsches Passwort.'
            except:
                status.status  = False
                status.message = 'Es ist ein unerwarteter Fehler aufgetreten.'

        return status

    @staticmethod
    def __check_profile_validity(id: int, username: str, email: str, first_name: str, last_name: str):
        """
        Checks if profile data to save is valid and complete.
        It returns a status object.

        Parameters:
        id (int)        : user id
        username (str)  : the user's unique username
        email (str)     : email address
        first_name (str): the user's first name
        last_name (str) : the user's last name

        Returns:
        Status: status
        """
        status = Status()
        if not id:
            status.message = 'Bitte ID angeben.'
        elif not len(username):
            status.message = 'Bitte Benutzername angeben.'
        elif len(username) > 150:
            status.message = 'Benutzername darf maximal 150 Zeichen lang sein.'
        elif not len(email):
            status.message = 'Bitte E-Mail-Adresse angeben.'
        elif len(email) > 64:
            status.message = 'E-Mail-Adresse darf maximal 64 Zeichen lang sein.'
        elif not len(first_name):
            status.message = 'Bitte Vornamen angeben.'
        elif len(first_name) > 150:
            status.message = 'Vorname darf maximal 150 Zeichen lang sein.'
        elif not len(last_name):
            status.message = 'Bitte Nachnamen angeben.'
        elif len(last_name) > 150:
            status.message = 'Nachname darf maximal 150 Zeichen lang sein.'
        else:
            users = User.objects.all()
            for user in users:
                if user.username == username and not user.id == id:
                    status.message = 'Dieser Benutzername ist bereits vergeben.'
                    break
                if not len(status.message):
                    status.status = True

        return status

    @staticmethod
    def __check_password_validity(id: int, old_password: str, new_password_1: str, new_password_2: str):
        """
        Checks if 'passwords' are valid.
        It returns a status object.

        Parameters:
        id (int)            : user id
        old_password (str)  : old password
        new_password_1 (str): new password
        new_password_2 (str): new password again

        Returns:
        Status: status
        """
        status = Status()
        if not id:
            status.message = 'Bitte ID angeben.'
        elif not len(old_password):
            status.message = 'Bitte altes Passwort angeben.'
        elif not len(new_password_1):
            status.message = 'Bitte neues Passwort angeben.'
        elif not len(new_password_2):
            status.message = 'Bitte neues Passwort wiederholen.'
        elif len(new_password_1) > 256:
            status.message = 'Passwörter sind auf maximal 256 Zeichen begrenzt.'
        elif not new_password_1 == new_password_2:
            status.message = 'Die Passwörter stimmen nicht überein.'
        else:
            status.status = True

        return status
