#!/usr/bin/env python

import sys, os

def isProperQuote(data):
    data1=data.strip()
    result = (data1[0] == '"' and data1[-1] == '"') or (data1[0] == "'" and data1[-1] == "'")
    return result

def getTrueFalse(data1):
    data=data1.strip()
    result=""
    if data == "True" or data == "true" or data == "1":
        result = True
    elif data == "False" or data == "false" or data == "0":
        result = False
    return result

def exceptionQuit(data):
    print "[plotter.py]",data
    sys.exit()

def CMDPrint(plotname):
    #print canvas, plots[plotname]
    
    # Initialize canvas and stuff
    gROOT.SetBatch(True)
    gROOT.SetStyle("Plain");
    gStyle.SetOptStat(0);
    
    c1 = TCanvas("c1","Histos")#, 640, 480)
    c1.SetBorderMode(0);

    if canvas["logx"] : c1.SetLogx(True)
    if canvas["logy"] : c1.SetLogy(True)
    if canvas["grid"] : c1.SetGrid(True)
    legy2=0.88
    perentry = 0.05
    leg = TLegend(0.60, 0.70, 0.85, legy2);
    leg.SetBorderSize(legend["BorderSize"])
    leg.SetFillColor(legend["FillColor"])
    doPlot=[]
    
    if plotname == "*":
        for p in plots.keys():
            doPlot.append(p)
    else:
        doPlot.append(plotname)
    
    for f in rootfiles.keys():
        fname = rootfiles[f]["location"]
        #print fname
        rf = TFile(fname)
        if not rf.IsOpen():
            exceptionQuit("Problem opening file:"+ fname) # !!! Didn't close the root files!
        rootfiles[f]["rootfile"] = rf
        
    for plot in doPlot:
        if not plot in plots.keys():
            exceptionQuit("The plot to be printed is undefined: "+ plot )
        target = []
        for ho in plots[plot]["pushed"]: # iteration
            #print ho
            tdata = ho.split(".")
            if len(tdata) == 2: # composite
                if tdata[0] == "*":
                    for rfname in rootfiles.keys():
                        target.append([rfname,tdata[1]])
                else: # must be a root file name
                    if rootfiles.has_key(tdata[0]):
                        target.append([tdata[0],tdata[1]])
                    else:
                        exceptionQuit("Undefined root file: "+ tdata[0] +"(Plot: " + plot + ", histogram item: " + ho + ")")
            elif len(tdata) == 1:
                if len(rootfiles.keys()) != 1:
                    exceptionQuit("When multiple root files are defined, you need to identify from which one to get the histogram (Plot: " + plot + ", histogram item: " + ho + ")")
                target.append([rootfiles.keys(0),tdata[1]])
    
        histograms = []
        legnrows = 0
        leg.Clear()
        #print plots[plot]["legpos"]
        if  plots[plot]["legpos"] == '2':
            leg.SetX1(0.60)
            leg.SetX2(0.85)
        elif  plots[plot]["legpos"] == '1':
            leg.SetX1(0.15)
            leg.SetX2(0.40)
        
        
        c1.Clear()
        c1.SetLogy(0)
        c1.SetLogx(0)
        for hfpair in target:
            f = hfpair[0]
            rootfile = rootfiles[f]["rootfile"]
            ho = histos[hfpair[1]]
            hname = ho["location"]
            histo = rootfile.Get(hname)
            #print hname,histo
            if histo == None:
                exceptionQuit("Root file '"+f+"' doesn't contain histogram: "+hname ) # !!! Didn't close the root files!
            histograms.append(histo)
            histo.SetLineColor(int(rootfiles[f]["linecolor"]))
            if ho.has_key("linewidth") : histo.SetLineWidth(int(ho["linewidth"]))
            if ho.has_key("normalize") :
                scale = 1/histo.Integral()
                histo.Scale(scale)
            if ho.has_key("linecolor") : histo.SetLineColor(int(ho["linecolor"])) # Override root file definition
            if plots[plot]["title"] != "" : histo.SetTitle(plots[plot]["title"])
            desc = rootfiles[f]["desc"]
            if ho.has_key("linecolor") : desc = ho["desc"] # Override root file definition
            leg.AddEntry(histo, desc ,"l");
            legnrows += 1
        
        #print histograms
        if plots[plot].has_key("logx") : c1.SetLogx(plots[plot]["logx"])
        if plots[plot].has_key("logy") : c1.SetLogy(plots[plot]["logy"])
        i = 0
        imax = 0
        maxval = 0
        for h in histograms:
            if h.GetMaximum() > maxval:
                maxval = h.GetMaximum()
                imax = i
            i+=1
        opt="hist "
        h=histograms.pop(imax)
        h.Draw(opt)
        #h.SetMinimum(0.1) #!!!!!!
        for h in histograms:
            h.SetMarkerStyle(22)
            h.Draw(opt+"same")
        leg.SetY1(legy2-perentry*legnrows)
        leg.Draw("same")
        plotfname = plots[plot]["filename"]
        if os.path.exists(plotfname) : os.remove(plotfname)
        c1.Print(plotfname)
        print "[plotter.py] Wrote", plotfname
        
    for f in rootfiles.keys(): rootfiles[f]["rootfile"].Close()

