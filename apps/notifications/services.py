from .models import Notification

def create_notification(user, type_notification, titre, message, lien=None):
    """
    Crée une notification in-app pour un utilisateur.
    """
    return Notification.objects.create(
        utilisateur=user,
        type_notification=type_notification,
        titre=titre,
        message=message,
        lien=lien
    )
