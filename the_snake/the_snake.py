from random import choice, randint

import pygame

# Константы для размеров поля и сетки:
SCREEN_WIDTH, SCREEN_HEIGHT = 640, 480
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE

# Центр игрового поля:
CENTER = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# Направления движения:
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# Цвет фона - черный:
BOARD_BACKGROUND_COLOR = (0, 0, 0)

# Цвет границы ячейки
BORDER_COLOR = (93, 216, 228)

# Цвет ячейки
STANDART_COLOR = (0, 0, 0)

# Цвет яблока
APPLE_COLOR = (255, 0, 0)

# Цвет змейки
SNAKE_COLOR = (0, 255, 0)

# Скорость движения змейки:
SPEED = 20

# Настройка игрового окна:
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), 0, 32)

# Заголовок окна игрового поля:
pygame.display.set_caption('Змейка')

# Настройка времени:
clock = pygame.time.Clock()


class GameObject:
    """
    Базовый класс, от которого наследуются другие игровые объекты.
    Содержит общие атрибуты игровых объектов.
    """

    def __init__(self, body_color=None) -> None:
        self.position = CENTER
        self.body_color = body_color

    def draw(self) -> None:
        """
        Абстрактный метод, который предназначен для переопределения
        в дочерних классах.
        Метод должен определять, как объект будет отрисовываться на экране.
        """
        raise NotImplementedError


class Apple(GameObject):
    """Класс, описывающий яблоко и действия с ним."""

    def __init__(self, occupied_cells: tuple = CENTER):
        super().__init__()
        self.position = self.randomize_position(occupied_cells=CENTER)
        self.body_color = APPLE_COLOR

    def draw(self):
        """Отрисовывает яблоко на игровой поверхности."""
        rect = pygame.Rect(self.position, (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, rect)
        pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

    def randomize_position(self,
                           # occupied_cells: list[tuple] = [CENTER]) -> tuple:
                           occupied_cells: tuple = CENTER) -> tuple:
        """Устанавливает случайное положение яблока на игровом поле.
        Координаты выбираются так,
        чтобы яблоко оказалось в пределах игрового поля,
        с учетом позиции змейки.
        """
        coordinate_generation = True
        while coordinate_generation:
            x_rand = randint(1, GRID_WIDTH - 1) * GRID_SIZE
            y_rand = randint(1, GRID_HEIGHT - 1) * GRID_SIZE
            if (x_rand, y_rand) not in occupied_cells:
                coordinate_generation = False
        return (x_rand, y_rand)


class Snake(GameObject):
    """Класс, описывающий змейку и её поведение."""

    def __init__(self):
        super().__init__()
        self.body_color = SNAKE_COLOR
        self.length = 1
        self.positions = []
        self.reset()

    def update_direction(self):
        """Обновляет направление движения змейки."""
        if self.next_direction:
            self.direction = self.next_direction
            self.next_direction = None

    def move(self):
        """Обновляет позицию змейки, добавляя новую голову в начало списка,
        и удаляя последний элемент, если длина змейки не увеличилась.
        """
        x_head_position, y_head_position = self.get_head_position()
        x_direction, y_direction = self.direction
        x_new_head_position = (
            x_head_position + (x_direction * GRID_SIZE)) % SCREEN_WIDTH
        y_new_head_position = (
            y_head_position + (y_direction * GRID_SIZE)) % SCREEN_WIDTH

        list.insert(
            self.positions, 0, (x_new_head_position, y_new_head_position)
        )
        if self.length == len(self.positions) - 1:
            self.last = list.pop(self.positions)

    def draw(self):
        """Отрисовывает змейку на экране, затирая след."""
        for position in self.positions[:-1]:
            rect = (pygame.Rect(position, (GRID_SIZE, GRID_SIZE)))
            pygame.draw.rect(screen, self.body_color, rect)
            pygame.draw.rect(screen, BORDER_COLOR, rect, 1)

        # Отрисовка головы змейки
        head_rect = pygame.Rect(self.positions[0], (GRID_SIZE, GRID_SIZE))
        pygame.draw.rect(screen, self.body_color, head_rect)
        pygame.draw.rect(screen, BORDER_COLOR, head_rect, 1)

        # Затирание последнего сегмента
        if self.last:
            last_rect = pygame.Rect(self.last, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)

    def get_head_position(self) -> tuple:
        """Возвращает текущее положение головы змейки."""
        return self.positions[0]

    def reset(self) -> None:
        """Сброс змейки в начальное состояние."""
        self.length = 1
        self.positions.clear()
        self.positions = [CENTER]
        self.direction = choice([UP, DOWN, LEFT, RIGHT])
        screen.fill(BOARD_BACKGROUND_COLOR)
        self.next_direction = None
        self.last = None


def handle_keys(game_object):
    """Функция обработки действий пользователя."""
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            raise SystemExit
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and game_object.direction != DOWN:
                game_object.next_direction = UP
            elif event.key == pygame.K_DOWN and game_object.direction != UP:
                game_object.next_direction = DOWN
            elif event.key == pygame.K_LEFT and game_object.direction != RIGHT:
                game_object.next_direction = LEFT
            elif event.key == pygame.K_RIGHT and game_object.direction != LEFT:
                game_object.next_direction = RIGHT


def main():
    """Инициализация и основная логика игры"""
    pygame.init()
    apple = Apple()
    snake = Snake()

    while True:
        clock.tick(SPEED)
        apple.draw()
        snake.draw()
        snake.move()
        snake.update_direction()
        handle_keys(snake)
        pygame.display.update()

        if snake.get_head_position() == apple.position:
            snake.length += 1
            last_rect = pygame.Rect(apple.position, (GRID_SIZE, GRID_SIZE))
            pygame.draw.rect(screen, BOARD_BACKGROUND_COLOR, last_rect)
            apple.__init__(occupied_cells=snake.positions)
            apple.draw()

        if snake.get_head_position() in snake.positions[1:]:
            snake.reset()


if __name__ == '__main__':
    main()