def write_template():
    ofname = "compare.plot"
    files = os.listdir(".")
    for i in range(len(files),0,-1):
        fname = files[i-1]
        if fname.split(".")[-1] != "root" : files.pop(i-1)
    if len(files) == 0:
        exceptionQuit("No root files found")
    if os.path.exists(ofname):
        exceptionQuit("A file named '" + ofname +"' already exists, please get it out of the way")
    fc = "#!/usr/bin/env plotter.py\n\n"
    color = 1
    for rf in files:
        fc += "rootfile "+rf.split(".")[0]+"\n"
        fc += '   location="' + rf + '"\n'
        fc += '   desc="' + rf + '"\n'
        fc += '   linecolor='+str(color)+"\n\n"
        color += 1
    fc += """#canvas
#   logy=true

histo MYHISTO
   location="LOCATION/TO/HISTOGRAM"
   
plot P_MYPLOT
   histogram=MYHISTO
   title="MY HISTOGRAM"
   filename="MYHISTO.gif"
   
print *
"""        
    f = file(ofname,"w")
    f.write(fc)
    f.close()
    
##############################################################################
if len(sys.argv) == 1:
    source = sys.stdin
else:
    fname = sys.argv[1]
    if fname == "-t":
        write_template()
        sys.exit()
    try:
       source = file(fname)
    except IOError:
       exceptionQuit("Failed to open file: "+ fname)

    

lines=source.readlines()
source.close()

# Import root
#try:
    
sys.stdout.flush()
    
from ROOT import *
    
gROOT.SetBatch()
#except:
#    exceptionQuit("ROOT environment not set. Quitting")


b_rootfile_quote = ["location", "desc"]
b_histo_quote = ["location","desc"]
b_plot_quote = ["title", "filename"]
b_canvas_bool = ["logx", "logy", "grid"]
b_histo_bool = ["normalize"]
b_plot_bool = ["logx", "logy", "grid"]
b_rootfile_attrib = ["location", "desc", "linecolor"]

b_histo_attrib = b_histo_bool+b_histo_quote+["linewidth", "linecolor"] #, "desc", "normalize"]
b_plot_attrib = b_canvas_bool+b_plot_quote+["push", "legpos"]
b_canvas_attrib = b_canvas_bool

rootfiles={}
histos={}
plots={}
canvas={"logy":False, "logx":False, "grid": False}
legend={"BorderSize":0,"FillColor":0}
indent=[0]
block=[""]
oname=[""]
iLine = 0

