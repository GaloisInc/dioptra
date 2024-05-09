{
  stdenv,
  toPythonModule,
  fetchFromGitHub,
  cmake,
  python,
  python3,
  openfhe-development,
}:

toPythonModule (stdenv.mkDerivation rec {
  pname = "openfhe-python";
  version = "0.8.6";

  src = fetchFromGitHub {
    owner = "openfheorg";
    repo = pname;
    rev = "v${version}";
    sha256 = "sha256-X3a6iGoqf40ZZPj8H8TjJMjoY+rm0z270oqn2Bj/Iwo=";
  };

  nativeBuildInputs = [ cmake openfhe-development (python3.withPackages (ps: [ ps.pybind11 ])) ];

  # make install does the wrong thing, and this can't be changed via
  # cmakeFlags (the package's CMakeLists.txt computes the Python site-packages,
  # when we need to save to a canonical location for Nix Python packages).
  installPhase =
    let
      outDir = "$out/${python.sitePackages}";
    in
    ''
      runHook preInstall
      mkdir -p ${outDir}
      cp *.so ${outDir}
      runHook postInstall
    '';
})
