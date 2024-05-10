let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-23.11";
  pkgs = import nixpkgs { config = {}; overlays = []; };

  openfhe-development = pkgs.callPackage ./nix/openfhe-development.nix { };
  openfhe = pkgs.python3Packages.callPackage ./nix/openfhe-python.nix {
    openfhe-development = openfhe-development;
  };
  dioptra = pkgs.python3Packages.callPackage ./build.nix { };
in

pkgs.mkShellNoCC {
  packages = [
    (pkgs.python3.withPackages (ps: [ ps.mypy openfhe ]))
    dioptra
  ];
}
