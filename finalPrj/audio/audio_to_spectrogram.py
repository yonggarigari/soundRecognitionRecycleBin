import numpy as np
import wave
import matplotlib as mpl
import matplotlib.pyplot as plt
import librosa
import os
import time
import cv2

OUTPUT_DIR = './images/반복/can'

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)
   
for i in range(130):

    SOUND_DURATION = 5
    sample_rate0 = 44100 # Hz  
    audio, sample_rate = librosa.load(f"./소리/반복/can/segment_{i}.wav",sr = sample_rate0, duration=SOUND_DURATION, res_type='kaiser_fast')
    #test_plastic
    #plastic_0
    Period = 1/sample_rate # second
    N = 1
    dt = Period / N
    t = np.arange(0, 1, dt)
    #sample_rate = sample_rate0 * 1 # delta t

    HOP_LENGTH =  1024       # number of samples between successive frames
    WINDOW_LENGTH = 1024     # length of the window in samples
    N_MEL = 256             # number of Mel bands to generate

    melspectrogram = librosa.feature.melspectrogram(y=audio,
        sr=sample_rate,
        hop_length=HOP_LENGTH,
        win_length=WINDOW_LENGTH,
        n_mels=N_MEL)

    # to dB
    melspectrogram_db = librosa.power_to_db(melspectrogram, ref=np.max)

    # normalized melspectrogram_db (0 ~ 1)
    vmin = -80 #np.min(melspectrogram_db)
    vmax = 0 #np.max(melspectrogram_db)

    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)

    # get colormap from melspectrogram_db
    cmap = librosa.display.cmap(melspectrogram_db)#, cmap_seq='magma')
    # get RGB value from colormap
    colormapping = mpl.cm.ScalarMappable(norm=norm, cmap=cmap) 
    # make image by mapping colormap
    image = colormapping.to_rgba(melspectrogram_db)
    image = image.astype(np.float32)
    W, H, _ = image.shape
    print((W, H))

    # convert image BGRA to RGB
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGRA2RGB)
    # flip image
    flipped_image = cv2.flip(image_rgb, 0) 

    # pad or fix the length of spectrogram 
    # if melspectrogram_length != sample_rate:
    #     melspectrogram_db = librosa.util.fix_length(melspectrogram_db, 
    #                                                 size=sample_rate, 
    #                                                 axis=1, 
    #                                                 constant_values=(0, -80.0))
    # sig = np.frombuffer(signal_wave.readframes(sample_rate), dtype=np.int16)

    cv2.imwrite(f"{OUTPUT_DIR}/can_{i}.jpg", flipped_image*255)  # 이미지 저장
    cv2.waitKey(1)
    cv2.destroyAllWindows()

    
