# import PySimpleGUI as sg
import pygame

from typing import Any, Generator, Callable
import copy

from pygame.event import Event

from .circle import Circle


class ParameterWidget:
    def __init__(self, 
                 label: str, 
                 position: tuple[int, int], 
                 parameter_menu,
                 label_display: str | None = None, 
                 surface: pygame.Surface | None = None,
                ) -> None:
        self.label: str = label
        self.label_display: str | None = label_display
        self.value = None
        self.position: tuple[int, int] = position

        self.parameter_menu = parameter_menu

        self.surface: pygame.Surface = surface if surface is not None else pygame.display.get_surface()
        self.font: pygame.font.Font = pygame.font.SysFont("Arial", 10, True)

        self.global_width: int = 200
        self.global_height: int = 30
    
    def get_mouse_pos(self) -> tuple[int, int]:
        mouse_pos = pygame.mouse.get_pos()
        return (mouse_pos[0] - self.parameter_menu.rectangle.left, mouse_pos[1] - self.parameter_menu.rectangle.top)

    def draw(self) -> None:
        pass
    
    def get_value(self) -> Any:
        return self.value
    
    def set_value(self, new_value: Any) -> None:
        self.value = new_value
    
    def update(self, all_events: list[pygame.event.Event]) -> None:
        self.draw()

    @staticmethod
    def is_different(value_a: Any, value_b: Any) -> bool:
        return value_a != value_b


class CheckBoxWidget(ParameterWidget):

    def __init__(self, 
                 label: str,
                 position: tuple[int, int],
                 parameter_menu,
                 default_value: bool = False,
                 label_display: str | None = None,
                 surface: pygame.Surface | None = None
                ) -> None:
        super().__init__(label, position, parameter_menu, label_display, surface)
        self.value: bool = default_value
        
        self.text_surf: pygame.Surface = self.font.render(
            self.label_display if self.label_display is not None else self.label,
            True,
            "white"
        )
        self.text_rect: pygame.Rect = self.text_surf.get_rect(midleft=self.position)
        
        self.checkbox_surf: pygame.Surface = pygame.Surface((10, 10))
        self.checkbox_surf.fill((250, 250, 250))
        self.checkbox_rect: pygame.Rect = self.checkbox_surf.get_rect(midleft=self.text_rect.midright)
        self.checkbox_rect.x += 5

    def draw(self) -> None:
        self.surface.blit(self.text_surf, self.text_rect)
        self.surface.blit(self.checkbox_surf, self.checkbox_rect)

        if self.value:
            pygame.draw.rect(
                self.surface,
                (180, 0, 0),
                self.checkbox_rect
            )

    def manage_click(self, all_events: list[Event]) -> None:
        for event in all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.checkbox_rect.collidepoint(self.get_mouse_pos()):
                    self.value = not self.value

    def update(self, all_events: list[Event]) -> None:
        self.manage_click(all_events)
        self.draw()


