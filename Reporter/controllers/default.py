# -*- coding: utf-8 -*-
def getsev(issue):
    return int(issue.impact)*int(issue.vuln_assert)*int(issue.exposure)*int(issue.combo_factor)

@auth.requires_login()
def updatesevs(issues):
    for issue in issues:
        issue.update_record(sev=getsev(issue))

@auth.requires_login()
def index():
    audits = db().select(db.audits.ALL)
    auditrows = []
    for audit in audits:
        auditrows.append([audit.id, audit.title, db(db.issues.audit == audit).count(), audit.profile ,audit.when_at, audit.who])
    return dict(audits=auditrows, auds=audits)

@auth.requires_login()
def listissues():
    orderby = request.vars.orderby
        
    if orderby:
        issues = db(db.issues.audit == request.args(0)).select(orderby=request.vars['orderby'])
        return dict(issues=issues, audit=request.args(0))
    else:
        issues = db(db.issues.audit == request.args(0)).select(orderby=~db.issues.sev)
        return dict(issues=issues, audit=request.args(0))

@auth.requires_login()
def editcategories():
    categories = db().select(db.categories.ALL)
    return dict(categories=categories)

@auth.requires_login()
def addissue():
    form = SQLFORM(db.issues,_name="prob")
    if form.accepts(request.vars, formname='prob'):
 #       form.vars.id = db.issues.insert(**dict(form.vars))
        response.flash = 'form accepted'
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'
    return dict(form=form, audit=request.args(0))

@auth.requires_login()
def sevclass(issue, profile):
    maximum = profile.maximum_severity
    sev=getsev(issue)
    impact,vulnerability, exposure, combo = int(issue.impact), int(issue.vuln_assert), int(issue.exposure), int(issue.combo_factor)
    if(sev > profile.urgent):
        return "%s (%d:%d:%d:%d)" % (profile.urgent_label,impact,vulnerability, exposure, combo)
    elif (sev > profile.critical):
        return "%s (%d:%d:%d:%d)" % (profile.critical_label,impact,vulnerability, exposure, combo)
    elif (sev > profile.serious):
        return "%s (%d:%d:%d:%d)" % (profile.serious_label,impact,vulnerability, exposure, combo)
    elif (sev > profile.medium):
        return "%s (%d:%d:%d:%d)" % (profile.medium_label,impact,vulnerability, exposure, combo)
    elif (sev > profile.low):
        return "%s (%d:%d:%d:%d)" % (profile.low_label,impact,vulnerability, exposure, combo)
    else:
        return "trouble.. %d (%d:%d:%d:%d)" % (sev,impact,vulnerability, exposure, combo)

@auth.requires_login()
def gentoc(issues, profile):
    toc = "#,Gravidade,Objecto,Problema\n"
    for issue in issues:
        toc += "%d,%s,%s,%s\n" % (issue.id, sevclass(issue,profile), issue.object, issue.title)
    return toc

@auth.requires_login()
def genreportissue(issue,profile):
    return "%s\nProblema: %d\nGravidade: %s\nVulnerabilidade: %s\nObjecto: %s\nDetalhes: %s\nCorrec&ccedil;&atilde;̃o: %s\n\n" % (issue.title, issue.id, sevclass(issue,profile), issue.vulnerability, issue.object, issue.details, issue.correction )

@auth.requires_login()
def editaudits():
    rows = []
    orderby = request.vars.orderby
    if orderby:
        rows = db().select(db.audits.ALL,orderby=orderby)
    else:
        rows = db().select(db.audits.ALL)
    return dict(rows=rows,query=request.vars.query)

@auth.requires_login()
def editsettings():
    rows = []
    orderby = request.vars.orderby
    if orderby:
        rows = db().select(db.settings.ALL,orderby=orderby)
    else:
        rows = db().select(db.settings.ALL)
    return dict(rows=rows,query=request.vars.query)

@auth.requires_login()
def genreport():
    response.view="default/report.html"
    audit = db(db.audits.id == request.args(0)).select(db.audits.ALL)[0]
    issues = db(db.issues.audit == request.args(0)).select()    
    profile = db(db.settings.id == audit.profile).select(db.settings.ALL)[0]
    updatesevs(issues)
    issues = db(db.issues.audit == request.args(0)).select(orderby=~db.issues.sev)            
    report = gentoc(issues, profile) + "\n\n"
    for issue in issues:
        report += genreportissue(issue,profile)
    return dict(report=report)

def user():
    """
    exposes:
    http://..../[app]/default/user/login
    http://..../[app]/default/user/logout
    http://..../[app]/default/user/register
    http://..../[app]/default/user/profile
    http://..../[app]/default/user/retrieve_password
    http://..../[app]/default/user/change_password
    use @auth.requires_login()
        @auth.requires_membership('group name')
        @auth.requires_permission('read','table name',record_id)
    to decorate functions that need access control
    """
    return dict(form=auth())

@auth.requires_login()
def download():
    """
    allows downloading of uploaded files
    http://..../[app]/default/download/[filename]
    """
    return response.download(request,db)

@auth.requires_login()
def ajaxlivesearch():
    partialstr = request.vars.values()[0]
    query = db.issues.title.like('%'+partialstr+'%')
    probs = db(query).select(db.issues.title,distinct=True)
    items = []
    for (i,prob) in enumerate(probs):
        items.append(DIV(A(prob.title, _id="res%s"%i, _href="#", _onclick="populateIssue($('#res%s').html())"%i), _id="resultLiveSearch"))

    return TAG[''](*items)

@auth.requires_login()
def ajaxgetissue():
    import gluon.contrib.simplejson as sj
    name = request.vars.values()[0]
    issue = db(db.issues.title.like(name)).select()
    return sj.dumps(issue.as_list()[0])

def call():
    """
    exposes services. for example:
    http://..../[app]/default/call/jsonrpc
    decorate with @services.jsonrpc the functions to expose
    supports xml, json, xmlrpc, jsonrpc, amfrpc, rss, csv
    """
    session.forget()
    return service()

def data(): return dict(form=crud())