
#! /usr/bin/env python

import os, multiprocessing, math
from array import array
from ROOT import TFile, TTree, TH1, TLorentzVector, TObject

########## SAMPLES ##########
data = ["data_obs"]
#data = []
back = ["Higgs", "WmWm", "WpWp", "VVV", "ZZ", "WZ", "WW", "TTTT", "TTZ", "TTW", "ST", "TTbar", "VGamma", "WJetsToLNu", "DYJetsToLL", "QCD"]
#back = ["TTZ"]
sign = []
variables = {
    "FIXME" : ["iSkim", "Z_mm", "Z_pt", "Z_Muonpt1", "Z_HT",\
             "Z_ee", "Z_ptee", "Z_Electronpt1", "Z_HTee",\
	     "Z_eebarrel", "Z_eeendcap", "Z_Elept1barrel", "Z_Elept1endcap",\
	     "Z_eeSSbarrel", "Z_eeSSendcap", "Z_Elept1SSbarrel", "Z_Elept1SSendcap",\
	     "H_M4mu", "H_M2mu2e", "H_M4e", "H_M4lept", \
             "Jpsi_mass", "Jpsi_massPt50", "Jpsi_massHT", "Jpsi_HT","Jpsi_dxy",\
             "Mue_isomu", "Mue_mass", "Mue_HT", "Mue_CSVmax", "Mue_nj30",\
             "ZW_MTW3lept", "ZW_MTWmmm","ZW_MTWmme","ZW_MTWeem", "ZW_MTWeee",\
	     "ZW_Mmm3mu"    , "ZW_Mmm2me"   , "ZW_Mee2em"   , "ZW_Mee3e"   , "ZW_nj30", "ZW_nj30CSV", "ZW_HT", "ZW_ptZ","ZW_CSV","ZW_CSV2",\
	     "ZW_Mmm3muCSV" , "ZW_Mmm2meCSV", "ZW_Mee2emCSV", "ZW_Mee3eCSV", "ZW_Mll3leptCSV", "ZW_HTCSV","ZW_ptZCSV",\
	     "ZW_MET3mu"  , "ZW_MET2me", "ZW_MET2em", "ZW_MET3e",\
             "ZW_MTW3leptCSV", "ZW_MTWmmmCSV","ZW_MTWmmeCSV","ZW_MTWeemCSV", "ZW_MTWeeeCSV",\
             "mu3_maxMuIso" ,"mu3_HT", "mu3_mMin" , "mu3_CSVmax", "mu3_maxMuIsoCSVpt1525","mu3_maxMuIsoCSVpt25" ,"mu3_maxMuIsoCSVpt40",\
             "e2mu_maxMuIso","e2mu_HT","e2mu_mMin","e2mu_CSVmax","e2mu_maxMuIsoCSVpt1525","e2mu_maxMuIsoCSVpt25","e2mu_maxMuIsoCSVpt40",\
	     "lept3_maxMuIsoCSVpt1525","lept3_maxMuIsoCSVpt25" ,"lept3_maxMuIsoCSVpt40",\
             "SSmu_maxMuIso","SSmu_HT", "SSmu_nj30","SSmu_maxMuIsoIPlow", "SSmu_maxMuIso2j", "SSmu_maxMuIsoHT200",\
	     "SSmu_CSVmax", "SSmu_CSVmaxLowIso",  \
             "SSmu_maxMuIso2jPt1525"     , "SSmu_maxMuIso2jPt2540"     , "SSmu_maxMuIso2jPt25"     , "SSmu_maxMuIso2jPt40", \
	     "SSmu_maxMuIso2jPt1525higIP", "SSmu_maxMuIso2jPt2540higIP", "SSmu_maxMuIso2jPt25higIP", "SSmu_maxMuIso2jPt40higIP", \
             "SSmu_maxMuIso2jbveto" , "SSmu_maxMuIso2jbvetoPt1525" , "SSmu_Mjjbveto", "SSmu_Mjjbvetoplus" , "SSmu_Mjjbvetominus" ,\
	     "SSmu_maxMuIsobvetoplus", "SSmu_maxMuIsobvetominus",\
	     "SSmu_maxMuIso2jbtag"  , "SSmu_maxMuIso2jbtagPt1525", "SSmu_maxMuIso2jbtagPt40", "SSmu_HTbtagPt25",\
	     "SSmu_maxMuIso2jbtagHT350",\
             "SSmue_maxMuIso","SSmue_HT", "SSmue_nj30","SSmue_maxMuIsoIPlow", "SSmue_maxMuIsoTRGele", "SSmue_maxMuIso2j", "SSmue_maxMuIsoHT200",\
	     "SSmue_CSVmax", "SSmue_CSVmaxLowIso",  \
             "SSmue_maxMuIso2jPt1525", "SSmue_maxMuIso2jPt2540", "SSmue_maxMuIso2jPt25", "SSmue_maxMuIso2jPt40", \
             "SSmue_maxMuIso2jbveto" , "SSmue_maxMuIso2jbvetoPt1525" , "SSmue_Mjjbveto", "SSmue_Mjjbvetoplus" , "SSmue_Mjjbvetominus" ,\
	     "SSmue_maxMuIsobvetoplus", "SSmue_maxMuIsobvetominus",\
	     "SSmue_maxMuIso2jbtag"  , "SSmue_maxMuIso2jbtagPt1525", "SSmue_maxMuIso2jbtagPt40","SSmue_HTbtagPt25",\
	     "SSmue_maxMuIso2jbtagHT350",\
	     "tt_Wqqmass"  , "tt_Tlvb1" , "tt_Tlvb2" , "tt_Tqqb1" , "tt_Tqqb2",\
	     "tte_Wqqmass" , "tte_Tlvb1", "tte_Tlvb2", "tte_Tqqb1", "tte_Tqqb2"],
    "Z2mCR" : [],
}
########## ######## ##########
		    


