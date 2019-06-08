import numpy as np

from pyquil import Program
from pyquil.gates import MEASURE, I, CNOT, X, H, T, S, CZ
from pyquil.quil import address_qubits
from pyquil.quilatom import QubitPlaceholder
from pyquil.api import QVMConnection

qvm = QVMConnection()

def hbb():
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

    return pq

def add_tomography(qubit_to_measure, basis):
	pq = Program()
	ro = pq.declare('ro', 'BIT', 1)

	if basis == "X":
		pq += H(qubit_to_measure)
	elif basis == "Y":
		pq += Program(S(qubit_to_measure)).dagger()
		pq += H(qubit_to_measure)

	pq += MEASURE(qubit_to_measure, ro)

	return pq


def run():
	pq = hbb()
	x_results = np.asarray(qvm.run(pq + add_tomography(3, "X"), trials=1000))
	y_results = np.asarray(qvm.run(pq + add_tomography(3, "Y"), trials=1000))
	z_results = np.asarray(qvm.run(pq + add_tomography(3, "Z"), trials=1000))

	x_pos = np.sum(x_results)
	x_neg = x_results.size - x_pos
	y_pos = np.sum(y_results)
	y_neg = y_results.size - y_pos
	z_pos = np.sum(z_results)
	z_neg = z_results.size - z_pos

	r_x = -(x_pos - x_neg) / (x_pos + x_neg)
	r_y = -(y_pos - y_neg) / (y_pos + y_neg)
	r_z = -(z_pos - z_neg) / (z_pos + z_neg)

	# r = np.asarray([r_x, r_y, r_z])
	# assert (np.linalg.norm(r) <= 1.0)

	PX = np.asarray([[0, 1], [1, 0]])
	PY = np.asarray([[0, -1j], [1j, 0]])
	PZ = np.asarray([[1, 0], [0, -1]])

	rho = 0.5 * (np.ones(2) + r_x * PX + r_y * PY + r_z * PZ)
	expected = 


if __name__ == '__main__':
	run()