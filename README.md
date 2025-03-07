# VLC Modulation Toolkit
**Summer 2019, WiroComm Group (IIIT Delhi)**

---

## 1. Overview
This toolkit provides a **user-centric platform** for simulating indoor **Visible Light Communication (VLC)** systems using the open-source **GNU Radio** framework. Users can switch between different modulation schemes (e.g., **OOK, DCO-OFDM, ACO-OFDM**) and configure parameters (like M-QAM order). The toolkit also computes **Bit Error Rate (BER)** to help evaluate performance. It can be readily adapted for **real-time experiments** by replacing file sinks/sources with **USRP** hardware.

This work was **published** in an 2019 IEEE International Conference on Advanced Networks and Telecommunications Systems (ANTS) – details and citation info below.

---

## 2. High-Level Implementation
- **Transmission Block**  
  1. Convert user input (text, audio, video) into a bitstream.  
  2. Encode and modulate (e.g., OOK, OFDM variants).  
  3. Save to a file (or send via USRP in real-time scenarios).

- **Receiver Block**  
  1. Receive the transmitted signal and optionally add **Gaussian noise**.  
  2. Demodulate and decode using a custom Python block.  
  3. Recover the original information and compute the **BER**.

Both blocks are built using **GNU Radio** flow graphs, with Python-based custom modules for the core signal processing.

---

## 3. Reference & Citation
The primary reference for this project is:

> **"Visible Light Communication Modulation Toolkit using Reconfigurable GNU Radio Framework,"**  
> S. Pandey, A. Singh, V. A. Bohara, and A. Srivastava,  
> in *2019 IEEE International Conference on Advanced Networks and Telecommunications Systems (ANTS)*, 2019.  
> [IEEE Xplore Link](https://ieeexplore.ieee.org/abstract/document/9118103)

**How to cite** (BibTeX format):
```bibtex
@INPROCEEDINGS{9118103,
  author={Pandey, Saaransh and Singh, Anand and Bohara, Vivek Ashok and Srivastava, Anand},
  booktitle={2019 IEEE International Conference on Advanced Networks and Telecommunications Systems (ANTS)}, 
  title={Visible Light Communication Modulation Toolkit using Reconfigurable GNU Radio Framework}, 
  year={2019},
  volume={},
  number={},
  pages={1-4},
  keywords={VLC;GNU Radio;OOK;DCO-OFDM;ACO-OFDM;BER},
  doi={10.1109/ANTS47819.2019.9118103}}

