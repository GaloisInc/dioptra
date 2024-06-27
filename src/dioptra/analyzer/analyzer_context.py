from openfhe import CryptoContext, Ciphertext

class AnalyzerContext:
    def __init__(self, crypto_context):# type: ignore
        self.crypto_context = crypto_context
        
    def __getattr__(self, name):# type: ignore
        try: 
            getattr(self.crypto_context, name)
        except AttributeError:
            raise Exception(f"Attribute {name} is not implemented in OpenFHE")   
        raise Exception(f"Attribute {name} is not implemented in Dioptra") 
    
    def EvalAdd(*args, **kwargs):# type: ignore
        print("EvalAdd!")
    def EvalNegate(self: CryptoContext, ciphertext: Ciphertext):# type: ignore
        print("EvalNegate!")

    def EvalMult(*args, **kwargs):# type: ignore
        print("EvalMult!")

    def EvalBootstrap(self: CryptoContext, ciphertext: Ciphertext, numIterations: int = 1, precision: int = 0):# type: ignore
        print("EvalBootstrap")

    def EvalDivide(self: CryptoContext, ciphertext: Ciphertext, a: float, b: float, degree: int):# type: ignore
        print("EvalDivide")

    def EvalSub(*args, **kwargs):# type: ignore
        print("EvalSub")

    def EvalSum(self: CryptoContext, ciphertext: Ciphertext, batchSize: int):# type: ignore
        print("EvalSum")