# Speech Transcription Demo

This Python script provides a demonstration of speech transcription using the AssemblyAI API and a Gradio interface. The script transcribes both uploaded audio files and recorded voice input, including optional speaker labels based on user preference.

## Requirements
Make sure to install the required Python libraries using the following command:

```bash
pip install -r requirements.txt
```

## Configuration
- Add your AssemblyAI API key to the `.env` file:

    ```env
    ASSEMBLYAI_API_KEY="your_assemblyai_api_key"
    ```

## Usage
1. Run the script ( your CMD should be at the same path where the directory deliverable is ):

    ```bash
    python app.py
    ```

2. The Gradio interface will be launched, allowing you to choose an audio file for transcription or record your voice.

3. Choose an audio file using the provided interface or click the record button to record your voice.

4. Toggle the checkbox to include speaker labels in the transcription.

5. The script will transcribe the speech and display the formatted output with speaker labels if enabled.

## Code Explanation
- The `transcribe` function uses the AssemblyAI Python SDK to transcribe the provided audio.
- The Gradio interface is configured with options for both uploading an audio file and recording voice input.
- Custom CSS is included to enhance the styling of the Gradio interface.

## Gradio Interface
- **Input:**
  - Audio file (choose a file using the file uploader) or record voice
  - Checkbox for enabling/disabling speaker labels
- **Output:**
  - Transcription result displayed as formatted text
