#! /usr/bin/env python

import os, multiprocessing, math
from array import array
from ROOT import TFile, TTree, TH1, TLorentzVector, TObject

########## SAMPLES ##########
data = ["data_obs"]
back = ["Higgs", "WmWm", "WpWp", "VVV", "ZZ", "WZ", "WW", "TTTT", "TTZ", "TTW", "ST", "TTbar", "VGamma", "WJetsToLNu", "DYJetsToLL", "QCD"]
sign = []
variables = ["iSkim", "Z_mass", "Z_pt", "Z_Muonpt1", "Z_HT", "H_mass",\
             "Jpsi_mass", "Jpsi_massPt50", "Jpsi_massHT", "Jpsi_HT",\
             "Mue_mass", "Mue_HT", "Mue_CSVmax", "Mue_nj30",\
             "ZW_MTWmmm","ZW_MTWmme","ZW_MTWeem","ZW_Mmm3mu", "ZW_Mmm2me", "ZW_Mee2em", "ZW_nj30", "ZW_HT",\
             "mu3_maxMuIso" ,"mu3_HT", "mu3_mMin" , "mu3_CSVmax", "mu3_maxMuIsoCSV","mu3_maxMuIsoCSVpt25" ,"mu3_maxMuIsoCSVpt40",\
             "e2mu_maxMuIso","e2mu_HT","e2mu_mMin","e2mu_CSVmax","e2mu_maxMuIsoCSV","e2mu_maxMuIsoCSVpt25","e2mu_maxMuIsoCSVpt40",\
             "SSmu_maxMuIso","SSmu_HT", "SSmu_nj30","SSmu_maxMuIsoIPlow", "SSmu_maxMuIso2j", "SSmu_maxMuIsoHT200", "SSmu_CSVmax", \
             "SSmu_maxMuIso2jPt1525", "SSmu_maxMuIso2jPt2540", "SSmu_maxMuIso2jPt25", "SSmu_maxMuIso2jPt40", \
             "SSmu_maxMuIso2jbveto" , "SSmu_maxMuIso2jbtag"  , "SSmu_maxMuIso2jbtagPt40"]
categories = ["FIXME", "Z2mCR"]
########## ######## ##########



