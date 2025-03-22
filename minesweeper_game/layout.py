import pygame

from .settings import (
                        BACKGROUND_COLOR,
                        # TILE_SIZE,
                        UNCOVERED_TILE_COLOR, 
                        COVERED_TILE_COLOR,
                        TOP_COVERED_TILE_COLOR,
                        MINE_COLOR, 
                        PROXIMITY_COLOR_PALETTE,
                    )
from .parameters_menu import ParametersMenu, Slider
from .range_picker import RangePicker
from .parameters_menu import ParametersMenu, CheckBox, Slider, SegmentedControl, SliderWidget, ParameterWidget, SegmentedControlWidget


import random
import time
from typing import Generator


class Layout:

    TILE_SIZES: RangePicker = RangePicker({
        4: 30,
        20: 25,
        25: 20
    })

    DIFFUCULTY: dict = {
        "beginner": {
            "show_bombs": False,
            "show_patches": False,
            # "show_tile_pos": False,
            "show_surrounding": False,
            "number_cols": 9.0,
            "number_rows": 9.0,
            "number_mines": 10.0,
            "guaranted_patch": True,
        },
        "intermediate": {
            "show_bombs": False,
            "show_patches": False,
            # "show_tile_pos": False,
            "show_surrounding": False,
            "number_cols": 16.0,
            "number_rows": 16.0,
            "number_mines": 40.0,
            "guaranted_patch": True,
        },
        "expert": {
            "show_bombs": False,
            "show_patches": False,
            # "show_tile_pos": False,
            "show_surrounding": False,
            "number_cols": 30.0,
            "number_rows": 16.0,
            "number_mines": 99.0,
            "guaranted_patch": True,
        }
    }

    def __init__(self, grid_size: tuple[int, int], number_mines: int) -> None:

        self.grid_size: tuple[int, int] = grid_size
        self.number_mines: int = number_mines

        self.screen: pygame.Surface = pygame.display.get_surface()

        self.parameter_menu: ParametersMenu = ParametersMenu(
            parameters=[
                CheckBox("show_bombs",label_display="Show bombs"),
                CheckBox("show_patches", label_display="Show empty field"),
                CheckBox("show_tile_pos", label_display="Show tile positions"),
                CheckBox("show_surrounding", label_display="Highlight surrounding tiles"),
                Slider("number_cols", 15, 4, 30, 1, label_display="Number of columns", value_format=lambda x: str(int(x))),
                Slider("number_rows", 10, 4, 16, 1, label_display="Number of rows", value_format=lambda x: str(int(x))),
                Slider("number_mines", 25, 3, 99, 1, label_display="Number of mines", value_format=lambda x: str(int(x))),
                CheckBox("guaranted_patch", default_value=True, label_display="Guaranted empty field first click"),
                SegmentedControl(
                    "difficulty", 
                    [], 
                    ["beginner", "intermediate", "expert"],
                    ["Beginner", "Intermediate", "Expert"],
                    True,
                    False,
                    "Difficulty"
                    )
            ], 
            screen_position="bottom",
            size=self.screen.get_height() // 2
        )

        self.mine_grid: list[list[int]] = []
        self.proximity_grid: list[list[int]] = []
        self.cover_grid: list[list[int]] = []
        

        self.uncover_groups: list[list[tuple[int, int]]] = []
        self.unvalid_chord_tiles: list[tuple[int, int]] = []

        self.grid_topleft: tuple[int, int] = (
            self.screen.get_width() // 2 - (self.grid_size[1] * self.TILE_SIZES[max(self.grid_size)]) // 2,
            self.screen.get_height() // 2 - (self.grid_size[0] * self.TILE_SIZES[max(self.grid_size)]) // 2
        )

        self.proximity_font = pygame.font.SysFont("Arial", self.TILE_SIZES[max(self.grid_size)] // 2, True)
        self.ui_font = pygame.font.SysFont("Arial", 20, True)

        self.flag_pole_surf: pygame.Surface = self.generate_flag_pole_surface(
            int(0.7 * self.TILE_SIZES[max(self.grid_size)]),
            TOP_COVERED_TILE_COLOR
        )
        

        self.game_over: bool = False
        self.win: bool = False
        self.lost: bool = False
        self.bomb_clicked: tuple[int, int] | None = None
        self.first_move: bool = True
        self.cheat_activated: bool = False
        self.start_time: int = time.time()
        self.game_over_time: int | None = None
        
        self.ignore_cheat_check: bool = False

        self.initiate_grid()


    def initiate_grid(self) -> None:

        self.grid_topleft: tuple[int, int] = (
            self.screen.get_width() // 2 - (self.grid_size[1] * self.TILE_SIZES[max(self.grid_size)]) // 2,
            self.screen.get_height() // 2 - (self.grid_size[0] * self.TILE_SIZES[max(self.grid_size)]) // 2
        )

        self.mine_grid.clear()
        self.proximity_grid.clear()
        self.cover_grid.clear()

        self.uncover_groups.clear()

        self.game_over: bool = False
        self.win: bool = False
        self.lost: bool = False
        self.bomb_clicked = None
        self.first_move: bool = True
        self.cheat_activated: bool = False
        self.start_time: int = time.time()
        self.game_over_time: int | None = None

        for _ in range(self.grid_size[0]):
            self.proximity_grid.append([0 for __ in range(self.grid_size[1])])
            self.cover_grid.append([1 for __ in range(self.grid_size[1])])
        
        # print(self.uncover_groups, len(self.uncover_groups))
  
        # self.draw()

    def place_mines_and_proximity_values(self, excluded_tile_coords: tuple[int, int]):
        
        excluded_tile_pos: int = excluded_tile_coords[0] * self.grid_size[1] + excluded_tile_coords[1]
        excluded_tile_positions: list[int] = [excluded_tile_pos]

        # Exclude surrounding coords to guarente a patch
        if self.parameter_menu["guaranted_patch"]:
            excluded_tile_positions.extend([
                excluded_tile_pos - 1,
                excluded_tile_pos + 1,
                excluded_tile_pos - self.grid_size[1] - 1,
                excluded_tile_pos - self.grid_size[1],
                excluded_tile_pos - self.grid_size[1] + 1,
                excluded_tile_pos + self.grid_size[1] - 1,
                excluded_tile_pos + self.grid_size[1],
                excluded_tile_pos + self.grid_size[1] + 1,
            ])
        # Mine positions
        mine_positions: list[int] = random.sample(
            population=list(pos for pos in range(0, self.grid_size[0] * self.grid_size[1]) if pos not in excluded_tile_positions),
            k=self.number_mines
        )

        for row_index in range(self.grid_size[0]):
            row_values: list[int] = []
            for col_index in range(self.grid_size[1]):
                tile_pos: int = row_index * self.grid_size[1] + col_index
                # print(tile_pos)
                row_values.append(int(tile_pos in mine_positions))
            
            self.mine_grid.append(row_values)
            
            
        
        # Proximity grid
        for row_index in range(self.grid_size[0]):
            for col_index in range(self.grid_size[1]):
                if self.mine_grid[row_index][col_index]:
                    continue
                for (d_row_index, d_col_index) in [(0, 1), (1, 1), (1, 0), (-1, 0), (-1, -1), (0, -1), (-1, 1), (1, -1)]:
                    try:
                        prox_row_index: int = row_index + d_row_index
                        prox_col_index: int = col_index + d_col_index
                        if prox_col_index < 0 or prox_row_index < 0:
                            continue
                        self.proximity_grid[row_index][col_index] += self.mine_grid[prox_row_index][prox_col_index]
                    except IndexError:
                        pass
        
        # Generate uncover groups
        for row_index in range(self.grid_size[0]):
            for col_index in range(self.grid_size[1]):
                if (row_index, col_index) not in sum(self.uncover_groups, start=[]):
                    group: list[tuple[int, int]] = self.get_zeros_and_surrounding(row_index, col_index, [])
                    if len(group) > 1:
                        self.uncover_groups.append(group)

    def get_surrounding_indexes(self, row_index: int, col_index: int) -> Generator[tuple[int, int], None, None]:
        # surorunding_indexes: list[tuple[int, int]] = []
        for (d_row_index, d_col_index) in [(0, 1), (1, 1), (1, 0), (-1, 0), (-1, -1), (0, -1), (-1, 1), (1, -1)]:

            prox_row_index: int = row_index + d_row_index
            prox_col_index: int = col_index + d_col_index

            # surorunding_indexes.append((prox_row_index, prox_col_index))
            if self.is_index_inbound(prox_row_index, prox_col_index):
                yield (prox_row_index, prox_col_index)

        # return surorunding_indexes

    def is_index_inbound(self, row_index: int, col_index: int) -> bool:
        return not (col_index < 0 or row_index < 0 or col_index >= self.grid_size[1] or row_index >= self.grid_size[0])

    def get_zeros_and_surrounding(self, row_index: int, col_index: int, groups: list[tuple[int, int]]) -> list[tuple[int, int]]:

        if not self.is_index_inbound(row_index, col_index):
            return groups
        
        # print(col_index, row_index, self.grid_size[0], self.grid_size[1])

        if self.mine_grid[row_index][col_index]:
            return groups

        if ((row_index, col_index) in groups):
            return groups
        
        groups.append((row_index, col_index))
        
        if self.proximity_grid[row_index][col_index] != 0:
            return groups
        
        # for (d_row_index, d_col_index) in [(0, 1), (1, 1), (1, 0), (-1, 0), (-1, -1), (0, -1), (-1, 1), (1, -1)]:

        #     prox_row_index: int = row_index + d_row_index
        #     prox_col_index: int = col_index + d_col_index

            
        for prox_row_index, prox_col_index in self.get_surrounding_indexes(row_index, col_index):
            # print(prox_row_index, prox_col_index)
            self.get_zeros_and_surrounding(prox_row_index, prox_col_index, groups)

        return groups
    


    def draw_background(self) -> None:
        background_color: tuple[int, int, int] = BACKGROUND_COLOR
        if self.win:
            background_color = (0, 150, 0)
        elif self.lost:
            background_color = (150, 0, 0)

        pygame.draw.rect(
            self.screen,
            background_color,
            self.screen.get_rect()
        )

    def draw_grid(self, show_patches: bool = False, show_bombs: bool = False, show_tile_pos: bool = False) -> None:
        # print(show_bombs, show_patches, show_tile_pos)
        for row_index in range(self.grid_size[0]):
            for col_index in range(self.grid_size[1]):
                top: int = self.grid_topleft[1] + row_index * self.TILE_SIZES[max(self.grid_size)]
                left: int = self.grid_topleft[0] + col_index * self.TILE_SIZES[max(self.grid_size)]

                rect_value: tuple[int, int, int, int] = (left, top, self.TILE_SIZES[max(self.grid_size)], self.TILE_SIZES[max(self.grid_size)])
                pygame.draw.rect(
                    self.screen,
                    UNCOVERED_TILE_COLOR,
                    rect_value,
                )

                if (row_index, col_index) == self.bomb_clicked:
                    pygame.draw.rect(
                        self.screen,
                        (200, 0, 0),
                        rect_value,
                    )

                if not self.first_move:
                    if self.mine_grid[row_index][col_index]:
                        pygame.draw.circle(
                            self.screen,
                            MINE_COLOR,
                            (left + self.TILE_SIZES[max(self.grid_size)] / 2, top + self.TILE_SIZES[max(self.grid_size)] / 2),
                            self.TILE_SIZES[max(self.grid_size)] / 6
                        )

                proximity_value: int = self.proximity_grid[row_index][col_index]

                if proximity_value > 0:
                    text_surf: pygame.Surface = self.proximity_font.render(
                        str(proximity_value),
                        False,
                        PROXIMITY_COLOR_PALETTE.get(proximity_value, "black")
                    )
                    text_rect: pygame.Rect = text_surf.get_rect(
                        center=(left + self.TILE_SIZES[max(self.grid_size)] / 2, top + self.TILE_SIZES[max(self.grid_size)] / 2)
                    )

                    self.screen.blit(text_surf, text_rect)


                if not self.game_over and self.cover_grid[row_index][col_index]:

                    pygame.draw.rect(
                        self.screen,
                        COVERED_TILE_COLOR,
                        rect_value,
                    )

                    top_cover_tile_size: int = int(0.7 * self.TILE_SIZES[max(self.grid_size)])

                    top_cover_surf: pygame.Surface = pygame.Surface((top_cover_tile_size, top_cover_tile_size))
                    top_cover_surf.fill(TOP_COVERED_TILE_COLOR)
                    top_cover_rect = top_cover_surf.get_rect(center=(left + self.TILE_SIZES[max(self.grid_size)] // 2, top + self.TILE_SIZES[max(self.grid_size)] // 2))
                
                    if self.cover_grid[row_index][col_index] == 2:
                    
                        top_text_rect: pygame.Rect = self.flag_pole_surf.get_rect(
                            center=(top_cover_tile_size // 2, top_cover_tile_size // 2)
                        )
                        top_cover_surf.blit(self.flag_pole_surf, top_text_rect)
                    elif self.cover_grid[row_index][col_index] == 3:
                        top_text_surf: pygame.Surface = self.proximity_font.render(
                            "?",
                            False,
                            "black"
                        )
                        top_text_rect: pygame.Rect = top_text_surf.get_rect(
                            center=(top_cover_tile_size // 2, top_cover_tile_size // 2)
                        )
                        top_cover_surf.blit(top_text_surf, top_text_rect)
                        

                    self.screen.blit(top_cover_surf, top_cover_rect)

                    if (row_index, col_index) in self.unvalid_chord_tiles:
                        pygame.draw.rect(
                            self.screen,
                            UNCOVERED_TILE_COLOR,
                            rect_value
                        )

                    
                pygame.draw.rect(
                    self.screen,
                    (50, 50, 50),
                    rect_value,
                    width=1
                )

                if show_patches and (row_index, col_index) in sum(self.uncover_groups, start=[]):
                    pygame.draw.rect(
                    self.screen,
                    "green",
                    rect_value,
                    width=1
                )
                
                if not self.first_move:
                    if show_bombs and self.mine_grid[row_index][col_index]:
                        pygame.draw.rect(
                        self.screen,
                        "red",
                        rect_value,
                        width=1
                    )
                    
                if show_tile_pos:
                    text_surf: pygame.Surface = self.proximity_font.render(
                            str(row_index * self.grid_size[1] + col_index),
                            False,
                            "white"
                        )
                    text_rect: pygame.Rect = text_surf.get_rect(
                        center=(left + self.TILE_SIZES[max(self.grid_size)] / 2, top + self.TILE_SIZES[max(self.grid_size)] / 2)
                    )
                    self.screen.blit(text_surf, text_rect)



    def get_current_mouse_tile_indexes(self) -> tuple[int, int] | None:
        
        mouse_pos: tuple[int, int] = pygame.mouse.get_pos()

        left_border, top_border = self.grid_topleft

        row_index = (mouse_pos[1] - top_border) // self.TILE_SIZES[max(self.grid_size)]
        col_index = (mouse_pos[0] - left_border) // self.TILE_SIZES[max(self.grid_size)]

        # print(row_index, col_index)
        if (row_index < 0 or col_index < 0 or row_index >= self.grid_size[0] or col_index >= self.grid_size[1]):
            return None
        
        return row_index, col_index
        
    def manage_user_input(self, all_events: list[pygame.event.Event]) -> None:
        clicked: bool = False
        button_value: int | None

        self.unvalid_chord_tiles = []

        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.initiate_grid()

        for event in all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
                button_value = event.button

        if self.game_over:
            return
            
        mouse_pos_indexes = self.get_current_mouse_tile_indexes()
        
        # Cancel if interacting with parameter menu or clicking outside the board
        if mouse_pos_indexes is None or self.parameter_menu.is_hovered():
            return
        
        row_index, col_index = mouse_pos_indexes

        mouse_pressed: tuple[int, int, int] = pygame.mouse.get_pressed()

        chording: bool = sum(mouse_pressed[::2]) == 2 or (pygame.key.get_pressed()[pygame.K_LCTRL] and mouse_pressed[0])
        # chording
        if self.cover_grid[row_index][col_index] == 0 and chording:
            proximity_mines: int = self.proximity_grid[row_index][col_index]
            if not proximity_mines: return
            
            tiles_to_uncover: list[tuple[int, int]] = []
            flag_count: int = 0

            for i, j in self.get_surrounding_indexes(row_index, col_index):
                is_flag: bool = self.cover_grid[i][j] == 2
                flag_count += is_flag

                if not is_flag and self.cover_grid[i][j] == 1:
                    tiles_to_uncover.append((i, j))

            if flag_count == proximity_mines:
                for i, j in tiles_to_uncover:
                    self.uncover_tiles(i, j)
            else:
                self.unvalid_chord_tiles = tiles_to_uncover

            return
        if self.cover_grid[row_index][col_index] == 0:
            return
        
        # Uncover tile(s) when clicking
        if clicked and button_value == 1:
            if self.first_move:
                self.place_mines_and_proximity_values((row_index, col_index))
                self.start_time = time.time()
                self.first_move = False

            self.uncover_tiles(row_index, col_index)

            # self.draw()

        
        elif clicked and button_value == 3:
            new_value: int = (self.cover_grid[row_index][col_index] + 1)
            if new_value > 3: new_value = 1
            self.cover_grid[row_index][col_index] = new_value



    def draw_ui(self) -> None:
        text_background_surf: pygame.Surface = pygame.Surface((90, 30))
        text_background_surf.fill((50, 50, 50))

        text_background_remaining_safe_tile_rect: pygame.Rect = text_background_surf.get_rect(
            bottomleft = (int(self.screen.get_width() * 0.2), self.grid_topleft[1] - 30)
        )

        text_background_minecount_rect: pygame.Rect = text_background_surf.get_rect(
            bottomright = (int(self.screen.get_width() * 0.8), self.grid_topleft[1] - 30)
        )

        remaining_safe_tile_text_surf: pygame.Surface = self.ui_font.render(
            str(self.grid_size[0] * self.grid_size[1] - self.number_mines if self.first_move else self.get_remaining_non_bomb_tile()),
            True,
            "red"
        )

        minecount_text_surf = self.ui_font.render(
            str(self.number_mines - self.get_number_of_flags()),
            True,
            "red"
        )

        remaining_safe_tile_text_rect: pygame.Rect = remaining_safe_tile_text_surf.get_rect(
            center=text_background_remaining_safe_tile_rect.center
        )

        minecount_text_rect: pygame.Rect = minecount_text_surf.get_rect(
            center=text_background_minecount_rect.center
        )

        game_time: int = self.get_game_time()

        hours: int = game_time // 3600
        minutes: int = game_time // 60
        seconds: int = game_time % 60

        time_text: str = ":".join(map(lambda t: str(t).zfill(2), [hours, minutes, seconds][int(hours == 0):]))

        time_text_surf = self.ui_font.render(
            time_text,
            True,
            "red"
        )

        time_text_background_rect = text_background_surf.get_rect(
            center=(self.screen.get_width() // 2, remaining_safe_tile_text_rect.centery)
        )

        time_text_rect = time_text_surf.get_rect(
            center=time_text_background_rect.center
        )

        self.screen.blit(text_background_surf, text_background_minecount_rect)
        self.screen.blit(text_background_surf, text_background_remaining_safe_tile_rect)
        self.screen.blit(text_background_surf, time_text_background_rect)

        self.screen.blit(remaining_safe_tile_text_surf, remaining_safe_tile_text_rect)
        self.screen.blit(minecount_text_surf, minecount_text_rect)
        self.screen.blit(time_text_surf, time_text_rect)

    def draw(self) -> None:
        self.draw_background()
        self.draw_grid(
            show_patches=self.parameter_menu.params["show_patches"],
            show_bombs=self.parameter_menu.params["show_bombs"], 
            show_tile_pos=self.parameter_menu.params["show_tile_pos"]
        )
        self.draw_tile_hover()
        self.draw_ui()
        self.parameter_menu.draw()

    def draw_tile_hover(self) -> None:
        # self.hover_surf.set_alpha(0)
        mouse_pos_indexes: tuple[int, int] | None = self.get_current_mouse_tile_indexes()

        if mouse_pos_indexes is None:
            return
        
        row_index, col_index = mouse_pos_indexes

        tile_size: int = self.TILE_SIZES[max(self.grid_size)]

        top: int = self.grid_topleft[1] + row_index * tile_size
        left: int = self.grid_topleft[0] + col_index * tile_size


        pygame.draw.rect(
            self.screen,
            "blue",
            (left, top, tile_size, tile_size),
            width=2
        )

        if self.parameter_menu["show_surrounding"]:
            for prox_row_index, prox_col_index in ((row, col) for row, col in self.get_surrounding_indexes(row_index, col_index) if self.is_index_inbound(row, col)):
                top: int = self.grid_topleft[1] + prox_row_index * tile_size
                left: int = self.grid_topleft[0] + prox_col_index * tile_size

                pygame.draw.rect(
                self.screen,
                "purple",
                (left, top, tile_size, tile_size),
                width=2
            )

    def uncover_tiles(self, row_index, col_index) -> None:

        if self.proximity_grid[row_index][col_index] == 0 and self.mine_grid[row_index][col_index] == 0:
            for uncover_group in self.uncover_groups:
                if (row_index, col_index) in uncover_group:
                    for r, c in uncover_group:
                        self.cover_grid[r][c] = 0
                    
                
        elif self.proximity_grid[row_index][col_index] != 0:
            self.cover_grid[row_index][col_index] = 0

        if self.mine_grid[row_index][col_index] == 1:
            self.game_over_time = self.get_game_time()
            self.game_over = True
            self.lost = True
            self.bomb_clicked = (row_index, col_index)

        if self.get_remaining_non_bomb_tile() == 0:
            self.game_over_time = self.get_game_time()
            self.win = True
            self.game_over = True
            

    def get_remaining_non_bomb_tile(self) -> int:
        return sum((cover > 0 for cover in sum(self.cover_grid, start=[]))) - self.number_mines
    
    def get_number_of_flags(self) -> int:
        return sum((cover == 2 for cover in sum(self.cover_grid, start=[])))
    
    def manage_parameters(self) -> None:
        value_changes: dict = self.parameter_menu.value_changes
        option_changes: list[str] = list(value_changes)

        if len(option_changes) == 0: return
        # print("-" * 20)
        # print(value_changes)
        # print(json.dumps(self.parameter_menu.params, indent=4))

        if any(opt in ["number_rows", "number_cols", "guaranted_patch"] for opt in option_changes):
            self.grid_size: tuple[int, int] = int(self.parameter_menu["number_rows"]), int(self.parameter_menu["number_cols"])
            max_mine_number = min(self.grid_size[0] * self.grid_size[1] - 1 - 8 * self.parameter_menu["guaranted_patch"], 99)

            self.number_mines = min(self.number_mines, max_mine_number)
            number_mines_slider: SliderWidget = self.parameter_menu.widgets["number_mines"]
            number_mines_slider.set_max_value(max_mine_number)
            
            self.initiate_grid()

        if "number_mines" in value_changes:
            self.number_mines = int(self.parameter_menu["number_mines"])
            self.initiate_grid()

        if any(opt in ["show_bombs", "show_patches", "show_surrounding"] for opt in option_changes) and not self.ignore_cheat_check:
            # print("cheat activated")
            self.cheat_activated = True
            self.parameter_menu.refresh_parameters()

        if "difficulty" in value_changes and len(self.parameter_menu["difficulty"]) == 1:
            # print("difficulty switch")
            diffuculty_options: dict = self.DIFFUCULTY[self.parameter_menu["difficulty"][0]]
            max_mine_number: int = int(min(diffuculty_options["number_rows"] * diffuculty_options["number_cols"] - 1 - 8 * diffuculty_options["guaranted_patch"], 99))

            # self.number_mines = min(self.number_mines, max_mine_number)
            number_mines_slider: SliderWidget = self.parameter_menu.widgets["number_mines"]
            number_mines_slider.set_max_value(max_mine_number)

            for opt, value in diffuculty_options.items():
                widget: ParameterWidget = self.parameter_menu.widgets[opt]
                widget.set_value(value)
            # self.parameter_menu.refresh_parameters()
            # print(self.parameter_menu.params, self.parameter_menu.old_params)
            self.cheat_activated = False
            self.ignore_cheat_check = True
            self.initiate_grid()
            # print("cheat deactivated")
        elif "difficulty" not in value_changes: # Activate difficulty settings if it is matching with one of the difficulty settings
            # print("difficulty check")
            difficulty_widget: SegmentedControlWidget = self.parameter_menu.widgets["difficulty"]
            similarity_found: bool = False
            
            if not self.cheat_activated:
                for difficulty, diffuculty_options in self.DIFFUCULTY.items():
                    for opt, value in diffuculty_options.items():
                        widget: ParameterWidget = self.parameter_menu.widgets[opt]
                        if widget.is_different(value, widget.value):
                            break
                    else: # Options match with difficulty
                        similarity_found = True
                        difficulty_widget.set_value([difficulty])
                        break

            # print("Similarity found", similarity_found)

            if not similarity_found:
                difficulty_widget.set_value([])
                self.parameter_menu.refresh_parameters()

            self.ignore_cheat_check = False

        # print(self.parameter_menu["difficulty"])

    def get_game_time(self) -> int:
        if self.first_move:
            return 0
        
        if self.game_over:
            return self.game_over_time

        return int(time.time() - self.start_time)

    def update(self, all_events: list[pygame.event.Event]):
        self.manage_user_input(all_events)
        self.parameter_menu.update(all_events)
        self.manage_parameters()
        self.draw()
        
        # print(self.parameter_menu.params)

    @staticmethod
    def generate_flag_pole_surface(tile_size: int, color: tuple[int, int, int]) -> pygame.Surface:
        tile_surf: pygame.Surface = pygame.Surface((tile_size, tile_size))
        tile_surf.fill(color)

        # Flag pole base
        pygame.draw.polygon(
            tile_surf,
            "black",
            (
                (int(tile_size * 0.2), int(tile_size * 0.9)),
                (int(tile_size * 0.8), int(tile_size * 0.9)),
                (int(tile_size * 0.5), int(tile_size * 0.8))
            )
        )

        # Flag pole bar
        pygame.draw.line(
            tile_surf,
            "black",
            (int(tile_size * 0.5), int(tile_size * 0.8)),
            (int(tile_size * 0.5), int(tile_size * 0.3)),
        )

        # Flag pole top
        pygame.draw.polygon(
            tile_surf,
            "red",
            (
                (int(tile_size * 0.5), int(tile_size * 0.4)),
                (int(tile_size * 0.5), int(tile_size * 0.1)),
                (int(tile_size * 0.2), int(tile_size * 0.25))
            )
        )

        return tile_surf