import getopt
import pygame
import logging
import sys

# constants
RED = (255, 0, 0)
GREEN = (0, 255, 0)


def triangle():
    return (50, 290), (125, 100), (200, 290)


def circle():
    return 350, 200


class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Controller Capture")
        self.screen = pygame.display.set_mode((500, 500))
        self.clock = pygame.time.Clock()
        self.running = True
        self.gui_font = pygame.font.Font(None, 30)


class Button:
    def __init__(self, game, controller, text, translation, width, height, pos, elevation):
        # Core attributes
        self.pressed = False
        self.elevation = elevation
        self.dynamic_elecation = elevation
        self.original_y_pos = pos[1]
        self.gui_font = game.gui_font
        self.screen = game.screen
        self.controller = controller

        # top rectangle
        self.top_rect = pygame.Rect(pos, (width, height))
        self.top_color = '#475F77'
        self.translation = translation
        # bottom rectangle
        self.bottom_rect = pygame.Rect(pos, (width, height))
        self.bottom_color = '#354B5E'
        # text
        self.text = text
        self.text_surf = self.gui_font.render(text, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def change_text(self, newtext):
        self.text_surf = self.gui_font.render(newtext, True, '#FFFFFF')
        self.text_rect = self.text_surf.get_rect(center=self.top_rect.center)

    def draw(self):
        # elevation logic
        self.top_rect.y = self.original_y_pos - self.dynamic_elecation
        self.text_rect.center = self.top_rect.center

        self.bottom_rect.midtop = self.top_rect.midtop
        self.bottom_rect.height = self.top_rect.height + self.dynamic_elecation

        pygame.draw.rect(self.screen, self.bottom_color, self.bottom_rect, border_radius=12)
        pygame.draw.rect(self.screen, self.top_color, self.top_rect, border_radius=12)
        self.screen.blit(self.text_surf, self.text_rect)
        self.check_click()

    def check_click(self):
        mouse_pos = pygame.mouse.get_pos()
        if self.top_rect.collidepoint(mouse_pos):
            self.top_color = '#D74B4B'
            if pygame.mouse.get_pressed()[0]:
                self.dynamic_elecation = 0
                self.pressed = True
                self.change_text(f"{self.translation}")
                self.controller.rumble()
            else:
                self.dynamic_elecation = self.elevation
                if self.pressed == True:
                    self.pressed = False
                    self.change_text(self.text)
        else:
            self.dynamic_elecation = self.elevation
            self.top_color = '#475F77'


class Controller:
    """ Class to interface with a Joystick """

    def __init__(self, joy_index=0):
        self.joystick = pygame.joystick.Joystick(joy_index)
        self.joystick.init()

    def rumble(self):
        self.joystick.rumble(1, 1, 100)

    def get_triangle_button_value(self):
        return self.joystick.get_button(2)

    def get_circle_button_value(self):
        return self.joystick.get_button(1)


def start_game():
    # pygame setup
    game = Game()
    controller = Controller()
    rumble = Button(game, controller, 'Rumble', "Rumbling", 200, 40, (150, 400), 5)

    logging.info("Started controller-capture")

    while game.running:
        # poll for events
        # pygame.QUIT event means the user clicked X to close your window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.running = False
            if event.type == pygame.JOYBUTTONDOWN:
                if controller.get_triangle_button_value():
                    logging.info("YES")
                if controller.get_circle_button_value():
                    logging.info("NO")

        # fill the screen with a color to wipe away anything from last frame
        game.screen.fill("black")

        pygame.draw.polygon(game.screen, GREEN, triangle(), int(not controller.get_triangle_button_value()))
        pygame.draw.circle(game.screen, RED, circle(), 90, int(not controller.get_circle_button_value()))

        rumble.draw()
        # flip() the display to put your work on screen
        pygame.display.flip()

        game.clock.tick(60)  # limits FPS to 60

    pygame.quit()


def main(argv):
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv, "ho:", ["ofile="])
    except getopt.GetoptError:
        print('controller-capture.py -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -o <outputfile>')
            sys.exit()
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    # logging setup
    logging.basicConfig(filename=outputfile, format='%(asctime)s - %(message)s', level=logging.INFO)
    start_game()


if __name__ == "__main__":
    main(sys.argv[1:])
