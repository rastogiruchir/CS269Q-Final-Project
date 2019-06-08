import numpy as np
import matplotlib.pyplot as plt
from grove.alpha.arbitrary_state import arbitrary_state

from pyquil import Program, get_qc
from pyquil.api import QVM, QVMConnection
from pyquil.gates import MEASURE, CNOT, CZ, H
from pyquil.noise import add_decoherence_noise

def hbb():
	pq = Program()

	''' Qubit assignments:
			0 = A (secret)
			1 = a (Alice's GHZ secret)
			2 = b (Bob's GHZ secret)
			3 = c (Charlie's GHZ secret)
	'''
	A, a, b, c = 0, 1, 2, 3

	# Prepare GHZ state
	pq += H(a)
	pq += CNOT(a, b)
	pq += CNOT(a, c)

	# Alice measures A and a in Bell basis
	pq += CNOT(A, a)
	pq += H(A)

	# Bob performs a measurement on his GHZ qubit in X basis
	pq += H(b)

	# Charlie reconstructs secrets from Alice and Bob's measurements
	pq += CNOT(a, c)
	pq += CZ(A, c)
	pq += CZ(b, c)

	# Reconstruct state
	ro = pq.declare('ro', 'BIT', 1)
	pq.define_noisy_readout(c, 0.9575, 0.9575)
	pq += MEASURE(c, ro[0])

	return pq

def create_secret(p0):
	coeff = np.asarray([np.sqrt(p0), np.sqrt(1.0 - p0)])
	return arbitrary_state.create_arbitrary_state(coeff)

def run():
	qvm = QVMConnection()
	qc = get_qc("9q-generic-qvm")

	t1 = 27.07 * 10**(-6)
	t2 = 21.43 * 10**(-6)

	expected = []
	actual = []

	# The below measures values when the creation of the secret is also subject to noise
	for p0 in np.arange(0.0, 1.05, 0.05):
		creation_pq = create_secret(p0)
		sharing_pq = hbb()
		pq = creation_pq + sharing_pq

		compiled_pq = qc.compiler.quil_to_native_quil(pq)
		noisy_pq = add_decoherence_noise(compiled_pq, T1=t1, T2=t2)

		results = np.asarray(qvm.run(noisy_pq, trials=1000))
		p1 = np.sum(results) / float(results.size)

		expected.append(p0)
		actual.append(1 - p1)


	plt.figure()
	plt.plot(expected, expected, c='r')
	plt.scatter(expected, actual)
	plt.xlabel("expected prob of |0>")
	plt.ylabel("measured prob of |0>")
	plt.title("performance of noisy program on different secrets")
	plt.savefig("error_performance.png")

if __name__ == '__main__':
    run()
