"""
    The configuration file for the psblog blog engine.

    Copyright (c) 2011 by Richard Wossal <richard@r-wos.org>

    Permission to use, copy, modify, and distribute this software and its
    documentation for any purpose and without fee is hereby granted, provided
    that the above copyright notice appear in all copies and that both that
    copyright notice and this permission notice appear in supporting
    documentation. This software is provided "as is" without express or
    implied warranty.
"""

# the blog's title
title = "Richard's Blog"

# the blog's subtitle
subtitle = "a programmer's view of the world"

# the URL of the out directory (please include the trailing slash)
blog_url = "http://blog.r-wos.org/"

# the URL of the comment.py cgi script
comment_url = "http://r-wos.org/blog/src/comment.py"

# the URL of the admin.py cgi script
admin_url = "http://r-wos.org/blog/src/admin.py"

# the blog's author, will be displayed below each post
author = "Richard Wossal"

# the blog author's email address
# Notifications and logs will be sent to this address.
author_email = "richard@r-wos.org"

# the output directory (please include the trailing slash)
# Point your server here, this is the home of your blog.
out_dir = "../out/"

# the data directory (please include the trailing slash)
# Nothing in this directory should be served by your webserver.
data_dir = "../data/"

# the log directory (please include the trailing slash)
# Nothing in this directory should be served by your webserver.
log_dir = "../log/"

# maximum size of the psblog.log file in multiples of 1024 bytes
# When this size is reached, the log file is emailed to author_email.
# TODO: emailing isn't implemented yet
max_log_size = 32

# strftime(3) date format for the psblog.log file
log_date_format = "%Y-%m-%d %H:%M:%S"

# End of configuration options.

# TODO: "hacky as hell" would be an understatement here
__options = dict(
    (name, globals()[name]) for name in dir() if not name.startswith('__'))
def options():
    """ Return all config options as a dict. """
    return __options

