
import numpy as np
import librosa
import os
import cv2
import openvino as ov
import sys
from time import sleep
import matplotlib as mpl
import matplotlib.pyplot as plt
from argparse import SUPPRESS, ArgumentParser
from pathlib import Path
import threading
from queue import Empty, Queue
import pyaudio
import wave
import copy

# os.environ["FEATURE_FLAGS_OTX_ACTION_TASKS"] = "1"

# # pylint: disable=no-name-in-module, import-error
# from otx.api.usecases.exportable_code.demo.demo_package import (
#     AsyncExecutor,
#     ChainExecutor,
#     ModelContainer,
#     SyncExecutor,
#     create_visualizer,
# )

def build_argparser():
    """Parses command line arguments."""
    parser = ArgumentParser(add_help=False)
    args = parser.add_argument_group("Options")
    args.add_argument(
        "-h",
        "--help",
        action="help",
        default=SUPPRESS,
        help="Show this help message and exit.",
    )
    args.add_argument(
        "-i",
        "--input",
        required=False,
        help="Required. An input to process. The input must be a single image, "
        "a folder of images, video file or camera id.",
    )
    args.add_argument(
        "-m",
        "--models",
        #help="Optional. Path to directory with trained model and configuration file. "
        #"If you provide several models you will start the task chain pipeline with "
        #"the provided models in the order in which they were specified. Default value "
        #"points to deployed model folder '../model'.",
        #nargs="+",
        #default=[Path("../model")],
        type=Path,
    )
    args.add_argument(
        "-it",
        "--inference_type",
        help="Optional. Type of inference for single model.",
        choices=["sync", "async"],
        default="sync",
        type=str,
    )
    args.add_argument(
        "-l",
        "--loop",
        help="Optional. Enable reading the input in a loop.",
        default=False,
        action="store_true",
    )
    args.add_argument(
        "--no_show",
        help="Optional. Disables showing inference results on UI.",
        default=False,
        action="store_true",
    )
    args.add_argument(
        "-d",
        "--device",
        help="Optional. Device to infer the model.",
        choices=["CPU", "GPU"],
        default="CPU",
        type=str,
    )
    args.add_argument(
        "--output",
        default=None,
        type=str,
        help="Optional. Output path to save input data with predictions.",
    )
    args.add_argument(
        "-a",
        "--audio",
        type=Path
    )

    return parser

def get_inferencer_class(type_inference, models):
    """Return class for inference of models."""
    if len(models) > 1:
        type_inference = "chain"
        print("You started the task chain pipeline with the provided models in the order in which they were specified")
    return EXECUTORS[type_inference]

def main():
    args = build_argparser().parse_args()
    if args.loop and args.output:
        raise ValueError("--loop and --output cannot be both specified")

    audio_queue = Queue()
    spec_audio_queue = Queue()
    lock = threading.Lock()
    Thread_audio_play = threading.Thread(target=Therad_audio_infer, args=(audio_queue, spec_audio_queue, lock))
    Thread_mic_record = threading.Thread(target=Therad_recording, args=(audio_queue, lock))

    Thread_audio_play.start()
    Thread_mic_record.start()
    FORCE_STOP = False
    while not FORCE_STOP:      
        try:
            with lock:
                event = spec_audio_queue.get_nowait()
                spec_audio_queue.task_done()
                name, frame = event
        except Empty:    
            continue
        
        with lock:
            if name == "spec_img": 
                cv2.imshow(name, frame) 
            cv2.waitKey(1)
        
    Thread_audio_play.join()
    Thread_mic_record.join()


def Therad_recording(audio_queue:Queue, lock)->None:
    CHUNK = 1024
    FORMAT = pyaudio.paFloat32
    CHANNELS = 2
    RATE = 44100
    RECORD_SECONDS = 5
    
    Pyaud = pyaudio.PyAudio()
    stream = Pyaud.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

    RECORD_FORCE_STOP = False
    print("Start recording")
    while not RECORD_FORCE_STOP:
        frames = []
        for i in range(0, int(RATE / CHUNK * RECORD_SECONDS)):
            data = stream.read(CHUNK)
            data = np.frombuffer(data, dtype=np.float32)
            frames.extend(data)
        # MUTAX
        with lock:
            audio_queue.put( ("wav", frames) )

    stream.close()

def Therad_audio_infer(audio_queue:Queue, spec_audio_queue:Queue, lock)->None:
    """Main function that is used to run demo."""
    
    args = build_argparser().parse_args()
    Classes_Name = ['Can', 'Others', 'Paper', 'Plastic']
        
    core = ov.Core()
    print(args.models)
    model = core.read_model(model=args.models)
    compiled_model = core.compile_model(model=model, device_name=args.device)

    input_layer_ir = compiled_model.input(0)
    output_layer_ir = compiled_model.output(0)
    N, C, H, W = input_layer_ir.shape
    print(input_layer_ir.shape)
    print(output_layer_ir.shape)
    
    SOUND_DURATION = 2
    sample_rate = 44100 # Hz
    HOP_LENGTH = 1024        # number of samples between successive frames
    WINDOW_LENGTH = 1024     # length of the window in samples
    N_MEL = 256             # number of Mel bands to generate

    Force_stop = False
    while not Force_stop:
        try:
            with lock:
                event = audio_queue.get_nowait()
                audio_queue.task_done()
        except Empty:
            continue
        name, frame = event

        if name == "wav":  
            frame = np.array(frame)
            # audio, sample_rate = librosa.load(args.audio, sr = sample_rate, duration=SOUND_DURATION, res_type='kaiser_fast')
            # convert sound to spectogram 
            with lock:
                melspectrogram = librosa.feature.melspectrogram(y=frame,
                sr=sample_rate,
                hop_length=HOP_LENGTH,
                win_length=WINDOW_LENGTH,
                n_mels=N_MEL)
                
            # to dB
            melspectrogram_db = librosa.power_to_db(melspectrogram, ref=np.max)
            # normalized melspectrogram_db (0 ~ 1)
            norm = mpl.colors.Normalize(vmin = -80, vmax = 0)
            # get colormap from melspectrogram_db
            melcmap = librosa.display.cmap(melspectrogram_db)
            # get RGB value from colormap
            ColorMapping = mpl.cm.ScalarMappable(norm=norm, cmap=melcmap)
            # cmapList = np.array(melcmap.colors) # magma

            # make image
            melspectrogram_db_map = ColorMapping.to_rgba(melspectrogram_db)  
            melspectrogram_db_map = melspectrogram_db_map.astype('float32')  
            # convert image BGRA to RGB
            melspectrogram_db_map_RGB = cv2.cvtColor(melspectrogram_db_map, cv2.COLOR_BGRA2RGB)
            # flip image
            melspectrogram_db_map_RGB_flip = np.flip(melspectrogram_db_map_RGB, axis = 0)
            # resize image
            resized_image = cv2.resize(melspectrogram_db_map_RGB_flip, (W, H))
            resized_image = resized_image*255
            resized_image_show = cv2.resize(melspectrogram_db_map_RGB_flip, (2*W, 2*H))
            que_img = copy.deepcopy(resized_image_show)    
            with lock:
                spec_audio_queue.put(("spec_img", que_img))
            
            # format change of image
            input_image = np.expand_dims(resized_image.transpose(2, 0, 1), 0)
            
            # Create an inference request.
            results = compiled_model([input_image])[output_layer_ir]
            print(Classes_Name[np.argmax(results)], results)





if __name__ == "__main__":
    sys.exit(main() or 0)
