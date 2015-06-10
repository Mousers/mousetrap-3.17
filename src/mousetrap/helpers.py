from __future__ import unicode_literals
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


#####################################################################
#                                                                   #
#  STRING -- Base type of strings in Python 2 or 3. Use with        #
#  isinstance to check if a value is a string type. E.g.,           #
#  isinstance(x, STRING)                                            #
#                                                                   #
#####################################################################

def _get_string_type():
    import sys
    PYTHON_3 = sys.version_info[0] == 3
    return (str, ) if PYTHON_3 else (basestring, )

STRING = _get_string_type()

#####################################################################
#                                                                   #
#  _(str) -- _ is shorthand for translations.gettext. Use it to     #
#  get mark that a string should be translated, and return the      #
#  translated string. E.g., _('This will be translated.').          #
#                                                                   #
#####################################################################

def _get_translation_function():
    import gettext
    from os.path import abspath, dirname, join, realpath
    locale_dir = abspath(join(dirname(realpath(__file__)), "locale"))
    translations = gettext.translation("mousetrap", localedir=locale_dir)
    try:
        return translations.ugettext
    except AttributeError:
        return translations.gettext

_ = _get_translation_function()
