#!/usr/bin/env python3
"""
3CX Voicemail Prompt Generator
Generates personalized voicemail prompts using Amazon Polly and converts them to 3CX-compatible format.
"""

import subprocess
import os
import csv
import argparse
from pathlib import Path
import boto3
from botocore.exceptions import ClientError, NoCredentialsError


DEFAULT_GREETING = "You have reached {firstname} {lastname}. Please leave a message after the tone."


def generate_polly_audio(text, output_file, voice_id='Joanna'):
    """Generate audio from text using Amazon Polly."""
    try:
        polly = boto3.client('polly')
        response = polly.synthesize_speech(
            Text=text,
            OutputFormat='pcm',
            VoiceId=voice_id,
            SampleRate='8000'
        )
        
        with open(output_file, 'wb') as f:
            f.write(response['AudioStream'].read())
        return True
    except (ClientError, NoCredentialsError) as e:
        print(f"Error: AWS Polly failed - {str(e)}")
        return False


def convert_to_3cx_format(input_file, output_file):
    """Convert audio to 3CX-compatible WAV format (Mono, 8kHz, 16-bit PCM)."""
    try:
        subprocess.run([
            'ffmpeg',
            '-f', 's16le',
            '-ar', '8000',
            '-ac', '1',
            '-i', input_file,
            '-acodec', 'pcm_s16le',
            '-ar', '8000',
            '-ac', '1',
            '-y',
            output_file
        ], check=True, capture_output=True, text=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error: FFmpeg conversion failed - {e.stderr}")
        return False
    except FileNotFoundError:
        print("Error: ffmpeg not found. Install ffmpeg and add to PATH.")
        return False


def process_user(firstname, lastname, greeting_template, output_dir, voice_id):
    """Generate voicemail prompt for a single user."""
    greeting = greeting_template.format(firstname=firstname, lastname=lastname)
    
    temp_file = os.path.join(output_dir, f"{firstname}_{lastname}_temp.pcm")
    output_file = os.path.join(output_dir, f"{firstname}_{lastname}.wav")
    
    print(f"Processing: {firstname} {lastname}")
    
    if not generate_polly_audio(greeting, temp_file, voice_id):
        return False
    
    if not convert_to_3cx_format(temp_file, output_file):
        os.remove(temp_file)
        return False
    
    os.remove(temp_file)
    print(f"Created: {output_file}")
    return True


def process_csv(csv_file, greeting_template, output_dir, voice_id):
    """Process all users from CSV file."""
    try:
        with open(csv_file, 'r') as f:
            reader = csv.reader(f)
            next(reader, None)  # Skip header if present
            
            success = 0
            failed = 0
            
            for row in reader:
                if len(row) < 2:
                    continue
                    
                firstname, lastname = row[0].strip(), row[1].strip()
                if firstname and lastname:
                    if process_user(firstname, lastname, greeting_template, output_dir, voice_id):
                        success += 1
                    else:
                        failed += 1
            
            print(f"\nCompleted: {success} successful, {failed} failed")
            return True
            
    except FileNotFoundError:
        print(f"Error: CSV file '{csv_file}' not found")
        return False
    except Exception as e:
        print(f"Error: {str(e)}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Generate 3CX voicemail prompts using Amazon Polly',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  Generate prompts for all users in CSV:
    python voicemail_generator.py -i users.csv

  Generate prompt for one user:
    python voicemail_generator.py -f John -l Doe

  Use custom greeting:
    python voicemail_generator.py -i users.csv -g "Hi, this is {firstname}. Leave a message."

  Use different voice:
    python voicemail_generator.py -f Jane -l Smith -v Matthew
        """
    )
    
    parser.add_argument('-i', '--input', help='CSV file with firstname,lastname columns')
    parser.add_argument('-f', '--firstname', help='First name for single user')
    parser.add_argument('-l', '--lastname', help='Last name for single user')
    parser.add_argument('-g', '--greeting', default=DEFAULT_GREETING,
                       help='Greeting template (use {firstname} and {lastname} placeholders)')
    parser.add_argument('-o', '--output', default='wav_output_3cx',
                       help='Output directory (default: wav_output_3cx)')
    parser.add_argument('-v', '--voice', default='Joanna',
                       help='Polly voice ID (default: Joanna)')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not args.input and not (args.firstname and args.lastname):
        parser.error("Either --input CSV file or both --firstname and --lastname required")
    
    if args.firstname and not args.lastname:
        parser.error("--lastname required when using --firstname")
    
    if args.lastname and not args.firstname:
        parser.error("--firstname required when using --lastname")
    
    # Create output directory
    os.makedirs(args.output, exist_ok=True)
    
    # Process single user or CSV
    if args.firstname and args.lastname:
        process_user(args.firstname, args.lastname, args.greeting, args.output, args.voice)
    else:
        process_csv(args.input, args.greeting, args.output, args.voice)


if __name__ == "__main__":
    main()