class SliderWidget(ParameterWidget):

    def __init__(self,
                 label: str, 
                 default_value: float, 
                 min_value: float, 
                 max_value: float, 
                 interval: float,
                 position: tuple[int, int],
                 parameter_menu,
                 width: int = 100,
                 label_display: str | None = None,
                 value_format: Callable | None = None,
                 surface: pygame.Surface | None = None
                ) -> None:
        super().__init__(label, position, parameter_menu, label_display, surface)

        # self.font: pygame.font.Font = pygame.font.SysFont("Arial", 15)

        self.label_surf: pygame.Surface = self.font.render(
            self.label_display if self.label_display else self.label,
            True,
            "white"
        )
        
        self.label_rect: pygame.Rect = self.label_surf.get_rect(midleft=self.position)
        self.value = default_value

        self.min_value: float = min_value
        self.max_value: float = max_value
        self.interval: float = interval
        self.width: int = width

        self.number_decimals: int = max(map(
            lambda number: 0 if isinstance(number, int) else len(str(number).split(".")[-1]),
            [self.min_value, self.max_value, self.interval]
            )
        )
        # print(self.number_decimals)

        self.rail_surf: pygame.Surface = pygame.Surface((width, 4))
        self.rail_rect: pygame.Rect = self.rail_surf.get_rect(midleft=self.label_rect.midright)
        self.rail_rect.x += 5
        self.slider_surf: pygame.Surface = pygame.Surface((10, 10))
        self.slider_surf.fill((180, 0, 0))
        self.slider_rect = self.slider_surf.get_rect(center=self.get_slider_pos(self.value))
        

        self.all_slider_positions: list[float] = [self.get_slider_pos(val)[0] for val in self]
        # print(self.all_slider_positions)
        self.is_selected: bool = False

        self.value_format: Callable = value_format if value_format is not None else str
        
    def get_slider_pos(self, value: float) -> tuple[float, float]:
        # x, y = self.position
        return self.rail_rect.left + self.rail_rect.width * (value - self.min_value) / (self.max_value - self.min_value), self.rail_rect.centery
    
    def manage_user_interaction(self, all_events: list[pygame.event.Event]) -> None:
        mouse_pos: tuple[int, int] = self.get_mouse_pos()

        for event in all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.slider_rect.collidepoint(mouse_pos) or self.rail_rect.collidepoint(mouse_pos):
                    self.is_selected = True
            
            if self.is_selected and event.type == pygame.MOUSEBUTTONUP:
                self.is_selected = False
        # print(self.is_selected)
        if self.is_selected and pygame.mouse.get_pressed():
            self.follow_mouse()

        # print(self.value)
        # print(mouse_pos, self.rail_rect.left)

    def follow_mouse(self) -> None:
        mouse_pos: tuple[int, int] = self.get_mouse_pos()
        # self.slider_rect.x = min(max(mouse_pos[0], self.position[0]), self.position[0] + self.width)
        new_position = min(max(mouse_pos[0], self.rail_rect.left), self.rail_rect.right)
        new_position = min(((pos, abs(new_position - pos)) for pos in self.all_slider_positions), key=lambda x: x[1])[0]
        self.slider_rect.centerx = new_position
        # rect.x = x + self.width * (self.value - self.min_value) / (self.max_value - self.min_value)
        # rect.x - x = self.width * (self.value - self.min_value) / (self.max_value - self.min_value)
        # (rect.x - x) / self.width * (self.max_value - self.min_value) + self.min_value = self.value 
        new_value = (self.slider_rect.centerx - self.rail_rect.left) / self.width * (self.max_value - self.min_value) + self.min_value

        self.value = round(new_value, self.number_decimals)
        # print(self.value)

    def draw(self) -> None:
        self.surface.blit(self.rail_surf, self.rail_rect)
        pygame.draw.rect(
            self.surface,
            color=(200, 200, 0),
            rect=(
                *self.rail_rect.topleft, 
                self.slider_rect.centerx - self.rail_rect.left,
                self.rail_rect.height
            )
        )
        self.surface.blit(self.slider_surf, self.slider_rect)
        self.surface.blit(self.label_surf, self.label_rect)

        text_value_surf: pygame.Surface = self.font.render(
            self.value_format(self.value),
            True,
            "white"
        )
        text_value_rect: pygame.Rect = text_value_surf.get_rect(midleft=self.rail_rect.midright)
        text_value_rect.x += 5

        self.surface.blit(text_value_surf, text_value_rect)

    def set_max_value(self, new_value: float) -> None:
        self.max_value: float = new_value
        self.rearrange_slider()

    def set_min_value(self, new_value: float) -> None:
        self.min_value: float = new_value
        self.rearrange_slider()

    def set_value(self, new_value: float) -> None:
        self.value: float = new_value
        self.rearrange_slider()

    def rearrange_slider(self):
        self.number_decimals: int = max(map(
            lambda number: 0 if isinstance(number, int) else len(str(number).split(".")[-1]),
            [self.min_value, self.max_value, self.interval]
            )
        )
        self.value = round(max(min(self.max_value, self.value), self.min_value), self.number_decimals)
        self.all_slider_positions: list[float] = [self.get_slider_pos(val)[0] for val in self]

        new_position: float = self.get_slider_pos(self.value)[0]
        slider_pos: float = min(((pos, abs(new_position - pos)) for pos in self.all_slider_positions), key=lambda x: x[1])[0]

        self.slider_rect.centerx = slider_pos


    def update(self, all_events: list[pygame.event.Event]) -> None:
        self.manage_user_interaction(all_events)
        self.draw()

    def __len__(self) -> int:
        return (self.max_value - self.min_value) // self.interval
    
    def __iter__(self) -> Generator:
        value: float = round(self.min_value, self.number_decimals)
        
        for _ in range(len(self) + 1):
            yield value
            value = round(value + self.interval)


