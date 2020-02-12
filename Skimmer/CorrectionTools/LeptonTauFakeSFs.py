#!/usr/bin/env python
# Author: Izaak Neutelings (December 2018)
# 2016: https://indico.cern.ch/event/566825/contributions/2398691/attachments/1385164/2107478/HIG-16-043-preapproval-rehearsal.pdf
# 2017: https://indico.cern.ch/event/715039/timetable/#2-lepton-tau-fake-rates-update
#       https://indico.cern.ch/event/719250/contributions/2971854/attachments/1635435/2609013/tauid_recommendations2017.pdf
#       https://twiki.cern.ch/twiki/bin/view/CMS/TauIDRecommendation13TeV#Muon%20to%20tau%20fake%20rate



class LeptonTauFakeSFs:
    
    def __init__(self, antiMuWP, antiEleWP, year=2017):
        """Initialize WP-dependent SFs."""
        
        assert antiMuWP in ['loose', 'tight'],\
               "LeptonTauFakeSFs: You must choose a anti-muon discriminator WP from: loose or tight"
        assert antiEleWP in ['vloose', 'loose', 'medium', 'tight', 'vtight'],\
               "LeptonTauFakeSFs: You must choose a anti-electron discriminator WP from: vloose, loose, medium, tight, or vtight"
        
        self.antiMuSFs  = [ ]
        self.antiEleSFs = [ ]
        if year==2016:
          #                               eta bins :  0.0 - 0.4 - 0.8 - 1.2 - 1.7 - 2.3
          if   antiMuWP=='loose':   self.antiMuSFs = (1.146, 1.084, 1.218, 1.490, 2.008)
          elif antiMuWP=='tight':   self.antiMuSFs = (1.470, 1.367, 1.251, 1.770, 1.713)
          
          #                                eta bins :  <1.460, >1.558
          if   antiEleWP=='vloose': self.antiEleSFs = ( 1.317,  1.547 )
          elif antiEleWP=='loose':  self.antiEleSFs = ( 1.466,  1.719 )
          elif antiEleWP=='medium': self.antiEleSFs = ( 1.502,  1.594 )
          elif antiEleWP=='tight':  self.antiEleSFs = ( 1.486,  1.560 )
          elif antiEleWP=='vtight': self.antiEleSFs = ( 1.601,  1.401 )
          
        else:
          #                               eta bins :  0.0 - 0.4 - 0.8 - 1.2 - 1.7 - 2.3
          if   antiMuWP=='loose':   self.antiMuSFs = (1.061, 1.022, 1.097, 1.030, 1.941)
          elif antiMuWP=='tight':   self.antiMuSFs = (1.170, 1.290, 1.140, 0.930, 1.610)
          
          #                                eta bins :  <1.460, >1.558
          if   antiEleWP=='vloose': self.antiEleSFs = ( 1.09,   1.19 )
          elif antiEleWP=='loose':  self.antiEleSFs = ( 1.17,   1.25 )
          elif antiEleWP=='medium': self.antiEleSFs = ( 1.40,   1.21 )
          elif antiEleWP=='tight':  self.antiEleSFs = ( 1.80,   1.53 )
          elif antiEleWP=='vtight': self.antiEleSFs = ( 1.96,   1.66 )
        
    
    def getSF(self, genmatch, eta):
        """Get anti-lepton discriminator SF for lepton to tau fake (tau objects that are faked by a leptons)."""
        eta = abs(eta)
        
        # electron -> tau
        if genmatch==1:
          if   eta<1.460: return self.antiEleSFs[0]
          elif eta>1.558: return self.antiEleSFs[1]
        
        # muon -> tau
        elif genmatch==2:
          if   eta<0.4: return self.antiMuSFs[0]
          elif eta<0.8: return self.antiMuSFs[1]
          elif eta<1.2: return self.antiMuSFs[2]
          elif eta<1.7: return self.antiMuSFs[3]
          else:         return self.antiMuSFs[4]
        
        # real tau (Tight)
        #elif genmatch_2==5
        #  return 0.88; // Tight
        
        return 1.0
        

