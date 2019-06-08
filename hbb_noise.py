import numpy as np

from pyquil import Program, get_qc
from pyquil.api import QVM, QVMConnection
from pyquil.gates import MEASURE, CNOT, CZ, H, T
from pyquil.noise import add_decoherence_noise

from matplotlib import pyplot as plt

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

    pq = hbb(1000)
    compiled_pq = qc.compiler.quil_to_native_quil(pq)
    noiseless_results = np.asarray(qvm.run(compiled_pq, trials=1000))
    noiseless_prob_1 = np.sum(noiseless_results) / noiseless_results.size

    t1s = np.logspace(-7, -3, num=30)
    xdata = []
    ydata = []
    for t1 in t1s:
        # NOTE: 1.5 ratio roughly corresponds to ratio found on Rigetti QPUs.
        t2 = t1/1.5
        # NOTE: add_decoherence_noise() can only be called on programs with
        #       only RX, CZ, I, RZ gates.
        noisy = add_decoherence_noise(compiled_pq, T1=t1, T2=t2, ro_fidelity=0.95)

        results = np.asarray(qvm.run(noisy, trials=1000))
        prob_1 = np.sum(results) / float(results.size)
        print(f"T1 = {t1}, T2 = {t2}")
        print(f"Prob 0: {1 - prob_1}, prob 1: {prob_1}")
        xdata.append(t1)
        ydata.append(1 - prob_1)

    plt.plot(xdata, ydata, "o-")
    plt.xscale("log")
    #plt.ylim((0, 1))
    plt.ylabel("Prob. 0")
    plt.xlabel("T1 (s)")
    # Plot noiseless probability.
    plt.axhline(y=1 - noiseless_prob_1, color='r', linestyle='-')
    plt.title("Probability of 0 state vs. T1 for HTH secret")
    plt.show()


if __name__ == '__main__':
    run()