for l in lines:
    iLine += 1
    if l.strip() == "" : continue
    if l.strip()[0] == "#" : continue
    l = (l+" ")[:l.find("#")]
    
    thisindent = len(l) - len(l.lstrip())
    if len(block) != len (indent) :
        indent.append(thisindent) # Entering the block
    else:
        if thisindent != indent[-1]:
            if thisindent == indent[-2]: # block terminated
                block.pop()
                indent.pop()
                oname.pop()
            else: #indentation error
                exceptionQuit("Indentation error on line #"+str(iLine))
    
    if len(block) == 1 :
        data0=l.split(" ")
    else:
        data0=l.split("=")
        if len(data0) != 2:
            exceptionQuit("Syntax error on line #"+str(iLine))
    
    if block[-1] == "": # No active block;
        mydata0 = data0[0].strip()
        if len(data0) > 1 : mydata1 = data0[1].strip()
        else: pass #print iLine
        
        if mydata0 == "rootfile":
            block.append("rootfile")
            oname.append(mydata1)
            rootfiles[mydata1] = {}
        elif mydata0 == "canvas":
            block.append("canvas")
        elif mydata0 == "histo":
            block.append("histo")
            oname.append(mydata1)
            histos[mydata1] = {}
        elif mydata0 == "plot":
            block.append("plot")
            oname.append(mydata1)
            plots[mydata1] = {"pushed":[], "title":"", "legpos":"2"}
        elif mydata0 == "print":
            CMDPrint(mydata1)
        elif mydata0 == "exit":
            sys.exit()
        else:
            exceptionQuit("Syntax error on line #"+str(iLine))
            sys.exit()
    else:
        
        myslot = data0[0].strip()
        mydata = data0[1].strip()
        
        if block[-1] == "rootfile":
            if myslot in b_rootfile_quote:
                if not isProperQuote(mydata):
                    exceptionQuit("Please check quotations on line #"+str(iLine))
                mydata=mydata[1:-1] #remove quotes
            if myslot not in b_rootfile_attrib:
                exceptionQuit("Unrecognized attribute on line #"+str(iLine)+ ": "+myslot)
            rootfiles[oname[-1]][myslot] = mydata
            
        elif block[-1] == "canvas":
            if myslot in b_canvas_bool:
                mydata = getTrueFalse(mydata)
                if mydata == "":
                    exceptionQuit("Please check the boolean assignment on line #"+str(iLine))
                if myslot not in b_canvas_attrib:
                    exceptionQuit("Unrecognized attribute on line #"+str(iLine)+ ": "+myslot)
                canvas[myslot] = mydata
                
        elif block[-1] == "histo":
            if myslot in b_histo_bool:
                mydata = getTrueFalse(mydata)
                if mydata == "":
                    exceptionQuit("Please check the boolean assignment on line #"+str(iLine))
                else: histos[oname[-1]][myslot] = mydata
            if myslot in b_histo_quote:
                if isProperQuote(mydata):
                    mydata=mydata[1:-1] #remove quotes
                    histos[oname[-1]][myslot] = mydata
                else:
                    exceptionQuit("Please check quotations on line #"+str(iLine))
                
            if myslot not in b_histo_attrib:
                exceptionQuit("[histo block] Unrecognized attribute on line #"+str(iLine)+ ": "+myslot)
            
            
        elif block[-1] == "plot":
            if myslot in b_plot_quote:
                if not isProperQuote(mydata):
                    exceptionQuit("Please check quotations on line #"+str(iLine))
                mydata=mydata[1:-1] #remove quotes
            elif myslot in b_plot_bool:
                mydata = getTrueFalse(mydata)
                if mydata == "":
                    exceptionQuit("Please check the boolean assignment on line #"+str(iLine))
            if myslot not in b_plot_attrib:
                exceptionQuit("Unrecognized attribute on line #"+str(iLine)+ ": "+myslot)
            if myslot == "push":
                plots[oname[-1]]["pushed"].append(mydata)
            else:
                plots[oname[-1]][myslot] = mydata
                

#Legend Example
#  TLegend *legend=new TLegend(.7,.75,.89,.89);  //geometry of legend
#  legend->SetHeader(histo1->GetName());  //leg. header (name of histogram or sth. else)
#  histo1->SetLineColor(2);  //histo1 in red
#  histo2->SetLineColor(1);  //histo2 in black
#  legend->AddEntry(histo1,label1,"L");  // see *http://root.cern.ch/root/html/TLegend.html *  for details
#  legend->AddEntry(histo2,label2,"L");
#  legend->SetBorderSize(0);  //no border for legend
#  legend->SetFillColor(0);  //fill color is white
#  legend->Draw();  //draw it
