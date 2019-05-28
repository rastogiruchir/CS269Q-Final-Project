import numpy as np

from pyquil import Program, get_qc
from pyquil.gates import MEASURE, I, CNOT, CZ, X, H, Z, T
from pyquil.quil import address_qubits
from pyquil.quilatom import QubitPlaceholder
from pyquil.api import QVM, QVMConnection
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


def hbb(lattice_name, num_trials):
	pq = Program()
	pq += Pragma('INITIAL_REWIRING', ['"GREEDY"'])

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
	device = query_device(lattice_name)
	
	if device is not None:
		A, a, b, c = device['qubits'].values()
	else:
		A, a, b, c = 0, 1, 2, 3

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

	pq.wrap_in_numshots_loop(num_trials)

	return pq


def run():
	print(f"Running on lattice: {lattice_name}")
	qc = get_qc(lattice_name)
	pq = hbb(lattice_name, 1000)
	compiled_pq = qc.compile(pq)
	results = qc.run(compiled_pq)

	prob_1 = np.sum(results) / float(results.size)
	print(f"Prob 0: {1 - prob_1}, prob 1: {prob_1}")


if __name__ == '__main__':
	run()


