from gluon.tools import Mail
mail = Mail()

mail.settings.server = '.com:465'
mail.settings.sender = '.com'
mail.settings.login = ':'

def generate_mail():
    '''mail.send(self, to, subject='None', message='None', attachments=[],
    cc=[], bcc=[], reply_to=[], sender=None, encoding='utf-8',
     raw=True, headers={})'''
    # x = mail.send(to=['adarshsanjeev@gmail.com'], subject="Test", message="ATTEMPT #!")
    curr_time = datetime.datetime.now()
    coming_time = curr_time + datetime.timedelta(minutes=15)
    rows = db((db.events.startAt < coming_time) & (db.events.startAt>curr_time)).select(orderby=db.events.startAt)
    x = None
    if x == True:
        session.flash = 'email sent sucessfully.'
    else:
        session.flash = 'fail to send email sorry!'

from gluon.scheduler import Scheduler
scheduler = Scheduler(db)

# scheduler.queue_task(generate_mail, period=300, repeats=0)
