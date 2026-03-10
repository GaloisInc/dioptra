from dioptra.estimate import dioptra_env_estimation
from dioptra.estimate.env import Environments
from dioptra.utils.measurement import BPS

@dioptra_env_estimation()
def env_example(envs: Environments):
  with envs.get_pke_ctx("client", "encrypt data") as client:
    keys = client.KeyGen()
    input_pt = client.ArbitraryPT()
    input_ct = client.Encrypt(keys.publicKey, input_pt)
    
  with envs.get_pke_ctx("server", "do computation") as server:
    output = server.EvalAdd(input_ct, input_ct)

  with envs.get_pke_ctx("client", "decrypt data") as client:
    client.Decrypt(keys.secretKey, output)

