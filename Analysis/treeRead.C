{
  TTree* tree = (TTree*)_file0->Get("Events");
  std::cout << "Tree has " << tree->GetEntriesFast() << " events" << std::endl;
//  TH1F* h = new TH1F("h", "", 100, 0, 200);
//  tree->Project("h", "H_mass", "");
//  h->Draw();
}
