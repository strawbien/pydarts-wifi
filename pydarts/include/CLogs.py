# To use exit...
import sys

class CLogs:
   def __init__(self):
      self.level=1
      # DEBUG for debug mode, WARNING for warnings, ERROR for non-fatals errors (non exiting), FATAL for errors leading to exit.
      self.facility=('NONE','DEBUG','WARNING','ERROR','FATAL')
      # First init, we have no config available (Logs is the first boject to be created), so we init with loglevel=1
      #self.UpdateFacility(1)
#
# Return true if an arguement is present
#

   def SetConfig(self,Config):
      self.Config=Config
      level=int(self.Config.GetValue('SectionGlobals','debuglevel'))
      self.UpdateFacility(self.level)

   def Log(self,facility,msg):
      # Get key of the message facility
      key=self.facility.index(facility)
      # If key is superior or equal to config, print
      if key>=self.level:
         print(("[{}] {}").format(facility,msg))


#
# Update facility
#
   def UpdateFacility(self,level):
      level=int(level)
      if self.level != level and level>0 and level<=4:
         msg="Updating debug facility from {} to {} and above.".format(self.facility[self.level],self.facility[level])
         try:
            self.Log("DEBUG",msg)
         except:
            print(msg)
         self.level = level
