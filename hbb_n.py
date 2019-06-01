import numpy as np

from pyquil import Program
from pyquil.gates import MEASURE, I, CNOT, X, H, Z, T
from pyquil.quil import address_qubits
from pyquil.quilatom import QubitPlaceholder
from pyquil.api import QVMConnection

qvm = QVMConnection()

def hbb(n):
	pq = Program()

	''' Qubit assignments:
		0 = A (secret)
		1 = a (Alice's GHZ qubit)
		2 = b (Bob's GHZ qubit)
		3 = c (Charlie's GHZ qubit)
	'''

	''' Prepare secret. Results in
			|0> with prob 0.8535 and
			|1> with prob 0.1464.
	'''
	alice_measurement = pq.declare('alice_measurement', 'BIT', 2*n)
	bob_measurement = pq.declare('bob_measurement', 'BIT', n)
	ro = pq.declare('ro', 'BIT', n)

	for i in range(n):
		pq += H(i)
		pq += T(i)
		pq += H(i)

		# Prepare GHZ state
		pq += H(i+n)
		pq += CNOT(i+n, i+2*n)
		pq += CNOT(i+n, i+3*n)

		# Alice measures A and a in Bell basis
		pq += CNOT(i, i+n)
		pq += H(i)

		pq += MEASURE(i, alice_measurement[i*2])
		pq += MEASURE(i+n, alice_measurement[i*2+1])

		# Bob performs a measurement on his GHZ qubit in X basis
		pq += H(i+2*n)

		pq += MEASURE(i+2*n, bob_measurement[i])

		# Charlie reconstructs secret from Alice and Bob's measurements
		pq.if_then(alice_measurement[i*2+1], Program(X(i+3*n)), Program())
		pq.if_then(alice_measurement[i*2], Program(Z(i+3*n)), Program())
		pq.if_then(bob_measurement[i], Program(Z(i+3*n)), Program())

		# Reconstruction of state
		pq += MEASURE(i+3*n, ro[i])

	return pq


def simulate(n):
	pq = hbb(n)
	results = np.asarray(qvm.run(pq, trials=10000))
	prob_1 = np.sum(results) / float(results.size)
	print(f"Prob 0: {1 - prob_1}, prob 1: {prob_1}")


if __name__ == '__main__':
	n = 2
	simulate(n)
