
#os.system("git clone https://github.com/R3gm/SoniTranslate")
# pip install -r requirements.txt
import numpy as np
import gradio as gr
import whisperx
import torch
from gtts import gTTS
import librosa
import edge_tts
import asyncio
import gc
from pydub import AudioSegment
from tqdm import tqdm
from deep_translator import GoogleTranslator
import os
from soni_translate.audio_segments import create_translated_audio
from soni_translate.text_to_speech import make_voice_gradio
from soni_translate.translate_segments import translate_text
#from soni_translate import test

title = "<center><strong><font size='7'>📽️ SoniTranslate 🈷️</font></strong></center>"

news = """ ## 📖 News
        🔥 2023/07/01: Support  (Thanks for [text](https://github.com)).
        """  

description = """ ## Translate the audio of a video content from one language to another while preserving synchronization.


                This is a demo on Github project 📽️ [SoniTranslate](https://github.com/R3gm/SoniTranslate).
                
                📼 You can upload a video or provide a video link. The generation is **limited to 10 seconds** to prevent errors with the queue in cpu. If you use a GPU, you won't have any of these limitations.
                
                🚀 For **translate a video of any duration** and faster results, you can use the Colab notebook with GPU.   

                [![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://github.com/R3gm/SoniTranslate/blob/main/SoniTranslate_Colab.ipynb)
                 
              """

tutorial = """ # 🔰 Instructions for use.
                
                1. Upload a video on the first tab or use a video link on the second tab.
                
                2. Choose the language in which you want to translate the video.
                
                3. Specify the number of people speaking in the video and assign each one a text-to-speech voice suitable for the translation language.
                
                4. Press the 'Translate' button to obtain the results.
                
              """


if not os.path.exists('audio'):
    os.makedirs('audio')

if not os.path.exists('audio2/audio'):
    os.makedirs('audio2/audio')

# Check GPU
if torch.cuda.is_available():
    device = "cuda"
    list_compute_type = ['float16', 'float32']
    compute_type_default = 'float16'
    whisper_model_default = 'large-v1'
else:
    device = "cpu"
    list_compute_type = ['float32']
    compute_type_default = 'float32'
    whisper_model_default = 'base'
print('Working in: ', device)


# Download an audio
#url = "https://www.youtube.com/watch?v=Rdi-SNhe2v4"

