import smtplib
import os
from dotenv import load_dotenv

load_dotenv()


class NotificationService:
    def __init__(self, email_host=None, email_port=None, email_user=None, email_password=None):
        self.email_host = email_host or os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
        self.email_port = email_port or int(os.environ.get('EMAIL_PORT', '587'))
        self.email_user = email_user or os.environ.get('EMAIL_USER', '')
        self.email_password = email_password or os.environ.get('EMAIL_PASSWORD', '')

    def send_email(self, to: str, subject: str, body: str) -> bool:
        try:
            server = smtplib.SMTP(self.email_host, self.email_port)
            server.starttls()
            server.login(self.email_user, self.email_password)
            message = f"Subject: {subject}\n\n{body}"
            server.sendmail(self.email_user, to, message)
            server.quit()
            return True
        except Exception as e:
            print(f"Erro ao enviar email: {str(e)}")
            return False

    def notify_task_assigned(self, user, task) -> None:
        subject = f"Nova task atribuída: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' foi atribuída a você.\n\n"
            f"Prioridade: {task.priority}\nStatus: {task.status}"
        )
        self.send_email(user.email, subject, body)

    def notify_task_overdue(self, user, task) -> None:
        subject = f"Task atrasada: {task.title}"
        body = (
            f"Olá {user.name},\n\n"
            f"A task '{task.title}' está atrasada!\n\n"
            f"Data limite: {task.due_date}"
        )
        self.send_email(user.email, subject, body)