class SegmentedControlWidget(ParameterWidget):

    def __init__(self, 
                 label: str, 
                 position: tuple[int, int], 
                 available_options: dict[str, str],
                 default_value: list[str],
                 parameter_menu, 
                 require_selection: bool = False,
                 allow_multiselection: bool = False,
                 label_display: str | None = None, 
                 surface: pygame.Surface | None = None
                 ) -> None:
        super().__init__(label, position, parameter_menu, label_display, surface)

        self.option_font: pygame.font.Font = pygame.sysfont.SysFont(
            "Arial", 10, True
        )

        self.available_options: dict[str, str] = available_options
        self.value: list[str] = default_value
        self.require_selection: bool = require_selection
        self.allow_multiselection: bool = allow_multiselection

        self.option_surf_rect: dict[str, dict[str, pygame.Surface, pygame.Rect]] = {}

        option_background_width: int = 0
        option_background_height: int = 0
        
        # Generate widgets
        for raw, display in self.available_options.items():
            option_infos: dict[str, pygame.Surface, pygame.Rect] = {}
            text_surf: pygame.Surface = self.option_font.render(
                display,
                True,
                "white" if raw in self.value else "black"
            )
            text_rect: pygame.Rect = text_surf.get_rect(topleft=self.position)

            option_infos["text_surf"] = text_surf
            option_infos["text_rect"] = text_rect

            self.option_surf_rect[raw] = option_infos

            option_background_width = max(text_rect.width, option_background_width)
            option_background_height = max(text_rect.height, option_background_height)
        
        option_background_width = int(option_background_width * 1.2)
        option_background_height = int(option_background_height * 1.2)

        # Place backgrounds and texts
        for i, raw in enumerate(self.available_options):
            background_surf: pygame.Surface = pygame.Surface((option_background_width, option_background_height))
            background_rect: pygame.Rect = background_surf.get_rect(midleft=(
                position[0] + i * option_background_width,
                position[1]
            ))
            background_surf.fill((180, 0, 0) if raw in self.value else (250, 250, 250))

            self.option_surf_rect[raw]["background_surf"] = background_surf
            self.option_surf_rect[raw]["background_rect"] = background_rect
            self.option_surf_rect[raw]["text_rect"].center = background_rect.center
    
    def draw(self) -> None:
        for raw in self.option_surf_rect:

            self.surface.blit(self.option_surf_rect[raw]["background_surf"], 
                              self.option_surf_rect[raw]["background_rect"])
            self.surface.blit(self.option_surf_rect[raw]["text_surf"], 
                              self.option_surf_rect[raw]["text_rect"])
            
            
    def regenerate_widget(self) -> None:
        for raw, display in self.available_options.items():
            self.option_surf_rect[raw]["background_surf"].fill((180, 0, 0) if raw in self.value else (250, 250, 250))

            text_surf: pygame.Surface = self.option_font.render(
                display,
                True,
                "white" if raw in self.value else "black"
            )
            text_rect: pygame.Rect = text_surf.get_rect(
                center=self.option_surf_rect[raw]["background_rect"].center
            )

            self.option_surf_rect[raw]["text_surf"] = text_surf
            self.option_surf_rect[raw]["text_rect"] = text_rect

    def manage_user_input(self, all_events: list[Event]) -> None:
        clicked: bool = False
        for event in all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                clicked = True
                break
        
        if not clicked: return

        for raw in self.option_surf_rect:
            background_rect: pygame.Rect = self.option_surf_rect[raw]["background_rect"]

            if background_rect.collidepoint(self.get_mouse_pos()):
                # Remove
                if raw in self.value:
                    if len(self.value) == 1 and self.require_selection:
                        return
                    self.value.remove(raw)
                # Add
                else:
                    if self.allow_multiselection:
                        self.value = [opt for opt in self.available_options if opt in self.value or opt == raw]
                    else:
                        self.value = [raw]
                
                self.regenerate_widget()

    def get_value(self) -> list[str]:
        return self.value[:]
    
    def set_value(self, new_value: Any) -> None:
        super().set_value(new_value)
        self.regenerate_widget()

    def update(self, all_events: list[Event]) -> None:
        self.manage_user_input(all_events)
        self.draw()

    @staticmethod
    def is_different(value_a: list[str], value_b: list[str]) -> bool:
        return str(value_a) != str(value_b)
            


class Param:
    label: str = ""
    default_value: Any = None
    label_display: str | None = None


