from personage import Hero, Enemy, Bonus, Labyrinth, Game


class GenerateLevel:
    def __init__(self):
        self.speed_enemy = 300
        self.labirinth_1 = Labyrinth("map1.tmx", [10, 46], 46)
        self.labirinth_2 = Labyrinth("map2.tmx", [15, 46], 46)
        self.labirinth_3 = Labyrinth("map3.tmx", [30, 46], 46)
        self.hero = Hero("hero.png", (10, 9))
        self.enemy_1 = Enemy("enemy.png", (19, 9), self.speed_enemy)
        self.enemy_2 = Enemy("enemy.png", (1, 7), self.speed_enemy)
        self.enemy_3 = Enemy("enemy.png", (19, 17), self.speed_enemy)
        self.bonus_1 = Bonus((17, 5))
        self.bonus_2 = Bonus((19, 17))
        self.bonus_3 = Bonus((1, 1))
        self.bonus_4 = Bonus((1, 9))
        self.bonus_5 = Bonus((8, 4))
        self.bonus_6 = Bonus((1, 17))
        self.all_bonus = [self.bonus_1, self.bonus_2, self.bonus_3, self.bonus_4, self.bonus_5, self.bonus_6]

    def level_selection(self, level):
        if level == 1:
            self.game = Game(self.labirinth_1, self.hero, [self.enemy_1], [self.bonus_1])
        elif level == 2:
            self.game = Game(self.labirinth_2, self.hero, [self.enemy_1], [self.bonus_2])
        elif level == 3:
            self.game = Game(self.labirinth_3, self.hero, [self.enemy_1], [self.bonus_3])
        elif level == 4:
            self.game = Game(self.labirinth_1, self.hero, [self.enemy_1, self.enemy_2], [self.bonus_1, self.bonus_2])
        elif level == 5:
            self.game = Game(self.labirinth_2, self.hero, [self.enemy_1, self.enemy_2], [self.bonus_3, self.bonus_2])
        elif level == 6:
            self.game = Game(self.labirinth_3, self.hero, [self.enemy_1, self.enemy_2], [self.bonus_3, self.bonus_2])
        elif level == 7:
            self.game = Game(self.labirinth_1, self.hero,
                             [self.enemy_1, self.enemy_2, self.enemy_3], [self.bonus_1, self.bonus_2, self.bonus_4])
        elif level == 8:
            self.game = Game(self.labirinth_2, self.hero,
                             [self.enemy_1, self.enemy_2, self.enemy_3], [self.bonus_3, self.bonus_2, self.bonus_5])
        elif level == 9:
            self.game = Game(self.labirinth_3, self.hero,
                             [self.enemy_1, self.enemy_2, self.enemy_3], [self.bonus_2, self.bonus_3, self.bonus_6])
        return self.game

    def score(self):
        all_score = 0
        for bonus in self.all_bonus:
            all_score += bonus.score
        return all_score
