from . import CScores

class CScoresPatches(CScores.CScores):
   def __init__(self,Logs):
      self.Logs=Logs
      CScores.CScores.__init__(self,None,self.Logs)

   def Patch_08_01_Score_format(self):
      """ Apply patch that correct the score format from one possibility to 3 per score - Apr 14. """
      self.ScoreFile.read(self.pathfile)
      SectionsList = self.ScoreFile.sections()
      PatchApplied = False
      for Section in SectionsList:
         Rewrite = False
         OptionsList = self.ScoreFile.options(Section)
         for Option in OptionsList:
            if Option.count("_1")==0 and Option.count("_2")==0 and Option.count("_3")==0:
               Rewrite = True
               PatchApplied = True
         if Rewrite:
            # Read actual options
            ActualOptions=self.ReadGameScores(Section)
            # Remove old section
            self.ScoreFile.remove_section(Section)
            with open(self.pathfile, 'w') as configfile:
               self.ScoreFile.write(configfile)
            # Create Section
            self.CheckSection(Section)
            # Append old options
            file = open(self.pathfile, 'a')
            for ActualScore,ActualValue in list(ActualOptions.items()):
               # Patch heart - Append the score podium value 1 if 1,2 or 3 is not found in the option name
               # if its a score line
               if Option.count("_1")==0 and Option.count("_2")==0 and Option.count("_3")==0 and Option.count("_who")==0:
                  ActualScore= ActualScore + "_1"
               # if it is a "who" line - split and happend
               elif Option.count("_1")==0 and Option.count("_2")==0 and Option.count("_3")==0 and Option.count("_who")>=1:
                  A_ActualScore = ActualScore.split('_')
                  A_ActualScore.insert(1,'1')
                  ActualScore = "_".join(A_ActualScore)

               file.write("{} = {}\n".format(ActualScore,ActualValue))

            file.close()

      if PatchApplied:
         self.Logs.Log("WARNING","The patch named \"PATCH_08_01_Score_format\" has been applied to your pydarts score.txt file. Please refer to the Changelog to know more.")
