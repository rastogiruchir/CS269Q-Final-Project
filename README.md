# CS269Q Final Project
`hbb.py` is the initial implementation of the HBB protocol according to the Hillery et al. paper.

`hbb_errors_different_states.py` and `hbb_errors_different_states_qcs.py` were used to measure the performance of a noisy QVM and a QPU on different secrets.

`hbb_n.py` implements the HBB protocol for N-qubit secrets.

`hbb_noise.py` was used to measure the performance of the HBB protocol across a variety of T1/T2 coherence values on a noisy QVM.

`hbb_qcs.py` implements our version of the HBB protocol using controlled gates to reconstruct the secret and was used to measure the performance of the HBB protocol on a QPU.
