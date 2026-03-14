#!/usr/bin/env python
#-*- coding: utf-8 -*-

# To use exit...
import sys
import locale
import gettext

class GTLocale:
   def __init__(self,Logs,Config):
      self.Config=Config
      self.Logs=Logs
      paramloc = False
      toloadloc = False
      aliasedloc=False
      self.localefallback='en_GB.UTF-8'
      localias={}
      localias['fr_FR']=['fr_FR','fr_BE','fr_CA','fr_CH','fr_LU','fr_MC']
      localias['en_GB']=['en_GB','en_029','en_AU','en_BZ','en_CA','en_GB','en_IE','en_IN','en_JM','en_MY','en_NZ','en_PH','en_SG','en_TT','en_US','en_ZA','en_ZW']
      localias['es_ES']=['es_ES','es_AR','es_BO','es_CL','es_CO','es_CR','es_DO','es_EC','es_GT','es_HN','es_MX','es_NI','es_PA','es_PE','es_PR','es_PY','es_SV','es_US','es_UY','es_VE']
      localias['de_DE']=['de_DE','de_CH']
      if (Config.GetValue('SectionGlobals','locale')):
         paramloc = Config.GetValue('SectionGlobals','locale')
         self.Logs.Log("DEBUG","You requested to load following locale {}".format(paramloc))
      else:
         paramloc = locale.getdefaultlocale() # get current user locale
         paramloc = paramloc[0]#Get only first part (remove char encoding)
         self.Logs.Log("DEBUG","Your detected locale name is \"{}\".".format(paramloc))
      for alloc in localias:#Search which main locale it belongs
         if paramloc and paramloc in localias[alloc]:# And load it
            toloadloc = "{}.UTF-8".format(alloc)
            self.Logs.Log("DEBUG","Your locale is mapped on locale : \"{}\".".format(toloadloc))
      # If at this stage toloadloc is not defined, use fallback (english)
      if not toloadloc:
         toloadloc = self.localefallback
         self.Logs.Log("WARNING","Unable to map your locale. Using fallback locale : \"{}\".".format(toloadloc))
      kwargs = {}
      if sys.version_info[0] < 3:
         # In Python 2, ensure that the _() that gets installed into built-ins
         # always returns unicodes.  This matches the default behavior under
         # Python 3, although that keyword argument is not present in the
         # Python 3 API.
         kwargs['unicode'] = True
      self.tr = gettext.translation('pydarts', 'locales', [toloadloc])
      self.tr.install( **kwargs)

   #
   # Return requested string
   #
   def lang(self,string):
      s=_(string)
      return s
