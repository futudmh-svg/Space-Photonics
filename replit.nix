{ pkgs }: {
  deps = [
    pkgs.python311
    pkgs.python311Packages.numpy
    pkgs.python311Packages.matplotlib
    pkgs.python311Packages.scipy
    pkgs.python311Packages.tqdm
    pkgs.git
  ];
}
