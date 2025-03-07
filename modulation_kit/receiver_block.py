#!/usr/bin/env python2
# -*- coding: utf-8 -*-
##################################################
# GNU Radio Python Flow Graph
# Title: Receiver Block
# Generated: Sat Mar 13 00:10:56 2021
##################################################

if __name__ == '__main__':
    import ctypes
    import sys
    if sys.platform.startswith('linux'):
        try:
            x11 = ctypes.cdll.LoadLibrary('libX11.so')
            x11.XInitThreads()
        except:
            print "Warning: failed to XInitThreads()"

from PyQt4 import Qt
from gnuradio import analog
from gnuradio import blocks
from gnuradio import eng_notation
from gnuradio import gr
from gnuradio.eng_option import eng_option
from gnuradio.filter import firdes
from optparse import OptionParser
import epy_block_0_0
import pmt
import sys
from gnuradio import qtgui


class receiver_block(gr.top_block, Qt.QWidget):

    def __init__(self):
        gr.top_block.__init__(self, "Receiver Block")
        Qt.QWidget.__init__(self)
        self.setWindowTitle("Receiver Block")
        qtgui.util.check_set_qss()
        try:
            self.setWindowIcon(Qt.QIcon.fromTheme('gnuradio-grc'))
        except:
            pass
        self.top_scroll_layout = Qt.QVBoxLayout()
        self.setLayout(self.top_scroll_layout)
        self.top_scroll = Qt.QScrollArea()
        self.top_scroll.setFrameStyle(Qt.QFrame.NoFrame)
        self.top_scroll_layout.addWidget(self.top_scroll)
        self.top_scroll.setWidgetResizable(True)
        self.top_widget = Qt.QWidget()
        self.top_scroll.setWidget(self.top_widget)
        self.top_layout = Qt.QVBoxLayout(self.top_widget)
        self.top_grid_layout = Qt.QGridLayout()
        self.top_layout.addLayout(self.top_grid_layout)

        self.settings = Qt.QSettings("GNU Radio", "receiver_block")
        self.restoreGeometry(self.settings.value("geometry").toByteArray())


        ##################################################
        # Variables
        ##################################################
        self.upsampling_factor = upsampling_factor = 10
        self.str_len = str_len = 22
        self.samp_rate = samp_rate = 32000
        self.mod_type = mod_type = 1
        self.m_qam_order = m_qam_order = 8

        ##################################################
        # Blocks
        ##################################################
        self.epy_block_0_0 = epy_block_0_0.blk(str_len=str_len, mod_type=mod_type, interpolation=upsampling_factor/2, m_qam=m_qam_order)
        self.blocks_throttle_0_0 = blocks.throttle(gr.sizeof_gr_complex*1, samp_rate,True)
        (self.blocks_throttle_0_0).set_min_output_buffer(1048576)
        self.blocks_file_source_1 = blocks.file_source(gr.sizeof_gr_complex*1, 'D:\\iiitd\\gnu_files\\modulation_kit\\tx_out', False)
        self.blocks_file_source_1.set_begin_tag(pmt.PMT_NIL)
        (self.blocks_file_source_1).set_min_output_buffer(1048576)
        self.blocks_file_source_0 = blocks.file_source(gr.sizeof_gr_complex*1, 'D:\\iiitd\\gnu_files\\modulation_kit\\dc_arr', False)
        self.blocks_file_source_0.set_begin_tag(pmt.PMT_NIL)
        (self.blocks_file_source_0).set_min_output_buffer(1048576)
        self.blocks_file_sink_0 = blocks.file_sink(gr.sizeof_gr_complex*1, 'D:\\iiitd\\gnu_files\\modulation_kit\\rx_out', False)
        self.blocks_file_sink_0.set_unbuffered(False)
        self.blocks_add_xx_0 = blocks.add_vcc(1)
        (self.blocks_add_xx_0).set_min_output_buffer(1048576)
        self.analog_noise_source_x_0 = analog.noise_source_c(analog.GR_GAUSSIAN, 0.0000001, 0)
        (self.analog_noise_source_x_0).set_min_output_buffer(1048576)



        ##################################################
        # Connections
        ##################################################
        self.connect((self.analog_noise_source_x_0, 0), (self.blocks_add_xx_0, 1))
        self.connect((self.analog_noise_source_x_0, 0), (self.epy_block_0_0, 3))
        self.connect((self.blocks_add_xx_0, 0), (self.blocks_throttle_0_0, 0))
        self.connect((self.blocks_file_source_0, 0), (self.epy_block_0_0, 1))
        self.connect((self.blocks_file_source_1, 0), (self.blocks_add_xx_0, 0))
        self.connect((self.blocks_file_source_1, 0), (self.epy_block_0_0, 0))
        self.connect((self.blocks_throttle_0_0, 0), (self.epy_block_0_0, 2))
        self.connect((self.epy_block_0_0, 0), (self.blocks_file_sink_0, 0))

    def closeEvent(self, event):
        self.settings = Qt.QSettings("GNU Radio", "receiver_block")
        self.settings.setValue("geometry", self.saveGeometry())
        event.accept()

    def get_upsampling_factor(self):
        return self.upsampling_factor

    def set_upsampling_factor(self, upsampling_factor):
        self.upsampling_factor = upsampling_factor
        self.epy_block_0_0.interpolation = self.upsampling_factor/2

    def get_str_len(self):
        return self.str_len

    def set_str_len(self, str_len):
        self.str_len = str_len
        self.epy_block_0_0.str_len = self.str_len

    def get_samp_rate(self):
        return self.samp_rate

    def set_samp_rate(self, samp_rate):
        self.samp_rate = samp_rate
        self.blocks_throttle_0_0.set_sample_rate(self.samp_rate)

    def get_mod_type(self):
        return self.mod_type

    def set_mod_type(self, mod_type):
        self.mod_type = mod_type
        self.epy_block_0_0.mod_type = self.mod_type

    def get_m_qam_order(self):
        return self.m_qam_order

    def set_m_qam_order(self, m_qam_order):
        self.m_qam_order = m_qam_order
        self.epy_block_0_0.m_qam = self.m_qam_order


def main(top_block_cls=receiver_block, options=None):

    from distutils.version import StrictVersion
    if StrictVersion(Qt.qVersion()) >= StrictVersion("4.5.0"):
        style = gr.prefs().get_string('qtgui', 'style', 'raster')
        Qt.QApplication.setGraphicsSystem(style)
    qapp = Qt.QApplication(sys.argv)

    tb = top_block_cls()
    tb.start()
    tb.show()

    def quitting():
        tb.stop()
        tb.wait()
    qapp.connect(qapp, Qt.SIGNAL("aboutToQuit()"), quitting)
    qapp.exec_()


if __name__ == '__main__':
    main()
