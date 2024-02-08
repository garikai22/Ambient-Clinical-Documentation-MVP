import gradio as gr
import assemblyai as aai
from dotenv import load_dotenv
import os
from functions.read_vocab import read_custom_vocabulary
from functions.load_template import load_template
from openai import OpenAI
import tempfile
import soundfile as sf  # Import the soundfile library
# Load environment variables from .env file
load_dotenv()

# Set your AssemblyAI API key
aai.settings.api_key = os.getenv("ASSEMBLYAI_API_KEY")

# 

def transcribe(audio_path, Allow, Number_Speakers): 
    try:        
        print("audio_path", audio_path)

        # list_of_custom_vocab=read_custom_vocabulary("data/Vocabulary Dataset.xlsx")

        transcriber = aai.Transcriber()
        config = aai.TranscriptionConfig(
        #   word_boost=list_of_custom_vocab,
        #   boost_param="high",
          speaker_labels=Allow,
          speakers_expected= int(Number_Speakers)
        )

        # Perform the transcription
        if isinstance(audio_path, tuple) and len(audio_path) == 2:
            # Assuming audio_path is a tuple (sample_rate, audio_data)
            sr, y = audio_path
            # User recorded audio, save it to a temporary WAV file using soundfile
            temp_wav_path = tempfile.mktemp(suffix=".wav")
            sf.write(temp_wav_path, y, sr)
            transcript = transcriber.transcribe(temp_wav_path, config)
            # Remove the temporary file after transcription
            os.remove(temp_wav_path)

        elif isinstance(audio_path, str):
            # User uploaded a file, use the file path directly
            transcript = transcriber.transcribe(audio_path, config)
        else:
            return "The audio is being processed, please try again"

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
                {"role": "system", "content": "You are an expert medical summariser and report builder, doctores relies on you on creating summaries of their conversation with patients. do your best to satisfy their needs since it is important to their carreers."},
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
    # Speech Transcription Demo!
    Transcribe speech and include speaker labels if desired.
    """)


    filepath = gr.Audio()

    with gr.Row():
        Allow=gr.Checkbox(label="Allow diarisation", value=True, info="check allow for speaker diarisation", show_label=False)
        Number_Speakers= gr.Number(label="Number_Speakers", minimum=1, maximum=10, step=1, info="number of speakers", show_label=False, value=1)
    transcribe_btn = gr.Button(value="Transcribe")
    transcription = gr.Textbox(value="", label="Transcription", interactive=True)
    transcribe_btn.click(transcribe, inputs=[filepath, Allow, Number_Speakers], outputs=[transcription])
    with gr.Row():
        template=gr.Dropdown(
                ["Clerking", "Clinic", "SOAP"], label="Templates", info="Please choose the summary template"
            )
        summarise_btn = gr.Button(value="summarise")
    summary = gr.Textbox(value="", label="summary", interactive=True)
    summarise_btn.click(generate_gpt, inputs=[template,transcription ], outputs=[summary])

if __name__ == "__main__":
    demo.launch(debug=True, share=True)
