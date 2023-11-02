import numpy as np
import matplotlib.pyplot as plt
from itertools import product
import networkx as nx

class CityGrid:
    def __init__(self, n, m, obstructed_probability=0.3):
        """
        Инициализация объекта CityGrid.

        Parameters:
            n (int): Количество строк в сетке.
            m (int): Количество столбцов в сетке.
            obstructed_probability (float): Вероятность препятствий в сетке.
        """
        self.n = n
        self.m = m
        self.grid = np.random.rand(n, m) > obstructed_probability
        self.towers = []

    def place_tower(self, x, y, range):
        """
        Размещение башни в сетке.

        Parameters:
            x (int): Координата x для размещения башни.
            y (int): Координата y для размещения башни.
            range (int): Дальность башни.

        Если координаты в пределах сетки и нет препятствий, то башня размещается.
        """
        if 0 <= x < self.n and 0 <= y < self.m and self.grid[x][y]:
            self.towers.append((x, y, range))

    def visualize_grid(self):
        """
        Визуализация сетки и размещенных башен.
        """
        plt.imshow(self.grid, cmap='gray')
        for tower in self.towers:
            x, y, _ = tower
            plt.scatter(y, x, color='red', marker='^', s=100)
        plt.show()

    def visualize_coverage(self):
        """
        Визуализация покрытия области башнями.
        """
        coverage_grid = np.zeros((self.n, self.m))
        for tower in self.towers:
            x, y, range = tower
            for i, j in product(range(-range, range+1), repeat=2):
                if 0 <= x + i < self.n and 0 <= y + j < self.m:
                    coverage_grid[x + i][y + j] = 1

        plt.imshow(coverage_grid, cmap='Blues')
        for tower in self.towers:
            x, y, _ = tower
            plt.scatter(y, x, color='red', marker='^', s=100)
        plt.show()

    def optimize_tower_placement(self, budget=1000, tower_types=[]):
        """
        Оптимизация размещения башен в соответствии с бюджетом и типами башен.

        Parameters:
            budget (int): Бюджет для размещения башен.
            tower_types (list): Список доступных типов башен с их характеристиками.

        Для каждой башни находится наилучшее местоположение и тип, учитывая бюджет и покрытие.
        """
        for tower_type in tower_types:
            remaining_budget = budget
            while remaining_budget >= tower_type['cost']:
                best_tower = None
                best_coverage = 0
                best_distance = 0

                for x in range(self.n):
                    for y in range(self.m):
                        if self.grid[x][y]:
                            total_coverage = 0
                            for tower in self.towers:
                                tx, ty, trange = tower
                                distance = (x - tx) ** 2 + (y - ty) ** 2
                                if distance <= trange ** 2:
                                    total_coverage += 1

                            if total_coverage == 0 and tower_type['coverage'] > best_coverage:
                                best_tower = (x, y)
                                best_coverage = tower_type['coverage']
                                best_distance = distance

                if best_tower is not None:
                    x, y = best_tower
                    self.place_tower(x, y, tower_type['range'])
                    remaining_budget -= tower_type['cost']
                else:
                    break

    def find_reliable_path(self, start, end):
        """
        Поиск надежного пути между башнями с использованием NetworkX.

        Parameters:
            start (int): Индекс начальной башни.
            end (int): Индекс конечной башни.

        Returns:
            path (list): Список индексов башен в пути или None, если путь не найден.
        """
        G = nx.Graph()
        for i, tower in enumerate(self.towers):
            x1, y1, _ = tower
            for j, other_tower in enumerate(self.towers):
                if i == j:
                    continue
                x2, y2, _ = other_tower
                distance = (x1 - x2) ** 2 + (y1 - y2) ** 2
                if distance <= tower[2] ** 2:
                    G.add_edge(i, j, weight=distance)

        try:
            path = nx.shortest_path(G, source=start, target=end, weight='weight')
            return path
        except nx.NetworkXNoPath:
            return None

    def visualize_path(self, path):
        """
        Визуализация пути передачи данных между башнями.

        Parameters:
            path (list): Список индексов башен в пути.
        """
        if path is None:
            print("No reliable path found.")
            return

        coverage_grid = np.zeros((self.n, self.m))
        for i in path:
            x, y, range = self.towers[i]
            for px, py in product(range(-range, range+1), repeat=2):
                if 0 <= x + px < self.n and 0 <= y + py < self.m:
                    coverage_grid[x + px][y + py] = 1

        plt.imshow(self.grid, cmap='gray')
        plt.imshow(coverage_grid, cmap='Blues', alpha=0.5)
        for tower in self.towers:
            x, y, _ = tower
            plt.scatter(y, x, color='red', marker='^', s=100)
        plt.show()


city = CityGrid(n=10, m=10, obstructed_probability=0.3)


city.place_tower(3, 4, range=2)
city.place_tower(7, 5, range=3)


city.visualize_grid()


tower_types = [
    {'range': 2, 'coverage': 10, 'cost': 200},
    {'range': 3, 'coverage': 15, 'cost': 300},
]
city.optimize_tower_placement(budget=1000, tower_types=tower_types)


city.visualize_coverage()


start_tower = 0  # Индекс начальной башни
end_tower = 1    # Индекс конечной башни

path = city.find_reliable_path(start_tower, end_tower)
city.visualize_path(path)