# Loop on events
def loop(hist, tree, ss, red):

    # ask which data you are looking for 
    Mudata  = ( "SingleMuon" in ss )
    Eledata = ( "SingleElectron" in ss )
    MCdata = 1
    if Mudata or Eledata : MCdata = 0
    
    for event in range(0, tree.GetEntries(), red):
   # for event in range(0, 10000, red):
      tree.GetEntry(event)
      weight = tree.eventWeightLumi * red # per-event weight that also accounts for a reduction factor to run faster on MC        
      hist["FIXME"]["iSkim"].Fill(tree.iSkim, weight)
      # special for J/psi (only single-mu data stream and MC ):
      if  Mudata or MCdata : 
        if tree.isSingleMuTrigger or tree.isSingleMuIsoTrigger :
          # ========================
	  # J/psi plots -----------------------------------------          
          # ========================
          if tree.nMuon == 2 and  tree.Muon_mediumId[1] > 0 and abs(tree.Muon_dz[1]) < 0.5  :
             m1, m2 = TLorentzVector(), TLorentzVector() 
             m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
             m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
             m12 = (m1+m2).M()
             hist["FIXME"]["Jpsi_mass"].Fill(m12, weight)
             if tree.Muon_pt[0] > 50:
               hist["FIXME"]["Jpsi_massPt50"].Fill(m12, weight)
               if abs( m12-3.096) < 0.100 : 
	         hist["FIXME"]["Jpsi_HT"].Fill(tree.HT30, weight)
		# dxymax = max( abs ( tree.Muon_dxy[0] ) , abs ( tree.Muon_dxy[1] )  
		# hist["FIXME"]["Jpsi_dxy"].Fill(dxymax, weight)
               if tree.HT30 > 200. : hist["FIXME"]["Jpsi_massHT"].Fill(m12, weight)
      # trigger selection for muon, electron and MC streams
      iselTRG = 0
      # muon data stream 
      if Mudata and tree.isSingleMuIsoTrigger : iselTRG = 1
      # electron data stream 
      if Eledata and tree.isSingleEleIsoTrigger and not tree.isSingleMuIsoTrigger : iselTRG = 1
      # MC data stream 
      if MCdata == 1 and ( tree.isSingleMuIsoTrigger or tree.isSingleEleIsoTrigger ) : iselTRG = 1 
      # trigger selection ################################################ 
      if iselTRG == 1 :
          # check high pT, isolated electrons -------------------------------------
          ieleveto = 0
	  neleHpt  = 0
          for je in range(0, tree.nElectron) :
             if abs(tree.Electron_dz[je]) < 0.5   and tree.Electron_cutBased[je] > 1 :
               if abs(tree.Electron_pt[je]) > 15. and tree.Electron_pfRelIso03_all[je] < 0.15 : 
	         ieleveto = 1
		 if tree.Electron_cutBased[je] > 2 : neleHpt = neleHpt + 1
          # check high pT, isolated muons -------------------------------------
          imuveto = 0
          for jmu in range(0, tree.nMuon) :
             if abs(tree.Muon_dz[jmu]) < 0.5   and tree.Muon_mediumId[jmu] > 0 :
               if abs(tree.Muon_pt[jmu]) > 15. and tree.Muon_pfRelIso03_all[jmu] < 0.15 : imuveto = 1 
          # ========================
          # Higgs, ZZ plots ------
	  # ========================
          if tree.nMuon == 4 :  # H-> 4 mu ---------------------------------
              iveto = 0
              for jmu in range(0, tree.nMuon) :
                if tree.Muon_mediumId[jmu] == 0 : iveto = 1
                if abs( tree.Muon_dz[jmu])  > 0.5    : iveto = 1
                if abs( tree.Muon_dxy[jmu]) > 0.0060 : iveto = 1 
                if tree.Muon_pfRelIso03_all[jmu] > 0.15 : iveto = 1
              if tree.Muon_pt[1] < 20. : iveto = 1         
              if tree.Muon_pt[2] < 10. : iveto = 1 
              if tree.Muon_pt[3] <  5. : iveto = 1 
              if tree.Muon_pfRelIso03_all[0] > 0.10 : iveto = 1
              if tree.Muon_pfRelIso03_all[1] > 0.10 : iveto = 1
              if iveto == 0 :
                m1, m2, m3, m4 = TLorentzVector(), TLorentzVector(),  TLorentzVector(), TLorentzVector()
                m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
                m3.SetPtEtaPhiM(tree.Muon_pt[2], tree.Muon_eta[2], tree.Muon_phi[2], tree.Muon_mass[2])        
                m4.SetPtEtaPhiM(tree.Muon_pt[3], tree.Muon_eta[3], tree.Muon_phi[3], tree.Muon_mass[3])
                m4mu = (m1+m2+m3+m4).M()                      
                hist["FIXME"]["H_M4mu"].Fill(m4mu, weight)
		hist["FIXME"]["H_M4lept"].Fill(m4mu, weight)
          if tree.nMuon == 2 and tree.nElectron == 2  :  # H-> 2mu 2e --------
              iveto = 0
              for jmu in range(0, tree.nMuon) :
                if tree.Muon_mediumId[jmu] == 0        : iveto = 1
                if abs( tree.Muon_dz[jmu])  > 0.5      : iveto = 1
                if abs( tree.Muon_dxy[jmu]) > 0.0060   : iveto = 1 
                if tree.Muon_pfRelIso03_all[jmu] > 0.1 : iveto = 1
              for je in range(0, tree.nElectron) :
                if tree.Electron_cutBased[je] < 3       : iveto = 1
                if abs( tree.Electron_dz[je])  > 0.5    : iveto = 1
                if abs( tree.Electron_dxy[je]) > 0.0100 : iveto = 1 
                if tree.Electron_pfRelIso03_all[je] > 0.07 : iveto = 1		
              if tree.Muon_pt[0] < 25. and  tree.Electron_pt[0] <  25. : iveto = 1         
              if tree.Muon_pt[1] <  5.      : iveto = 1 
	      if tree.Electron_pt[1] <  10. : iveto = 1 
	      if tree.Muon_charge[0]*tree.Muon_charge[1] > 0         : iveto = 1
	      if tree.Electron_charge[0]*tree.Electron_charge[1] > 0 : iveto = 1
              if iveto == 0 :
                m1, m2, m3, m4 = TLorentzVector(), TLorentzVector(),  TLorentzVector(), TLorentzVector()
                m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
                m3.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])        
                m4.SetPtEtaPhiM(tree.Electron_pt[1], tree.Electron_eta[1], tree.Electron_phi[1], tree.Electron_mass[1])
                m2mu2e = (m1+m2+m3+m4).M()     
                hist["FIXME"]["H_M2mu2e"].Fill(m2mu2e, weight)
		hist["FIXME"]["H_M4lept"].Fill(m2mu2e, weight)     
          if tree.nElectron == 4 :  # H-> 4 e ---------------------------------
              iveto = 0
              for je in range(0, tree.nElectron) :
                if tree.Electron_cutBased[je] < 2           : iveto = 1
                if abs( tree.Electron_dz[je])  > 0.5        : iveto = 1
                if abs( tree.Electron_dxy[je]) > 0.0100     : iveto = 1 
                if tree.Electron_pfRelIso03_all[je] > 0.15  : iveto = 1
              if tree.Electron_pt[0] < 27. : iveto = 1         
              if tree.Electron_pt[1] < 20. : iveto = 1 
	      if tree.Electron_pt[2] < 10. : iveto = 1 
              if tree.Electron_pt[3] <  5. : iveto = 1 
              if iveto == 0 :
                m1, m2, m3, m4 = TLorentzVector(), TLorentzVector(),  TLorentzVector(), TLorentzVector()
                m1.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])
                m2.SetPtEtaPhiM(tree.Electron_pt[1], tree.Electron_eta[1], tree.Electron_phi[1], tree.Electron_mass[1])
                m3.SetPtEtaPhiM(tree.Electron_pt[2], tree.Electron_eta[2], tree.Electron_phi[2], tree.Electron_mass[2])        
                m4.SetPtEtaPhiM(tree.Electron_pt[3], tree.Electron_eta[3], tree.Electron_phi[3], tree.Electron_mass[3])
                m4e = (m1+m2+m3+m4).M()                      
                hist["FIXME"]["H_M4e"].Fill(m4e, weight)
		hist["FIXME"]["H_M4lept"].Fill(m4e, weight)		
          # ========================     
	  # Z->ee plots -------------------------------------------
          # ========================
	  if tree.nElectron > 1 and tree.iSkim == 6 and tree.Electron_pt[1] > 20.  :   
	    if tree.Electron_charge[0]*tree.Electron_charge[1]<0 and tree.Electron_cutBased[0]>2 and  tree.Electron_cutBased[1]>2  :
	      etamax = abs( tree.Electron_eta[0] )
	      if abs(tree.Electron_eta[1]) > etamax : etamax = abs( tree.Electron_eta[1] )
              if etamax < 2.1  and tree.Electron_pfRelIso03_all[0]<0.10 and tree.Electron_pfRelIso03_all[1]<0.10 :
                hist["FIXME"]["Z_ee"].Fill(tree.Z_mass, weight)
                if abs(tree.Z_mass - 91.1)  < 15. :
                  hist["FIXME"]["Z_ptee"].Fill(tree.Z_pt, weight)
                  hist["FIXME"]["Z_Electronpt1"].Fill(tree.Electron_pt[0], weight)
                  hist["FIXME"]["Z_HTee"].Fill(tree.HT30, weight)		
		# only for tight charge ID: ---------
		if tree.Electron_tightCharge[0] > 0 and tree.Electron_tightCharge[1] > 0 :
                  if( etamax < 1.5)  : hist["FIXME"]["Z_eebarrel"].Fill(tree.Z_mass, weight)
	          if( etamax > 1.5)  : hist["FIXME"]["Z_eeendcap"].Fill(tree.Z_mass, weight)
                  if abs(tree.Z_mass - 91.1)  < 15. :
                    if( etamax < 1.5) : hist["FIXME"]["Z_Elept1barrel"].Fill(tree.Electron_pt[0], weight)
		    if( etamax > 1.5) : hist["FIXME"]["Z_Elept1endcap"].Fill(tree.Electron_pt[0], weight)		  
	  # misId charge study	:e+e+ and e-e- inv.mass -------------------------
	  if tree.nElectron > 1 and  tree.Electron_pt[1] > 20. and tree.Electron_charge[0]*tree.Electron_charge[1]>0  :   
	    etamax = abs( tree.Electron_eta[0] )
	    if abs(tree.Electron_eta[1]) > etamax : etamax = abs( tree.Electron_eta[1] )
	    if etamax < 2.1 and tree.Electron_cutBased[0]>2 and  tree.Electron_cutBased[1]>2  :
	      if tree.Electron_tightCharge[0] > 0 and tree.Electron_cutBased[0]>2    :
                # only for tight charge ID: --------
		if tree.Electron_tightCharge[1] > 0 and tree.Electron_cutBased[1]>2  :
                  if tree.Electron_pfRelIso03_all[0]<0.1 and tree.Electron_pfRelIso03_all[1]<0.1 :
                    m1, m2 = TLorentzVector(), TLorentzVector()
                    m1.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])
                    m2.SetPtEtaPhiM(tree.Electron_pt[1], tree.Electron_eta[1], tree.Electron_phi[1], tree.Electron_mass[1])
                    m2e = (m1+m2).M()
                    if( etamax < 1.5)  : hist["FIXME"]["Z_eeSSbarrel"].Fill(m2e, weight)
		    if( etamax > 1.5)  : hist["FIXME"]["Z_eeSSendcap"].Fill(m2e, weight)
		    if abs(m2e - 91.1)  < 15. :
                      if( etamax < 1.5) : hist["FIXME"]["Z_Elept1SSbarrel"].Fill(tree.Electron_pt[0], weight)
		      if( etamax > 1.5) : hist["FIXME"]["Z_Elept1SSendcap"].Fill(tree.Electron_pt[0], weight)	    
          # ========================     
	  # Z->mm plots -------------------------------------------
          # ========================  
	  if tree.nMuon > 1 and tree.iSkim == 1  :     	    
	    if tree.Muon_charge[0]*tree.Muon_charge[1]<0 and tree.Muon_mediumId[0] > 0 and tree.Muon_mediumId[1] > 0 :
	      if tree.Muon_pfRelIso03_all[0]<0.10 and tree.Muon_pfRelIso03_all[1]<0.10 :                                  
                hist["FIXME"]["Z_mm"].Fill(tree.Z_mass, weight)
                if tree.Z_mass > 70 and tree.Z_mass < 110 :
                  hist["FIXME"]["Z_pt"].Fill(tree.Z_pt, weight)
                  hist["FIXME"]["Z_Muonpt1"].Fill(tree.Muon_pt[0], weight)
                  hist["FIXME"]["Z_HT"].Fill(tree.HT30, weight)
          # ========================
          # WZ plots: Z->mm, W->munu case -----------
          # ========================
          if tree.nMuon == 3 and ieleveto == 0 and tree.Muon_pt[2] > 20.:
              m1, m2 = TLorentzVector(), TLorentzVector()
              jmu1Z , jmu2Z, jmuW = -1 , -1, -1
              mDZmin = 9999.
              mZ , ptZ = 0. , 0.
              for jmu1 in range(0, tree.nMuon-1) :
                if tree.Muon_mediumId[jmu1] > 0 and tree.Muon_pfRelIso03_all[jmu1] < 0.15 : 
                  if abs( tree.Muon_dz[jmu1])  < 0.5  and abs( tree.Muon_dxy[jmu1]) < 0.0060 : 
                    for jmu2 in range(jmu1+1, tree.nMuon) :     
                      if tree.Muon_charge[jmu1]*tree.Muon_charge[jmu2]<0 and tree.Muon_pt[jmu2] > 20. :
                        if tree.Muon_mediumId[jmu2] > 0 and tree.Muon_pfRelIso03_all[jmu2] < 0.15 : 
                          if abs( tree.Muon_dz[jmu2])  < 0.5  and abs( tree.Muon_dxy[jmu2]) < 0.0060 :
                            m1.SetPtEtaPhiM(tree.Muon_pt[jmu1], tree.Muon_eta[jmu1], tree.Muon_phi[jmu1], tree.Muon_mass[jmu1])
                            m2.SetPtEtaPhiM(tree.Muon_pt[jmu2], tree.Muon_eta[jmu2], tree.Muon_phi[jmu2], tree.Muon_mass[jmu2])
                            m2mu  = (m1+m2).M()
                            mDZ = abs(m2mu - 91.1)
                            if mDZ < mDZmin :
                              mDZmin = mDZ
                              jmu1Z, jmu2Z = jmu1, jmu2
                              mZ = m2mu
			      ptZ = (m1+m2).Pt()      
              for jmu in range(0, tree.nMuon) : 
                iveto = 0
		if jmu == jmu1Z or jmu == jmu2Z : iveto = 1
                if iveto == 0 : jmuW = jmu
	      if mZ > 0. and tree.Muon_mediumId[jmuW] > 0 and tree.Muon_pfRelIso03_all[jmuW] < 0.1 :	
                if abs(tree.Muon_eta[jmuW])  < 2.1 and tree.Muon_pt[jmuW] > 25.  :
		  hist["FIXME"]["ZW_Mmm3mu"].Fill(mZ, weight) 
		  if tree.CSV1 > 0.8 and tree.nj30 > 2 : 
		    hist["FIXME"]["ZW_Mmm3muCSV"].Fill(mZ, weight) 
                    hist["FIXME"]["ZW_Mll3leptCSV"].Fill(mZ, weight) 
		  if abs( mZ - 91.1) < 15. : 
		    hist["FIXME"]["ZW_MET3mu"].Fill(tree.MET_pt, weight)  
		    if tree.MET_pt > 30. :
		      m1.SetPtEtaPhiM(tree.Muon_pt[jmuW], 0., tree.Muon_phi[jmuW], tree.Muon_mass[jmuW])
                      m2.SetPtEtaPhiM(tree.MET_pt, 0., tree.MET_phi, 0.)
                      mTW = (m1+m2).M()
		      hist["FIXME"]["ZW_MTW3lept"].Fill(mTW, weight)
                      hist["FIXME"]["ZW_MTWmmm"].Fill(mTW, weight)
                      hist["FIXME"]["ZW_nj30"].Fill(tree.nj30, weight)
                      hist["FIXME"]["ZW_HT"].Fill(tree.HT30, weight)
		      hist["FIXME"]["ZW_CSV"].Fill(tree.CSV1, weight)
                      hist["FIXME"]["ZW_ptZ"].Fill(ptZ, weight)
		      # target ttZ : tighter MZ cut to reduce tt background...
		      if tree.CSV1 > 0.8 and  abs( mZ - 91.1) < 8. :
		        hist["FIXME"]["ZW_CSV2"].Fill(tree.CSV2, weight)
			hist["FIXME"]["ZW_nj30CSV"].Fill(tree.nj30, weight)
			if tree.nj30 > 2 and tree.CSV2 > 0.25 :        
		          hist["FIXME"]["ZW_MTWmmmCSV"].Fill(mTW, weight)
			  hist["FIXME"]["ZW_MTW3leptCSV"].Fill(mTW, weight)
			  hist["FIXME"]["ZW_HTCSV"].Fill(tree.HT30, weight)
                          hist["FIXME"]["ZW_ptZCSV"].Fill(ptZ, weight)
          # ========================
          # WZ plots: Z->mm, W->enu case -----------
          # ========================
          if tree.nMuon == 2 and tree.nElectron == 1 and tree.Electron_pt[0] > 30. and abs(tree.Electron_eta[0]) < 2.1 :
              if tree.Electron_cutBased[0] > 2  and tree.Electron_pfRelIso03_all[0] < 0.08 :
                if tree.Muon_charge[0]*tree.Muon_charge[1]<0 and tree.Muon_pt[1] > 20. :
                  if tree.Muon_mediumId[0] > 0 and tree.Muon_pfRelIso03_all[0] < 0.15 : 
                    if tree.Muon_mediumId[1] > 0 and tree.Muon_pfRelIso03_all[1] < 0.15 : 
                      m1, m2 = TLorentzVector(), TLorentzVector()
                      m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                      m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
                      m2mu = (m1+m2).M()
		      ptZ = (m1+m2).Pt() 
                      hist["FIXME"]["ZW_Mmm2me"].Fill(m2mu, weight) 
		      if tree.CSV1 > 0.8 and tree.nj30 > 2 : 
		        hist["FIXME"]["ZW_Mmm2meCSV"].Fill(m2mu, weight) 
                        hist["FIXME"]["ZW_Mll3leptCSV"].Fill(m2mu, weight) 
		      if abs( m2mu - 91.1) < 15 :
		        hist["FIXME"]["ZW_MET2me"].Fill(tree.MET_pt, weight)
			if tree.MET_pt > 30. :
                          m1.SetPtEtaPhiM(tree.Electron_pt[0], 0., tree.Electron_phi[0], tree.Electron_mass[0])
                          m2.SetPtEtaPhiM(tree.MET_pt, 0., tree.MET_phi, 0.)
                          mTW = (m1+m2).M()
                          hist["FIXME"]["ZW_MTW3lept"].Fill(mTW, weight)
                          hist["FIXME"]["ZW_MTWmme"].Fill(mTW, weight)
                          hist["FIXME"]["ZW_nj30"].Fill(tree.nj30, weight)
                          hist["FIXME"]["ZW_HT"].Fill(tree.HT30, weight)
		          hist["FIXME"]["ZW_CSV"].Fill(tree.CSV1, weight)
			  hist["FIXME"]["ZW_ptZ"].Fill(ptZ, weight)
			  # target ttZ: tighter MZ cut to reduce tt background...		  
                          if tree.CSV1 > 0.8 and  abs( m2mu - 91.1) < 8. : 
	                    hist["FIXME"]["ZW_CSV2"].Fill(tree.CSV2, weight)
			    hist["FIXME"]["ZW_nj30CSV"].Fill(tree.nj30, weight)
			    if tree.nj30 > 2 and tree.CSV2 > 0.25 : 	  
			      hist["FIXME"]["ZW_MTWmmeCSV"].Fill(mTW, weight)
			      hist["FIXME"]["ZW_MTW3leptCSV"].Fill(mTW, weight)
			      hist["FIXME"]["ZW_HTCSV"].Fill(tree.HT30, weight)
			      hist["FIXME"]["ZW_ptZCSV"].Fill(ptZ, weight)
          # ========================
          # WZ plots: Z->ee, W->mu nu case -----------
          # ========================
          if tree.nMuon == 1 and tree.nElectron == 2 and tree.Muon_pt[0] > 20.:
              if tree.Muon_mediumId[0] > 0 and tree.Muon_pfRelIso03_all[0] < 0.1 and abs(tree.Muon_eta[0]) < 2.1 :
                if tree.Electron_charge[0]*tree.Electron_charge[1]<0 and tree.Electron_pt[1] > 20. :
                  if tree.Electron_cutBased[0] > 2  and tree.Electron_pfRelIso03_all[0] < 0.1 : 
                    if tree.Electron_cutBased[1] > 2 and tree.Electron_pfRelIso03_all[1] < 0.1 : 
                      m1, m2 = TLorentzVector(), TLorentzVector()
                      m1.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])
                      m2.SetPtEtaPhiM(tree.Electron_pt[1], tree.Electron_eta[1], tree.Electron_phi[1], tree.Electron_mass[1])
                      m2e = (m1+m2).M()
		      ptZ = (m1+m2).Pt() 
                      hist["FIXME"]["ZW_Mee2em"].Fill(m2e, weight)
		      if tree.CSV1 > 0.8 and tree.nj30 > 2 : 
		        hist["FIXME"]["ZW_Mee2emCSV"].Fill(m2e, weight)
			hist["FIXME"]["ZW_Mll3leptCSV"].Fill(m2e, weight) 
                      if abs( m2e - 91.1) < 15 :    
		        hist["FIXME"]["ZW_MET2em"].Fill(tree.MET_pt, weight)
			if tree.MET_pt > 30. : 
                          m1.SetPtEtaPhiM(tree.Muon_pt[0], 0., tree.Muon_phi[0], tree.Muon_mass[0])
                          m2.SetPtEtaPhiM(tree.MET_pt, 0., tree.MET_phi, 0.)
                          mTW = (m1+m2).M()
                          hist["FIXME"]["ZW_MTWeem"].Fill(mTW, weight)
		  	  hist["FIXME"]["ZW_MTW3lept"].Fill(mTW, weight)
                          hist["FIXME"]["ZW_nj30"].Fill(tree.nj30, weight)
                          hist["FIXME"]["ZW_HT"].Fill(tree.HT30, weight)
		          hist["FIXME"]["ZW_CSV"].Fill(tree.CSV1, weight)			  
			  hist["FIXME"]["ZW_ptZ"].Fill(ptZ, weight)  
			  # target ttZ : tighter MZ cut to reduce tt background...                        
			  if tree.CSV1 > 0.8 and  abs( m2e - 91.1) < 8.  : 
			    hist["FIXME"]["ZW_CSV2"].Fill(tree.CSV2, weight)
	                    hist["FIXME"]["ZW_nj30CSV"].Fill(tree.nj30, weight)
			    if tree.nj30 > 2 and tree.CSV2 > 0.25 : 
			      hist["FIXME"]["ZW_MTWeemCSV"].Fill(mTW, weight)
			      hist["FIXME"]["ZW_MTW3leptCSV"].Fill(mTW, weight)
			      hist["FIXME"]["ZW_HTCSV"].Fill(tree.HT30, weight)
			      hist["FIXME"]["ZW_ptZCSV"].Fill(ptZ, weight)
          # ========================
          # WZ plots: Z->ee, W->enu case -----------
          # ========================
          if tree.nElectron == 3 and imuveto == 0 and tree.Electron_pt[2] > 20.:
              m1, m2 = TLorentzVector(), TLorentzVector()
              je1Z, je2Z , jeW = -1, -1, -1
              mDZmin = 9999.
              mZ, ptZ = 0. , 0.
              for je1 in range(0, tree.nElectron-1) :
                if tree.Electron_cutBased[je1] > 2 and tree.Electron_pfRelIso03_all[je1] < 0.12 : 
                  if abs( tree.Electron_dz[je1])  < 0.5  and abs( tree.Electron_dxy[je1]) < 0.0100 : 
                    for je2 in range(je1+1, tree.nElectron) :     
                      if tree.Electron_charge[je1]*tree.Electron_charge[je2]<0 and tree.Electron_pt[je2] > 20. :
                        if tree.Electron_cutBased[je2] > 2 and tree.Electron_pfRelIso03_all[je2] < 0.12 : 
                          if abs( tree.Electron_dz[je2])  < 0.5  and abs( tree.Electron_dxy[je2]) < 0.0100 :
                            m1.SetPtEtaPhiM(tree.Electron_pt[je1], tree.Electron_eta[je1], tree.Electron_phi[je1], tree.Electron_mass[je1])
                            m2.SetPtEtaPhiM(tree.Electron_pt[je2], tree.Electron_eta[je2], tree.Electron_phi[je2], tree.Electron_mass[je2])
                            m2e = (m1+m2).M()
                            mDZ = abs(m2e - 91.1)
                            if mDZ < mDZmin :
                              mDZmin = mDZ
                              je1Z, je2Z = je1, je2
                              mZ = m2e
			      ptZ = (m1+m2).Pt() 
              for je in range(0, tree.nElectron) :
                iveto = 0 
                if je == je1Z or je == je2Z : iveto = 1
		if iveto == 0 : jeW = je
              if mZ > 0. and tree.Electron_cutBased[jeW] > 2 and tree.Electron_pfRelIso03_all[jeW] < 0.05 : 
	        if abs(tree.Electron_eta[jeW]) < 2.1 and tree.Electron_pt[jeW] > 25.  :	      
	          hist["FIXME"]["ZW_Mee3e"].Fill(mZ, weight)   
		  if tree.CSV1 > 0.8 and tree.nj30 > 2 : 
		    hist["FIXME"]["ZW_Mee3eCSV"].Fill(mZ, weight)    
                    hist["FIXME"]["ZW_Mll3leptCSV"].Fill(mZ, weight) 
		  if abs( mZ - 91.1) < 15. : 
		    hist["FIXME"]["ZW_MET3e"].Fill(tree.MET_pt, weight)
		    if tree.MET_pt > 30. :                         
		      m1.SetPtEtaPhiM(tree.Electron_pt[jeW], 0., tree.Electron_phi[jeW], tree.Electron_mass[jeW])
                      m2.SetPtEtaPhiM(tree.MET_pt, 0., tree.MET_phi, 0.)
                      mTW = (m1+m2).M()
                      hist["FIXME"]["ZW_MTWeee"].Fill(mTW, weight)
		      hist["FIXME"]["ZW_MTW3lept"].Fill(mTW, weight)
                      hist["FIXME"]["ZW_nj30"].Fill(tree.nj30, weight)
                      hist["FIXME"]["ZW_HT"].Fill(tree.HT30, weight)
		      hist["FIXME"]["ZW_CSV"].Fill(tree.CSV1, weight)
		      hist["FIXME"]["ZW_ptZ"].Fill(ptZ, weight)
		      # target ttZ: tighter MZ cut to reduce tt background...
                      if tree.CSV1 > 0.8 and  abs( mZ - 91.1) < 8. : 
		        hist["FIXME"]["ZW_CSV2"].Fill(tree.CSV2, weight)
		        hist["FIXME"]["ZW_nj30CSV"].Fill(tree.nj30, weight)
			if tree.nj30 > 2 and tree.CSV2 > 0.25 : 
		          hist["FIXME"]["ZW_MTWeeeCSV"].Fill(mTW, weight)
		          hist["FIXME"]["ZW_MTW3leptCSV"].Fill(mTW, weight)
			  hist["FIXME"]["ZW_HTCSV"].Fill(tree.HT30, weight)
			  hist["FIXME"]["ZW_ptZCSV"].Fill(ptZ, weight)
	  # ========================
          # 3 muons plots -------------------------------------------
          # ========================
          if tree.nMuon == 3 and ieleveto == 0 and tree.Muon_pt[2] > 15.  :
	    if tree.Muon_mediumId[0] > 0 and  tree.Muon_mediumId[1] > 0 and tree.Muon_mediumId[2] > 0 :
	      if abs( tree.Muon_dz[0] ) < 0.5 and abs( tree.Muon_dz[1] ) < 0.5 and abs( tree.Muon_dz[2] < 0.5 ) : 
                etamax = abs(tree.Muon_eta[0] )
                if  abs(tree.Muon_eta[1] ) > etamax : etamax = abs(tree.Muon_eta[1] )
                if  abs(tree.Muon_eta[2] ) > etamax : etamax = abs(tree.Muon_eta[2] )
                if etamax < 2.1 :
                  m1, m2, m3 = TLorentzVector(), TLorentzVector(),  TLorentzVector()
                  m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                  m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
                  m3.SetPtEtaPhiM(tree.Muon_pt[2], tree.Muon_eta[2], tree.Muon_phi[2], tree.Muon_mass[2])
                  m12 = (m1+m2).M()
                  m13 = (m1+m3).M()
                  m23 = (m2+m3).M()
                  mMin = m12
                  if m13 < mMin : mMin = m13
                  if m23 < mMin : mMin = m23
                  hist["FIXME"]["mu3_mMin"].Fill(mMin, weight)
                  iZveto = 0
                  if abs(m12-91.1) < 15. and tree.Muon_charge[0]*tree.Muon_charge[1]<0 : iZveto = 1
                  if abs(m13-91.1) < 15. and tree.Muon_charge[0]*tree.Muon_charge[2]<0 : iZveto = 1
                  if abs(m23-91.1) < 15. and tree.Muon_charge[1]*tree.Muon_charge[2]<0 : iZveto = 1
                  if mMin > 15. and iZveto == 0:
		    isomu1 = tree.Muon_pfRelIso03_all[0]	
		    isomu2 = tree.Muon_pfRelIso03_all[1]	
		    isomu3 = tree.Muon_pfRelIso03_all[2]
		    # solve ambituity when two muons have iso = 0 (the higher iso is defined to be the lower pT...)
		    if isomu2 == 0. : isomu2 = 0.0002	
		    if isomu3 == 0. : isomu3 = 0.0003	
                    isomax =  isomu1	   
                    jmax = 0
		    if  isomu2 > isomax : 
		      isomax = isomu2
		      jmax = 1
                    if  isomu3 > isomax : 
		      isomax = isomu3
		      jmax = 2
		    isomin =  isomu1  
                    jmin = 0
		    if  isomu2 < isomin : 
		      isomin = isomu2
                      jmin = 1
		    if  isomu3  < isomin : 
		      isomin = isomu3		   
                      jmin = 2
		    if  tree.Muon_pfRelIso03_all[jmin] < 0.05 :
		      hist["FIXME"]["mu3_maxMuIso"].Fill(isomax, weight)  
                      hist["FIXME"]["mu3_HT"].Fill(tree.HT30, weight) 
                      hist["FIXME"]["mu3_CSVmax"].Fill(tree.CSV1, weight) 
                      if tree.HT30 > 100. and  tree.CSV1 > 0.4  : 
                        if tree.Muon_pt[2] < 25. :  hist["FIXME"]["mu3_maxMuIsoCSVpt1525"].Fill(isomax, weight)
                        if tree.Muon_pt[2] > 25. :  hist["FIXME"]["mu3_maxMuIsoCSVpt25"].Fill(isomax, weight)
                        if tree.Muon_pt[2] > 40. :  hist["FIXME"]["mu3_maxMuIsoCSVpt40"].Fill(isomax, weight) 
                        if tree.Muon_pt[2] < 25. :  hist["FIXME"]["lept3_maxMuIsoCSVpt1525"].Fill(isomax, weight)
                        if tree.Muon_pt[2] > 25. :  hist["FIXME"]["lept3_maxMuIsoCSVpt25"].Fill(isomax, weight)
                        if tree.Muon_pt[2] > 40. :  hist["FIXME"]["lept3_maxMuIsoCSVpt40"].Fill(isomax, weight) 			                             
          # ========================
          # OS mu-e plots -------------------------------------------
          # ========================
          if tree.nElectron > 0 and tree.nMuon >0 and tree.Muon_pt[0] > 25. and tree.Electron_pt[0] > 25. :
	    if tree.Muon_charge[0]*tree.Electron_charge[0]<0 and abs(tree.Electron_eta[0]) < 2.1 :
	     # electron must be isolated...
	     if tree.Electron_cutBased[0] > 2  and abs( tree.Electron_dz[0]) < 0.5 and tree.Electron_pfRelIso03_all[0]<0.07 :
	       if tree.Muon_mediumId[0] > 0    and abs( tree.Muon_dz[0]) < 0.5 and abs(tree.Muon_eta[0]) < 2.1 :  
                 m1, m2 = TLorentzVector(), TLorentzVector()
                 m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                 m2.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])
                 mMue = (m1+m2).M()
                 # Z-> tau tau -> mu e  veto ------
                 iZveto = 0 
                 if mMue > 50. and mMue < 90. : iZveto = 1	
		 # plot mu isolation only for electron triggers...	 
		 if iZveto == 0 and tree.isSingleEleIsoTrigger  : hist["FIXME"]["Mue_isomu"].Fill( tree.Muon_pfRelIso03_all[0], weight)		         
		 if tree.Muon_pfRelIso03_all[0] < 0.10 :                           
                     hist["FIXME"]["Mue_mass"].Fill(mMue, weight)
                     hist["FIXME"]["Mue_HT"].Fill(tree.HT30, weight)
                     hist["FIXME"]["Mue_nj30"].Fill(tree.nj30, weight)  
                     hist["FIXME"]["Mue_CSVmax"].Fill(tree.CSV1, weight)  
		     # ===============================
                     # 2mu - e plots --------------------------------------
		     # ===============================
                     if tree.nMuon == 2 and tree.Muon_mediumId[1] > 0 and tree.Muon_pt[1] > 15. and abs(tree.Muon_eta[1] ) < 2.1 :
                       m3 = TLorentzVector()
                       m3.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
                       m13 = (m1+m3).M()
                       m23 = (m2+m3).M()
                       mMin = mMue
                       if m13 < mMin : mMin = m13
                       if m23 < mMin : mMin = m23
                       hist["FIXME"]["e2mu_mMin"].Fill(mMin, weight)
                       # Z-> mu mu veto ---------
		       if abs(m13-91.1) < 15. and tree.Muon_charge[0]*tree.Muon_charge[1]<0 : iZveto = 1
                       if mMin > 15. and iZveto == 0:
                         isomax = tree.Muon_pfRelIso03_all[0]
                         if  tree.Muon_pfRelIso03_all[1] > isomax : isomax = tree.Muon_pfRelIso03_all[1]                                 
                         hist["FIXME"]["e2mu_maxMuIso"].Fill(isomax, weight) 
                         hist["FIXME"]["e2mu_HT"].Fill(tree.HT30, weight)
                         hist["FIXME"]["e2mu_CSVmax"].Fill(tree.CSV1, weight)  
                         if tree.HT30 > 100. and  tree.CSV1 > 0.4 : 
                           if tree.Muon_pt[1] < 25. :  hist["FIXME"]["e2mu_maxMuIsoCSVpt1525"].Fill(isomax, weight) 
                           if tree.Muon_pt[1] > 25. :  hist["FIXME"]["e2mu_maxMuIsoCSVpt25"].Fill(isomax, weight)
                           if tree.Muon_pt[1] > 40. :  hist["FIXME"]["e2mu_maxMuIsoCSVpt40"].Fill(isomax, weight)
                           if tree.Muon_pt[1] < 25. :  hist["FIXME"]["lept3_maxMuIsoCSVpt1525"].Fill(isomax, weight)
                           if tree.Muon_pt[1] > 25. :  hist["FIXME"]["lept3_maxMuIsoCSVpt25"].Fill(isomax, weight)
                           if tree.Muon_pt[1] > 40. :  hist["FIXME"]["lept3_maxMuIsoCSVpt40"].Fill(isomax, weight) 			                             
          # ========================
          # SS muon plots -------------------------------------------
          # ========================
          if tree.nMuon == 2  and ieleveto == 0 and tree.Muon_mediumId[1] > 0  and tree.Muon_pt[1] > 15. :
            if abs( tree.Muon_dz[0]) < 0.5 and abs( tree.Muon_dz[1]) < 0.5 and abs(tree.Muon_dxy[0]) < 0.0050:
	      etamax = abs(tree.Muon_eta[0] )
              if  abs(tree.Muon_eta[1] ) > etamax : etamax = abs(tree.Muon_eta[1] )
              if tree.Muon_charge[0]*tree.Muon_charge[1] > 0 and etamax < 2.1 :
                isomax = tree.Muon_pfRelIso03_all[0]
                if  tree.Muon_pfRelIso03_all[1] > isomax : isomax = tree.Muon_pfRelIso03_all[1]                        
                hist["FIXME"]["SSmu_maxMuIso"].Fill(isomax, weight)
		# this is for background shape of isomu variable:		  
		if tree.nj30 > 1 and tree.HT30 > 200. and abs(tree.Muon_dxy[1]) > 0.0060 and abs(tree.Muon_dxy[1]) < 0.0500 :
                  if tree.Muon_pt[1] < 25. : hist["FIXME"]["SSmu_maxMuIso2jPt1525higIP"].Fill(isomax, weight)
                  if tree.Muon_pt[1] > 25. and tree.Muon_pt[1] < 40.: hist["FIXME"]["SSmu_maxMuIso2jPt2540higIP"].Fill(isomax, weight)
                  if tree.Muon_pt[1] > 25. : hist["FIXME"]["SSmu_maxMuIso2jPt25higIP"].Fill(isomax, weight)
                  if tree.Muon_pt[1] > 40. : hist["FIXME"]["SSmu_maxMuIso2jPt40higIP"].Fill(isomax, weight)		
                if  abs(tree.Muon_dxy[1]) < 0.0050 :
                  hist["FIXME"]["SSmu_maxMuIsoIPlow"].Fill(isomax, weight)
                  hist["FIXME"]["SSmu_nj30"].Fill(tree.nj30, weight)		  
                  if tree.nj30 > 1 : 
                    hist["FIXME"]["SSmu_HT"].Fill(tree.HT30, weight)		    
                    if tree.HT30 > 100 : 
                      hist["FIXME"]["SSmu_maxMuIso2j"].Fill(isomax, weight)
		      hist["FIXME"]["SSmu_CSVmax"].Fill(tree.CSV1, weight)
		      if isomax < 0.05 : hist["FIXME"]["SSmu_CSVmaxLowIso"].Fill(tree.CSV1, weight)
                      if tree.HT30 > 200. :
                        hist["FIXME"]["SSmu_maxMuIsoHT200"].Fill(isomax, weight)                        
                        if tree.Muon_pt[1] < 25. : hist["FIXME"]["SSmu_maxMuIso2jPt1525"].Fill(isomax, weight)
                        if tree.Muon_pt[1] > 25. and tree.Muon_pt[1] < 40.: hist["FIXME"]["SSmu_maxMuIso2jPt2540"].Fill(isomax, weight)
                        if tree.Muon_pt[1] > 25. : hist["FIXME"]["SSmu_maxMuIso2jPt25"].Fill(isomax, weight)
                        if tree.Muon_pt[1] > 40. : hist["FIXME"]["SSmu_maxMuIso2jPt40"].Fill(isomax, weight)
			# ======================
			# btag veto : W+W+ ,W-W- search
			# ======================
			if tree.CSV1 < 0.4 : 
			  if tree.Muon_pt[1] < 25. : hist["FIXME"]["SSmu_maxMuIso2jbvetoPt1525"].Fill(isomax, weight)
			  if tree.Muon_pt[1] > 25. :
			    hist["FIXME"]["SSmu_maxMuIso2jbveto"].Fill(isomax, weight)
			    if isomax < 0.05 : hist["FIXME"]["SSmu_Mjjbveto"].Fill(tree.jj_mass, weight)
			    # W+W+ ----
			    if tree.Muon_charge[0] > 0 :   
			      hist["FIXME"]["SSmu_maxMuIsobvetoplus"].Fill(isomax, weight)
			      if isomax < 0.05 : hist["FIXME"]["SSmu_Mjjbvetoplus"].Fill(tree.jj_mass, weight)
			    # W-W- -----  
			    if tree.Muon_charge[0] < 0 : 
			      hist["FIXME"]["SSmu_maxMuIsobvetominus"].Fill(isomax, weight)
			      if isomax < 0.05 : hist["FIXME"]["SSmu_Mjjbvetominus"].Fill(tree.jj_mass, weight)
			# ======================
			# btag  : ttW search
			# ======================
                        if tree.CSV1 > 0.4 : 
			  if tree.Muon_pt[1] < 25. : hist["FIXME"]["SSmu_maxMuIso2jbtagPt1525"].Fill(isomax, weight)
                          if tree.Muon_pt[1] > 25. : 
			    hist["FIXME"]["SSmu_maxMuIso2jbtag"].Fill(isomax, weight)
                            if tree.Muon_pt[1] > 40. : hist["FIXME"]["SSmu_maxMuIso2jbtagPt40"].Fill(isomax, weight)
			    if isomax < 0.025  : hist["FIXME"]["SSmu_HTbtagPt25"].Fill(tree.HT30, weight)
			    if tree.HT30 > 350.: hist["FIXME"]["SSmu_maxMuIso2jbtagHT350"].Fill(isomax, weight)
          # ========================
          # SS mu-e plots -------------------------------------------
          # ========================
          if tree.nMuon == 1  and tree.nElectron > 0 and neleHpt < 2 and tree.Muon_mediumId[0] > 0  and tree.Electron_cutBased[0] > 2 :
            # SS mu-e, requiring tight charge ID for electron....
	    if tree.Muon_charge[0]*tree.Electron_charge[0] > 0 and tree.Electron_tightCharge[0] > 0 :
	      if abs( tree.Muon_dz[0]) < 0.5 and abs( tree.Electron_dz[0]) < 0.5 and tree.Electron_pt[0] > 25. and tree.Muon_pt[0] > 15.:
                m1, m2 = TLorentzVector(), TLorentzVector()
                m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                m2.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])
                mMue = (m1+m2).M()
		# eta fiducial region for muon ( eta<2.1) end electron (eta < 1.5, due to charge misID...)
                if abs(tree.Muon_eta[0] ) < 2.1 and abs(tree.Electron_eta[0] ) < 1.5 and mMue > 15. :
                  isomax = tree.Muon_pfRelIso03_all[0]                   
                  hist["FIXME"]["SSmue_maxMuIso"].Fill(isomax, weight)
                  if abs(tree.Muon_dxy[0]) < 0.0050 and abs(tree.Electron_dxy[0]) < 0.0100 :                    
		    hist["FIXME"]["SSmue_maxMuIsoIPlow"].Fill(isomax, weight)
		    # plot iso mu only for electron triggers
		    if tree.isSingleEleIsoTrigger : hist["FIXME"]["SSmue_maxMuIsoTRGele"].Fill(isomax, weight) 
                    hist["FIXME"]["SSmue_nj30"].Fill(tree.nj30, weight)                  
                    if tree.nj30 > 1 : 
                      hist["FIXME"]["SSmue_HT"].Fill(tree.HT30, weight)
                      if tree.HT30 > 100 : 
                        hist["FIXME"]["SSmue_maxMuIso2j"].Fill(isomax, weight)
		        hist["FIXME"]["SSmue_CSVmax"].Fill(tree.CSV1, weight)
		        if isomax < 0.05 : hist["FIXME"]["SSmue_CSVmaxLowIso"].Fill(tree.CSV1, weight)
                        if tree.HT30 > 200 :
                          hist["FIXME"]["SSmue_maxMuIsoHT200"].Fill(isomax, weight)                        
                          if tree.Muon_pt[0] < 25. : hist["FIXME"]["SSmue_maxMuIso2jPt1525"].Fill(isomax, weight)
                          if tree.Muon_pt[0] > 25. and tree.Muon_pt[0] < 40.: hist["FIXME"]["SSmue_maxMuIso2jPt2540"].Fill(isomax, weight)
                          if tree.Muon_pt[0] > 25. : hist["FIXME"]["SSmue_maxMuIso2jPt25"].Fill(isomax, weight)
                          if tree.Muon_pt[0] > 40. : hist["FIXME"]["SSmue_maxMuIso2jPt40"].Fill(isomax, weight)
		  	  # ======================
			  # btag veto : W+W+ ,W-W- search
			  # ======================
			  if tree.CSV1 < 0.4 : 
			    if tree.Muon_pt[0] < 25. : hist["FIXME"]["SSmue_maxMuIso2jbvetoPt1525"].Fill(isomax, weight)
			    if tree.Muon_pt[0] > 25. :
			      hist["FIXME"]["SSmue_maxMuIso2jbveto"].Fill(isomax, weight)
			      if isomax < 0.05 : hist["FIXME"]["SSmue_Mjjbveto"].Fill(tree.jj_mass, weight)
			    # W+W+ ----
			    if tree.Muon_charge[0] > 0 :   
			      hist["FIXME"]["SSmue_maxMuIsobvetoplus"].Fill(isomax, weight)
			      if isomax < 0.05 : hist["FIXME"]["SSmue_Mjjbvetoplus"].Fill(tree.jj_mass, weight)
			    # W-W- -----  
			    if tree.Muon_charge[0] < 0 : 
			      hist["FIXME"]["SSmue_maxMuIsobvetominus"].Fill(isomax, weight)
			      if isomax < 0.05 : hist["FIXME"]["SSmue_Mjjbvetominus"].Fill(tree.jj_mass, weight)
			  # ======================
			  # btag  : ttW search
			  # ======================
                          if tree.CSV1 > 0.4 : 
			    if tree.Muon_pt[0] < 25. : hist["FIXME"]["SSmue_maxMuIso2jbtagPt1525"].Fill(isomax, weight)
                            if tree.Muon_pt[0] > 25. : 
			      hist["FIXME"]["SSmue_maxMuIso2jbtag"].Fill(isomax, weight)
                              if tree.Muon_pt[0] > 40. : hist["FIXME"]["SSmue_maxMuIso2jbtagPt40"].Fill(isomax, weight)
			      if isomax < 0.025   : hist["FIXME"]["SSmue_HTbtagPt25"].Fill(tree.HT30, weight)
			      if tree.HT30 > 350. : hist["FIXME"]["SSmue_maxMuIso2jbtagHT350"].Fill(isomax, weight)
			      
          # ========================
          # top bjj blnu plots -------------------------------------------
          # ========================
	  if tree.iSkim == 5 :	
	    nj, jet1, jet2 = 0, -1, -1  
	    for jet in range(0, tree.nJet) :
	      if tree.Jet_pt[jet] > 30. and abs( tree.Jet_eta[jet] ) < 2.5 :
	        if tree.Jet_muEF[jet] < 0.8 and tree.Jet_chEmEF[jet]  < 0.9 :
		 iveto = 0
		 if tree.Jet_pt[jet] < 50. and tree.Jet_puId[jet] == 4 : iveto = 1 
	         if iveto == 1 or tree.Jet_btagCSVV2[jet] < 0.4 :
		   nj = nj + 1
		   if nj == 1 : jet1 = jet
 	           if nj == 2 : jet2 = jet
            # at least 2 jet candidates found for W->jj
	    if jet2 > -1:  
	      m1, m2 = TLorentzVector(), TLorentzVector()
              m1.SetPtEtaPhiM(tree.Jet_pt[jet1], tree.Jet_eta[jet1], tree.Jet_phi[jet1], 1.)
              m2.SetPtEtaPhiM(tree.Jet_pt[jet2], tree.Jet_eta[jet2], tree.Jet_phi[jet2], 1.)
              mjj = (m1+m2).M()
              hist["FIXME"]["tt_Wqqmass"].Fill(tree.Wqq_mass, weight)	      
	      if abs(mjj-80.4) < 20. : 
	        jb1 , jb2 = tree.iCSV1, tree.iCSV2
	        if tree.CSV1 > 0.8 : 	        
		  m3 = TLorentzVector()
                  m3.SetPtEtaPhiM(tree.Jet_pt[jb1], tree.Jet_eta[jb1], tree.Jet_phi[jb1], 5.)
                  mjjb1 = (m1+m2+m3).M()
		  hist["FIXME"]["tt_Tqqb1"].Fill( mjjb1, weight)
                  if tree.CSV2 > 0.8 :
                    m3.SetPtEtaPhiM(tree.Jet_pt[jb2], tree.Jet_eta[jb2], tree.Jet_phi[jb2], 5.)
                    mjjb2 = (m1+m2+m3).M()
		    hist["FIXME"]["tt_Tqqb2"].Fill(mjjb2, weight)

	   #   if tree.Wqq_mass > 60. and tree.Wqq_mass < 100. :
	   #     hist["FIXME"]["tt_Tlvb1"].Fill(tree.Tlvb1_mass, weight)
           #     hist["FIXME"]["tt_Tlvb2"].Fill(tree.Tlvb2_mass, weight)
 	   #     hist["FIXME"]["tt_Tqqb1"].Fill(tree.Tqqb1_mass, weight)
 	   #     hist["FIXME"]["tt_Tqqb2"].Fill(tree.Tqqb2_mass, weight)
      
     # end loop =============================================

    return