### INIT
list_tts = ['af-ZA-AdriNeural-Female', 'af-ZA-WillemNeural-Male', 'am-ET-AmehaNeural-Male', 'am-ET-MekdesNeural-Female', 'ar-AE-FatimaNeural-Female', 'ar-AE-HamdanNeural-Male', 'ar-BH-AliNeural-Male', 'ar-BH-LailaNeural-Female', 'ar-DZ-AminaNeural-Female', 'ar-DZ-IsmaelNeural-Male', 'ar-EG-SalmaNeural-Female', 'ar-EG-ShakirNeural-Male', 'ar-IQ-BasselNeural-Male', 'ar-IQ-RanaNeural-Female', 'ar-JO-SanaNeural-Female', 'ar-JO-TaimNeural-Male', 'ar-KW-FahedNeural-Male', 'ar-KW-NouraNeural-Female', 'ar-LB-LaylaNeural-Female', 'ar-LB-RamiNeural-Male', 'ar-LY-ImanNeural-Female', 'ar-LY-OmarNeural-Male', 'ar-MA-JamalNeural-Male', 'ar-MA-MounaNeural-Female', 'ar-OM-AbdullahNeural-Male', 'ar-OM-AyshaNeural-Female', 'ar-QA-AmalNeural-Female', 'ar-QA-MoazNeural-Male', 'ar-SA-HamedNeural-Male', 'ar-SA-ZariyahNeural-Female', 'ar-SY-AmanyNeural-Female', 'ar-SY-LaithNeural-Male', 'ar-TN-HediNeural-Male', 'ar-TN-ReemNeural-Female', 'ar-YE-MaryamNeural-Female', 'ar-YE-SalehNeural-Male', 'az-AZ-BabekNeural-Male', 'az-AZ-BanuNeural-Female', 'bg-BG-BorislavNeural-Male', 'bg-BG-KalinaNeural-Female', 'bn-BD-NabanitaNeural-Female', 'bn-BD-PradeepNeural-Male', 'bn-IN-BashkarNeural-Male', 'bn-IN-TanishaaNeural-Female', 'bs-BA-GoranNeural-Male', 'bs-BA-VesnaNeural-Female', 'ca-ES-EnricNeural-Male', 'ca-ES-JoanaNeural-Female', 'cs-CZ-AntoninNeural-Male', 'cs-CZ-VlastaNeural-Female', 'cy-GB-AledNeural-Male', 'cy-GB-NiaNeural-Female', 'da-DK-ChristelNeural-Female', 'da-DK-JeppeNeural-Male', 'de-AT-IngridNeural-Female', 'de-AT-JonasNeural-Male', 'de-CH-JanNeural-Male', 'de-CH-LeniNeural-Female', 'de-DE-AmalaNeural-Female', 'de-DE-ConradNeural-Male', 'de-DE-KatjaNeural-Female', 'de-DE-KillianNeural-Male', 'el-GR-AthinaNeural-Female', 'el-GR-NestorasNeural-Male', 'en-AU-NatashaNeural-Female', 'en-AU-WilliamNeural-Male', 'en-CA-ClaraNeural-Female', 'en-CA-LiamNeural-Male', 'en-GB-LibbyNeural-Female', 'en-GB-MaisieNeural-Female', 'en-GB-RyanNeural-Male', 'en-GB-SoniaNeural-Female', 'en-GB-ThomasNeural-Male', 'en-HK-SamNeural-Male', 'en-HK-YanNeural-Female', 'en-IE-ConnorNeural-Male', 'en-IE-EmilyNeural-Female', 'en-IN-NeerjaExpressiveNeural-Female', 'en-IN-NeerjaNeural-Female', 'en-IN-PrabhatNeural-Male', 'en-KE-AsiliaNeural-Female', 'en-KE-ChilembaNeural-Male', 'en-NG-AbeoNeural-Male', 'en-NG-EzinneNeural-Female', 'en-NZ-MitchellNeural-Male', 'en-NZ-MollyNeural-Female', 'en-PH-JamesNeural-Male', 'en-PH-RosaNeural-Female', 'en-SG-LunaNeural-Female', 'en-SG-WayneNeural-Male', 'en-TZ-ElimuNeural-Male', 'en-TZ-ImaniNeural-Female', 'en-US-AnaNeural-Female', 'en-US-AriaNeural-Female', 'en-US-ChristopherNeural-Male', 'en-US-EricNeural-Male', 'en-US-GuyNeural-Male', 'en-US-JennyNeural-Female', 'en-US-MichelleNeural-Female', 'en-US-RogerNeural-Male', 'en-US-SteffanNeural-Male', 'en-ZA-LeahNeural-Female', 'en-ZA-LukeNeural-Male', 'es-AR-ElenaNeural-Female', 'es-AR-TomasNeural-Male', 'es-BO-MarceloNeural-Male', 'es-BO-SofiaNeural-Female', 'es-CL-CatalinaNeural-Female', 'es-CL-LorenzoNeural-Male', 'es-CO-GonzaloNeural-Male', 'es-CO-SalomeNeural-Female', 'es-CR-JuanNeural-Male', 'es-CR-MariaNeural-Female', 'es-CU-BelkysNeural-Female', 'es-CU-ManuelNeural-Male', 'es-DO-EmilioNeural-Male', 'es-DO-RamonaNeural-Female', 'es-EC-AndreaNeural-Female', 'es-EC-LuisNeural-Male', 'es-ES-AlvaroNeural-Male', 'es-ES-ElviraNeural-Female', 'es-GQ-JavierNeural-Male', 'es-GQ-TeresaNeural-Female', 'es-GT-AndresNeural-Male', 'es-GT-MartaNeural-Female', 'es-HN-CarlosNeural-Male', 'es-HN-KarlaNeural-Female', 'es-MX-DaliaNeural-Female', 'es-MX-JorgeNeural-Male', 'es-NI-FedericoNeural-Male', 'es-NI-YolandaNeural-Female', 'es-PA-MargaritaNeural-Female', 'es-PA-RobertoNeural-Male', 'es-PE-AlexNeural-Male', 'es-PE-CamilaNeural-Female', 'es-PR-KarinaNeural-Female', 'es-PR-VictorNeural-Male', 'es-PY-MarioNeural-Male', 'es-PY-TaniaNeural-Female', 'es-SV-LorenaNeural-Female', 'es-SV-RodrigoNeural-Male', 'es-US-AlonsoNeural-Male', 'es-US-PalomaNeural-Female', 'es-UY-MateoNeural-Male', 'es-UY-ValentinaNeural-Female', 'es-VE-PaolaNeural-Female', 'es-VE-SebastianNeural-Male', 'et-EE-AnuNeural-Female', 'et-EE-KertNeural-Male', 'fa-IR-DilaraNeural-Female', 'fa-IR-FaridNeural-Male', 'fi-FI-HarriNeural-Male', 'fi-FI-NooraNeural-Female', 'fil-PH-AngeloNeural-Male', 'fil-PH-BlessicaNeural-Female', 'fr-BE-CharlineNeural-Female', 'fr-BE-GerardNeural-Male', 'fr-CA-AntoineNeural-Male', 'fr-CA-JeanNeural-Male', 'fr-CA-SylvieNeural-Female', 'fr-CH-ArianeNeural-Female', 'fr-CH-FabriceNeural-Male', 'fr-FR-DeniseNeural-Female', 'fr-FR-EloiseNeural-Female', 'fr-FR-HenriNeural-Male', 'ga-IE-ColmNeural-Male', 'ga-IE-OrlaNeural-Female', 'gl-ES-RoiNeural-Male', 'gl-ES-SabelaNeural-Female', 'gu-IN-DhwaniNeural-Female', 'gu-IN-NiranjanNeural-Male', 'he-IL-AvriNeural-Male', 'he-IL-HilaNeural-Female', 'hi-IN-MadhurNeural-Male', 'hi-IN-SwaraNeural-Female', 'hr-HR-GabrijelaNeural-Female', 'hr-HR-SreckoNeural-Male', 'hu-HU-NoemiNeural-Female', 'hu-HU-TamasNeural-Male', 'id-ID-ArdiNeural-Male', 'id-ID-GadisNeural-Female', 'is-IS-GudrunNeural-Female', 'is-IS-GunnarNeural-Male', 'it-IT-DiegoNeural-Male', 'it-IT-ElsaNeural-Female', 'it-IT-IsabellaNeural-Female', 'ja-JP-KeitaNeural-Male', 'ja-JP-NanamiNeural-Female', 'jv-ID-DimasNeural-Male', 'jv-ID-SitiNeural-Female', 'ka-GE-EkaNeural-Female', 'ka-GE-GiorgiNeural-Male', 'kk-KZ-AigulNeural-Female', 'kk-KZ-DauletNeural-Male', 'km-KH-PisethNeural-Male', 'km-KH-SreymomNeural-Female', 'kn-IN-GaganNeural-Male', 'kn-IN-SapnaNeural-Female', 'ko-KR-InJoonNeural-Male', 'ko-KR-SunHiNeural-Female', 'lo-LA-ChanthavongNeural-Male', 'lo-LA-KeomanyNeural-Female', 'lt-LT-LeonasNeural-Male', 'lt-LT-OnaNeural-Female', 'lv-LV-EveritaNeural-Female', 'lv-LV-NilsNeural-Male', 'mk-MK-AleksandarNeural-Male', 'mk-MK-MarijaNeural-Female', 'ml-IN-MidhunNeural-Male', 'ml-IN-SobhanaNeural-Female', 'mn-MN-BataaNeural-Male', 'mn-MN-YesuiNeural-Female', 'mr-IN-AarohiNeural-Female', 'mr-IN-ManoharNeural-Male', 'ms-MY-OsmanNeural-Male', 'ms-MY-YasminNeural-Female', 'mt-MT-GraceNeural-Female', 'mt-MT-JosephNeural-Male', 'my-MM-NilarNeural-Female', 'my-MM-ThihaNeural-Male', 'nb-NO-FinnNeural-Male', 'nb-NO-PernilleNeural-Female', 'ne-NP-HemkalaNeural-Female', 'ne-NP-SagarNeural-Male', 'nl-BE-ArnaudNeural-Male', 'nl-BE-DenaNeural-Female', 'nl-NL-ColetteNeural-Female', 'nl-NL-FennaNeural-Female', 'nl-NL-MaartenNeural-Male', 'pl-PL-MarekNeural-Male', 'pl-PL-ZofiaNeural-Female', 'ps-AF-GulNawazNeural-Male', 'ps-AF-LatifaNeural-Female', 'pt-BR-AntonioNeural-Male', 'pt-BR-FranciscaNeural-Female', 'pt-PT-DuarteNeural-Male', 'pt-PT-RaquelNeural-Female', 'ro-RO-AlinaNeural-Female', 'ro-RO-EmilNeural-Male', 'ru-RU-DmitryNeural-Male', 'ru-RU-SvetlanaNeural-Female', 'si-LK-SameeraNeural-Male', 'si-LK-ThiliniNeural-Female', 'sk-SK-LukasNeural-Male', 'sk-SK-ViktoriaNeural-Female', 'sl-SI-PetraNeural-Female', 'sl-SI-RokNeural-Male', 'so-SO-MuuseNeural-Male', 'so-SO-UbaxNeural-Female', 'sq-AL-AnilaNeural-Female', 'sq-AL-IlirNeural-Male', 'sr-RS-NicholasNeural-Male', 'sr-RS-SophieNeural-Female', 'su-ID-JajangNeural-Male', 'su-ID-TutiNeural-Female', 'sv-SE-MattiasNeural-Male', 'sv-SE-SofieNeural-Female', 'sw-KE-RafikiNeural-Male', 'sw-KE-ZuriNeural-Female', 'sw-TZ-DaudiNeural-Male', 'sw-TZ-RehemaNeural-Female', 'ta-IN-PallaviNeural-Female', 'ta-IN-ValluvarNeural-Male', 'ta-LK-KumarNeural-Male', 'ta-LK-SaranyaNeural-Female', 'ta-MY-KaniNeural-Female', 'ta-MY-SuryaNeural-Male', 'ta-SG-AnbuNeural-Male', 'ta-SG-VenbaNeural-Female', 'te-IN-MohanNeural-Male', 'te-IN-ShrutiNeural-Female', 'th-TH-NiwatNeural-Male', 'th-TH-PremwadeeNeural-Female', 'tr-TR-AhmetNeural-Male', 'tr-TR-EmelNeural-Female', 'uk-UA-OstapNeural-Male', 'uk-UA-PolinaNeural-Female', 'ur-IN-GulNeural-Female', 'ur-IN-SalmanNeural-Male', 'ur-PK-AsadNeural-Male', 'ur-PK-UzmaNeural-Female', 'uz-UZ-MadinaNeural-Female', 'uz-UZ-SardorNeural-Male', 'vi-VN-HoaiMyNeural-Female', 'vi-VN-NamMinhNeural-Male', 'zh-CN-XiaoxiaoNeural-Female', 'zh-CN-XiaoyiNeural-Female', 'zh-CN-YunjianNeural-Male', 'zh-CN-YunxiNeural-Male', 'zh-CN-YunxiaNeural-Male', 'zh-CN-YunyangNeural-Male', 'zh-CN-liaoning-XiaobeiNeural-Female', 'zh-CN-shaanxi-XiaoniNeural-Female'] 


