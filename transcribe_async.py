#!/usr/bin/env python

"""Google Cloud Speech API application using the REST API for async
batch processing.

Example usage:
    python transcribe_async.py res/sample.wav
"""

import argparse
import io
import os
import time


# [START speech_transcribe_async]
def transcribe_file(speech_file):
    """Transcribe the given audio file asynchronously."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    with io.open(speech_file, 'rb') as audio_file:
        content = audio_file.read()

    audio = types.RecognitionAudio(content=content)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_automatic_punctuation=True,
        use_enhanced=True,
        model='phone_call',
        speech_contexts=[
            types.SpeechContext(phrases=['we are releasing'])
            ]
        )

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = operation.result(timeout=90)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    output_file_name = speech_file + '.txt'
    with io.open(output_file_name, 'w', encoding='utf8') as output_file:
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            alternative = result.alternatives[0]
            output_file.write(alternative.transcript.strip())
            output_file.write(' Confidence: {}\n'.format(alternative.confidence))
# [END speech_transcribe_async]

# [START speech_transcribe_async_gcs]
def transcribe_gcs(gcs_uri):
    """Asynchronously transcribes the audio file specified by the gcs_uri."""
    from google.cloud import speech
    from google.cloud.speech import enums
    from google.cloud.speech import types
    client = speech.SpeechClient()

    audio = types.RecognitionAudio(uri=gcs_uri)
    config = types.RecognitionConfig(
        encoding=enums.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
        language_code='en-US',
        enable_automatic_punctuation=True,
        use_enhanced=True,
        model='phone_call',
        speech_contexts=[
            types.SpeechContext(phrases=['we are releasing'])
            ]
        )

    operation = client.long_running_recognize(config, audio)

    print('Waiting for operation to complete...')
    response = operation.result(900)

    # Each result is for a consecutive portion of the audio. Iterate through
    # them to get the transcripts for the entire audio file.
    output_file_name = os.path.basename(gcs_uri) + '.txt'
    with io.open(output_file_name, 'w', encoding='utf8') as output_file:
        for result in response.results:
            # The first alternative is the most likely one for this portion.
            alternative = result.alternatives[0]
            output_file.write(alternative.transcript.strip())
            output_file.write(' Confidence: {}\n'.format(alternative.confidence))
# [END speech_transcribe_async_gcs]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        'path', help='File or GCS path for audio file to be recognized')
    args = parser.parse_args()
    if args.path.startswith('gs://'):
        transcribe_gcs(args.path)
    else:
        transcribe_file(args.path)
