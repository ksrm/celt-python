from ctypes import *

# Constants
CELT_OK                         = 0
CELT_BAD_ARG                    = -1
CELT_INVALID_MODE               = -2
CELT_INTERNAL_ERROR             = -3
CELT_CORRUPTED_DATA             = -4
CELT_UNIMPLEMENTED              = -5
CELT_INVALID_STATE              = -6
CELT_ALLOC_FAIL                 = -7
CELT_GET_MODE_REQUEST           = 1
CELT_SET_COMPLEXITY_REQUEST     = 2
CELT_SET_PREDICTION_REQUEST     = 4
CELT_SET_VBR_RATE_REQUEST       = 6
CELT_RESET_STATE_REQUEST        = 8
CELT_GET_FRAME_SIZE             = 1000
CELT_GET_LOOKAHEAD              = 1001
CELT_GET_SAMPLE_RATE            = 1003
CELT_GET_BITSTREAM_VERSION      = 2000

# Load DLL (Windows)
libcelt = cdll.celt070

class Encoder:
	def __init__(self, sample_rate, frame_size, channels):
		self.sample_rate = sample_rate
		self.frame_size = frame_size
		self.channels = channels

		self.mode = libcelt.celt_mode_create(sample_rate, frame_size)
		self.encoder = libcelt.celt_encoder_create(self.mode, channels)

	def bitstream_version(self):
		bitver = create_string_buffer(4)
		libcelt.celt_mode_info(self.mode, CELT_GET_BITSTREAM_VERSION, bitver)
		return cast(bitver, POINTER(c_int32))[0]

	def set_prediction_request(self, prediction_request):
		# 0 = independent frames
		# 1 = short term interframe prediction allowed
		# 2 = long term interframe prediction allowed
		self.prediction_request = prediction_request
		return libcelt.celt_encoder_ctl(self.encoder, CELT_SET_PREDICTION_REQUEST, prediction_request)
	
	def set_vbr_rate(self, vbr_rate):
		# vbr_rate : target bitrate in bits per second (0 = constant bitrate)
		self.vbr_rate = vbr_rate
		return libcelt.celt_encoder_ctl(self.encoder, CELT_SET_VBR_RATE_REQUEST, vbr_rate)

	def encode(self, data, outsize):
		# data    : frame of frame_size * 16-bit signed PCM samples
		# outsize : max size of compressed output in bytes
		out = create_string_buffer(len(data) + 1)
		buf = create_string_buffer(data)
		length = libcelt.celt_encode(self.encoder, buf, None, out, outsize)
		# length = outsize unless stream is VBR
		return out.raw[0:length]

class Decoder:
	def __init__(self, sample_rate, frame_size, channels):
		self.sample_rate = sample_rate
		self.frame_size = frame_size
		self.channels = channels

		self.mode = libcelt.celt_mode_create(sample_rate, frame_size)
		self.decoder = libcelt.celt_decoder_create(self.mode, channels)

	def decode(self, data):
		# data must be the exact output of the encoder (no padding)
		pcm = create_string_buffer(2 * self.frame_size * self.channels)
		buf = create_string_buffer(data)
		libcelt.celt_decode(self.decoder, data, len(data), pcm)
		return pcm.raw