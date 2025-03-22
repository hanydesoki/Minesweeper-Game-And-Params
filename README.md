# Minesweeper game with parameters

## What is it about

Classic minesweeper + game parameter management fully implemented with the  pygame module.

## Features:

  - Minesweeper game with a timer:
      The goal is to clear every tiles that doesn't hide a bomb. To do so, we uncover the tiles by clicking on them.
      The number showing up on a tile indicate the number of mines surrounding that tile. We can indicate with a flag
      a mine position by right clicking on the suspected tile (it is not a requierement but it will help the player).
    
      Also the 'Chording' mechanic is implemented: Holding right click (or CTRL) on a revealed tile with a number on it will
      highlight all the non revealed surrounding tiles. If the number of flags within these tiles match the number of surrounding mines,
      it will automatically reveal all the non flag tiles.

      <img width="500px" src="https://github.com/hanydesoki/Minesweeper-Game-And-Params/blob/main/Screen_and_illustratons/chording_feature.PNG"></img>
   
  - Parameter menu which control every aspect of the game:

      <img width="500px" src="https://github.com/hanydesoki/Minesweeper-Game-And-Params/blob/main/Screen_and_illustratons/parameter_menu.PNG"></img>
    
      - Number of rows / cols
      - Number of mines
      - Difficulty options to get preset options: Beginner, Intermediate, Expert
      - Option to guarantee an empty field on the first click
      - Show tile position (more for debugging than for player)
      - Help and Cheats:
         - Show mine locations
           
          <img width="500px" src="https://github.com/hanydesoki/Minesweeper-Game-And-Params/blob/main/Screen_and_illustratons/show_bomb_features.PNG"></img>
         - Show empty fields
       
          <img width="500px" src="https://github.com/hanydesoki/Minesweeper-Game-And-Params/blob/main/Screen_and_illustratons/show_empty_field_feature.PNG"></img>
         - Show surrounding tiles of mouse position (helpful for counting tiles around the targeted tile)
       
          <img width="500px" src="https://github.com/hanydesoki/Minesweeper-Game-And-Params/blob/main/Screen_and_illustratons/show_surrounding_tiles_features.PNG"></img>

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
  
  The parameter menu is coded to be easy to create and manage in any pygame project. Made the **ParametersMenu** class (parameters_menu.py) a very high 
  level interface:

  - Provide a list of parameters. Each type of parameter has its own class with all of the needed parameters.
  
  - No need to specify any screen coordinates neither for the parameters or the menu itself (only "top", "left", "right", "bottom" and menu size)
    the class will manage those elements itself.
    
  - Each parameter will have a key label and will generate the associated widget.
  
  - Once the menu instanciated, it will need to be updated (with the **update** and **draw** method) for each frame of the game loop to be fully functionnal. From 
    here, we can access every parameter directly with the label key passed associated with the parameter.
    
  - We will also be able to track all the parameters that are changing during this frame using the **value_changes** attribute.

  - We can access at any moment any widget in the menu. All of the widget parameter can be modified during the game loop using some method. The common one
    is **set_value**.

  ```py
    # Example of code with parameter menu. It is a very simplified version of a section of the minesweeper code.

    NUMBER_ROWS: int = 10
    NUMBER_COLS: int = 10

    parameter_menu: ParametersMenu = ParametersMenu(
            parameters=[
                CheckBox("guaranted_patch", default_value=True, label_display="Guaranted empty field first click"),
                CheckBox("show_surrounding", label_display="Highlight surrounding tiles"),
                Slider("number_mines", default_value=25, min_value=3, max_value=99, interval=1, label_display="Number of mines", value_format=lambda x: str(int(x))),
                SegmentedControl(
                    "difficulty", 
                    default_value=["beginner"], 
                    available_options_raw=["beginner", "intermediate", "expert"],
                    available_options_display=["Beginner", "Intermediate", "Expert"],
                    require_selection=True,
                    allow_multiselection=False,
                    label_display"Difficulty"
                )
            ], 
            screen_position="bottom",
            size=300
        )

    game_loop: bool = True

    while game_loop:

        ...

        parameter_menu.update()

        # Exemple: access to the "number_mines" parameter
        number_mines = parameter_menu["number_mines"]

        all_changes: dict = parameter_menu.value_changes # dictionnary containing all the parameters
                                                         # that change with also the old value and new value provided

        # Change number of mines slider max value when guaranted empty field option change
        if all_changes.get("guaranted_patch", None) is not None:
            number_mine_widget = parameter_menu.widgets["guaranted_patch"]
            number_mine_widget.set_max_value(NUMBER_ROWS * NUMBER_COLS - (9 if parameter_menu["guaranted_patch"] else 1))
        
        parameter_menu.draw()
        
  ```

  ### Widget implemented

  - **Checkbox**: Switch on and off
  - **Slider**: Slide a value between a min and a max value. All of theses 3 values can be set at any moment in the game loop.
  - **Segmented control**: Option tabs that can be selected: Can allow or not multi selection + one minimum option requiered or not.

  ## Future improvements / fixes

  - Save personal best game time (only for preset difficulty settings) and settings in a json file and showing them in the game.
  - Unexpected behaviour: Resetting a game with SPACE when we activated a cheat before will not recheck if options are matching any difficulty.
    The difficulty option segmented control will still be empty even if it is matching one of them.
  - Improve performances: Still drawing tiles even when they are covered ...
  - Improve display
  - More options to generate the parameter menu (widget colors, size etc...)
    

  
  
