#!/usr/bin/python
"""
    The comment module of the psblog blog engine.

    A very simple cgi script that enables users to comment on posts.

    Copyright (c) 2011 by Richard Wossal <richard@r-wos.org>

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted, provided
    that the above copyright notice appear in all copies and that both that
    copyright notice and this permission notice appear in supporting
    documentation. This software is provided "as is" without express or
    implied warranty.
"""
import cgi   

import psblog

def add_comment(name, mail, url, text, post_id):
    """ Add a comment to a specific post. """
    if not psblog.existing_post_id(post_id):
        return # no post to comment on
    new_comment = {
        "mail": mail,
        "name": cgi.escape(name),
        "url": cgi.escape(url, True),
        "text": cgi.escape(text)
    }
    current = psblog.get_comments(post_id)
    current.append(new_comment)
    psblog.save_comments(current, post_id)

my_form = cgi.FieldStorage()
if "text" not in my_form or len(my_form["text"].value) < 1:
    print("Content-Type: text/html\n\n")
    print("nothing to see here")
else:
    try:
        # TODO: proper form handling
        name = cgi.escape(my_form["name"].value)
        if "mail" in my_form:
            mail = cgi.escape(my_form["mail"].value)
        else:
            mail = ""
        if "url" in my_form:
            url = cgi.escape(my_form["url"].value)
        else:
            url = ""
        text = cgi.escape(my_form["text"].value)
        if "href" in text:
            psblog.log_err("rejecting comment: "
               +str([name, mail, url, text]))
            print("Content-Type: text/html\n\n")
            print("no html hyperlinks, please use markdown syntax")
        else:
            post_id = cgi.escape(my_form["post_id"].value)
            add_comment(name, mail, url, text, post_id)
            psblog.compile_everything()
            print("Location: "+my_form["post_url"].value+"\n\n")
    except KeyError:
        print("Content-Type: text/html\n\n")
        print("Sorry, but that didn't work...")

