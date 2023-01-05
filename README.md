# digiscoreDobot
Digital Score experimental with Dobot Magician Lite


## Quick Start

Run 

    main.py

## About main.py
The main script to start the robot arm drawing digital score work.
Digibot calls the local interpretor for project specific functions.
This communicates directly to the pydobot library.
Nebula kick starts the AI Factory for generating NNet data and affect flows.
This script also controls the live mic audio analyser.

Args:
    
    duration_of_piece: the duration in seconds of the drawing
        
    continuous_line: Bool: True = will not jump between points
        
    speed: int the dynamic tempo of the all processes. 1 = slow, 5 = fast
