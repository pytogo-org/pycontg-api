
from utils.email_templates import render_email_template
from utils.ticket import  ticket_system
from email.message import EmailMessage
from email.utils import formataddr
import os
import smtplib


SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_EMAIL_PASSWORD = os.environ.get("SENDER_EMAIL_PASSWORD")
SMTP_SERVER = os.environ.get("SMTP_SERVER")
SMTP_SERVER_PORT = os.environ.get("SMTP_SERVER_PORT")

def send_ticket_email(participant_name, participant_email, participant_id, organization="", country_city="Togo/Lomé"):
    msg = EmailMessage()
    ticket_url = ticket_system(data=participant_id, name=participant_name, organization=organization, country_city=country_city)
    msg['Subject'] = "🎫 Your Ticket | Votre ticket pour le PyCon Togo 2025"
    msg['From'] = formataddr(('PyCon Togo Organizing Team', SENDER_EMAIL))
    msg['To'] = participant_email

    msg.set_content("Votre client mail ne supporte pas HTML. Cliquez sur le lien pour télécharger votre ticket.")
    message = f"""
        
    <h2>Bonjour {participant_name},</h2>
        <p>
      Merci pour votre inscription au <strong>PyCon Togo 2025</strong> !
        </p>
    <p>
      Voici votre <a href="{ticket_url}" target="_blank">ticket</a> 📩 à présenter à l’entrée de l’événement.
    </p>
    <hr style="margin: 20px 0;">
    <h2>Hello {participant_name},</h2>
    <p>
      Thank you for registering for <strong>PyCon Togo 2025</strong>!
    </p>
    <p>
      Here is your <a href="{ticket_url}" target="_blank">ticket</a> 📩 to present at the entrance of the event.
    </p>
 
    """
    full_message = render_email_template(message=message)
    msg.add_alternative(full_message, subtype='html')

    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_SERVER_PORT) as server:
        server.login(SENDER_EMAIL, SENDER_EMAIL_PASSWORD)
        server.send_message(msg)

if __name__ == "__main__":
    data = "5c663cb9-5b6c-4ff6-a2cf-0c87f2f5127c"  # Example participant ID
    name = "tester 1"
    ref = "TCK-2025-00042"
    organization = ""
    participant_email = "ibrahim@pytogo.org"

    send_ticket_email(name, participant_email, data, organization)
    print("Ticket email sent successfully!")