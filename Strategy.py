from API import Game
import random


class Strategy(Game):
    """
        FILL THIS METHOD OUT FOR YOUR BOT:
        Method to set unit initializations. Run at the beginning of a game, after assigning player numbers.
        We have given you a default implementation for this method.
        OUTPUT:
            An array of 3 dictionaries, where each dictionary details a unit. The dictionaries should have the following fields
                "health": An integer indicating the desired health for that unit
                "speed": An integer indicating the desired speed for that unit
                "unitId": An integer indicating the desired id for that unit. In this provided example, we assign Ids 1,2,3 if you are player1, or 4,5,6 if you are player2
                "attackPattern": a 7x7 2d integer list indicating the desired attack pattern for that unit
                "terrainPattern": a 7x7 2d boolean list indicating the desired terrain pattern for that unit.
        Note: terrainPattern and attackPattern should be indexed x,y. with (0,0) being the bottom left
        If player_id is 1, UnitIds for the bots should be 1,2,3. If player_id is 2, UnitIds should be 4,5,6
    """

    def get_setup(self):
        units = []
        for i in range(3):
            unit = {"health": 6, "speed": 4}
            unit["attackPattern"] = [[0] * 7 for j in range(7)]
            # if you are player1, unitIds will be 1,2,3. If you are player2, they will be 4,5,6
            unit["unitId"] = i + 1
            if self.player_id == 2:
                unit["unitId"] += 3
            unit["terrainPattern"] = [[False]*7 for j in range(7)]
            # These sample bot will do damage to the tiles to its left, right, and up. And build terrain behind it
            unit["attackPattern"][3][5] = 4
            units.append(unit)
        return units

    """
        FILL THIS METHOD OUT FOR YOUR BOT:
        Method to implement the competitors strategy in the next turn of the game.
        We have given you a default implementation here.
        OUTPUT:
            A list of 3 dictionaries, each of which indicates what to do on a given turn with that specific unit. Each dictionary should have the following keys:
                "unitId": The Id of the unit this dictionary will detail the action for
                "movement": an array of directions ("UP", "DOWN", "LEFT", or "RIGHT") details how you want that unit to move on this turn
                "attack": the direction in which to attack ("UP", "DOWN", "LEFT", or "RIGHT")
                "priority": The bots move one at a time, so give the priority which you want them to act in (1,2, or 3)
    """

    def do_turn(self):
        my_units = self.get_my_units()
        firstRound = False
        for unit in my_units:
            if unit.pos.x == 0 and unit.pos.y == 0:
                firstRound = True
        if firstRound == False:
            order = list(range(len(my_units)))
        random.shuffle(order)
        decision = []
        unitIndex = 0
        blockedTiles = self.get_blocks()
        for i in range(len(my_units)):
            blockedTiles.append((my_units[i].pos.x, my_units[i].pos.y))

        for i in order:
            our_location = (my_units[unitIndex].pos.x,
                            my_units[unitIndex].pos.y)
            futureBlock = self.find_new_blocked_by_ally(
                our_location, blockedTiles)
            blockedTiles.remove(our_location)
            print(self.offensive_move(our_location, blockedTiles), flush=True)
            decision.append(
                {
                    "priority": i + 1,
                    "movement": self.offensive_move(our_location, blockedTiles),
                    "attack": self.able_to_attack(our_location),
                    "unitId": my_units[unitIndex].id
                }
            )
            blockedTiles.append(futureBlock)
            unitIndex += 1
        return decision

    # Remove tiles from movement options if they are covered by battle royale border
    def get_blocks(self):
        tiles_to_avoid = []
        for i in range(12):
            for j in range(12):
                tile = self.get_tile((i, j))
                if tile.type != 'BLANK':
                    tiles_to_avoid.append((i, j))
        enemyUnits = self.get_enemy_units()
        for unit in enemyUnits:
            tiles_to_avoid.append((unit.pos.x, unit.pos.y))
        if self.turnsTaken > 13:
            for i in range(12):
                tiles_to_avoid.append(self.get_tile((i, 0)))
                tiles_to_avoid.append(self.get_tile((i, 11)))
                tiles_to_avoid.append(self.get_tile((0, i)))
                tiles_to_avoid.append(self.get_tile((11, i)))
        if self.turnsTaken > 18:
            for i in range(12):
                tiles_to_avoid.append(self.get_tile((i, 2)))
                tiles_to_avoid.append(self.get_tile((i, 10)))
                tiles_to_avoid.append(self.get_tile((2, i)))
                tiles_to_avoid.append(self.get_tile((10, i)))
        if self.turnsTaken > 22:
            for i in range(12):
                tiles_to_avoid.append(self.get_tile((i, 3)))
                tiles_to_avoid.append(self.get_tile((i, 9)))
                tiles_to_avoid.append(self.get_tile((3, i)))
                tiles_to_avoid.append(self.get_tile((9, i)))
        if self.turnsTaken > 25:
            for i in range(12):
                tiles_to_avoid.append(self.get_tile((i, 4)))
                tiles_to_avoid.append(self.get_tile((i, 8)))
                tiles_to_avoid.append(self.get_tile((4, i)))
                tiles_to_avoid.append(self.get_tile((8, i)))
        if self.turnsTaken > 27:
            for i in range(12):
                tiles_to_avoid.append(self.get_tile((i, 5)))
                tiles_to_avoid.append(self.get_tile((i, 7)))
                tiles_to_avoid.append(self.get_tile((5, i)))
                tiles_to_avoid.append(self.get_tile((7, i)))
        return tiles_to_avoid

    # Find tiles that would allow for attacking an enemy's current location
    def find_attack_positions(self):
        attackPositions = []
        enemy_units = self.get_target_units()
        for enemy_unit in enemy_units:
            attackPositions.append(
                (enemy_unit[0], enemy_unit[1] + 2, enemy_unit[2]))
            attackPositions.append(
                (enemy_unit[0] + 2, enemy_unit[1], enemy_unit[2]))
            attackPositions.append(
                (enemy_unit[0], enemy_unit[1] - 2, enemy_unit[2]))
            attackPositions.append(
                (enemy_unit[0] - 2, enemy_unit[1], enemy_unit[2]))
        for attackPosition in attackPositions:
            if attackPosition[0] < 1 or attackPosition[1] < 0 or attackPosition[0] > 10 or attackPosition[1] > 10:
                attackPositions.remove(attackPosition)
        return attackPositions

    # Returns positions that will be blocked by future allied movement
    def find_new_blocked_by_ally(self, our_location, blocks):
        attackPositions = self.find_attack_positions()
        paths = []
        for attackPosition in attackPositions:
            paths.append((self.path_to(
                our_location, (attackPosition[0], attackPosition[1]), blocks), attackPosition[2]))
        paths = list(filter(lambda path: path[0] != None, paths))
        botOnlyPaths = list(filter(lambda path: path[1] == 'BOT', paths))
        if len(botOnlyPaths) > 0:
            paths = botOnlyPaths
        if len(paths) > 0:
            path = paths[0][0]
            print(path, flush=True)
            for i in range(4):
                path.append("STAY")
            # THIS IS SPEED DEPENDENT!
            path = path[:4]
            x = our_location[0]
            y = our_location[1]
            for move in path:
                if move == "UP":
                    y += 1
                elif move == "RIGHT":
                    x += 1
                elif move == "DOWN":
                    y -= 1
                elif move == "LEFT":
                    x -= 1
            return (x, y)
        return our_location

    # Returns a path to use for movement
    def offensive_move(self, our_location, blocks):
        attackPositions = self.find_attack_positions()
        paths = []
        for attackPosition in attackPositions:
            paths.append((self.path_to(
                our_location, (attackPosition[0], attackPosition[1]), blocks), attackPosition[2]))
        paths = list(filter(lambda path: path[0] != None, paths))
        botOnlyPaths = list(filter(lambda path: path[1] == 'BOT', paths))
        if len(botOnlyPaths) > 0:
            paths = botOnlyPaths
        if len(paths) > 0:
            path = paths[0][0]
            for i in range(4):
                path.append("STAY")
            # THIS IS SPEED DEPENDENT!
            return path[:4]
        return ["STAY", "STAY", "STAY", "STAY"]

    # Returns direction to fire if movement will leave us somewhere we will be able to hit a enemy that has yet to move
    def able_to_attack(self, our_location):
        enemy_units = self.get_target_units()
        for enemy_unit in enemy_units:
            if enemy_unit[0] == our_location[0] and enemy_unit[1] + 2 == our_location[1]:
                print("FIRE UP", flush=True)
                return "UP"
            elif enemy_unit[0] == our_location[0] + 2 and enemy_unit[1] == our_location[1]:
                print("FIRE RIGHT", flush=True)
                return "RIGHT"
            elif enemy_unit[0] == our_location[0] and enemy_unit[1] - 2 == our_location[1]:
                print("FIRE DOWN", flush=True)
                return "DOWN"
            elif enemy_unit[0] == our_location[0] - 2 and enemy_unit[1] == our_location[1]:
                print("FIRE LEFT", flush=True)
                return "LEFT"
            else:
                return "DOWN"

    # Returns list of units to attack (Enemy bots and rocks)
    def get_target_units(self):
        target_units = list(
            map(lambda unit: (unit.pos.x, unit.pos.y, "BOT"), self.get_enemy_units()))
        if self.get_tile((4, 3)).type == 'DESTRUCTIBLE':
            target_units.append((4, 3, "NOT BOT"))
        if self.get_tile((5, 4)).type == 'DESTRUCTIBLE':
            target_units.append((5, 4, "NOT BOT"))
        if self.get_tile((6, 7)).type == 'DESTRUCTIBLE':
            target_units.append((6, 7, "NOT BOT"))
        if self.get_tile((7, 8)).type == 'DESTRUCTIBLE':
            target_units.append((7, 8, "NOT BOT"))
        return target_units
