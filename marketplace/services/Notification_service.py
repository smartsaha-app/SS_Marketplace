from marketplace.models import Notification
from django.core.mail import send_mail
from django.conf import settings

class NotificationService:
    @staticmethod
    def create_notification(user, message, notification_type, reference_id=None, send_email=True):
        """
        Crée une notification dans la base et optionnellement envoie un email.

        :param user: instance User destinataire
        :param message: texte de la notification
        :param notification_type: type de la notification (ex: 'user_registration')
        :param reference_id: référence optionnelle (id utilisateur, post, bid...)
        :param send_email: bool, envoyer un email ou pas
        """
        # Création en base
        notif = Notification.objects.create(
            id_user=user,
            message=message,
            notification_type=notification_type,
            reference_id=reference_id
        )

        # Envoi email si activé
        if send_email and user.email:
            subject = f"Nouvelle notification : {notification_type.replace('_', ' ').capitalize()}"
            send_mail(
                subject,
                message,
                settings.DEFAULT_FROM_EMAIL,
                [user.email],
                fail_silently=False,
            )

        # Ici tu peux aussi ajouter un push notification via FCM / OneSignal
        # NotificationService.push_notification(user, message)

        return notif

    # Exemple pour push (à compléter selon ton service)
    @staticmethod
    def push_notification(user, message):
        """
        Envoi d'une notification push (ex: FCM, OneSignal)
        """
        # Code pour push notification ici
        pass
