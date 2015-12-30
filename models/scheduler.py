
def generate_mail():
    '''mail.send(self, to, subject='None', message='None', attachments=[],
    cc=[], bcc=[], reply_to=[], sender=None, encoding='utf-8',
     raw=True, headers={})'''
    pass

from gluon.scheduler import Scheduler
scheduler = Scheduler(db)

# scheduler.queue_task(generate_mail, period=300, repeats=0)
