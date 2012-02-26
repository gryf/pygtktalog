"All your bases are belong to us."
"
" Author: Roman.Dobosz at gmail.com
" Date: 2011-12-09 12:11:00

if !has("python")
  finish
endif

let g:project_dir = expand("%:p:h")

python << EOF
import os
import vim

PROJECT_DIR = vim.eval('project_dir')
TAGS_FILE = os.path.join(PROJECT_DIR, "tags")

if not PROJECT_DIR.endswith("/"):
    PROJECT_DIR += "/"
PYFILES= []

if os.path.exists(PROJECT_DIR + "tmp"):
    os.system('rm -fr ' + PROJECT_DIR + "tmp")

## icard specific
#for dir_ in os.listdir(os.path.join(PROJECT_DIR, "..", "externals")):
#    if dir_ != 'mako':
#        PYFILES.append(dir_)

vim.command("set tags+=" + TAGS_FILE)

# make all directories accessible by gf command
def req(path):
    root, dirs, files = os.walk(path).next()
    for dir_ in dirs:
        newroot = os.path.join(root, dir_)
        # all but the dot dirs
        if dir_ in (".svn", ".hg", "locale", "tmp"):
            continue
        if "static" in root and dir_ != "js":
            continue

        vim.command("set path+=" + newroot)
        req(newroot)

req(PROJECT_DIR)

# generate tags
def update_tags(path):
    assert os.path.exists(path)

    pylib_path = os.path.normpath(path)
    pylib_path += " " + os.path.normpath('/usr/lib/python2.7/site-packages')

    # find tags for all files
    cmd = 'ctags -R --python-kinds=-i'
    cmd += ' -f ' + TAGS_FILE + ' ' + pylib_path
    print cmd
    os.system(cmd)
EOF

"
command UpdateTags python update_tags(PROJECT_DIR)
