import numpy as np
import matplotlib.pyplot as plt
from grove.alpha.arbitrary_state import arbitrary_state

from pyquil import Program, get_qc
from pyquil.gates import MEASURE, CNOT, CZ, H
from pyquil.api._devices import list_lattices
from pyquil.quil import Pragma

# lattice_name = "Aspen-4-4Q-A"
lattice_name = "9q-generic-qvm"


def query_device(device_name) -> dict:
    """
    Try to query the device from QCS. Return the lattice dict if it exists, or
    or None otherwise.
    """
    lattices = list_lattices()
    if device_name in list(lattices.keys()):
        return lattices[device_name]
    return None


def hbb(lattice_name):
	pq = Program()
	pq += Pragma('INITIAL_REWIRING', ['"GREEDY"'])

	''' Qubit assignments:
			0 = A (secret)
			1 = a (Alice's GHZ secret)
			2 = b (Bob's GHZ secret)
			3 = c (Charlie's GHZ secret)
	'''
	device = query_device(lattice_name)
	if device is not None:
		A, a, b, c = device['qubits'].values()
	else:
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
	pq += MEASURE(c, ro[0])

	return pq

def create_secret(p0):
	coeff = np.asarray([np.sqrt(p0), np.sqrt(1.0 - p0)])
	return arbitrary_state.create_arbitrary_state(coeff)

def run():
	print(f"Running on lattice: {lattice_name}")
	qc = get_qc(lattice_name)

	expected = []
	actual = []

	# The below measures values when the creation of the secret is also subject to noise
	for p0 in np.arange(0.0, 1.05, 0.05):
		creation_pq = create_secret(p0)
		sharing_pq = hbb(lattice_name)
		pq = creation_pq + sharing_pq
		pq.wrap_in_numshots_loop(1000)

		pq_exec = qc.compile(pq)

		results = qc.run(pq_exec)
		p1 = np.sum(results) / float(results.size)

		expected.append(p0)
		actual.append(1 - p1)


	plt.figure()
	plt.plot(expected, expected, c='r')
	plt.scatter(expected, actual)
	plt.xlabel("expected prob of |0>")
	plt.ylabel("measured prob of |0>")
	plt.title("performance of noisy program on different secrets")

	#plt.show()
	plt.savefig("error_performance.png")

if __name__ == '__main__':
    run()
