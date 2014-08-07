#!/usr/bin/env plotter.py

rootfile good_run
   location="Playback_V0001_HLT_R000180250.root"
   desc="Run 180250 (good)"
   linecolor=1

rootfile bad_run
   location="Playback_V0001_HLT_R000176464.root"
   desc="Run 176464 (bad)"
   linecolor=2

histo HLT_SingleMu_1dEta__bad
   location = "DQMData/Run 176464/HLT/Run summary/OccupancyPlots/HLT_SingleMu_1dEta"
   linewidth = 2
   normalize = true

histo HLT_SingleMu_1dEta__good
   location = "DQMData/Run 180250/HLT/Run summary/OccupancyPlots/HLT_SingleMu_1dEta"
   linewidth = 2
   normalize=true

plot HLT_SingleMu_1dEta__bad
   logy=false
   push=bad_run.HLT_SingleMu_1dEta__bad
   title="HLT_SingleMu_1dEta__bad"
   filename="HLT_SingleMu_1dEta__bad.gif"

plot HLT_SingleMu_1dEta__good
   logy=false
   push=good_run.HLT_SingleMu_1dEta__good
   title="HLT_SingleMu_1dEta__good"
   filename="HLT_SingleMu_1dEta__good.gif"

plot HLT_SingleMu_1dEta__comp
   #logy=false
   legpos=4
   push=good_run.HLT_SingleMu_1dEta__good
   push=bad_run.HLT_SingleMu_1dEta__bad
   title="HLT_SingleMu_1dEta comparison"
   filename="HLT_SingleMu_1dEta__comp.gif"


#print HLT_SingleMu_1dEta__bad
#print HLT_SingleMu_1dEta__good
exit
print HLT_SingleMu_1dEta__comp
