import resend

from .settings import settings

resend.api_key = settings.RESEND_API_KEY


def send_mail(recievers_list: list[str], subject: str, html: str) -> resend.Email:
    params: resend.Emails.SendParams = {
        "from": "info@algorithmicdev.in",
        "to": recievers_list,
        "subject": subject,
        "html": html,
    }
    email: resend.Email = resend.Emails.send(params)
    return email
