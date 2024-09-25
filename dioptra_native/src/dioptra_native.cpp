#include"pybind11/pybind11.h"
#include"openfhe.h"

namespace py = pybind11;
using namespace lbcrypto;

inline size_t poly_size(Poly const& p) {
  assert(p.IsEmpty());
  return sizeof(p);
}

inline size_t native_poly_size(NativePoly const& p) {
  if(p.IsEmpty()) {
    return sizeof(p);
  }

  return p.GetLength() * sizeof(NativePoly::Integer) + sizeof(p);
}

inline size_t dcrt_poly_size(DCRTPoly const& elt) {
  size_t size = 0;
  size += sizeof(elt);
  for(NativePoly const& p : elt.GetAllElements()) {
    size += native_poly_size(p);
  }
  return size;
}

inline size_t dcrt_poly_vec_size(std::vector<DCRTPoly> const& vec) {
  size_t size = 0;
  for(DCRTPoly const& elt : vec) {
    size += dcrt_poly_size(elt);
  }
  return size;
}

size_t ciphertext_size(Ciphertext<DCRTPoly> const& ct) {
  return sizeof(*ct) + dcrt_poly_vec_size(ct->GetElements());
}

size_t plaintext_size(Plaintext const& pt) {
  return sizeof(*pt)
       + dcrt_poly_size(pt->GetElement<DCRTPoly>())
       + native_poly_size(pt->GetElement<NativePoly>())
       + poly_size(pt->GetElement<Poly>());
}

size_t eval_key_size(EvalKey<DCRTPoly> const& eval_key) {
  return sizeof(*eval_key)
       + dcrt_poly_vec_size(eval_key->GetAVector())
       + dcrt_poly_vec_size(eval_key->GetBVector());
}

size_t eval_key_vec_size(std::vector<EvalKey<DCRTPoly>> const& eval_keys) {
  size_t size = 0;
  for(auto const& ek : eval_keys) {
    size += eval_key_size(ek);
  }
  return size;  
}

PYBIND11_MODULE(dioptra_native, m) {
  m.doc() = "dioptra native module";
  m.def("ciphertext_size", &ciphertext_size, "Compute the size of a ciphertext");
  m.def("plaintext_size", &plaintext_size, "Compute the size of a plaintext");
}

