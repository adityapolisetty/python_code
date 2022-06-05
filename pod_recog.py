import numpy as np
from scipy.io import wavfile
from scipy import signal
import os
from pydub import AudioSegment

## This script analyses the intro and outro audio samples from the Conan podcast and removes the guest interview part. Beats skipping manually for every episode. This is implemented for one episode that I found on Youtube. This is written for this podcast only but will work for any episode.  

os.chdir("D:\Dropbox\Dropbox\My_files")

# recognise audio samples from full episodes
def pod_recog(source, sample,span):

  # read the sample to look for
  snippet = wavfile.read(sample);
  snippet = np.array(snippet, dtype='float')

  # read the source
  rate, source = wavfile.read(source);
  source = np.array(source, dtype='float')

  # compute the cross-correlation
  z = signal.correlate(source, snippet);

  peak = np.argmax(np.abs(z))
  start = (((peak-len(snippet)+1)/rate -10)/3.025)
  end   = start+span
  print("start {} end {}".format(start, end))
  return (start, end  )

# segment audio clips we want
def segment(t1,t2,infile,outfile):
  t1 = pod_recog(source, 'ending_rhythm_start.wav', 5)[1] * 1000
  t2 = pod_recog(source, 'ending_rhythm_end.wav', 64.5)[0] * 1000

  newAudio = AudioSegment.from_wav(infile)
  newAudio = newAudio[t1:t2]
  newAudio.export(outfile, format="wav")

source  = "billburr.wav"

# sample file collection
segment( ((1 * 60 ) +18) * 1000,((1 * 60 ) +21) * 1000, source, 'starting_end.wav' )
segment( ((39 * 60 ) +34) * 1000  ,((39 * 60 ) +39) * 1000  , source, 'ending_rhythm_start.wav' )
segment( ((49 * 60 ) +52.5) * 1000,((50 * 60 ) +57) * 1000, source, 'ending_rhythm_end.wav' )
segment( (15) * 1000 ,(16) * 1000  , source, 'starting_start.wav' )

# recognition
segment( (pod_recog(source, 'starting_start.wav', 21)[1] +20) * 1000, pod_recog(source, 'starting_end.wav', 3)[0] * 1000  , source, 'chitchat_1.wav' )
segment(pod_recog(source, 'ending_rhythm_start.wav', 5)[1] * 1000 , pod_recog(source, 'ending_rhythm_end.wav', 64.5)[0] * 1000, source, 'chitchat_2.wav' )

# combine the audio clips we obtained
sound1 = AudioSegment.from_wav("chitchat_1.wav")
sound2 = AudioSegment.from_wav("chitchat_2.wav")
combined_sounds = sound1 + sound2
combined_sounds.export("chitchat_main.wav", format="wav")
