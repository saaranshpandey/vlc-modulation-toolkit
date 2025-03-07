"""
Embedded Python Blocks:

Each time this file is saved, GRC will instantiate the first class it finds
to get ports and parameters of your block. The arguments to __init__  will
be the parameters. All of them are required to have default values!
"""

import numpy as np
from gnuradio import gr


class blk(gr.sync_block):  # other base classes are basic_block, decim_block, interp_block
    """Embedded Python Block example - a simple multiply const"""

    def __init__(self, str_len=1,mod_type=3,interpolation=5,m_qam = 4):  # only default arguments here
        """arguments to this function show up as parameters in GRC"""
        gr.sync_block.__init__(
            self,
            name='Demod Python Block',   # will show up in GRC
            in_sig=[np.complex64,np.complex64,np.complex64,np.complex64],
            out_sig=[np.complex64]
        )
        # if an attribute with the same name as a parameter is found,
        # a callback is registered (properties work, too).
        self.str_len = str_len
        self.mod_type = mod_type
        self.interpolation = interpolation
        self.set_history(2)
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

    def Demapping(self,QAM):
    # array of possible constellation points
        constellation = []
        if(self.m_qam == 4):
            constellation = np.array([x for x in self.demapping_table.keys()])
        elif(self.m_qam == 8):
            constellation = np.array([x for x in self.demapping_table_8.keys()])
        elif(self.m_qam == 16):
            constellation = np.array([x for x in self.demapping_table_16.keys()])
        
        # calculate distance of each RX point to each possible point
        dists = abs(QAM.reshape((-1,1)) - constellation.reshape((1,-1)))
        
        # for each element in QAM, choose the index in constellation 
        # that belongs to the nearest constellation point
        const_index = dists.argmin(axis=1)
        
        # get back the real constellation point
        hardDecision = constellation[const_index]

        # transform the constellation point into the bit groups
        if(self.m_qam == 4):
            return np.vstack([self.demapping_table[C] for C in hardDecision]), hardDecision
        elif(self.m_qam == 8):
            return np.vstack([self.demapping_table_8[C] for C in hardDecision]), hardDecision
        elif(self.m_qam == 16):
            return np.vstack([self.demapping_table_16[C] for C in hardDecision]), hardDecision
            

    def print_msg(self, str_final):
        #print(str_final)
        msg = ""
        for a_2 in range(0,len(str_final),8):
            t = ''.join(map(str,(str_final[a_2:a_2+8])))
            msg=msg+chr(int(t,2))
    
        print("Message: ",msg) 

    def calc_BER_OOK(self,tx_out,rx_final):
        ##OOK
        for i in range(0,len(tx_out)):
            if(np.absolute(tx_out[i].real)> 0):
                tx_out[i] = 1
            else:
                tx_out[i] = 0
        demod_out = tx_out.real
        ##Reverse of Up-Sample
        factor = 5
        rev_upsamp_out = demod_out[::factor]
        ##Manchester-Decoding
        manch_decode = []
        if(rev_upsamp_out.size % 2!=0):
            rev_upsamp_out = rev_upsamp_out[:-1]
    
        for i in range(0,len(rev_upsamp_out),2):
            if(rev_upsamp_out[i] == 0 and rev_upsamp_out[i+1] == 1):
                manch_decode.append(1)
            else: 
                manch_decode.append(0)
        manch_decode = np.array(manch_decode)
        str_final = manch_decode[52:]
        ##BER
        BER = (( (str_final!=rx_final).sum().astype(float) ) / str_final.size)
        print('BER: ', BER)

    def calc_BER_DCO_OFDM(self,tx_out,rx_final,DC):
        ##DCO-OFDM
        data = tx_out
        N = 64
        a = N
        b = data.size//N
        tx_out = data.reshape((a,b))

        y_demod = np.zeros((64,b)).astype(complex)
        PS_est_final = []
        hardDecision_final = []
        for i in range(0,b):
            #rx_out = tx_out
    
            tx_out[:,i] = tx_out[:,i] - DC[i]

            y_fft = np.fft.fft(tx_out[:,i],64)
            y1 = y_fft[1:32]
            
            PS_est, hardDecision = self.Demapping(y1)
            PS_est_final.append(PS_est)
            hardDecision_final.append(hardDecision)


        PS_est_final = np.array(PS_est_final)
        #print(PS_est_final)
        output = []
        a,b,c= PS_est_final.shape
        for i in range(0,b):
            for j in range(0,a):
                output.append(PS_est_final[j][i].reshape(-1,))
                #output.append(PS_est_final[1][i].reshape(-1,))
        output = np.array(output)
        hardDecision_final = np.array(hardDecision_final)
        output = output.reshape(-1,)
        str_final = output[:8*self.str_len]
        ##BER
        BER = (( (str_final!=rx_final).sum().astype(float) ) / str_final.size)
        print('BER: ',BER)

    def calc_BER_ACO_OFDM(self,tx_out,rx_final):
         ##ACO-OFDM
        data = tx_out
        N = 124
        a = N
        b = data.size//N
        tx_out = data.reshape((a,b))

        PS_est_final = []
        hardDecision_final = []
        for i in range(0,b):
            #rx_out = tx_out
            y_fft = np.fft.fft(tx_out[:,i])[1::2]
            y1 = np.around(y_fft)
            PS_est, hardDecision = self.Demapping(y1[:31])
            PS_est_final.append(PS_est)
            hardDecision_final.append(hardDecision)

        PS_est_final = np.array(PS_est_final)
        #print(PS_est_final)
        output = []
        a,b,c= PS_est_final.shape
        for i in range(0,b):
            for j in range(0,a):
                output.append(PS_est_final[j][i].reshape(-1,))
        output = np.array(output)
        hardDecision_final = np.array(hardDecision_final)
        output = output.reshape(-1,)
        str_final = output[:8*self.str_len]
        ##BER
        BER = (( (str_final!=rx_final).sum().astype(float) ) / str_final.size)
        print('BER: ',BER)
            
        

    def work(self, input_items, output_items):
        if(input_items[0][0] <0):
            input_items[0][-1] = -1
            return len(output_items[0])
        tx_out = input_items[0][1:]
        DC_arr = input_items[1][1:]
        rx_out = input_items[2][1:]
        input_items[0][-1] = -1

        tx_len = DC_arr[0].real.astype(int)
        #print(tx_len)
        #print(tx_out.size)
        DC_len = DC_arr[1].real.astype(int)
        DC = DC_arr[2:2+DC_len]
        tx_out = tx_out[:tx_len]
        rx_out = rx_out[:tx_len]
        noise = input_items[3][:tx_len]
        """ print('noise:',np.max(np.absolute(noise)))
        print('tx:',np.max(np.absolute(tx_out))) """
        if(self.mod_type == 0):
            ##OOK
            rx = np.zeros(rx_out.size)
            tx = np.zeros(tx_out.size)
            for i in range(0,len(rx_out)):
                if(np.absolute(rx_out[i].real)> np.max(noise)):
                    rx[i] = 1
                else:
                    rx[i] = 0
            demod_out = rx.real
            ##Reverse of Up-Sample
            factor = 5
            rev_upsamp_out = demod_out[::factor]
            ##Manchester-Decoding
            manch_decode = []
            if(rev_upsamp_out.size % 2!=0):
                rev_upsamp_out = rev_upsamp_out[:-1]
        
            for i in range(0,len(rev_upsamp_out),2):
                if(rev_upsamp_out[i] == 0 and rev_upsamp_out[i+1] == 1):
                    manch_decode.append(1)
                else: 
                    manch_decode.append(0)
                """ elif(rev_upsamp_out[i] == 1 and rev_upsamp_out[i+1] == 0):
                    manch_decode.append(0) """
            manch_decode = np.array(manch_decode)
            str_final = manch_decode[52:]
            print('len', str_final.size)
            #self.print_msg(str_final) ##Print-msg
            self.calc_BER_OOK(tx_out,str_final) ##Calc-BER

        elif(self.mod_type == 1):
            ##DCO-OFDM
            data = rx_out
            N = 64
            a = N
            b = data.size//N
            rx_out = data.reshape((a,b))

            y_demod = np.zeros((64,b)).astype(complex)
            PS_est_final = []
            hardDecision_final = []
            for i in range(0,b):
                #rx_out = tx_out
        
                rx_out[:,i] = rx_out[:,i] - DC[i]

                y_fft = np.fft.fft(rx_out[:,i],64)
                y1 = y_fft[1:32]
                
                PS_est, hardDecision = self.Demapping(y1)
                PS_est_final.append(PS_est)
                hardDecision_final.append(hardDecision)
    

            PS_est_final = np.array(PS_est_final)
            #print(PS_est_final)
            output = []
            a,b,c= PS_est_final.shape
            for i in range(0,b):
                for j in range(0,a):
                    output.append(PS_est_final[j][i].reshape(-1,))
                    #output.append(PS_est_final[1][i].reshape(-1,))
            output = np.array(output)
            hardDecision_final = np.array(hardDecision_final)
            output = output.reshape(-1,)
            str_final = output[:8*self.str_len]
            print('len', str_final.size)
            #print(str_final)
            self.print_msg(str_final) 
            ##BER
            self.calc_BER_DCO_OFDM(tx_out,str_final,DC)
        
            output_items[0][:len(hardDecision_final.reshape((-1,)))] = hardDecision_final.reshape((-1,))
            output_items[0][len(hardDecision_final.reshape((-1,))):] =  -1 + 1j

        elif(self.mod_type == 2):
            ##ACO-OFDM
            data = rx_out
            N = 124
            a = N
            b = data.size//N
            rx_out = data.reshape((a,b))

            PS_est_final = []
            hardDecision_final = []
            for i in range(0,b):
                #rx_out = tx_out
                y_fft = np.fft.fft(rx_out[:,i])[1::2]
                y1 = np.around(y_fft)
                PS_est, hardDecision = self.Demapping(y1[:31])
                PS_est_final.append(PS_est)
                hardDecision_final.append(hardDecision)
    
            PS_est_final = np.array(PS_est_final)
            #print(PS_est_final)
            output = []
            a,b,c= PS_est_final.shape
            for i in range(0,b):
                for j in range(0,a):
                    output.append(PS_est_final[j][i].reshape(-1,))
            output = np.array(output)
            hardDecision_final = np.array(hardDecision_final)
            output = output.reshape(-1,)
            str_final = output[:8*self.str_len]
            print('len', str_final.size)
            #print(str_final)
            #self.print_msg(str_final) 
            ##BER
            self.calc_BER_ACO_OFDM(tx_out,str_final)
        
            output_items[0][:len(hardDecision_final.reshape((-1,)))] = hardDecision_final.reshape((-1,))
            output_items[0][len(hardDecision_final.reshape((-1,))):] =  -1 + 1j

        elif(self.mod_type >= 3):
            print('Wrong input')

        
        return len(output_items[0])
