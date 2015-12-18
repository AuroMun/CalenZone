# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

#########################################################################
## This is a sample controller
## - index is the default action of any application
## - user is required for authentication and authorization
## - download is for downloading files uploaded in the db (does streaming)
#########################################################################
import time
import datetime

def index():
    """
    example action using the internationalization operator T and flash
    rendered by views/default/index.html or views/generic.html

    if you need a simple wiki simply replace the two lines below with:
    return auth.wiki()
    """
    response.flash = T("Welcome to IIIT Calendar Portal")
    redirect(URL('calendar'))
    return dict(title='Please Log in')


@auth.requires_login()
def profile():
    form = SQLFORM(db.userTag)
    # dn=db(db.auth_user.id==request.args[0]).select()
    # tags = db(db.auth_user.id==db.userTag.auth_user and db.tag.id==db.userTag.tag).select(db.auth_user.email, db.tag.tagName)
    temp = db(db.userTag.auth_user == session.auth.user.id).select()
    mytags = []
    mytags += [(db.tag[i.tag].tagName, i.id) for i in temp]
    form.vars.auth_user = session.auth.user.id
    grid = SQLFORM.grid(db.events.ownerOfEvent == session.auth.user.id)
    if form.process().accepted:
        response.flash = T("Tag Added!")
        redirect(URL())
    return locals()

@auth.requires_login()
def deleteGroup():
    try:
        id = request.args[0]
    except IndexError:
        redirect(URL('profile'))
    crud.delete(db.userTag, id)
    redirect(URL('profile'))
    return

def groupNameFormatter(x):
    y = ""
    for i in x:
        y = y + "\'" + str(i.tagName) + "\'"
        y = y + ","
    if y != "":
        y = y[:-1]
    return y

@auth.requires_login()
def createEvent():
    form = SQLFORM(db.events)
    form.vars.ownerOfEvent = session.auth.user.id

    ##adding group names
    x = db(db.tag).select(db.tag.tagName)
    y = groupNameFormatter(x)

    ##Processing Form
    if form.process().accepted:
        response.flash = "Event created successfully"
        groups = request.vars.groups.split(", ")
        for group in groups:
            gr_id = db(db.tag.tagName == group).select(db.tag.id)[0].id
            response.flash += ":" + str(gr_id)
            db.eventTag.insert(tag=gr_id, events=form.vars.id)
        redirect(URL('calendar'))
    return dict(form=form, grouplist=T(y))

@auth.requires_login()
def changeTags():
    try:
        request.args[0]
    except IndexError:
        redirect(URL('myEvents'))
    form_id = request.args[0]

    ##adding group names
    x = db(db.tag).select(db.tag.tagName)
    y = groupNameFormatter(x)
    q1 = db.eventTag.events == form_id
    q2 = db.tag.id == db.eventTag.tag
    currentTags = groupNameFormatter(db(q1 & q2).select(db.tag.tagName))
    if request.vars.groups:
        db(db.eventTag.events==form_id).delete()
        groups = request.vars.groups.split(", ")
        for group in groups:
            gr_id = db(db.tag.tagName == group).select(db.tag.id)[0].id
            db.eventTag.insert(tag=gr_id, events=form_id)
        redirect(URL('myEvents'))
    return dict(grouplist=T(y), currentTags=currentTags)

@auth.requires_login()
def setEventTags():
    myevents = db(db.events.ownerOfEvent == session.auth.user.id).select(db.events.id)
    temp = [i for i in myevents]
    form = SQLFORM.grid(db.eventTag.events.belongs(temp))
    # if form.process().accepted:
    #    response.flash = T("Tag added!")
    return locals()


def showEvent():
    event = db(db.events.auth_user == request.args[0]).select()[0]
    return locals();


def showDes():
    des = db(db.events.id == request.args[0]).select(db.events.description, db.events.startAt, db.events.endAt,
                                                     db.events.link, db.events.contact, db.events.eventName,
                                                     db.events.venue)[0]
    return dict(des=des)

@auth.requires_login()
def myEvents():
    events = db(db.events.ownerOfEvent == session.auth.user.id).select()
    return dict(events=events)

@auth.requires_login()
def editEvent():
    try:
        request.args[0]
    except IndexError:
        redirect(URL('myEvents'))
    eventId = request.args[0]
    ownerOfEvent = db(db.events.id==eventId).select(db.events.ownerOfEvent)[0].ownerOfEvent
    if ownerOfEvent != session.auth.user.id:
        redirect(URL('myEvents'))
    # form1=crud.update(db.events,eventId)
    # crud.settings.update_next = URL('myEvents')
    record = db.events(eventId)
    form = SQLFORM(db.events, record)
    if form.process().accepted:
        redirect(URL('myEvents'))
    return dict(form=form)


@auth.requires_login()
def calendar():
    return locals()


@auth.requires_login()
def deleteEvent():
    event_id = request.args[0]
    event = db.events[event_id]
    if event.created_by == session.auth.user.id:
        session.flash = "Event deleted!"
        db(db.events.id == event_id).delete()
    else:
        session.flash = "You do no have permission to delete this event!"
    redirect(URL('myEvents'))

@auth.requires_login()
def eventView():
    ##db(db.userTag.auth_user==session.auth.user.id).select()
    # tags=db(db.userTag.auth_user==session.auth.user.id).select(db.userTag.tag)
    # events = []
    # blah = tags[0]
    # for taga in tags:
    #    events = db(db.eventTag.tag == taga).select(db.events.eventName)
    cond1 = (db.userTag.auth_user == session.auth.user.id)
    q1 = db.userTag.tag == db.eventTag.tag
    q2 = db.userTag.auth_user == session.auth.user.id
    q3 = db.events.id == db.eventTag.events
    #q4 = db.events.ownerOfEvent = session.auth.user.id
    events = db((q1 & q2 & q3)).select(db.userTag.tag, db.events.eventName, db.events.id, db.events.startAt,
                                                   db.events.endAt, db.events.typeOfEvent, db.eventTag.tag,
                                                   distinct=True)
    # events = db(cond1 and db.userTag.tag==db.eventTag.tag and db.events.id == db.eventTag.events).select()
    for event in events:
        event.id = event.events["id"]
        event.eventName = event.events["eventName"]
        event.startAt = event.events["startAt"]

        ## default endtime to start time if there is none
        if event.events["endAt"]:
            event.endAt = event.events["endAt"]
        else:
            event.endAt = event.startAt
            event.events["endAt"] = event.startAt

        ##TODO - Fix auro's messy ass code -_-
        event.typeOfEvent = event.events["typeOfEvent"]
        event["title"] = event.events["eventName"]
        if event.events.typeOfEvent == 'Academic':
            event["class"] = "event-info"
        if event.events.typeOfEvent == 'Cultural':
            event["class"] = "event-success"
        if event.events.typeOfEvent == 'Sports':
            event["class"] = "event-special"
        if event.events.typeOfEvent == 'Holiday':
            event["class"] = "event-warning"
        if event.events.typeOfEvent == 'Other':
            event["class"] = "event-inverse"
        if event.events.typeOfEvent == 'Urgent':
            event["class"] = "event-important"
        event["url"] = URL('showDes.html', args=[event.events.id])
        event["start"] = (event.events["startAt"] - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
        event["end"] = (event.endAt - datetime.datetime(1970, 1, 1)).total_seconds() * 1000
        # event["url"] = event.eventName

    return dict(success=1, result=events)


def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    http://..../[app]/default/user/manage_users (requires membership in
    http://..../[app]/default/user/bulk_register
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())


@cache.action()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request, db)


def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    return service()