# Loop on events
def loop(hist, tree, red):
    for event in range(0, tree.GetEntries(), red):
        tree.GetEntry(event)
        weight = tree.eventWeightLumi * red # per-event weight that also accounts for a reduction factor to run faster on MC
        
        hist["FIXME"]["iSkim"].Fill(tree.iSkim, weight)
        if tree.isSingleMuIsoTrigger and tree.nMuon > 0 and tree.Muon_mediumId[0] > 0 and abs(tree.Muon_dz[0]) < 0.5 :
          # check electrons -------------------------------------
          ieleveto = 0
          for je in range(0, tree.nElectron) :
             if abs(tree.Electron_dz[je]) < 0.5   and tree.Electron_cutBased[je] > 2 :
               if abs(tree.Electron_pt[je]) > 15. and tree.Electron_pfRelIso03_all[je] < 0.15 : ieleveto = 1
          # J/psi plots -----------------------------------------          
          if tree.nMuon == 2 and  tree.Muon_mediumId[1] > 0 and abs(tree.Muon_dz[1]) < 0.5  :
             m1, m2 = TLorentzVector(), TLorentzVector() 
             m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
             m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
             m12 = (m1+m2).M()
             hist["FIXME"]["Jpsi_mass"].Fill(m12, weight)
             if tree.Muon_pt[0] > 50:
               hist["FIXME"]["Jpsi_massPt50"].Fill(m12, weight)
               if abs( m12-3.096) < 0.100 : hist["FIXME"]["Jpsi_HT"].Fill(tree.HT30, weight)
               if tree.HT30 > 200. : hist["FIXME"]["Jpsi_massHT"].Fill(m12, weight)
          # Higgs, ZZ plots ------
          if tree.nMuon == 4 :
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
              hist["FIXME"]["H_mass"].Fill(m4mu, weight)
          if abs(tree.Muon_dxy[0]) < 0.0050 :
            # Z plots -------------------------------------------
            if tree.iSkim==1  and tree.Muon_charge[0]*tree.Muon_charge[1]<0 and tree.Muon_pfRelIso03_all[0]<0.10 and tree.Muon_pfRelIso03_all[1]<0.10 :                                  
              hist["FIXME"]["Z_mass"].Fill(tree.Z_mass, weight)
              if tree.Z_mass > 70 and tree.Z_mass < 110 :
                hist["FIXME"]["Z_pt"].Fill(tree.Z_pt, weight)
                hist["FIXME"]["Z_Muonpt1"].Fill(tree.Muon_pt[0], weight)
                hist["FIXME"]["Z_HT"].Fill(tree.HT30, weight)
            # WZ plots: Z->mm, W->munu case -----------
            if tree.nMuon == 3 and ieleveto == 0 and tree.Muon_pt[2] > 20.:
              m1, m2 = TLorentzVector(), TLorentzVector()
              jmu1Z = -1
              jmu2Z = -1
              mDZmin = 9999.
              mZ = 0.
              for jmu1 in range(0, tree.nMuon-1) :
                if tree.Muon_mediumId[jmu1] > 0 and tree.Muon_pfRelIso03_all[jmu1] < 0.15 : 
                  if abs( tree.Muon_dz[jmu1])  < 0.5  and abs( tree.Muon_dxy[jmu1]) < 0.0060 : 
                    for jmu2 in range(jmu1+1, tree.nMuon) :     
                      if tree.Muon_charge[jmu1]*tree.Muon_charge[jmu2]<0 and tree.Muon_pt[jmu2] > 20. :
                        if tree.Muon_mediumId[jmu2] > 0 and tree.Muon_pfRelIso03_all[jmu2] < 0.15 : 
                          if abs( tree.Muon_dz[jmu2])  < 0.5  and abs( tree.Muon_dxy[jmu2]) < 0.0060 :
                            m1.SetPtEtaPhiM(tree.Muon_pt[jmu1], tree.Muon_eta[jmu1], tree.Muon_phi[jmu1], tree.Muon_mass[jmu1])
                            m2.SetPtEtaPhiM(tree.Muon_pt[jmu2], tree.Muon_eta[jmu2], tree.Muon_phi[jmu2], tree.Muon_mass[jmu2])
                            m2mu = (m1+m2).M()
                            mDZ = abs(m2mu - 91.1)
                            if mDZ < mDZmin :
                              mDZmin = mDZ
                              jmu1Z = jmu1
                              jmu2Z = jmu2
                              mZ = m2mu
              if mZ > 0. : hist["FIXME"]["ZW_Mmm3mu"].Fill(mZ, weight)                
              if abs( mZ - 91.1) < 15. :                        
                for jmuW in range(0, tree.nMuon) :
                  iveto = 0 
                  if jmuW == jmu1Z or jmuW == jmu2Z : iveto = 1
                  if iveto == 0 and tree.Muon_mediumId[jmuW] > 0 and tree.Muon_pfRelIso03_all[jmuW] < 0.15 and tree.Muon_pt[jmuW] > 20. :
                    m1.SetPtEtaPhiM(tree.Muon_pt[jmuW], 0., tree.Muon_phi[jmuW], tree.Muon_mass[jmuW])
                    m2.SetPtEtaPhiM(tree.MET_pt, 0., tree.MET_phi, 0.)
                    mTW = (m1+m2).M()
                    hist["FIXME"]["ZW_MTWmmm"].Fill(mTW, weight)
                    hist["FIXME"]["ZW_nj30"].Fill(tree.nj30, weight)
                    hist["FIXME"]["ZW_HT"].Fill(tree.HT30, weight)
            # WZ plots: Z->mm, W->enu case -----------
            if tree.nMuon == 2 and tree.nElectron == 1 and tree.Electron_pt[0] > 25. and abs(tree.Electron_eta[0]) < 2.1 :
              if tree.Electron_cutBased[0] > 2  and tree.Electron_pfRelIso03_all[0] < 0.05 :
                if tree.Muon_charge[0]*tree.Muon_charge[1]<0 and tree.Muon_pt[1] > 20. :
                  if tree.Muon_mediumId[0] > 0 and tree.Muon_pfRelIso03_all[0] < 0.15 : 
                    if tree.Muon_mediumId[1] > 0 and tree.Muon_pfRelIso03_all[1] < 0.15 : 
                      m1, m2 = TLorentzVector(), TLorentzVector()
                      m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                      m2.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
                      m2mu = (m1+m2).M()
                      hist["FIXME"]["ZW_Mmm2me"].Fill(m2mu, weight) 
                      if abs( m2mu - 91.1) < 15 :
                        m1.SetPtEtaPhiM(tree.Electron_pt[0], 0., tree.Electron_phi[0], tree.Electron_mass[0])
                        m2.SetPtEtaPhiM(tree.MET_pt, 0., tree.MET_phi, 0.)
                        mTW = (m1+m2).M()
                        hist["FIXME"]["ZW_MTWmme"].Fill(mTW, weight)
            # WZ plots: Z->ee, W->mu nu case -----------
            if tree.nMuon == 1 and tree.nElectron == 2 :
              if tree.Muon_mediumId[0] > 0 and tree.Muon_pfRelIso03_all[0] and tree.Muon_pt[0] > 20. :
                if tree.Electron_charge[0]*tree.Electron_charge[1]<0 and tree.Electron_pt[1] > 20. :
                  if tree.Electron_cutBased[0] > 2  and tree.Electron_pfRelIso03_all[0] < 0.1 : 
                    if tree.Electron_cutBased[1] > 2 and tree.Electron_pfRelIso03_all[0] < 0.1 : 
                      m1, m2 = TLorentzVector(), TLorentzVector()
                      m1.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])
                      m2.SetPtEtaPhiM(tree.Electron_pt[1], tree.Electron_eta[1], tree.Electron_phi[1], tree.Electron_mass[1])
                      m2e = (m1+m2).M()
                      hist["FIXME"]["ZW_Mee2em"].Fill(m2e, weight)
                      if abs( m2e - 91.1) < 15 :                                
                        m1.SetPtEtaPhiM(tree.Muon_pt[0], 0., tree.Muon_phi[0], tree.Muon_mass[0])
                        m2.SetPtEtaPhiM(tree.MET_pt, 0., tree.MET_phi, 0.)
                        mTW = (m1+m2).M()
                        hist["FIXME"]["ZW_MTWeem"].Fill(mTW, weight)                               
            # 3 muons plots -------------------------------------------
            if tree.nMuon == 3 and  tree.Muon_pt[2] > 15.  and  tree.Muon_mediumId[1] > 0 and tree.Muon_mediumId[2] > 0 :
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
                   isomax = tree.Muon_pfRelIso03_all[0]
                   if  tree.Muon_pfRelIso03_all[1] > isomax : isomax = tree.Muon_pfRelIso03_all[1]
                   if  tree.Muon_pfRelIso03_all[2] > isomax : isomax = tree.Muon_pfRelIso03_all[2]
                   hist["FIXME"]["mu3_maxMuIso"].Fill(isomax, weight)  
                   hist["FIXME"]["mu3_HT"].Fill(tree.HT30, weight) 
                   hist["FIXME"]["mu3_CSVmax"].Fill(tree.CSV1, weight) 
                   if tree.HT30 > 100. and  tree.CSV1 > 0.4  : 
                     hist["FIXME"]["mu3_maxMuIsoCSV"].Fill(isomax, weight)
                     if tree.Muon_pt[2] > 25. :  hist["FIXME"]["mu3_maxMuIsoCSVpt25"].Fill(isomax, weight)
                     if tree.Muon_pt[2] > 40. :  hist["FIXME"]["mu3_maxMuIsoCSVpt40"].Fill(isomax, weight)                              
            # mu-e plots -------------------------------------------
            if tree.nElectron > 0 and tree.Muon_pt[0] > 25. and tree.Muon_charge[0]*tree.Electron_charge[0]<0 :
               if tree.Electron_cutBased[0] > 2 and tree.Electron_pt[0] > 20. :
                 if tree.Muon_pfRelIso03_all[0]<0.10 and tree.Electron_pfRelIso03_all[0]<0.10 :
                   etamax = abs(tree.Muon_eta[0] )                             
                   if  abs(tree.Electron_eta[0] ) > etamax : etamax = abs(tree.Electron_eta[0] )
                   if etamax < 2.1 :                           
                     m1, m2 = TLorentzVector(), TLorentzVector()
                     m1.SetPtEtaPhiM(tree.Muon_pt[0], tree.Muon_eta[0], tree.Muon_phi[0], tree.Muon_mass[0])
                     m2.SetPtEtaPhiM(tree.Electron_pt[0], tree.Electron_eta[0], tree.Electron_phi[0], tree.Electron_mass[0])
                     m12 = (m1+m2).M()
                     hist["FIXME"]["Mue_mass"].Fill(m12, weight)
                     hist["FIXME"]["Mue_HT"].Fill(tree.HT30, weight)
                     hist["FIXME"]["Mue_nj30"].Fill(tree.nj30, weight)  
                     hist["FIXME"]["Mue_CSVmax"].Fill(tree.CSV1, weight)  
                     iZveto = 0 
                     if m12 > 50. and m12 < 90. : iZveto = 1
                     # 2mu -e plots --------------------------------------
                     if tree.nMuon == 2 and tree.Muon_pt[1] > 15. and abs(tree.Muon_eta[1] ) < 2.1 :
                       m3 = TLorentzVector()
                       m3.SetPtEtaPhiM(tree.Muon_pt[1], tree.Muon_eta[1], tree.Muon_phi[1], tree.Muon_mass[1])
                       m13 = (m1+m3).M()
                       m23 = (m2+m3).M()
                       mMin = m12
                       if m13 < mMin : mMin = m13
                       if m23 < mMin : mMin = m23
                       hist["FIXME"]["e2mu_mMin"].Fill(mMin, weight)
                       if abs(m13-91.1) < 15. and tree.Muon_charge[0]*tree.Muon_charge[1]<0 : iZveto = 1
                       if mMin > 15. and iZveto == 0:
                         isomax = tree.Muon_pfRelIso03_all[0]
                         if  tree.Muon_pfRelIso03_all[1] > isomax : isomax = tree.Muon_pfRelIso03_all[1]                                 
                         hist["FIXME"]["e2mu_maxMuIso"].Fill(isomax, weight) 
                         hist["FIXME"]["e2mu_HT"].Fill(tree.HT30, weight)
                         hist["FIXME"]["e2mu_CSVmax"].Fill(tree.CSV1, weight)  
                         if tree.HT30 > 100. and  tree.CSV1 > 0.4 : 
                           hist["FIXME"]["e2mu_maxMuIsoCSV"].Fill(isomax, weight) 
                           if tree.Muon_pt[1] > 25. :  hist["FIXME"]["e2mu_maxMuIsoCSVpt25"].Fill(isomax, weight)
                           if tree.Muon_pt[1] > 40. :  hist["FIXME"]["e2mu_maxMuIsoCSVpt40"].Fill(isomax, weight)
            # SS muon plots -------------------------------------------
            if tree.nMuon == 2  and ieleveto == 0 and tree.Muon_mediumId[1] > 0  and tree.Muon_pt[1] > 15. :
              etamax = abs(tree.Muon_eta[0] )
              if  abs(tree.Muon_eta[1] ) > etamax : etamax = abs(tree.Muon_eta[1] )
              if tree.Muon_charge[0]*tree.Muon_charge[1] > 0 and etamax < 2.1 :
                isomax = tree.Muon_pfRelIso03_all[0]
                if  tree.Muon_pfRelIso03_all[1] > isomax : isomax = tree.Muon_pfRelIso03_all[1]                        
                hist["FIXME"]["SSmu_maxMuIso"].Fill(isomax, weight)
                if abs(tree.Muon_dz[1]) < 0.5 and abs(tree.Muon_dxy[1]) < 0.0050 :
                  hist["FIXME"]["SSmu_maxMuIsoIPlow"].Fill(isomax, weight)
                  hist["FIXME"]["SSmu_nj30"].Fill(tree.nj30, weight)
                  if tree.nj30 > 1 : 
                    hist["FIXME"]["SSmu_HT"].Fill(tree.HT30, weight)
                    if tree.HT30 > 100 : 
                      hist["FIXME"]["SSmu_maxMuIso2j"].Fill(isomax, weight)
                      if tree.HT30 > 200 :
                        hist["FIXME"]["SSmu_maxMuIsoHT200"].Fill(isomax, weight)
                        hist["FIXME"]["SSmu_CSVmax"].Fill(tree.CSV1, weight)
                        if tree.Muon_pt[1] < 25. : hist["FIXME"]["SSmu_maxMuIso2jPt1525"].Fill(isomax, weight)
                        if tree.Muon_pt[1] > 25. and tree.Muon_pt[1] < 40.: hist["FIXME"]["SSmu_maxMuIso2jPt2540"].Fill(isomax, weight)
                        if tree.Muon_pt[1] > 25. : hist["FIXME"]["SSmu_maxMuIso2jPt25"].Fill(isomax, weight)
                        if tree.Muon_pt[1] > 40. : hist["FIXME"]["SSmu_maxMuIso2jPt40"].Fill(isomax, weight)
                        if tree.Muon_pt[1] > 25. :
                          if tree.CSV1 < 0.4 :  hist["FIXME"]["SSmu_maxMuIso2jbveto"].Fill(isomax, weight)
                          if tree.CSV1 > 0.4 : 
                            hist["FIXME"]["SSmu_maxMuIso2jbtag"].Fill(isomax, weight)
                            if tree.Muon_pt[1] > 40. : hist["FIXME"]["SSmu_maxMuIso2jbtagPt40"].Fill(isomax, weight)
                 # end loop =============================================

    return
