#! /usr/bin/env python


sample = {
    'data_obs' : {
        'files' : [
            'SingleMuon_Run2016B_ver1-Nano1June2019_ver1-v1', 'SingleMuon_Run2016B_ver2-Nano1June2019_ver2-v1', 'SingleMuon_Run2016C-Nano1June2019-v1', 'SingleMuon_Run2016D-Nano1June2019-v1', 'SingleMuon_Run2016E-Nano1June2019-v1', 'SingleMuon_Run2016F-Nano1June2019-v1', 'SingleMuon_Run2016G-Nano1June2019-v1', 'SingleMuon_Run2016H-Nano1June2019-v1', \
            'SingleMuon_Run2017B-Nano1June2019-v1', 'SingleMuon_Run2017C-Nano1June2019-v1', 'SingleMuon_Run2017D-Nano1June2019-v1', 'SingleMuon_Run2017E-Nano1June2019-v1', 'SingleMuon_Run2017F-Nano1June2019-v1', \
            'SingleMuon_Run2018A-Nano1June2019-v1', 'SingleMuon_Run2018B-Nano1June2019-v1', 'SingleMuon_Run2018C-Nano1June2019-v1', 'SingleMuon_Run2018D-Nano1June2019-v1', \
            'SingleElectron_Run2016B_ver1-Nano1June2019_ver1-v1', 'SingleElectron_Run2016B_ver2-Nano1June2019_ver2-v1', 'SingleElectron_Run2016C-Nano1June2019-v1', 'SingleElectron_Run2016D-Nano1June2019-v1', 'SingleElectron_Run2016E-Nano1June2019-v1', 'SingleElectron_Run2016F-Nano1June2019-v1', 'SingleElectron_Run2016G-Nano1June2019-v1', 'SingleElectron_Run2016H-Nano1June2019-v1', \
            'SingleElectron_Run2017B-Nano1June2019-v1', 'SingleElectron_Run2017C-Nano1June2019-v1', 'SingleElectron_Run2017D-Nano1June2019-v1', 'SingleElectron_Run2017E-Nano1June2019-v1', 'SingleElectron_Run2017F-Nano1June2019-v1', \
            'EGamma_Run2018A-Nano1June2019-v1', 'EGamma_Run2018B-Nano1June2019-v1', 'EGamma_Run2018C-Nano1June2019-v1', 'EGamma_Run2018D-Nano1June2019-v1', \
        ],
        'fillcolor' : 0,
        'fillstyle' : 1,
        'linecolor' : 1,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "Data",
        'weight': 1.,
        'plot': True,
    },
    'DYJetsToLL' : {
        'files' : ['DYJetsToLL_M-50_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17', 'DYJetsToLL_M-50_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18', 'DYJetsToLL_M-10to50_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17', 'DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18'],
        'fillcolor' : 418,
        'fillstyle' : 1001,
        'linecolor' : 418,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "Z(ll) + jets",
        'weight': 1.,
        'plot': True,
    },
    'DYJetsToNuNu' : {
        'files' : ['DYJetsToNuNu'],
        'fillcolor' : 856,
        'fillstyle' : 1001,
        'linecolor' : 856,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "Z(#nu#nu) + jets",
        'weight': 1.,
        'plot': True,
    },
    'WJetsToLNu' : {
        'files' : ['WJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'WJetsToLNu_Pt-100To250_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'WJetsToLNu_Pt-250To400_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'WJetsToLNu_Pt-400To600_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'WJetsToLNu_Pt-600ToInf_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17', 'WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17', 'WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17', 'WJetsToLNu_0J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18', 'WJetsToLNu_1J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18', 'WJetsToLNu_2J_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18',],
        'fillcolor' : 881,
        'fillstyle' : 1001,
        'linecolor' : 882,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "W(l#nu) + jets",
        'weight': 1.,
        'plot': True,
    },
    'VGamma' : {
        'files' : ['WGToLNuG_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIFall17', 'WGToLNuG_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', 'ZGTo2LG_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17', 'ZGToLLG_01J_5f_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18',],
        'fillcolor' : 835,
        'fillstyle' : 1001,
        'linecolor' : 835,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "V#gamma + jets",
        'weight': 1.,
        'plot': True,
    },
    'TTbar' : {
        'files' : ['TTToHadronic_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIISummer16', 'TTToHadronic_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'TTToHadronic_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18', 'TTToSemiLeptonic_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIISummer16', 'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'TTToSemiLeptonic_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18', 'TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIISummer16', 'TTTo2L2Nu_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIIFall17', 'TTTo2L2Nu_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18'],
        'fillcolor' : 798,
        'fillstyle' : 1001,
        'linecolor' : 798,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "t#bar{t}",#, single t
        'weight': 1.,
        'plot': True,
    },
    'TTW' : {
        'files' : ['TTWJetsToLNu_TuneCUETP8M1_13TeV-amcatnloFXFX-madspin-pythia8_RunIISummer16', 'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIFall17', 'TTWJetsToLNu_TuneCP5_13TeV-amcatnloFXFX-madspin-pythia8_RunIIAutumn18'],
        'fillcolor' : 901,
        'fillstyle' : 1001,
        'linecolor' : 901,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "t#bar{t}+W",#, single t
        'weight': 1.,
        'plot': True,
    },
    'TTZ' : {
        'files' : ['TTZToLLNuNu_M-10_TuneCUETP8M1_13TeV-amcatnlo-pythia8_RunIISummer16', 'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'TTZToLLNuNu_M-10_TuneCP5_13TeV-amcatnlo-pythia8_RunIIAutumn18'],
        'fillcolor' : 902,
        'fillstyle' : 1001,
        'linecolor' : 902,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "t#bar{t}+Z",#, single t
        'weight': 1.,
        'plot': True,
    },
    'TTTT' : {
        'files' : ['TTTT_TuneCUETP8M2T4_13TeV-amcatnlo-pythia8_RunIISummer16', 'TTTT_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'TTTT_TuneCP5_13TeV-amcatnlo-pythia8_RunIIAutumn18'],
        'fillcolor' : 799,
        'fillstyle' : 1001,
        'linecolor' : 799,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "t#bar{t}t#bar{t}",#, single t
        'weight': 1.,
        'plot': True,
    },
    'ST' : {
        'files' : [
            'ST_s-channel_4f_hadronicDecays_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_RunIISummer16', 'ST_s-channel_4f_hadronicDecays_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'ST_s-channel_4f_hadronicDecays_TuneCP5_13TeV-madgraph-pythia8_RunIIAutumn18', \
            'ST_s-channel_4f_leptonDecays_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_RunIISummer16', 'ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'ST_s-channel_4f_leptonDecays_TuneCP5_13TeV-madgraph-pythia8_RunIIAutumn18', \
            'ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIISummer16', 'ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIIFall17', 'ST_t-channel_antitop_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8_RunIIAutumn18', \
            'ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIISummer16', 'ST_t-channel_top_4f_InclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIIFall17', 'ST_t-channel_top_4f_InclusiveDecays_TuneCP5_13TeV-powheg-madspin-pythia8_RunIIAutumn18',\
            'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIISummer16', 'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'ST_tW_antitop_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18', \
            'ST_tW_top_5f_inclusiveDecays_TuneCP5_PSweights_13TeV-powheg-pythia8_RunIISummer16', 'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'ST_tW_top_5f_inclusiveDecays_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18', \
        ],
        'fillcolor' : 801,
        'fillstyle' : 1001,
        'linecolor' : 801,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "t+X",
        'weight': 1.,
        'plot': True,
    },
    'WW' : {
        'files' : ['WWTo2L2Nu_13TeV-powheg_RunIISummer16', 'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'WWTo2L2Nu_NNPDF31_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18', 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8_RunIISummer16', 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8_RunIIFall17', 'WWTo2L2Nu_DoubleScattering_13TeV-pythia8_RunIIAutumn18'],
        'fillcolor' : 860-4,
        'fillstyle' : 1001,
        'linecolor' : 860-4,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "WW",
        'weight': 1.,
        'plot': True,
    },
    'WZ' : {
        'files' : [
            'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIISummer16', 'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIIFall17', 'WZTo1L1Nu2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIIAutumn18', \
            'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIISummer16', 'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIIFall17', 'WZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIIAutumn18', \
            'WZTo3LNu_TuneCUETP8M1_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17', 'WZTo3LNu_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18',\
        ],
        'fillcolor' : 860-2,
        'fillstyle' : 1001,
        'linecolor' : 860-2,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "WZ",
        'weight': 1.,
        'plot': True,
    },
    'ZZ' : {
        'files' : [
            'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIISummer16', 'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIIFall17', 'ZZTo2L2Q_13TeV_amcatnloFXFX_madspin_pythia8_RunIIAutumn18', \
            'ZZTo4L_13TeV-amcatnloFXFX-pythia8_RunIISummer16', 'ZZTo4L_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIFall17', 'ZZTo4L_TuneCP5_13TeV-amcatnloFXFX-pythia8_RunIIAutumn18', \
            'ZZTo4L_DoubleScattering_13TeV-pythia8_RunIISummer16', 'ZZTo4L_TuneCP5_DoubleScattering_13TeV-pythia8_RunIIFall17', 'ZZTo4L_TuneCP5_DoubleScattering_13TeV-pythia8_RunIIAutumn18', \
        ],
        'fillcolor' : 860-1,
        'fillstyle' : 1001,
        'linecolor' : 860-1,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "ZZ",
        'weight': 1.,
        'plot': True,
    },
    'WmWm' : {
        'files' : ['WmWmJJ_EWK_TuneCUETP8M1_13TeV-powheg-pythia8_RunIISummer16', 'WmWmJJ_EWK_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'WmWmJJ_EWK_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18'],
        'fillcolor' : 910,
        'fillstyle' : 1001,
        'linecolor' : 910,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "W^{-}W^{-}",
        'weight': 1.,
        'plot': True,
    },
    'WpWp' : {
        'files' : ['WpWpJJ_EWK-QCD_TuneCUETP8M1_13TeV-madgraph-pythia8_RunIISummer16', 'WpWpJJ_EWK-QCD_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'WpWpJJ_EWK-QCD_TuneCP5_13TeV-madgraph-pythia8_RunIIAutumn18',],
        'fillcolor' : 909,
        'fillstyle' : 1001,
        'linecolor' : 909,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "W^{+}W^{+}",
        'weight': 1.,
        'plot': True,
    },
    'VVV' : {
        'files' : [
            'WWW_4F_TuneCUETP8M1_13TeV-amcatnlo-pythia8_RunIISummer16', 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'WWW_4F_TuneCP5_13TeV-amcatnlo-pythia8_RunIIAutumn18', \
            'WWZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8_RunIISummer16', 'WWZ_4F_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'WWZ_TuneCP5_13TeV-amcatnlo-pythia8_RunIIAutumn18', \
            'WZG_TuneCUETP8M1_13TeV-amcatnlo-pythia8_RunIISummer16', 'WZG_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'WZG_TuneCP5_13TeV-amcatnlo-pythia8_RunIIAutumn18', \
            'WZZ_TuneCUETP8M1_13TeV-amcatnlo-pythia8_RunIISummer16', 'WZZ_TuneCP5_13TeV-amcatnlo-pythia8_RunIIFall17', 'WZZ_TuneCP5_13TeV-amcatnlo-pythia8_RunIIAutumn18', \
        ],
        'fillcolor' : 602,
        'fillstyle' : 1001,
        'linecolor' : 602,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "V^{+}V^{-}V^{#pm}",
        'weight': 1.,
        'plot': True,
    },
    'Higgs' : {
        'files' : [
            'GluGluHToBB_M125_13TeV_powheg_pythia8_RunIISummer16', 'GluGluHToBB_M-125_13TeV_powheg_MINLO_NNLOPS_pythia8_RunIIFall17', 'GluGluHToBB_M-125_13TeV_powheg_MINLO_NNLOPS_pythia8_RunIIAutumn18', \
            'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUgenV6_pythia8_RunIISummer16', 'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8_RunIIFall17', 'GluGluHToZZTo4L_M125_13TeV_powheg2_JHUGenV7011_pythia8_RunIIAutumn18', \
            'HWminusJ_HToWW_M125_13TeV_powheg_pythia8_RunIISummer16', 'HWminusJ_HToWW_M125_13TeV_powheg_pythia8_TuneCP5_RunIIFall17', 'HWminusJ_HToWW_M125_13TeV_powheg_jhugen724_pythia8_TuneCP5_RunIIAutumn18', \
            'HWplusJ_HToWW_M125_13TeV_powheg_pythia8_RunIISummer16', 'HWplusJ_HToWW_M125_13TeV_powheg_pythia8_TuneCP5_RunIIFall17', 'HWplusJ_HToWW_M125_13TeV_powheg_jhugen724_pythia8_TuneCP5_RunIIAutumn18', \
            'WminusHToTauTau_M125_13TeV_powheg_pythia8_RunIISummer16', 'WminusHToTauTau_M125_13TeV_powheg_pythia8_RunIIAutumn18', \
            'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_RunIISummer16', 'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_RunIIFall17', 'WminusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_RunIIAutumn18', \
            'WplusHToTauTau_M125_13TeV_powheg_pythia8_RunIISummer16', 'WplusHToTauTau_M125_13TeV_powheg_pythia8_RunIIFall17', 'WplusHToTauTau_M125_13TeV_powheg_pythia8_RunIIAutumn18', \
            'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_RunIISummer16', 'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_RunIIFall17', 'WplusH_HToBB_WToLNu_M125_13TeV_powheg_pythia8_RunIIAutumn18', \
            'ZHToTauTau_M125_13TeV_powheg_pythia8_RunIISummer16', 'ZHToTauTau_M125_13TeV_powheg_pythia8_RunIIFall17', 'ZHToTauTau_M125_13TeV_powheg_pythia8_RunIIAutumn18', \
            'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8_RunIISummer16', 'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8_RunIIFall17', 'ZH_HToBB_ZToLL_M125_13TeV_powheg_pythia8_RunIIAutumn18', \
            'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_RunIISummer16', 'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_RunIIFall17', 'ZH_HToBB_ZToNuNu_M125_13TeV_powheg_pythia8_RunIIAutumn18', \
            'HZJ_HToWW_M125_13TeV_powheg_jhugen714_pythia8_TuneCP5_RunIIFall17', 'HZJ_HToWW_M125_13TeV_powheg_jhugen714_pythia8_TuneCP5_RunIIAutumn18', \
            'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_RunIISummer16', 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'ttHToNonbb_M125_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18', \
            'ttHTobb_M125_13TeV_powheg_pythia8_RunIISummer16', 'ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8_RunIIFall17', 'ttHTobb_M125_TuneCP5_13TeV-powheg-pythia8_RunIIAutumn18', \
        ],
        'fillcolor' : 628,
        'fillstyle' : 1001,
        'linecolor' : 628,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "Higgs",
        'weight': 1.,
        'plot': True,
    },
    'QCD' : {
        'files' : [
#            'QCD_HT100to200_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT100to200_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT100to200_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
#            'QCD_HT200to300_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT200to300_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT200to300_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
#            'QCD_HT300to500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT300to500_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT300to500_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
            'QCD_HT500to700_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT500to700_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT500to700_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
            'QCD_HT700to1000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT700to1000_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT700to1000_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
            'QCD_HT1000to1500_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT1000to1500_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT1000to1500_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
            'QCD_HT1500to2000_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT1500to2000_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT1500to2000_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
            'QCD_HT2000toInf_TuneCUETP8M1_13TeV-madgraphMLM-pythia8_RunIISummer16', 'QCD_HT2000toInf_TuneCP5_13TeV-madgraph-pythia8_RunIIFall17', 'QCD_HT2000toInf_TuneCP5_13TeV-madgraphMLM-pythia8_RunIIAutumn18', \
        ],
        'fillcolor' : 921,
        'fillstyle' : 1001,
        'linecolor' : 921,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "multijet",
        'weight': 1.,
        'plot': True,
    },
    'tZq' : {
        'files' : ['tZq_ll_4f_13TeV-amcatnlo-pythia8_RunIISummer16', 'tZq_ll_4f_ckm_NLO_TuneCP5_PSweights_13TeV-amcatnlo-pythia8_RunIIFall17', 'tZq_ll_4f_ckm_NLO_TuneCP5_13TeV-madgraph-pythia8_RunIIAutumn18'],
        'fillcolor' : 629,
        'fillstyle' : 1001,
        'linecolor' : 623,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "t#rigtharrow Zq",
        'weight': 1.,
        'plot': True,
    },
    'ZToJPsiG' : {
        'files' : ['ZToJPsiGamma-TuneCUETP8M1_13TeV-pythia8_RunIISummer16', 'ZToJPsiGamma_TuneCP5_13TeV-pythia8_RunIIFall17', 'ZToJPsiGamma_TuneCP5_13TeV-pythia8_RunIIAutumn18'],
        'fillcolor' : 629,
        'fillstyle' : 1001,
        'linecolor' : 629,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "Z #rightarrow J/#Psi #gamma",
        'weight': 1.,
        'plot': True,
    },
    'HToJPsiG' : {
        'files' : ['HToJPsiG_ToMuMuG_allProdMode_M125_TuneCUETP8M1_13TeV_Pythia8_RunIISummer16',],
        'fillcolor' : 629,
        'fillstyle' : 1001,
        'linecolor' : 629,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "H #rightarrow J/#Psi #gamma",
        'weight': 1.,
        'plot': True,
    },
    
    'AllBkg' : {
        'files' : [],
        'fillcolor' : 856,
        'fillstyle' : 1001,
        'linecolor' : 856,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "All backgrounds",
        'weight': 1.,
        'plot': True,
    },
    
        
    # Dummy entry for background sum
    'BkgSum' : {
        'order' : 0,
        'files' : [],
        'fillcolor' : 1,
        'fillstyle' : 3003,
        'linecolor' : 1,
        'linewidth' : 2,
        'linestyle' : 1,
        'label' : "MC stat.",
        'weight': 1.,
        'plot': True,
    },
    
    'PreFit' : {
        'order' : 0,
        'files' : [],
        'fillcolor' : 1,
        'fillstyle' : 1,
        'linecolor' : 923,
        'linewidth' : 3,
        'linestyle' : 2,
        'label' : "Pre-fit",
        'weight': 1.,
        'plot': True,
    },
    

}

