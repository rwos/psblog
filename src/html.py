"""
    HTML generation for the psblog blog engine.

    Provides utility routines for generating html content.
    This is custom-built for psblog, not a universal html generation module.

    Copyright (c) 2011 by Richard Wossal <richard@r-wos.org>

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted, provided
    that the above copyright notice appear in all copies and that both that
    copyright notice and this permission notice appear in supporting
    documentation. This software is provided "as is" without express or
    implied warranty.
"""
from cgi import escape
from re import sub

import config
import psblog

def date(dt_obj):
    """ Return a date line from a datetime object. """
    return dt_obj.strftime("%a, %F")

def author():
    """ Return the post author line. """
    return small(config.author)

def post_link(post):
    """ Return a link to the given post. """
    # TODO: make absolute
    urlpath = str(post["meta"]["datetime"].year)+"/"+post["meta"]["url_heading"]
    return a(urlpath, escape(post["meta"]["heading"]))

def block(html, class_=""):
    """ Return a block. """
    return "<div class='block "+class_+"'>"+html+"</div>"

def comment_meta(comment):
    """ Return the meta info line for a comment. """
    if len(comment["url"]) > 5:
        return small(a(comment["url"], comment["name"]))
    else:
        return small(comment["name"])

def comment_form(page_id, page_url):
    """ Return the comment form for the given page id. """
    # TODO: proper form handling
    return "".join([
        "<form action='", config.comment_url, "' method='POST'>",
        h(3, "$ cat >> comments.txt"),
        in_("hidden", "post_id", page_id),
        in_("hidden", "post_url", page_url),
        # TODO: mv inline style to style.css
            "<table style='border:none;width:100%;'>",
        "<tr><td>name</td><td>",
        in_("text", "name"), "</td></tr>",
        "<tr><td>website (optional)</td><td>",
        in_("text", "url"), "</td></tr>",
        "<tr><td colspan='2'><textarea name='text'></textarea></td></tr>",
        "<tr><td><input type='submit' value='submit'></td></tr></table>",
        "</form>"])

def hex_dump(s):
    """ Return a hex dump (like hd(1)) of the given data. """
    off = 0
    o = ""
    for i in range(5):
        o += "%08x " % off
        os = ""
        for j in range(16):
            if j == 8:
                o += " "
            if off+j < len(s):
                o += " %02x" % ord(s[off+j])
                os += sub('[^a-zA-Z0-9 ]', '.', s[off+j])
            else:
                o += " 00"
                os += "."
        o += "  |"+os+"|\n"
        off += 16
    return "<pre class='hd'>"+o.strip()+"</pre>"

def minify_css(src):
    """ Minify CSS. """
    src = sub(r"\s+", " ", src)
    src = sub(r"\s*([{};:,])\s*", r"\1", src)
    return src

def minify_html(src):
    """ Minify HTML. """
    # TODO
    return src

# generic stuff follows

def a(url, txt):
    """ Return an HTML link. """
    return "<a href=\""+escape(url, True)+"\">"+txt+"</a>"

def h(n, html):
    """ Return an HTML heading. """
    return tag("h"+str(n), html)

def in_(type_, name, value=""):
    """ Return an HTML input tag. """
    return "<input type='"+type_+"' name='"+name+"' value='"+value+"'>"

def p(html):
    """ Return an HTML paragraph. """
    return tag("p", html)

def pre(html):
    """ Return an HTML pre-formatted block. """
    return tag("pre", html)

def small(html):
    """ Not big. """
    return tag("small", html)

def ul(ls):
    """ Make an HTML list from a Python list. """
    o = ""
    for el in ls:
        o += tag("li", el)
    return tag("ul", o)

def tag(name, html):
    """ Encapsulate the given HTML into an HTML tag. """
    return "<"+name+">"+html+"</"+name+">"

def render_front(content, page_title=None):
    """ Render the given content into the frontend template. """
    return render(minify_html(content), "front_template.html", page_title)

def render_admin(content, page_title=None):
    """ Render the given content into the admin template. """
    return render(content, "admin_template.html", page_title)

templates = {} # pre-rendered templates
def render(content, name, page_title=None):
    """ Render the given content into the template and return the result. """
    global templates
    if name not in templates:
        templates[name] = pre_render_template(name)
    if page_title is None:
        temp = templates[name].replace("%%%PAGETITLE%%%", "")
    else:
        temp = templates[name].replace("%%%PAGETITLE%%%", " | "+page_title)
    return temp.replace("%%%CONTENT%%%", content)

def pre_render_template(name):
    """ Replace config strings in the template and return the result. """
    template = psblog.readfile(name)
    for opt, val in config.options().items():
        if type(val) is not str:
            val = str(val)
        template = template.replace("%%%"+opt+"%%%", val)
    return template

