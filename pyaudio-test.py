import celt
import pyaudio

sample_rate = 44100
samples_per_frame = 256
bytes_per_sample = 2
channels = 1
seconds = 10

enc = celt.Encoder(sample_rate, samples_per_frame, channels)
dec = celt.Decoder(sample_rate, samples_per_frame, channels)
p = pyaudio.PyAudio()

print enc.set_vbr_rate(256000)  # VBR, target 256kbit/sec

stream = p.open(format=p.get_format_from_width(bytes_per_sample),
                channels=channels,
                rate=sample_rate,
                input=True,
                output=True,
                frames_per_buffer=samples_per_frame)

for i in range(0, int(sample_rate / samples_per_frame * seconds)):
	# Read frame from input device
    inframe = stream.read(samples_per_frame)

    # Encode & decode stream
    celtframe = enc.encode(inframe, 128)    # 128 bytes per encoded frame (does not apply in VBR mode)
    outframe = dec.decode(celtframe)

    # Write frame to output
    stream.write(outframe, samples_per_frame)

stream.stop_stream()
stream.close()
p.terminate()