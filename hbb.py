import numpy as np

from pyquil import Program
from pyquil.gates import MEASURE, I, CNOT, X, H, Z
from pyquil.quil import address_qubits
from pyquil.quilatom import QubitPlaceholder
from pyquil.api import QVMConnection

qvm = QVMConnection(random_seed=1337)

def hbb():
	pass
