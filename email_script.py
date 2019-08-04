import email
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import aiosmtplib
from email.utils import formataddr

from config import EMAIL_USER, EMAIL_PASSWORD


async def send(send_to, msg):
    server = aiosmtplib.SMTP("smtp.gmail.com")
    await server.connect()
    await server.ehlo()
    await server.starttls()
    await server.ehlo()
    await server.login(EMAIL_USER, EMAIL_PASSWORD)
    await server.sendmail("merkosdb@gmail.com", [send_to], msg)
    server.close()
    print("Email sent succesfully")


async def email_csv(csv_file, email, collection, search_terms):
    msg = MIMEMultipart("alternative")
    msg['From'] = formataddr(("Merkos DB by Moshe Uminer", "merkosdb@gmail.com"))
    msg["To"] = "mosheduminer@gmail.com"
    if len(search_terms) == 0 :
        msg["Subject"] = f"Contacts from {collection} collection"
    else:
        msg["Subject"] = f"Contacts from {collection} collection - matching {search_terms}"
    part = MIMEApplication(open(csv_file, "rb").read(), Name="contacts.csv")
    part['Content-Disposition'] = "attachment; filename=contacts.csv"
    msg.attach(part)
    await send(email, msg.as_string())