def translate_from_video(video, WHISPER_MODEL_SIZE, batch_size, compute_type, 
                         TRANSLATE_AUDIO_TO, min_speakers, max_speakers,
                         tts_voice00, tts_voice01,tts_voice02,tts_voice03,tts_voice04,tts_voice05):

    YOUR_HF_TOKEN = os.getenv("My_hf_token")

                             
    OutputFile = 'Video.mp4'
    audio_wav = "audio.wav"
    Output_name_file = "audio_dub_solo.wav"
    mix_audio = "audio_mix.mp3"
    video_output = "diar_output.mp4"
                             
    os.system(f"rm {Output_name_file}")
    os.system("rm Video.mp4")
    #os.system("rm diar_output.mp4")
    os.system("rm audio.wav")
                            

    if os.path.exists(video):
        print(f"### Start Video ###")  
        if device == 'cpu':
            # max 1 minute in cpu
            print('10 s. Limited for CPU ')
            os.system(f"ffmpeg -y -i {video} -ss 00:00:20 -t 00:00:10 -c:v libx264 -c:a aac -strict experimental Video.mp4")
        else:
            os.system(f"ffmpeg -y -i {video} -c:v libx264 -c:a aac -strict experimental Video.mp4")
        
        os.system("ffmpeg -y -i Video.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 2 audio.wav")
    else:
        print(f"### Start {video} ###")  
        if device == 'cpu':
            # max 1 minute in cpu
            print('10 s. Limited for CPU ')
            #https://github.com/yt-dlp/yt-dlp/issues/2220
            mp4_ = f'yt-dlp -f "mp4" --downloader ffmpeg --downloader-args "ffmpeg_i: -ss 00:00:20 -t 00:00:10" --force-overwrites --max-downloads 1 --no-warnings --no-abort-on-error --ignore-no-formats-error --restrict-filenames -o {OutputFile} {video}'
            wav_ = "ffmpeg -y -i Video.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 audio.wav"
        else:
            mp4_ = f'yt-dlp -f "mp4" --force-overwrites --max-downloads 1 --no-warnings --no-abort-on-error --ignore-no-formats-error --restrict-filenames -o {OutputFile} {video}'
            wav_ = f'python -m yt_dlp --output {audio_wav} --force-overwrites --max-downloads 1 --no-warnings --no-abort-on-error --ignore-no-formats-error --extract-audio --audio-format wav {video}'
            
        os.system(mp4_)
        os.system(wav_)

    print("Set file complete.")
        
    # 1. Transcribe with original whisper (batched)
    model = whisperx.load_model(
        WHISPER_MODEL_SIZE,
        device,
        compute_type=compute_type
        )
    audio = whisperx.load_audio(audio_wav)
    result = model.transcribe(audio, batch_size=batch_size)
    gc.collect(); torch.cuda.empty_cache(); del model
    print("Transcript complete")
                             
    # 2. Align whisper output
    model_a, metadata = whisperx.load_align_model(
        language_code=result["language"], 
        device=device
        )
    result = whisperx.align(
        result["segments"],
        model_a,
        metadata,
        audio,
        device,
        return_char_alignments=True,
        )
    gc.collect(); torch.cuda.empty_cache(); del model_a
    print("Align complete")
                             
    # 3. Assign speaker labels
    diarize_model = whisperx.DiarizationPipeline(use_auth_token=YOUR_HF_TOKEN, device=device)
    diarize_segments = diarize_model(
        audio_wav,
        min_speakers=min_speakers,
        max_speakers=max_speakers)
    result_diarize = whisperx.assign_word_speakers(diarize_segments, result)
    gc.collect(); torch.cuda.empty_cache(); del diarize_model
    print("Diarize complete")
                             
    result_diarize['segments'] = translate_text(result_diarize['segments'], TRANSLATE_AUDIO_TO)
    print("Translation complete")
    
    audio_files = []

    # Mapping speakers to voice variables
    speaker_to_voice = {
        'SPEAKER_00': tts_voice00,
        'SPEAKER_01': tts_voice01,
        'SPEAKER_02': tts_voice02,
        'SPEAKER_03': tts_voice03,
        'SPEAKER_04': tts_voice04,
        'SPEAKER_05': tts_voice05
    }

    for segment in result_diarize['segments']:

        text = segment['text']
        start = segment['start']
        end = segment['end']

        try:
            speaker = segment['speaker']
        except KeyError:
            segment['speaker'] = "SPEAKER_99"
            speaker = segment['speaker']
            print("NO SPEAKER DETECT IN SEGMENT")

        # make the tts audio
        filename = f"audio/{start}.ogg"

        if speaker in speaker_to_voice and speaker_to_voice[speaker] != 'None':
            make_voice_gradio(text, speaker_to_voice[speaker], filename)
        elif speaker == "SPEAKER_99":
            try:
                tts = gTTS(text, lang=TRANSLATE_AUDIO_TO)
                tts.save(filename)
                print('Using GTTS')
            except:
                tts = gTTS('a', lang=TRANSLATE_AUDIO_TO)
                tts.save(filename)
                print('ERROR AUDIO GTTS')

        # duration
        duration_true = end - start
        duration_tts = librosa.get_duration(filename=filename)

        # porcentaje
        porcentaje = duration_tts / duration_true

        if porcentaje > 2.1:
            porcentaje = 2.1  
        elif porcentaje <= 1.2 and porcentaje >= 0.8:
            porcentaje = 1.0
        elif porcentaje <= 0.79:
            porcentaje = 0.8

        # Smoth and round
        porcentaje = round(porcentaje+0.0, 1)

        # apply aceleration or opposite to the audio file in audio2 folder
        os.system(f"ffmpeg -y -loglevel panic -i {filename} -filter:a atempo={porcentaje} audio2/{filename}")

        duration_create = librosa.get_duration(filename=f"audio2/{filename}")
        audio_files.append(filename)

    # replace files with the accelerates
    os.system("mv -f audio2/audio/*.ogg audio/")

    os.system(f"rm {Output_name_file}")

    create_translated_audio(result_diarize, audio_files, Output_name_file)

    os.system("rm audio_dub_stereo.wav")                        
    os.system("ffmpeg -i audio_dub_solo.wav -ac 1 audio_dub_stereo.wav")
                             
    #os.system(f"ffmpeg -i Video.mp4 -i {Output_name_file} -c:v copy -c:a copy -map 0:v -map 1:a -shortest {video_output}")

    os.system(f"rm {mix_audio}")
    #os.system(f'''ffmpeg -i {audio_wav} -i audio_dub_stereo.wav -filter_complex "[1:a]asplit=2[sc][mix];[0:a][sc]sidechaincompress=threshold=0.003:ratio=20[bg]; [bg][mix]amerge[final]" -map [final] {mix_audio}''')
    #os.system(f'ffmpeg -y -i {audio_wav} -i audio_dub_stereo.wav -filter_complex "[0:0][1:0] amix=inputs=2:duration=longest" -c:a libmp3lame {mix_audio}')
    os.system(f'ffmpeg -y -i audio.wav -i audio_dub_stereo.wav -filter_complex "[0:0]volume=0.15[a];[1:0]volume=1.90[b];[a][b]amix=inputs=2:duration=longest" -c:a libmp3lame {mix_audio}')
                             
    os.system(f"rm {video_output}")
    os.system(f"ffmpeg -i {OutputFile} -i {mix_audio} -c:v copy -c:a copy -map 0:v -map 1:a -shortest {video_output}")
        
    return video_output



