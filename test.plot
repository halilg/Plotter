rootfile testfile
   location="test.root"
   desc="Test ROOT File"
   linecolor=1
   
histo pt_bJet
   location = "HISTOFirstBJet/pt_bJet"
   linewidth = 2
   #normalize = false
   
histo eta_bJet
   location = "HISTOFirstBJet/eta_bJet"
   linewidth = 2
   #normalize = false
   
plot pt_bJet
   logy=false
   push=testfile.pt_bJet
   title="b Jet pt; pt; Jets"
   filename="test-pt_bJet.png"
   
plot eta_bJet
   logy=false
   push=testfile.eta_bJet
   title="b Jet eta; eta; Jets"
   filename="test-eta_bJet.pdf"

#exit

print pt_bJet
print eta_bJet
