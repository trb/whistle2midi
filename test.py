from numpy.fft import rfft, fftfreq


import numpy as np
import wave
import struct
import midi


def window(signal, window_size=2048):
    total_samples = len(signal)
    windows = []
    for i in xrange(0, total_samples, window_size):
        window = signal[i:i+window_size]
        if len(window) < window_size:
            """Pad window with zeroes if it's shorter than windows_size
            """
            window = np.append(window, [0] * (window_size - len(window)))
        windows.append(window * np.hamming(window_size))
        
    return windows


def find_frequency(window, sample_rate):
    fft_magnitude = np.abs(rfft(window))[0:-1]
    n = window.size
    freq = fftfreq(n, d=1./sample_rate)[0:len(fft_magnitude)]
    max_at_index = 0
    max_so_far = 0
    for i in xrange(1, len(fft_magnitude)):
        if fft_magnitude[i] > max_so_far:
            max_at_index = i
            max_so_far = fft_magnitude[i]
            
    #import pylab
    #pylab.plot(freq, fft_magnitude)
    #pylab.show()
            
    return freq[max_at_index]


def difference_notes(a, b):
    if a == 0 and b == 0:
        return 0
    
    return abs(a - b) / (a + b)


def consolidate(notes):
    last_note = notes[0]
    current_consolidation = { 'frequency': last_note, 'windows': 1 }
    consolidated = []
    for i in xrange(1, len(notes)):
        note = notes[i]
        """ It's unlikely someone whistled less than 200hz, it's most
        likely noise, so pretend it's a pause.
        """
        if note < 250:
            note = 0
            
        if difference_notes(last_note, note) > 0.5: # defautl value: 0.01
            consolidated.append(current_consolidation)
            current_consolidation = { 'frequency': note, 'windows': 0 }
            
        current_consolidation['windows'] += 1
        last_note = note
        
    consolidated.append(current_consolidation)
    return consolidated


file = wave.open('./samples/fast_whistling.wav')
total_frames = file.getnframes()
signal = np.array(struct.unpack('%ih' % total_frames
                                , file.readframes(total_frames))
                  , dtype=float)
import pylab
splot = pylab.subplot(211)
nplot = pylab.subplot(212)

splot.plot(signal)

windows = window(signal)
resolution = file.getframerate()
notes = [ find_frequency(window, resolution) for window in windows]

nplot.plot(notes)
pylab.show()

consolidated = consolidate(notes)
print notes
print consolidated
midi.save_to_file('./midi.midi', consolidated)