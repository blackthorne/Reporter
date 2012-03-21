# -*- coding: utf-8 -*-
# this file is released under public domain and you can use without limitations

response.title = request.application
response.subtitle = T('reporting')

#http://dev.w3.org/html5/markup/meta.name.html
response.meta.author = 'you'
response.meta.description = 'Free and open source full-stack enterprise framework for agile development of fast, scalable, secure and portable database-driven web-based applications. Written and programmable in Python'
response.meta.keywords = 'reports, syndicate, audit, security'
response.meta.generator = 'Web2py Enterprise Framework'
response.meta.copyright = 'Copyright 2007-2010'

if auth.is_logged_in():
    response.menu = [
        (T('Home'), False, URL('default','index'), []),
        (T('Edit'), False, None, [
            (T('Categories'), False, URL('default','editcategories'), []),
            (T('Profiles'), False, URL('default','editsettings'), []),
            (T('Audits'), False, URL('default','editaudits'), []),            
        ]),
        (T('Manage DB'), False, URL(c='appadmin',f='index',args=''))
    ]