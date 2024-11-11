import random
import time

from dioptra.utils.util import format_ns
from dioptra_examples.contexts import ckks_small1
from dioptra_examples.matrix_mult import matrix_mult
from dioptra_examples.schemes import CKKS

# Actually run a matrix multiply and time it.
xrows = 3
xcols = 3

yrows = xcols
ycols = 1
(cc, _, key_pair, _) = ckks_small1()

# encode and encrypt inputs labels, the inputs are generated at random
xs = [[[random.random()] for _ in range(xcols)] for _ in range(xrows)]
ys = [[[random.random()] for _ in range(ycols)] for _ in range(yrows)]

x_ct = [[[None] for _ in range(xcols)] for _ in range(xrows)]
for i in range(xrows):
    for j in range(xcols):
        x_pt = cc.MakeCKKSPackedPlaintext(xs[i][j])
        x_pt.SetLength(1)
        x_enc = cc.Encrypt(key_pair.publicKey, x_pt)
        x_ct[i][j] = x_enc

y_ct = [[[0] for _ in range(ycols)] for _ in range(yrows)]
for i in range(yrows):
    for j in range(ycols):
        y_pt = cc.MakeCKKSPackedPlaintext(ys[i][j])
        y_pt.SetLength(1)
        y_enc = cc.Encrypt(key_pair.publicKey, y_pt)
        y_ct[i][j] = y_enc

# time and run the program
start_ns = time.time_ns()
result_ct = matrix_mult(CKKS(), cc, x_ct, y_ct)
end_ns = time.time_ns()

# decrypt results
result = [[[random.random()] for _ in range(ycols)] for _ in range(xrows)]
for i in range(xrows):
    for j in range(ycols):
        result_dec = cc.Decrypt(key_pair.secretKey, result_ct[i][j])
        result_dec.SetLength(1)
        result[i][j] = result_dec.GetCKKSPackedValue()
    print(result[i])

print(f"Actual runtime: {format_ns(end_ns - start_ns)}")
