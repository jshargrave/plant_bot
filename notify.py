import smtplib
import email
import abc

# Email server
EMAIL_SERVER = "smtp-mail.outlook.com"


EMAIL_SERVER_DICT = {
    "Gmail":   "smtp.gmail.com",
    "Hotmail": "smtp.live.com:587",
    "Outlook": "smtp-mail.outlook.com",
    "AT&T":    "smpt.mail.att.net:465",
    "Verizon": "smtp.verizon.net:465"
}

SMS_GATEWAY_DICT = {
    "Alltel":            "sms.alltelwireless.com",
    "AT&T":              "txt.att.net",
    "Boost Mobile":      "sms.myboostmobile.com",
    "Cricket Wireless":  "sms.mycricket.com",
    "MetroPCS":          "mymetropcs.com",
    "Project Fi":        "msg.fi.google.com",
    "Republic Wireless": "text.republicwireless.com",
    "Straight Talk":     "vtext.com",
    "Sprint":            "messaging.sprintpcs.com",
    "T-Mobile":          "tmomail.net",
    "U.S. Cellular":     "email.uscc.net",
    "Verizon Wireless":  "vtext.com",
    "Virgin Mobile":     "vmobl.com",
}


class InvalidSender(Exception):
    pass


class EmailNotify:
    def __init__(self, sender, recipient_list, credentials):
        self.credentials = credentials
        self.sender = sender
        self.recipient_list = recipient_list
        self.subject = "PlantBot Notification"

    def notify(self, msg_str):
        try:
            server_str = self.get_server()

            s = smtplib.SMTP(server_str)
            s.ehlo()  # Hostname to send for this command defaults to the fully qualified domain name of the local host.

            if server_str.endswith("587"):
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
        except InvalidSender as e:
            print("Error: {}".format(e))
        except smtplib.SMTPServerDisconnected as e:
            print("Error: {}".format(e))

    def get_server(self):
        server = ""

        # Check if this is a regular address
        for key, value in EMAIL_SERVER_DICT.items():
            if key.upper() in self.sender.upper():
                server = value

        # Check if this is a sms gateway address
        for key, value in SMS_GATEWAY_DICT.items():
            if key.upper() in self.sender.upper():
                server = value

        if not server:
            raise InvalidSender("Could not find email server for email '{}' ".format(self.sender))

        return server
