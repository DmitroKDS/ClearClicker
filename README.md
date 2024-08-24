---

# ClearClicker

ClearClicker is a desktop automation tool that allows users to record their mouse and keyboard actions and then repeat them at will. It is particularly useful for automating repetitive tasks on your computer.

## Key Features

- **Recording Actions**: ClearClicker records mouse movements, clicks, keyboard presses, and releases. It stores these actions in a sequence that can be replayed later.
- **Customizable Repetition**: Users can choose to repeat the recorded actions a specific number of times or for a set duration.
- **Interactive Interface**: The application provides a user-friendly interface built with Flet, where users can easily start recording actions, customize repetition settings, and control the playback of recorded actions.
- **Playback Control**: Users can start, stop, and customize the playback of recorded actions, ensuring that the automation behaves exactly as needed.

## How It Works

1. **Recording Moves**: When the "Record" button is pressed, ClearClicker starts recording all mouse and keyboard actions until the "Stop Record" button is clicked. The recorded actions are saved in a file for future playback.
2. **Replaying Actions**: Users can choose to replay the recorded actions by pressing the "Start" button. The actions are replayed in the same order and with the same timing as recorded, either a set number of times or for a specific duration.
3. **Customization**: The app allows users to set various parameters for repeating actions, such as the number of repetitions, the interval between actions, and whether to repeat by count or time.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/yourusername/ClearClicker.git
   ```

2. **Install the required packages**:
   ```bash
   pip install flet pynput
   ```

3. **Run the application**:
   ```bash
   python ClearClicker.py
   ```

## Requirements

- Python 3.x
- Flet
- Pynput

## Usage

- **Recording**: Click "Record" to start recording your mouse and keyboard actions. Click "Stop Record" when finished.
- **Playback**: Click "Start" to begin replaying the recorded actions. You can customize the repetition settings before starting playback.

---
