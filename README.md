# naraka-midi-connector

This tool converts MIDI signals from a digital piano into keyboard keystrokes, allowing you to play instruments in the game NARAKA: BLADEPOINT.

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/QuynhVir/naraka-midi-connector.git
    ```
2. Navigate to the project directory:
    ```
    cd naraka-midi-connector
    ```
3. Install the required dependencies:
    ```
    pip install -r requirements.txt
    ```

## Building the Executable

Run the following command to build the executable:
```
pyinstaller 'Naraka MIDI Connector.spec'
```

The resulting executable will be located in the `dist` directory and named `Naraka MIDI Connector.exe`.

## Usage

1. Run the `Naraka MIDI Connector.exe` executable.
2. Select your MIDI device from the dropdown menu.
3. Select the base octave for your instrument.
4. Click the "Start" button to start listening for MIDI signals.
5. Play your MIDI instrument. The tool will convert the MIDI signals into keyboard keystrokes for the game.

## Pre-built Binary

A pre-built binary is available in the [latest release](https://github.com/QuynhVir/naraka-midi-connector/releases/latest) on GitHub.

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the terms of the MIT license.
