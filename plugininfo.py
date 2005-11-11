"""
This plugin goes through and pulls the __doc__ and other documentation
from plugins currently installed on your system.  At some point it may
also go through and pull configuration information.

And some day it might do my laundry.

To kick it off, the url starts with /plugin_info .

If there are plugins you want to run that you don't want showing up,
list them in the "plugininfo_hide" property of your config.py file:

   py["plugininfo_hide"] = ["myplugin", "myotherplugin"]

It takes a list of strings.


Permission is hereby granted, free of charge, to any person
obtaining a copy of this software and associated documentation
files (the "Software"), to deal in the Software without restriction,
including without limitation the rights to use, copy, modify,
merge, publish, distribute, sublicense, and/or sell copies of the
Software, and to permit persons to whom the Software is furnished
to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN
ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN
CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Copyright 2002-2004 Will Guaraldi

CVS VERSION: $Id: plugininfo.py,v 1.8 2005/10/26 18:40:43 willg Exp $

Revisions:
1.8 - (26 October, 2005) pulled into new version control system
1.7 - (09 December, 2004) fixed date_head issue and stopped showing 
      docstrings
1.6 - (04 May 2004) added comment handling
1.5 - (18 February 2004) added the ability to "hide" plugins so that
      we don't talk about them
1.4 - (17 February 2004) added alphabetical sorting of plugins and fixed
      num_entries issue
1.3 - (14 July 2003) added $plugincount variable
1.2 - (5/27/2003) minor fixes in the build_entry
"""
import Pyblosxom.plugin_utils
import Pyblosxom.entries.base
import time, os.path

__author__ = "Will Guaraldi - willg at bluesock dot org"
__version__ = "$Revision: 1.8 $ $Date: 2005/10/26 18:40:43 $"
__url__ = "http://www.bluesock.org/~willg/pyblosxom/"
__description__ = "Shows information about plugins that you're running."

TRIGGER = "/plugin_info"

def verify_installation(request):
    config = request.getConfiguration()
    if not config.has_key("plugininfo_hide"):
        print "Note: You can set 'plugininfo_hide' to hide plugins you don't want showing up."
    else:
        if not type(config["plugininfo_hide"]) == type([]):
            print "'plugininfo_hide' must be a list of strings."
            return 0
        for mem in config["plugininfo_hide"]:
            if not type(mem) == type(""):
                print "'plugininfo_hide' must be a list of strings."
                return 0
    return 1

def build_entry(request, mem):
    docstring = getattr(mem, "__doc__")
    if not docstring:
        docstring = "No documentation for this plugin."

    docstring = docstring.replace("<", "&lt;")
    docstring = docstring.replace(">", "&gt;")

    plugindata = []
    plugindata.append("<pre>")
    if hasattr(mem, "__author__"):
        plugindata.append("AUTHOR: " + str(mem.__author__) + "\n")
    if hasattr(mem, "__version__"):
        plugindata.append("VERSION: " + str(mem.__version__) + "\n")
    if hasattr(mem, "__url__"):
        plugindata.append("URL: <a href=\"%s\">%s</a>\n" % (str(mem.__url__), str(mem.__url__)))

    # plugindata.append(docstring)
    plugindata.append("</pre>")

    entry = Pyblosxom.entries.base.generate_entry(request, 
                    { "title": mem.__name__,
                      "absolute_path": TRIGGER[1:],
                      "fn": mem.__name__,
                      "file_path": TRIGGER[1:] + "/" + mem.__name__ },
                    "".join(plugindata), None)
    return entry

def cb_prepare(args):
    request = args["request"]
    data = request.getData()
    config = request.getConfiguration()
    antiplugins = config.get("plugininfo_hide", [])

    plugins = Pyblosxom.plugin_utils.plugins
    plugins = [m for m in plugins if m.__name__ not in antiplugins]

    data["plugincount"] = len(plugins)

INIT_KEY = "plugininfo_initiated"

def cb_date_head(args):
    request = args["request"]
    data = request.getData()

    if data.has_key(INIT_KEY):
        args["template"] = ""
    return args

def cb_staticrender_filelist(args):
    request = args["request"]
    filelist = args["filelist"]
    flavours = args["flavours"]

    config = request.getConfiguration()

    antiplugins = config.get("plugininfo_hide", [])

    plugins = Pyblosxom.plugin_utils.plugins
    plugins = [m for m in plugins if m.__name__ not in antiplugins]

    if plugins:
        for mem in plugins:
            url = os.path.normpath(TRIGGER + "/" + mem.__name__ + ".")
            for f in flavours:
                filelist.append( (url + f, "") )
        for f in flavours:
            filelist.append( (os.path.normpath(TRIGGER + "/index." + f), "") )

    
def cb_filelist(args):
    request = args["request"]
    pyhttp = request.getHttp()
    data = request.getData()
    config = request.getConfiguration()

    if not pyhttp["PATH_INFO"].startswith(TRIGGER):
        return

    data[INIT_KEY] = 1
    data['root_datadir'] = config['datadir']
    config['num_entries'] = 9999
    entry_list = []

    antiplugins = config.get("plugininfo_hide", [])

    plugins = Pyblosxom.plugin_utils.plugins
    plugins = [m for m in plugins if m.__name__ not in antiplugins]

    pathinfo = pyhttp["PATH_INFO"]

    if pathinfo == TRIGGER or pathinfo.startswith(TRIGGER + "/index"):
        plugins.sort(lambda x,y: cmp(x.__name__, y.__name__))
        for mem in plugins:
            entry_list.append(build_entry(request, mem))
        return entry_list

    pathinfo = pathinfo[len(TRIGGER):]

    if pathinfo.startswith("/"): pathinfo = pathinfo[1:]
    if pathinfo.endswith("/"): pathinfo = pathinfo[:-1]

    filename, ext = os.path.splitext(pathinfo)
    if ext[1:]:
        data["flavour"] = ext[1:]

    d = {}
    for mem in plugins:
        d[mem.__name__] = mem

    if d.has_key(filename):
        return [build_entry(request, d[filename])]

    return []

# vim: tabstop=4 shiftwidth=4
