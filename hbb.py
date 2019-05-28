import numpy as np

from pyquil import Program
from pyquil.gates import MEASURE, I, CNOT, X, H, Z, T
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

	''' Prepare secret. Results in 
			|0> with prob 0.8535 and 
			|1> with prob 0.1464.
	'''
	pq += H(0)
	pq += T(0)
	pq += H(0)

	# Prepare GHZ state
	pq += H(1)
	pq += CNOT(1, 2)
	pq += CNOT(1, 3)

	# Alice measures A and a in Bell basis
	pq += CNOT(0, 1)
	pq += H(0)

	alice_measurement = pq.declare('alice_measurement', 'BIT', 2)
	pq += MEASURE(0, alice_measurement[0])
	pq += MEASURE(1, alice_measurement[1])

	# Bob performs a maesurement on his GHZ qubit in X basis
	pq += H(2)

	bob_measurement = pq.declare('bob_measurement', 'BIT', 1)
	pq += MEASURE(2, bob_measurement[0])

	# Charlie reconstructs secret from Alice and Bob's measurements
	pq.if_then(alice_measurement[1], Program(X(3)), Program())
	pq.if_then(alice_measurement[0], Program(Z(3)), Program())
	pq.if_then(bob_measurement[0], Program(Z(3)), Program())

	# Reconstruction of state
	ro = pq.declare('ro', 'BIT', 1)
	pq += MEASURE(3, ro[0])

	return pq


def simulate():
	pq = hbb()
	results = np.asarray(qvm.run(pq, trials=10000))
	prob_1 = np.sum(results) / float(results.size)
	print(f"Prob 0: {1 - prob_1}, prob 1: {prob_1}")


if __name__ == '__main__':
	simulate()


