import smtplib
import email


# Email server
EMAIL_SERVER = "smtp.live.com"


class EmailNotify:
    def __init__(self, sender, recipient_list, credentials):
        self.credentials = credentials
        self.sender = sender
        self.recipient_list = recipient_list
        self.subject = "PlantBot Notification"

    def notify(self, msg_str):
        s = smtplib.SMTP(EMAIL_SERVER, 587)
        s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.
        s.starttls()  # Puts connection to SMTP server in TLS mode
        s.ehlo()
        s.login(*self.credentials)

        # Setup email message
        msg = email.message_from_string(msg_str)
        msg['From'] = self.sender
        msg['To'] = self.recipient_list
        msg['Subject'] = self.subject

        # Send email
        s.sendmail(self.sender, self.recipient_list, msg.as_string())

        # Close server connection
        s.quit()


class SMSNotify:
    pass


