# Minesweeper game with parameters

## What is it about

Classic minesweeper + game parameter management fully implemented with the  pygame module.

## Features:

  - Minesweeper game with a timer
  - Parameter menu which control every aspect of the game:
    
      - Number of rows / cols
      - Number of mines
      - Difficulty options to get preset options: Beginner, Intermediate, Expert
      - Option to guarantee an empty field on the first click
      - Show tile position (more for debugging than for player)
      - Help and Cheats:
         - Show bomb locations
         - Show empty fields
         - Show surrounding tiles of mouse position (helpful for counting tiles around the targeted tile)

  ## Behaviour
  
  To open the parameter menu, click on the bottom of the screen. These parameters will automatically reset game on change:

  - Number of columns
  - Number of rows
  - Number of mines
  - Difficulty options
  - Guaranted empty field first click

  Pressing SPACE at anytime will reset the game. Bombs are generated only after the first click to prevent losing instantly.

  Changing difficulty option in the segmented control will pick a preset of parameters (Future improvement will be to
  save your personal best game time only when a difficulty option is selected). When modifying the options, the menu will
  check if it is matching to one of the difficulty settings and activate it if it is the case, otherwise it will be deactivated. 
  Activate one of the help / cheat option will deactivate the difficulty option until game is over or reset (even when we deactivate the cheat).

  Number of mines slider max value is adapting depending on the grid size and also the "Guaranted empty field first click" option.

  ## Parameter menu

  ### Goal: Very high level code and flexible!
  
  The parameter menu is coded to be easy to create and manage in any pygame project. Made the ParameterMenu class a very high 
  level interface:

  - Provide a list of parameters. Each type of parameter has its own class with all of the needed parameters.
  
  - No need to specify any screen coordinates neither for the parameters or the menu itself (only "top", "left", "right", "bottom" and menu size)
    the class will manage those elements itself.
    
  - Each parameter will have a key label and will generate the associated widget.
  
  - Once the menu instanciated, it will need to be updated (with the update method) for each frame of the game loop to be fully functionnal. From 
    here, we can access every parameter directly with the label key passed associated with the parameter (Ex: number_mines = parameter_menu["number_mines"])
    
  - We will also be able to track all the parameters that are changing during this frame using the value_changes attribute.

  - We can access at any moment any widget in the menu. All of the widget parameter can be modified during the game loop using some method. The common one
    is set_value.

  ### Widget implemented

  - **Checkbox**: Switch on and off
  - **Slider**: Slide a value between a min and a max value. All of theses 3 values can be set at any moment in the game loop.
  - **Segmented control**: Option tabs that can be selected: Can allow or not multi selection + one minimum option requiered or not.

  ## Future improvements / fixes

  - Save personal best game time (only for preset difficulty settings) and settings in a json file and getting showing them in the game.
  - Unexpected behaviour: Resetting a game with SPACE when we activated a cheat before will not recheck if options are matching any difficulty.
    The difficulty option segmented control will still be empty even if it is matching one of them.
  - Improve performances: Still drawing tiles even when they are covered ...
  - Improve display
  - More options to generate the parameter menu (widget colors, size etc...)
    

  
  