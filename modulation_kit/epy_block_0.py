"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
import matplotlib.pyplot as plt
import scipy
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, string_len=1,mod_type = 3, interpolation = 5,m_qam=4):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Modulation Python Block',   # will show up in GRC
            in_sig=[np.uint8,np.float32],
            out_sig=[np.complex64,np.complex64,np.complex64]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.string_len = string_len
        self.set_history(2)    
        self.mod_type = mod_type 
        self.interpolation = interpolation
        self.set_min_output_buffer(2**20)
        self.m_qam = m_qam

    mapping_table = {
        (0,0) : -1 + 1j,
        (0,1) :  1 + 1j,
        (1,0) : -1 - 1j,
        (1,1) :  1 - 1j
    }

    mapping_table_8 = {
        (0,0,0) : -3+1j,
        (0,0,1) : -1+1j,
        (0,1,0) :  3+1j,
        (0,1,1) :  1+1j,
        (1,0,0) : -3-1j,
        (1,0,1) : -1-1j,
        (1,1,0) :  3-1j,
        (1,1,1) :  1-1j
    }

    mapping_table_16 = {
        (0,0,0,0) : -3+3j,
        (0,0,0,1) : -1+3j,
        (0,0,1,0) : -3+1j,
        (0,0,1,1) : -1+1j,
        (0,1,0,0) : -3-3j,
        (0,1,0,1) : -1-3j,
        (0,1,1,0) : -3-1j,
        (0,1,1,1) : -1-1j,
        (1,0,0,0) :  3+3j,
        (1,0,0,1) :  1+3j,
        (1,0,1,0) :  3+1j,
        (1,0,1,1) :  1+1j,
        (1,1,0,0) :  3-3j,
        (1,1,0,1) :  1-3j,
        (1,1,1,0) :  3-1j,
        (1,1,1,1) :  1-1j
    }

    demapping_table = {v : k for k, v in mapping_table.items()}

    demapping_table_8 = {v : k for k, v in mapping_table_8.items()}

    demapping_table_16 = {v : k for k, v in mapping_table_16.items()}

    def ofdm_config(self,bits_arr):
        m = np.log2(self.m_qam).astype(int)
        ##S/P
        rem = len(bits_arr)%m
        bits_arr = np.append(bits_arr,np.zeros(m-rem))
        bits = bits_arr.reshape((len(bits_arr)//m, m))            
        #print(bits_arr)
        ##QAM-Mod
        QAM = []
        if(self.m_qam == 4):
            QAM = np.array([self.mapping_table[tuple(b)] for b in bits])
        elif(self.m_qam == 8):
            QAM = np.array([self.mapping_table_8[tuple(b)] for b in bits])
        elif(self.m_qam == 16):
            QAM = np.array([self.mapping_table_16[tuple(b)] for b in bits])
        #print(QAM.shape)
        N = 64
        if(QAM.size < 62):
            dummy = np.zeros(62).astype(complex)
            if(self.m_qam == 4):
                dummy[:] = -1 + 1j
            elif(self.m_qam == 8):
                dummy[:] = -3 + 1j
            elif(self.m_qam == 16):
                dummy[:] = -3 - 3j
            dummy[:len(QAM)] = QAM
            QAM = dummy

        elif(QAM.size %((N/2)-1) !=0 ):
            val = ((N/2)-1) - (QAM.size %((N/2)-1))
            dummy = np.zeros(val).astype(complex)
            if(self.m_qam == 4):
                dummy[:] = -1 + 1j
            elif(self.m_qam == 8):
                dummy[:] = -3 + 1j
            elif(self.m_qam == 16):
                dummy[:] = -3 - 3j
            QAM = np.append(QAM,dummy)

        l = len(QAM)
        a = (int) ((N/2) - 1)
        b = (int) ( l/((N/2)-1) )
        inp = np.reshape(QAM, (a,b))
        return QAM,inp,a,b



    def work(self, input_items, output_items):
        
        data = []
        bits_arr = []
        final_out = []
        carrier_sig = input_items[1]
        cond = True
        
        if(input_items[0][0] == 0):
            data = input_items[0][1:1+self.string_len]
            bits_arr = np.zeros(self.string_len*8).astype(int)

            for i in range(0,len(data)):
                bits_arr[i*8:(i*8)+8] = np.unpackbits(np.uint8(data[i]))
            ##Generating-Sync-Bits-Block.
            sync_bits = [1, 1, 1, 1, 1, 0, 0, 1, 1, 0, 1, 0, 1]
            out_sync_bits = np.repeat(sync_bits,2)
            gen_sync_bits = np.tile(out_sync_bits,2).reshape(-1,)
            ##Data-Stream-Mux
            stream_out = np.append(gen_sync_bits,bits_arr)
            ##Manchester-Coding-Block
            manch_input = []
            for i in range(0,len(stream_out)):
                if stream_out[i] == 0:
                    manch_input.append(1)
                    manch_input.append(0)
                else:
                    manch_input.append(0)
                    manch_input.append(1)
            manch_input = np.array(manch_input)
            ##Repeat/Interpolation
            final_out = np.repeat(manch_input,self.interpolation)
        
        else:
            output_items[1][:] = -1 + 1j
            cond = False

        if(self.mod_type == 0 and cond):
            ##OOK
            ook_mod_sig = []
            ook_mod_sig = carrier_sig[:len(final_out)]*final_out
            output_items[0][:len(ook_mod_sig)] = ook_mod_sig
            
            ##tx-out-size
            output_items[2][0] = len(ook_mod_sig)
        
        elif(self.mod_type == 1 and cond):
            ##DCO-OFDM 
            N = 64
            QAM,inp,a,b = self.ofdm_config(bits_arr)
            tx_out = np.zeros((N,b)).astype(complex)
            ##tx_out-size
            output_items[2][0] = N*b
            ##DC-size
            output_items[2][1] = b

            DC = np.zeros(b).astype(complex)
            temp = []

            ##Herm-prop
            for i in range(0,b):
                x = inp[:,i]
                x1 = np.append([0],x)
                x2 = np.append([0],np.flip(np.conj(x1)))
                x_herm = np.append(x1,x2)
                x2 = np.fft.ifft(x_herm,64)
                DC[i] = -np.min(x2)
                output_items[2][2+i] = DC[i] ##storing DC values.
                x_tx = x2 + DC[i]
                tx_out[:,i] = x_tx

            tx_out = tx_out.reshape((-1,))
            
            output_items[0][:len(tx_out)] = tx_out
            output_items[1][:len(QAM)] = QAM
            output_items[1][len(QAM):] = -1 + 1j

        
        elif(self.mod_type == 2 and cond):
            ##ACO-OFDM
            N = 124
            QAM,inp,a,b = self.ofdm_config(bits_arr)
            tx_out = np.zeros((N,b)).astype(complex)
            ##tx_out-size
            output_items[2][0] = N*b
            
            ##Herm-prop
            for i in range(0,b):
                x = inp[:,i]
                x_bar = np.append(x,np.flip(np.conj(x)))
                t = np.zeros(2*x_bar.size).astype(complex)
                t[1::2] = x_bar
                x_tx = np.fft.ifft(t)
                tx_out[:,i] = x_tx
            print(tx_out.shape)
            tx_out = tx_out.reshape((-1,))
            
            output_items[0][:len(tx_out)] = tx_out
            output_items[1][:len(QAM)] = QAM
            output_items[1][len(QAM):] = -1 + 1j

        elif(self.mod_type >= 3):
            print("Wrong input.")

        
        #print(output_items[0][output_items[0] >= 0].size)
        return len(output_items)
