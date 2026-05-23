# File36

A file-transfer-over-audio utility, aka a slow modem. 

## Usage

```
file36 <command> [options]
```

### Commands

**play** - Encode some input and play audio

```
file36 play [-t|-f|-b] <input> [--visualize] [--volume INTEGER] [--speed TEXT] [--save]
```

| Flag | Description |
|------|-------------|
| `-t`, `--text` | Encode and play a text string |
| `-f`, `--file` | Encode and play a file from the specified file path |
| `-b`, `--bytes` | Encode and play raw bytes (input hex) |
| `--visualize` | Show a spectrogram alongside audio playback |
| `-v`, `--volume` | Volume from 1 to 100 (default: 5 to avoid hearing damage) |
| `--speed` | Transmission speed (`SLOW`, `FAST`, etc.) |
| `--save` | Export the played audio as a WAV file |

**receive** - Listen for and decode audio (WIP)

```
file36 receive [--save]
```

| Flag | Description |
|------|-------------|
| `--save` | Save the received data |

### Examples

```
file36 play -t "hello, modem"
file36 play -f ./top-secret.txt --visualize
file36 play -b deadbeef --volume 80 --speed FAST --save
file36 receive # WIP
file36 receive --save # WIP
```