class CheckBox(Param):
    def __init__(self,
                label: str,
                default_value: bool = False,
                label_display: str | None = None,
            ) -> None:
        super().__init__()
        self.label: str = label
        self.default_value: float = default_value
        self.label_display: str | None = label_display


class Slider(Param):
    def __init__(self,
                label: str,
                default_value: float,
                min_value: float,
                max_value: float,
                interval: float,
                label_display: str | None = None,
                value_format: Callable | None = None
            ) -> None:
        super().__init__()
        self.label: str = label
        self.default_value: float = default_value
        self.min_value: float = min_value
        self.max_value: float = max_value
        self.interval: float = interval
        self.label_display: str | None = label_display
        self.value_format: Callable | None = value_format


class SegmentedControl(Param):
    
    def __init__(self, 
                 label: str,
                 default_value: list[str],
                 available_options_raw: list[str],
                 available_options_display: list[str] | None = None,
                 require_selection: bool = False,
                 allow_multiselection: bool = False,
                 label_display: str | None = None) -> None:
        super().__init__()
        self.label: str = label
        self.default_value: list[str] = default_value
        available_options_display: list[str] = available_options_display if available_options_display is not None else available_options_raw[:]

        self.available_options = {raw: display for raw, display in zip(available_options_raw, available_options_display)}
        self.require_selection: bool = require_selection
        self.allow_multiselection: bool = allow_multiselection
        self.label_display: str | None = label_display




