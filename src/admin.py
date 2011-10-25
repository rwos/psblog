#!/usr/bin/python
"""
    The admin module of the psblog blog engine.

    A very simple cgi script that provides basic blog administration.

    Copyright (c) 2011 by Richard Wossal <richard@r-wos.org>

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted, provided
    that the above copyright notice appear in all copies and that both that
    copyright notice and this permission notice appear in supporting
    documentation. This software is provided "as is" without express or
    implied warranty.
"""
import cgi
import cgitb
import datetime as dt
import os

import config
import html
import psblog

cgitb.enable() # traceback always enabled because this is admin-only area
print("Content-Type: text/html\n\n") # everything here is html

def show_overview():
    """ Show an overview over the blog. """
    posts = psblog.get_all_posts()
    comments_num = 0
    for p in posts:
        comments_num += len(p["comments"])
    o = [html.h(2, "Overview"),
         html.p(html.a("?page=list", str(len(posts))+" Posts")),
         html.p(html.a("#TODO", str(comments_num)+" Comments")),
         html.p(html.a("?page=add_new", "Add New Post")),
         html.p(html.a("?page=compile", "Re-Compile"))]
    o = html.block("".join(o))
    o += html.block(html.p("last compile log:"+html.pre(
            psblog.readfile(config.log_dir+"compile.log"))))
    log_ls = psblog.readfile(config.log_dir+"psblog.log").splitlines()
    log_ls.reverse()
    o += html.block(html.p("blog log:"+html.pre("\n".join(log_ls))))
    print(html.render_admin(o))

def show_list():
    """ Show a list of all posts. """
    posts = psblog.get_all_posts()
    ls_data = []
    for p in posts:
        ls_data.append("".join([
              p["meta"]["datetime"].strftime("%x")," - ",
              html.a("?page=single&id="+psblog.post_id(p["meta"]),
              p["meta"]["heading"]), " - ", 
              str(len(p["comments"])), " comment(s)"]))
    print(html.render_admin(html.block(html.ul(ls_data))))

def show_single(post_id):
    """ Show/edit a single post. """
    p = psblog.get_post(post_id)
    # TODO: proper form handling for html module
    o=""
    o+="<form action=\"?page=save\" method=\"POST\">"
    o+="<input type=\"text\" name=\"heading\" value=\""+p["meta"]["heading"]+"\"><br>"
    o+="<input type=\"text\" name=\"category\" value=\""+p["meta"]["category"]+"\"><br>"
    o+="<input type=\"hidden\" name=\"id\" value=\""+post_id+"\"><br>"
    o+="<input type=\"hidden\" name=\"save\" value=\"save\"><br>"
    o+="<textarea style='width:100%;height:40em;' name=\"text\">"+p["text"].decode("utf8")+"</textarea><br>"
    o+="<input type=\"submit\"><br>" 
    o+="</form>"
    i = 0
    for c in p["comments"]:
        # TODO: make delete link a POSTing form
        o2=html.a("?page=del_comment&id="+post_id+"&cid="+str(i), "delete")
        o2+="<br>"
        for key,item in c.items():
            # XXX HACK
            try:
                o2+=key+" - "+item.decode("utf8")+"<br>"
            except UnicodeEncodeError:
                o2+=key+" - "+item+"<br>"
        o += html.block(o2)
        i += 1
    o+=html.block(p["html"])
    print(html.render_admin(o.encode("utf8")))

def add_new(params):
    """ Add a new post to the blog. """
    if "save" in params:
        add_post(
            params["heading"].value,
            params["category"].value,
            params["text"].value)
    else:
        # TODO: form handling, form handling, form handling!!!
        o=""
        o+="<form action='?page=add_new&save=save' method=\"POST\">"
        o+="Heading: <input type=\"text\" name=\"heading\"><br>"
        o+="Category: <input type=\"text\" name=\"category\"><br>"
        o+="<input type=\"hidden\" name=\"save\" value=\"save\"><br>"
        o+="<textarea style='width:100%;height:40em;' name=\"text\"></textarea><br>"
        o+="<input type=\"submit\"><br>" 
        o+="</form>"
        print(html.render_admin(html.block(o.encode("utf8"))))

def del_comment(post_id, cid):
    """ Delete a comment. """
    p = psblog.get_post(post_id)
    del p["comments"][cid]
    rm_post(post_id)
    add_post(
        p["meta"]["heading"],
        p["meta"]["category"],
        p["text"],
        p["meta"]["datetime"],
        p["comments"])
    psblog.compile_everything()

def save_single(path, params):
    """ Save a single post, replacing the old one. """
    old = psblog.get_post(path)
    old_date = old["meta"]["datetime"]
    old_comments = old["comments"]
    rm_post(path)
    print("old page deleted<br>")
    add_post(
        params["heading"].value,
        params["category"].value,
        params["text"].value,
        old_date,
        old_comments)
    psblog.compile_everything()
    print("new page added<br>")

def rm_post(post_id):
    """ Remove a page (removes only the data files). """
    if psblog.existing_post_id(post_id):
        os.remove(post_id+".txt")
        os.remove(post_id+".meta")
        os.remove(post_id+".comments")

def add_post(heading, category, text, date=dt.datetime.now(), comments=[]):
    """ Add a post to the blog. """
    meta = {
        "heading": heading,
        "url_heading": psblog.urlify(heading),
        "category": category,
        "datetime": date}
    post_id = psblog.post_id(meta)
    psblog.save_text(text, post_id)
    psblog.save_meta(meta, post_id)
    psblog.save_comments(comments, post_id)

params = cgi.FieldStorage()

if "page" not in params.keys():
    show_overview()
else:
    if params["page"].value == "list":
        show_list()
    elif params["page"].value == "compile":
        psblog.compile_everything()
        show_overview()
    elif params["page"].value == "single":
        show_single(params["id"].value)
    elif params["page"].value == "save":
        save_single(params["id"].value, params)
        show_single(params["id"].value)
    elif params["page"].value == "del_comment":
        del_comment(params["id"].value, int(params["cid"].value))
        show_single(params["id"].value)
    elif params["page"].value == "add_new":
        add_new(params)

