import numpy as np

from pyquil import Program, get_qc
from pyquil.api import QVM, QVMConnection
from pyquil.gates import MEASURE, CNOT, CZ, H, T
from pyquil.noise import add_decoherence_noise

from pyquil.gates import RZ, RX
from numpy import pi

def hbb(num_trials):
    pq = Program()

    ''' Qubit assignments:
            0 = A (secret)
            1 = a (Alice's GHZ qubit)
            2 = b (Bob's GHZ qubit)
            3 = c (Charlie's GHZ qubit)
    '''
    A, a, b, c = 0, 1, 2, 3

    ''' Prepare secret. Results in
                    |0> with prob 0.8535 and
                    |1> with prob 0.1464.
    '''
    pq += H(A)
    pq += T(A)
    pq += H(A)

    # Prepare GHZ state
    pq += H(a)
    pq += CNOT(a, b)
    pq += CNOT(a, c)

    # Alice measures A and a in Bell basis
    pq += CNOT(A, a)
    pq += H(A)

    # Bob performs a measurement on his GHZ qubit in X basis
    pq += H(b)

    # Charlie reconstructs secret from Alice and Bob's measurements
    pq += CNOT(a, c)
    pq += CZ(A, c)
    pq += CZ(b, c)

    # Reconstruction of state
    ro = pq.declare('ro', 'BIT', 1)
    pq += MEASURE(c, ro[0])

    #pq.wrap_in_numshots_loop(num_trials)

    return pq


def run():
    qvm = QVMConnection()
    qc = get_qc("9q-generic-qvm")
    t1s = np.logspace(-6, -1, num=20)
    for t1 in t1s:
        t2 = t1/2
        pq = hbb(1000)
        # NOTE: add_decoherence_noise() can only be called on programs with
        #       only RX, CZ, I, RZ gates.
        compiled_pq = qc.compiler.quil_to_native_quil(pq)
        noisy = add_decoherence_noise(compiled_pq, T1=t1, T2=t2)

        results = np.asarray(qvm.run(noisy, trials=1000))
        prob_1 = np.sum(results) / float(results.size)
        print(f"T1 = {t1}, T2 = {t2}")
        print(f"Prob 0: {1 - prob_1}, prob 1: {prob_1}")


if __name__ == '__main__':
    run()


