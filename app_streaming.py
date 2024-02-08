import gradio as gr
import assemblyai as aai
from dotenv import load_dotenv
import os
from functions.read_vocab import read_custom_vocabulary
from functions.load_template import load_template
from openai import OpenAI
import tempfile
import soundfile as sf  # Import the soundfile library
import numpy as np
# Load environment variables from .env file
load_dotenv()

# Set your AssemblyAI API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# 
# Global variables to store the accumulated audio data and its streaming rate
audio_data = None
streaming_rate = None


def capture_audio(stream, new_chunk): 
    global audio_data
    global streaming_rate

    # Extract sampling rate and audio chunk, normalize the audio
    sr, y = new_chunk
    streaming_rate = sr
    y = y.astype(np.float32)
    y /= np.max(np.abs(y))

    # Concatenate new audio chunk to the existing stream or start a new one
    if stream is not None:
        stream = np.concatenate([stream, y])
    else:
        stream = y

    # Update the global variable with the new audio data
    streaming_tuple = (streaming_rate, stream)
    audio_data = stream
    return stream, streaming_tuple

def transcribe( Allow, Number_Speakers): 
    try:
        global audio_data        
        print("audio_data", audio_data)

        # list_of_custom_vocab=read_custom_vocabulary("data/Vocabulary Dataset.xlsx")

        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
        #   word_boost=list_of_custom_vocab,
        #   boost_param="high",
          speaker_labels=Allow,
          speakers_expected= int(Number_Speakers)
        )

        global streaming_rate

        # Transcribe the audio data if available
        if audio_data is not None and streaming_rate is not None:
            temp_wav_path = tempfile.mktemp(suffix=".wav")
            sf.write(temp_wav_path, audio_data, streaming_rate)
            transcript = transcriber.transcribe(temp_wav_path, config)
 

        if transcript == None:
            return transcript.error

        # Initialize a list to store the formatted output
        result = []
        # Loop through each utterance and format the output
        for utterance in transcript.utterances:
            result.append(f"Speaker {utterance.speaker}: {utterance.text}")

        # Return the formatted result as a string
        return "\n".join(result)

    except Exception as e:
        # Handle exceptions (e.g., API errors) and return an error message
        return f"Error: {str(e)}"
    
def generate_gpt(template_name, transcription):
    prompt, template = load_template(template_name, "config.json")
    client = OpenAI(
    # This is the default and can be omitted
    api_key=os.environ.get("OPENAI_API_KEY"),
        )
    try:
        response =  client.chat.completions.create(
            messages=[
                {"role": "system", "content": "You are an expert in medical summarisation and report creation, vital for doctors who depend on you to accurately condense conversations with patients into summaries. Strive for excellence to meet their needs, as your work is crucial to their careers."},
                {"role": "user", "content": prompt + transcription + template}
            ],
            model="gpt-4-turbo-preview",
                temperature=0.3
        )
 
        return response.choices[0].message.content
    except Exception as e:
        print(f"An error occurred: {str(e)}")

with gr.Blocks() as demo:
    
    
    gr.Markdown(
    """
    # Ambient Clinical Documentation MVP
    This application allows you to record real-time patient-doctor consultations to generate structured summaries as clerking, clinical, or SOAP notes. 
    Please wait at least 30s before transcribing to allow the audio recording to be processed.
    """)

    state = gr.State()
    audio = gr.Audio(label="Start recording", sources=["microphone"], streaming=True, type="numpy")

    out = gr.Audio(label="The recorded audio")
    with gr.Row():
        Allow=gr.Checkbox(label="Allow diarisation", value=True, info="Select to allow speaker diarisation", show_label=False)
        Number_Speakers= gr.Number(label="Number_Speakers", minimum=1, maximum=10, step=1, info="Number of speakers", show_label=False, value=1)
    transcribe_btn = gr.Button(value="Transcribe")
    transcription = gr.Textbox(value="", label="Transcription", interactive=True)
    transcribe_btn.click(transcribe, inputs=[Allow, Number_Speakers], outputs=[transcription])
    # Streaming setup to handle real-time audio capture
    audio.stream(fn=capture_audio, inputs=[state, audio], outputs=[state, out])
    with gr.Row():
        template=gr.Dropdown(
                ["Clerking Note", "Clinic Letter", "SOAP Note"], label="Templates", info="Please choose the summary template"
            )
        summarise_btn = gr.Button(value="Summarise")
    summary = gr.Textbox(value="", label="Summary", interactive=True)
    summarise_btn.click(generate_gpt, inputs=[template,transcription ], outputs=[summary])

if __name__ == "__main__":
    demo.launch(debug=True, share=True)


