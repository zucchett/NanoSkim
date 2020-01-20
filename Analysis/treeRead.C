{
  TTree* tree = (TTree*)_file0->Get("Events");
  std::cout << "Tree has " << tree->GetEntriesFast() << " events";
}