class ParametersMenu:

    SPEED: int = 16

    def __init__(self,
                 parameters: list[Param],
                 screen_position: str,
                 size: int
                ) -> None:
        self.screen: pygame.Surface = pygame.display.get_surface()
        self.parameters: list[Param] = parameters

        self.screen_position: str = screen_position
        self.size: int = size

        self.menu_switcher_circle: Circle = Circle((0, 0), 30)

        if screen_position == "top":
            self.surface_size: tuple[int, int] = (self.screen.get_width(), size)
            self.retracted_pos: tuple[int, int] = (0, -size)
            self.deployed_pos: tuple[int, int] = (0, 0)
        elif screen_position == "bottom":
            self.surface_size: tuple[int, int] = (self.screen.get_width(), size)
            self.retracted_pos: tuple[int, int] = (0, self.screen.get_height())
            self.deployed_pos: tuple[int, int] = (0, self.screen.get_height() - size)
        elif screen_position == "left":
            self.surface_size: tuple[int, int] = (size, self.screen.get_height())
            self.retracted_pos: tuple[int, int] = (-size, 0)
            self.deployed_pos: tuple[int, int] = (0, 0)
        elif screen_position == "right":
            self.surface_size: tuple[int, int] = (size, self.screen.get_height())
            self.retracted_pos: tuple[int, int] = (self.screen.get_width(), 0)
            self.deployed_pos: tuple[int, int] = (self.screen.get_width() - size, 0)
        

        self.deployed: bool = False
        
        self.surface: pygame.Surface = pygame.Surface(self.surface_size)
        self.rectangle: pygame.Rect = self.surface.get_rect(topleft=self.retracted_pos)
        self.surface.fill((50, 50, 50))
        

        # Set layout

        x_offset: int = 10
        y_offset: int = 5

        x_pos: int = x_offset
        y_pos: int = y_offset * 2

        col_parameters: list[ParameterWidget] = []

        self.params: dict = {}

        self.widgets: dict[str, ParameterWidget] = {}

        for param in self.parameters:
            self.params[param.label] = param.default_value

            widget: ParameterWidget = ParameterWidget("", (0, 0), self, "", self.surface)

            if isinstance(param, Slider):
                widget: SliderWidget = SliderWidget(
                    label=param.label,
                    default_value=param.default_value,
                    min_value=param.min_value,
                    max_value=param.max_value,
                    interval=param.interval,
                    position=(x_pos, y_pos),
                    value_format=param.value_format,
                    surface=self.surface,
                    parameter_menu=self,
                    label_display=param.label_display
                )

            if isinstance(param, CheckBox):
                widget: CheckBoxWidget = CheckBoxWidget(
                    label=param.label,
                    default_value=param.default_value,
                    position=(x_pos, y_pos),
                    surface=self.surface,
                    parameter_menu=self,
                    label_display=param.label_display
                )

            if isinstance(param, SegmentedControl):
                widget: SegmentedControlWidget = SegmentedControlWidget(
                    label=param.label,
                    default_value=param.default_value,
                    position=(x_pos, y_pos),
                    surface=self.surface,
                    parameter_menu=self,
                    label_display=param.label_display,
                    available_options=param.available_options,
                    require_selection=param.require_selection,
                    allow_multiselection=param.allow_multiselection

                )

            col_parameters.append(widget)
            self.widgets[param.label] = widget
            y_pos += widget.global_height + y_offset
            
            # Switch layout column
            if y_pos + 70 > self.surface_size[1]:
                y_pos = y_offset * 2
                x_pos += max(w.global_width for w in col_parameters) + x_offset
                col_parameters.clear()
        
        self.old_params: dict = copy.deepcopy(self.params)
        self.value_changes: dict = {}

    def draw(self) -> None:
        # print(self.menu_switcher_circle)
        pygame.draw.circle(
            self.screen,
            (50, 50, 50),
            self.menu_switcher_circle.center,
            self.menu_switcher_circle.radius
        )
        self.screen.blit(self.surface, self.rectangle)
    
    def extract_params(self) -> None:
        for label, widget in self.widgets.items():
            self.params[label] = widget.value

    def manage_parameters(self, all_events: list[pygame.event.Event]) -> None:
        self.surface.fill((50, 50, 50))
        # for widget in self.widgets.values():
        #     widget.update(all_events)

        self.value_changes.clear()
        for label, widget in self.widgets.items():
            widget.update(all_events)
            self.params[label] = widget.value

            # if widget.value != self.old_params[label]:
            if widget.is_different(widget.value, self.old_params[label]):
                self.value_changes[label] = {
                    "old_value": self.old_params[label],
                    "new_value": widget.value
                }

            self.old_params[label] = widget.get_value()

        for event in all_events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos: tuple[int, int] = pygame.mouse.get_pos()
                if self.menu_switcher_circle.collidepoint(mouse_pos) and not self.rectangle.collidepoint(mouse_pos):
                    self.switch_deployment()

    def refresh_parameters(self) -> None:
        for label, widget in self.widgets.items():
            self.params[label] = widget.value
        self.old_params: dict = copy.deepcopy(self.params)


    def manage_panel_pos(self) -> None:


        dx: float = 0
        dy: float = 0

        if self.deployed and self.rectangle.topleft != self.deployed_pos:   
            dx = self.deployed_pos[0] - self.rectangle.left
            dy = self.deployed_pos[1] - self.rectangle.top 

        elif not self.deployed and self.rectangle.topleft != self.retracted_pos:
            dx = self.retracted_pos[0] - self.rectangle.left
            dy = self.retracted_pos[1] - self.rectangle.top 

        # print(dx, dy)

        if abs(dx) >= self.SPEED:
            self.rectangle.x += dx / abs(dx) * self.SPEED
        else:
            self.rectangle.left = self.deployed_pos[0] if self.deployed else self.retracted_pos[0]
        if abs(dy) >= self.SPEED :
            self.rectangle.y += dy / abs(dy) * self.SPEED
        else:
            self.rectangle.top = self.deployed_pos[1] if self.deployed else self.retracted_pos[1]

        if self.screen_position == "top":
            self.menu_switcher_circle.center = self.rectangle.midbottom
            self.menu_switcher_circle.y -= self.menu_switcher_circle.radius // 2
        elif self.screen_position == "bottom":
            self.menu_switcher_circle.center = self.rectangle.midtop
            self.menu_switcher_circle.y += self.menu_switcher_circle.radius // 2
        elif self.screen_position == "left":
            self.menu_switcher_circle.center = self.rectangle.midright
            self.menu_switcher_circle.x -= self.menu_switcher_circle.radius // 2
        elif self.screen_position == "right":
            self.menu_switcher_circle.center = self.rectangle.midleft
            self.menu_switcher_circle.x += self.menu_switcher_circle.radius // 2

    def is_hovered(self) -> bool:
        return self.rectangle.collidepoint(pygame.mouse.get_pos()) or self.menu_switcher_circle.collidepoint(pygame.mouse.get_pos())
        

    def switch_deployment(self) -> None:
        self.deployed = not self.deployed
        
    def update(self, all_events: list[pygame.event.Event]) -> None:
        self.manage_panel_pos()
        # self.draw()
        self.manage_parameters(all_events)

    def __getitem__(self, key: str) -> Any:
        return self.params.get(key, None)


