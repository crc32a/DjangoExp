from app.main.models import *
from app.main.tools import *
from app.main.const import *
from app.main.util import *
from django.http import Http404

linkTableAttrs = {"class":"linkTable","align":"center"}

def reader(self,rc):
    req_path = splitUrlPath(rc)
    if len(req_path) == 3: #Show books
        rc.ctx["books"] = getbookshtml(rc)
        return self.render(rc)
    if len(req_path) == 4: #Show chapters
        try:
            book_num = int(req_path[3])
        except (TypeError, ValueError):
            msg = "%s is not a valid book number"%req_path[3]
            rc.ctx["operror"] = rc.logger.log(msg)
        try:
            q = Q(num=book_num)&Q(bible__name=default_bible)
            book = BibleBook.objects.get(q)
        except BibleBook.DoesNotExist:
            rc.ctx["operror"] = rc.logger.log("Book %i not found",book_num)
            raise Http404
        q = Q(book=book)
        ch = "chapter"
        qs = BibleVerse.objects.filter(q).values(ch).distinct().order_by(ch)
        rc.ctx["chapters"] = getchaptershtml(rc,book,qs)
        return self.render(rc)
    if len(req_path) == 5:
        try:
            book_num = int(req_path[3])
        except (TypeError,ValueError):
            msg = "%s is not a valid book number"%req_path[3]
            rc.ctx["operror"] = rc.logger.log(msg)
            return self.render(rc)
        try:
            chapter_num = int(req_path[4])
        except (TypeError,ValueError):
            msg = "%s is not a valid chapter"%req_path[4]
            rc.ctx["operror"] = rc.logger.log(msg)
            return self.render(rc)
        rc.ctx["verses"] = getChapterHtml(rc,book_num,chapter_num)
        return self.render(rc)
    return self.render(rc)

def bightml(text,bigness):
    fmt = ""
    for i in xrange(0,bigness):
        fmt += "<big>"
    fmt += "%s"
    for i in xrange(0,bigness):
        fmt += "</big>"
    return fmt%text

def getChapterHtml(rc,book_num,chapter_num):
    out = ""
    try:
        q = Q()
        q &= Q(bible__name=default_bible)
        q &= Q(num=book_num)
        book = BibleBook.objects.get(q)
    except BibleBook.DoesNotExist:
        rc.logger.log("Book %i not found",book_num)
        raise Http404
    out += "<p align=\"center\">%s</p>\n"%bightml("Book of %s"%book.name,5)
    out += "<p align=\"center\">%s</p>\n"%bightml("Chapter %i"%chapter_num,3)
    q = Q(verse__book=book)&Q(verse__chapter=chapter_num)
    frags = [f for f in BibleFrag.objects.select_related(depth=1).filter(q)]
    verseMap = {}
    spancolorfmt = """<span style="color: %s">%s</span>"""
    for f in frags:
        (v,ft,fv) = (f.verse.verse,f.ftype,f.fval)
        if not verseMap.has_key(v):
            verseMap[v] = "<big>%i.</big>%s"%(v,nbs)
        if ft == "wj":
            verseMap[v] += spancolorfmt%("#800000",fv) + nbs
        elif ft == "f":
            verseMap[v] += spancolorfmt%("#008000",fv) + nbs
        elif ft == "add":
            verseMap[v] += spancolorfmt%("#000080",fv) + nbs
        else:
            verseMap[v] += fv + nbs

    if len(frags) > 0:
        pfrag = prev_frag(frags[0])
        if pfrag != None:
            pbook = pfrag.verse.book.num
            pchap = pfrag.verse.chapter
            rc.ctx["prev_link"] = "/bible/reader/%i/%i"%(pbook,pchap)

        nfrag = next_frag(frags[-1])
        if nfrag != None:
            nbook = nfrag.verse.book.num
            nchap = nfrag.verse.chapter
            rc.ctx["next_link"] = "/bible/reader/%i/%i"%(nbook,nchap)

    keys = verseMap.keys()
    keys.sort()
    if len(keys) <= 0:
        raise Http404
        return out
    for v in keys:
        out += "<p>%s</p>\n"%verseMap[v]
    
    return out


def prev_frag(frag):
    try:
       q = Q(id__lt=frag.id)
       qs = BibleFrag.objects.filter(q).order_by('-id')[0]
    except IndexError:
       return None
    return qs

def next_frag(frag):
    try:
        q = Q(id__gt=frag.id)
        qs = BibleFrag.objects.filter(q).order_by('id')[0]
    except IndexError:
        return None
    return qs

def getchaptershtml(rc,book,qs):
    kw = {}
    kw["table_attrs"] = linkTableAttrs
    kw["ncols"]=5
    kw["caption"] = "The Book of %s"%book.name
    links = []
    chapters = sorted([r["chapter"] for r in qs])
    for chapter in chapters:
        href = "/bible/reader/%i/%i"%(book.num,chapter)
        name = "Chapter %i"%chapter
        links.append( (href,name) )
    return tableLinks(rc,links,**kw)

    
        

def getbookshtml(rc):
    kw = {}
    kw["table_attrs"] = linkTableAttrs
    kw["ncols"] = 5
    kw["caption"] = "Books of the Bible"
    q = Q(bible__name=default_bible)
    books = BibleBook.objects.filter(q).order_by('num')
    links = []
    for book in books:
        href = "/bible/reader/%i"%book.num
        name = book.name
        links.append( (href,name) )
    return tableLinks(rc,links,**kw)


def tableLinks(rc,linksIn,**kw):
    links = linksIn[:]
    ncols = kw.get("ncols",4)
    out = ""
    out += "<table"
    if kw.has_key("table_attrs"):
        out += " "
        kv_pairs = ["%s=\"%s\""%(k,v) for (k,v) in kw["table_attrs"].items()]
        out += string.join(kv_pairs," ")
    out += ">\n"
    if kw.has_key("caption"):
        out += "<caption>%s</caption>\n"%kw["caption"]

    nc = ncols
    nr = (len(linksIn)-1)/nc + 1
    rci = RowColIndex(nr)
    for r in xrange(0,nr):
        out += "<tr>\n"
        for c in xrange(0,nc):
            li = rci.rc2abs(r,c,inv=True)
            try:
                (href,name) = links[li]
                out += "<td><a href=\"%s\">%s</a></td>\n"%(href,name)
            except IndexError:
                out += "<td></td>\n"
        out += "</tr>\n"
    out += "</table>\n"
    return out


