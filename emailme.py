import smtplib
from email.mime.text import MIMEText
from sys import argv

def emailme(title, msg):
    #need to turn on less secure gmail client on gmail!
    fromaddress='xxxx@gmail.com'
    frompass='xxxx'
    receiveraddress='xxxx@gmail.com'

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.ehlo()
    server.starttls()
    server.login(fromaddress, frompass)

    if title == '':
        title = 'Email from ufindcar.com: something may be wrong!'
    if msg == '':
        msg = 'Nothing in body, check the title.'
    mail_body = MIMEText(msg)
    mail_body['Subject'] = title
    mail_body['From'] = fromaddress
    mail_body['To'] = receiveraddress

    server.sendmail(fromaddress, receiveraddress, mail_body.as_string())
    server.quit()

if __name__ == '__main__':
    script, data_file = argv
    email_body = open(data_file).read()
    email_title = '(ufindcar)Spiders daily update'
    emailme(email_title,email_body)

