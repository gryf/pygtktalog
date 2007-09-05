#  Author: Roberto Cavada <cavada@irst.itc.it>
#
#  Copyright (c) 2006 by Roberto Cavada
#
#  pygtkmvc is free software; you can redistribute it and/or
#  modify it under the terms of the GNU Lesser General Public
#  License as published by the Free Software Foundation; either
#  version 2 of the License, or (at your option) any later version.
#
#  pygtkmvc is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#  Lesser General Public License for more details.
#
#  You should have received a copy of the GNU Lesser General Public
#  License along with this library; if not, write to the Free Software
#  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307  USA.
#
#  For more information on pygtkmvc see <http://pygtkmvc.sourceforge.net>
#  or email to the author <cavada@irst.itc.it>.
#  Please report bugs to <cavada@irst.itc.it>.



# ======================================================================
# This module is used only as a utility to import gtkmvc when not
# installed.

import utils.globals

if __name__ != "__main__":
    try: import gtkmvc
    except:
        import os.path; import sys

        rel_path = os.path.join(utils.globals.TOP_DIR, "..")
        top_dir = os.path.dirname(os.path.abspath(rel_path))
        sys.path = [top_dir] + sys.path
        import gtkmvc
        pass

    gtkmvc.require("1.0.0")
pass

