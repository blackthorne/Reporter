# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

# My preps
import datetime
now=datetime.datetime.now()

#########################################################################
## This scaffolding model makes your app work on Google App Engine too
#########################################################################

if request.env.web2py_runtime_gae:            # if running on Google App Engine
    db = DAL('google:datastore')              # connect to Google BigTable
                                              # optional DAL('gae://namespace')
    session.connect(request, response, db = db) # and store sessions and tickets there
    ### or use the following lines to store sessions in Memcache
    # from gluon.contrib.memdb import MEMDB
    # from google.appengine.api.memcache import Client
    # session.connect(request, response, db = MEMDB(Client()))
else:                                         # else use a normal relational database
    db = DAL('sqlite://storage.sqlite')       # if not, use SQLite or other DB
## if no need for session
# session.forget()

from gluon.tools import *
mail = Mail()                                  # mailer
auth = Auth(globals(),db)                      # authentication/authorization
crud = Crud(globals(),db)                      # for CRUD helpers using auth
service = Service(globals())                   # for json, xml, jsonrpc, xmlrpc, amfrpc
plugins = PluginManager()

mail.settings.server = 'logging' or 'smtp.gmail.com:587'  # your SMTP server
mail.settings.sender = 'you@gmail.com'         # your email
mail.settings.login = 'username:password'      # your credentials or None

auth.settings.hmac_key = 'sha512:56a2f989-c2e9-44f8-82cc-c04a9d2e8875'   # before define_tables()
auth.define_tables()                           # creates all needed tables
auth.settings.mailer = mail                    # for user email verification
auth.settings.registration_requires_verification = False
auth.settings.registration_requires_approval = False
auth.messages.verify_email = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['verify_email'])+'/%(key)s to verify your email'
auth.settings.reset_password_requires_verification = True
auth.messages.reset_password = 'Click on the link http://'+request.env.http_host+URL('default','user',args=['reset_password'])+'/%(key)s to reset your password'

crud.settings.auth =None #TODO: enforce authorization on crud

#########################################################################
## Define your tables below (or better in another model file) for example
##
## >>> db.define_table('mytable',Field('myfield','string'))
##
## Fields can be 'string','text','password','integer','double','boolean'
##       'date','time','datetime','blob','upload', 'reference TABLENAME'
## There is an implicit 'id integer autoincrement' field
## Consult manual for more options, validators, etc.
##
## More API examples for controllers:
##
## >>> db.mytable.insert(myfield='value')
## >>> rows=db(db.mytable.myfield=='value').select(db.mytable.ALL)
## >>> for row in rows: print row.id, row.myfield
#########################################################################

db.auth_user.format= '%(first_name)s %(last_name)s'

db.define_table('settings',
                SQLField('profile','string',requires=IS_NOT_EMPTY()),
                SQLField('maximum_severity', 'integer', requires=IS_INT_IN_RANGE(0,500)),
                SQLField('urgent','integer',requires=IS_INT_IN_RANGE(0,500)),
                SQLField('critical','integer', requires=IS_INT_IN_RANGE(0,500)),
                SQLField('serious','integer', requires=IS_INT_IN_RANGE(0,500)),
                SQLField('medium','integer', requires=IS_INT_IN_RANGE(0,500)),
                SQLField('low','integer', requires=IS_INT_IN_RANGE(0,500)),
                SQLField('urgent_label','string',requires=IS_NOT_EMPTY()),
                SQLField('critical_label','string', requires=IS_NOT_EMPTY()),
                SQLField('serious_label','string', requires=IS_NOT_EMPTY()),
                SQLField('medium_label','string', requires=IS_NOT_EMPTY()),
                SQLField('low_label','string', requires=IS_NOT_EMPTY()),
                format=lambda r: r.profile
                
                )
                
db.define_table('audits',
    SQLField('title','string', requires=IS_NOT_IN_DB(db,'audits.title')),
    SQLField('who','reference auth_user', default=auth.user_id),
    SQLField('fingerprint','text'), #,writable=False, readable=False
    SQLField('profile','reference settings', default=1),
    SQLField('when_at','datetime',default=now),
    format=lambda r: r.title)

db.define_table('categories',
    SQLField('name','string', requires=IS_NOT_IN_DB(db,'categories.name')),
    format=lambda r: r.name)
db.categories.id.represent = lambda value:A(T('remove'),_href=URL(r=request, c='default',f='data/delete/categories', args=str(value)))
crud.settings.delete_next = URL(r=request, c='default',f='listissues')

db.define_table('issues',
    SQLField('title','string'),
    SQLField('category','reference categories'),
    SQLField('object','string'),
    SQLField('vulnerability','string'),
    SQLField('sev','integer', writable=False, default=0),
    SQLField('impact', requires=IS_INT_IN_RANGE(1,6)),
    SQLField('vuln_assert', requires=IS_INT_IN_RANGE(1,6)), 
    SQLField('exposure', requires=IS_INT_IN_RANGE(1,6)),
    SQLField('combo_factor', requires=IS_INT_IN_RANGE(1,4)),
    SQLField('details','text'),
    SQLField('links','text'),
    SQLField('correction','text'),
    SQLField('file','upload'),
    SQLField('found_by','reference auth_user',default=auth.user_id),
    SQLField('when_at','datetime', default=now),
    SQLField('audit','reference audits'))

db.issues.id.represent = lambda value: UL( 
        LI(A(T('edit'),_href=URL(r=request, c='default',f='data/update/issues', args=str(value)))), 
        LI(A(T('remove'),_href=URL(r=request, c='default',f='data/delete/issues', args=str(value))))) 