{
  stdenv,
  fetchgit,
  autoconf,
  cmake,
  gmp,
  llvmPackages,
  ntl,
}:

let
  ompInput = if stdenv.isDarwin then [ llvmPackages.openmp ] else [];
in
stdenv.mkDerivation rec {
  pname = "openfhe-development";
  version = "1.1.4";

  src = fetchgit {
    url = "https://github.com/openfheorg/openfhe-development.git";
    rev = "v${version}";
    sha256 = "sha256-nyolaz+n0CbemGrUGJRRP7Ou7d1kR1RwauoXV8kCKTk=";
  };

  cmakeFlags = [
    "-DBUILD_UNITTESTS=OFF"
    "-DBUILD_EXAMPLES=OFF"
    "-DBUILD_BENCHMARKS=OFF"
    "-DWITH_NTL=ON"
  ];

  nativeBuildInputs = [
    autoconf
    cmake
    gmp
    ntl
  ] ++ ompInput;
  propagatedBuildInputs = [ gmp ntl ] ++ ompInput;
}