import sys

class Logger:
    def __init__(self, filename):
        self.terminal = sys.stdout
        self.log = open(filename, "w")

    def write(self, message):
        self.terminal.write(message)
        self.log.write(message)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def isatty(self):
        return False

sys.stdout = Logger("output.log")

def read_logs():
    sys.stdout.flush()
    with open("output.log", "r") as f:
        
        if str(f.read())[:17] != "Model was trained":
            return f.read()


with gr.Blocks() as demo:
    gr.Markdown(title)
    gr.Markdown(description)
    gr.Markdown(tutorial)

    with gr.Tab("Translate audio from video"):
        with gr.Row():
            with gr.Column():
                video_input = gr.Video() # height=300,width=300
                
                gr.Markdown("Select the target language, and make sure to select the language corresponding to the speakers of the target language to avoid errors in the process.")  
                TRANSLATE_AUDIO_TO = gr.inputs.Dropdown(['en', 'fr', 'de', 'es', 'it', 'ja', 'zh', 'nl', 'uk', 'pt'], default='en',label = 'Translate audio to')
    
                gr.Markdown("Select how many people are speaking in the video.")
                min_speakers = gr.inputs.Slider(1, 6, default=1, label="min_speakers", step=1)
                max_speakers = gr.inputs.Slider(1, 6, default=2, label="max_speakers",step=1) 
                  
                gr.Markdown("Select the voice you want for each speaker.")
                tts_voice00 = gr.inputs.Dropdown(list_tts, default='en-AU-WilliamNeural-Male', label = 'TTS Speaker 1')
                tts_voice01 = gr.inputs.Dropdown(list_tts, default='en-CA-ClaraNeural-Female', label = 'TTS Speaker 2')
                tts_voice02 = gr.inputs.Dropdown(list_tts, default='en-GB-ThomasNeural-Male', label = 'TTS Speaker 3')
                tts_voice03 = gr.inputs.Dropdown(list_tts, default='en-GB-SoniaNeural-Female', label = 'TTS Speaker 4')
                tts_voice04 = gr.inputs.Dropdown(list_tts, default='en-NZ-MitchellNeural-Male', label = 'TTS Speaker 5')
                tts_voice05 = gr.inputs.Dropdown(list_tts, default='en-GB-MaisieNeural-Female', label = 'TTS Speaker 6')
    
                gr.Markdown("Default configuration of Whisper.")
                WHISPER_MODEL_SIZE = gr.inputs.Dropdown(['tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2'], default=whisper_model_default, label="Whisper model")
                batch_size = gr.inputs.Slider(1, 32, default=16, label="Batch size", step=1)
                compute_type = gr.inputs.Dropdown(list_compute_type, default=compute_type_default, label="Compute type")  
        
            with gr.Column(variant='compact'): 
                with gr.Row():
                    video_button = gr.Button("Translate audio of video", )
                with gr.Row():
                    video_output = gr.Video()


                gr.Examples(
                    examples=[
                        [
                            "./assets/Video_subtitled.mp4",
                            "base",
                            16,
                            "float32",
                            "en",
                            1,
                            2,
                            'en-AU-WilliamNeural-Male',
                            'en-CA-ClaraNeural-Female',
                            'en-GB-ThomasNeural-Male',
                            'en-GB-SoniaNeural-Female',
                            'en-NZ-MitchellNeural-Male',
                            'en-GB-MaisieNeural-Female',
                        ],
                    ],
                    fn=translate_from_video,
                    inputs=[
                    video_input,
                    WHISPER_MODEL_SIZE, 
                    batch_size,
                    compute_type, 
                    TRANSLATE_AUDIO_TO, 
                    min_speakers,
                    max_speakers,
                    tts_voice00,
                    tts_voice01,
                    tts_voice02,
                    tts_voice03,
                    tts_voice04,
                    tts_voice05,
                    ],
                    outputs=[video_output],
                    #cache_examples=True,
                )


    with gr.Tab("Translate audio from video link"):
        with gr.Row():
            with gr.Column():
                
                link_input = gr.Textbox(label="Media link. Example: www.youtube.com/watch?v=g_9rPvbENUw", placeholder="URL goes here...")
                #filename = gr.Textbox(label="File name", placeholder="best-vid")
                
                gr.Markdown("Select the target language, and make sure to select the language corresponding to the speakers of the target language to avoid errors in the process.")
                bTRANSLATE_AUDIO_TO = gr.inputs.Dropdown(['en', 'fr', 'de', 'es', 'it', 'ja', 'zh', 'nl', 'uk', 'pt'], default='en',label = 'Translate audio to')
        
                gr.Markdown("Select how many people are speaking in the video.")
                bmin_speakers = gr.inputs.Slider(1, 6, default=1, label="min_speakers", step=1)
                bmax_speakers = gr.inputs.Slider(1, 6, default=2, label="max_speakers",step=1) 
                  
                gr.Markdown("Select the voice you want for each speaker.")
                btts_voice00 = gr.inputs.Dropdown(list_tts, default='en-AU-WilliamNeural-Male', label = 'TTS Speaker 1')
                btts_voice01 = gr.inputs.Dropdown(list_tts, default='en-CA-ClaraNeural-Female', label = 'TTS Speaker 2')
                btts_voice02 = gr.inputs.Dropdown(list_tts, default='en-GB-ThomasNeural-Male', label = 'TTS Speaker 3')
                btts_voice03 = gr.inputs.Dropdown(list_tts, default='en-GB-SoniaNeural-Female', label = 'TTS Speaker 4')
                btts_voice04 = gr.inputs.Dropdown(list_tts, default='en-NZ-MitchellNeural-Male', label = 'TTS Speaker 5')
                btts_voice05 = gr.inputs.Dropdown(list_tts, default='en-GB-MaisieNeural-Female', label = 'TTS Speaker 6')
        
                gr.Markdown("Default configuration of Whisper.")
                bWHISPER_MODEL_SIZE = gr.inputs.Dropdown(['tiny', 'base', 'small', 'medium', 'large-v1', 'large-v2'], default=whisper_model_default, label="Whisper model")
                bbatch_size = gr.inputs.Slider(1, 32, default=16, label="Batch size", step=1)
                bcompute_type = gr.inputs.Dropdown(list_compute_type, default=compute_type_default, label="Compute type")
                
                # text_button = gr.Button("Translate audio of video")
                # link_output = gr.Video() #gr.outputs.File(label="Download!")



            with gr.Column(variant='compact'): 
                with gr.Row():
                    text_button = gr.Button("Translate audio of video")
                with gr.Row():
                    link_output = gr.Video() #gr.outputs.File(label="Download!") # gr.Video()

                gr.Examples(
                    examples=[
                        [
                            "https://www.youtube.com/watch?v=5ZeHtRKHl7Y",
                            "base",
                            16,
                            "float32",
                            "en",
                            1,
                            2,
                            'en-CA-ClaraNeural-Female',
                            'en-AU-WilliamNeural-Male',
                            'en-GB-ThomasNeural-Male',
                            'en-GB-SoniaNeural-Female',
                            'en-NZ-MitchellNeural-Male',
                            'en-GB-MaisieNeural-Female',
                        ],
                    ],
                    fn=translate_from_video,
                    inputs=[
                    link_input,
                    bWHISPER_MODEL_SIZE, 
                    bbatch_size,
                    bcompute_type, 
                    bTRANSLATE_AUDIO_TO, 
                    bmin_speakers,
                    bmax_speakers,
                    btts_voice00,
                    btts_voice01,
                    btts_voice02,
                    btts_voice03,
                    btts_voice04,
                    btts_voice05,
                    ],
                    outputs=[video_output],
                    #cache_examples=True,
                )


    
    with gr.Accordion("Logs"):
        logs = gr.Textbox()
        demo.load(read_logs, None, logs, every=1)

    # run
    video_button.click(translate_from_video, inputs=[
        video_input, 
        WHISPER_MODEL_SIZE, 
        batch_size,
        compute_type, 
        TRANSLATE_AUDIO_TO, 
        min_speakers,
        max_speakers,
        tts_voice00,
        tts_voice01,
        tts_voice02,
        tts_voice03,
        tts_voice04,
        tts_voice05,], outputs=video_output)
    text_button.click(translate_from_video, inputs=[
        link_input,
        bWHISPER_MODEL_SIZE, 
        bbatch_size,
        bcompute_type, 
        bTRANSLATE_AUDIO_TO, 
        bmin_speakers,
        bmax_speakers,
        btts_voice00,
        btts_voice01,
        btts_voice02,
        btts_voice03,
        btts_voice04,
        btts_voice05,], outputs=link_output)


demo.launch(enable_queue=True)




