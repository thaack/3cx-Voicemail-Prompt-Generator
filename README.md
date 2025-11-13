# 3CX Voicemail Prompt Generator

Generate personalized voicemail prompts using Amazon Polly and convert them to 3CX-compatible WAV format.

## Requirements

- Python 3.6+
- FFmpeg
- AWS Account with Polly access
- boto3 Python library

## Installation

1. **Install FFmpeg**
   - **macOS**: `brew install ffmpeg`
   - **Ubuntu/Debian**: `sudo apt-get install ffmpeg`
   - **Windows**: Download from [ffmpeg.org](https://ffmpeg.org/download.html)

2. **Install Python dependencies**
   ```bash
   pip install boto3
   ```

3. **Configure AWS credentials**
   ```bash
   aws configure
   ```
   Enter your AWS Access Key ID, Secret Access Key, and region.

## Usage

### Generate prompts for all users from CSV

```bash
python voicemail_generator.py -i users.csv
```

**CSV Format:**
```csv
firstname,lastname
John,Doe
Jane,Smith
Michael,Johnson
```

### Generate prompt for a single user

```bash
python voicemail_generator.py -f John -l Doe
```

### Use a custom greeting

```bash
python voicemail_generator.py -i users.csv -g "Hi, you've reached {firstname} {lastname}. I'm unavailable. Please leave a detailed message."
```

**Note:** Use `{firstname}` and `{lastname}` as placeholders in your greeting template.

### Use a different Polly voice

```bash
python voicemail_generator.py -f Jane -l Smith -v Matthew
```

**Popular voices:**
- Joanna (US Female) - Default
- Matthew (US Male)
- Amy (British Female)
- Brian (British Male)
- Salli (US Female)

[Full voice list](https://docs.aws.amazon.com/polly/latest/dg/voicelist.html)

### Specify output directory

```bash
python voicemail_generator.py -i users.csv -o /path/to/output
```

## Command-Line Options

| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `--input` | `-i` | CSV file with user data | - |
| `--firstname` | `-f` | First name (single user mode) | - |
| `--lastname` | `-l` | Last name (single user mode) | - |
| `--greeting` | `-g` | Custom greeting template | "You have reached {firstname} {lastname}. Please leave a message after the tone." |
| `--output` | `-o` | Output directory | wav_output_3cx |
| `--voice` | `-v` | Amazon Polly voice ID | Joanna |

## Examples

### Basic batch processing
```bash
python voicemail_generator.py -i employees.csv
```

### Single user with custom message
```bash
python voicemail_generator.py -f Sarah -l Connor -g "{firstname} {lastname} is not available. Leave your name and number."
```

### Different voice and output location
```bash
python voicemail_generator.py -i users.csv -v Matthew -o /mnt/pbx/greetings
```

### Professional greeting
```bash
python voicemail_generator.py -i team.csv -g "Thank you for calling {firstname} {lastname}. I'm unable to take your call right now. Please leave a detailed message and I'll return your call as soon as possible."
```

## Output

The script generates WAV files with the following specifications (3CX compatible):
- **Format:** PCM 16-bit
- **Sample Rate:** 8 kHz
- **Channels:** Mono
- **Naming:** `Firstname_Lastname.wav`

## Uploading to 3CX

1. Log into 3CX Management Console
2. Navigate to **Users** → Select user → **Voicemail**
3. Click **Upload** under "Greeting Message"
4. Select the generated WAV file
5. Click **OK** to save

## Troubleshooting

**"Error: ffmpeg not found"**
- Ensure FFmpeg is installed and in your system PATH

**"Error: AWS Polly failed - Unable to locate credentials"**
- Run `aws configure` and enter your credentials
- Verify IAM user has `AmazonPollyReadOnlyAccess` permission

**"Error: CSV file not found"**
- Check the file path and ensure the CSV exists
- Use absolute path if necessary: `-i /full/path/to/users.csv`

## License

Apache 2.0 - Free to use and modify.
