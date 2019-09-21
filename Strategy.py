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
            unit = {"health": 5, "speed": 5}
            unit["attackPattern"] = [[0] * 7 for j in range(7)]
            # if you are player1, unitIds will be 1,2,3. If you are player2, they will be 4,5,6
            unit["unitId"] = i + 1
            if self.player_id == 2:
                unit["unitId"] += 3
            unit["terrainPattern"] = [[False]*7 for j in range(7)]
            # These sample bot will do damage to the tiles to its left, right, and up. And build terrain behind it
            # unit["attackPattern"][3][2] = 2
            # unit["attackPattern"][2][3] = 2
            # unit["attackPattern"][4][2] = 2
            # unit["terrainPattern"][3][2] = True
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
        order = list(range(len(my_units)))
        random.shuffle(order)
        decision = []
        unitId = 0
        blockedTiles = self.get_blocks()

        gradient = self.flatten_2d_array(self.gen_atk_tileset_all())

        greater_than_1 = list(filter(lambda tile: tile[0] > 3, gradient))

        greater_than_1.sort(key=self.take_threat)

        for i in order:
            movement = ["STAY"]*my_units[unitId].speed
            bestBackupMove = ["STAY"]*my_units[unitId].speed
            for tile in greater_than_1:
                path = self.path_to(
                    (my_units[unitId].pos.x, my_units[unitId].pos.y), (tile[1], tile[2]), blockedTiles)
                if path != None:
                    bestBackupMove = path[0: my_units[unitId].speed]
                if path != None and len(path) <= my_units[unitId].speed:
                    movement = path
                    while len(movement) < my_units[unitId].speed:
                        movement.append("STAY")
            if len(movement) == 0:
                movement = bestBackupMove

            print(unitId, flush=True)
            print(movement, flush=True)
            decision.append(
                {
                    "priority": i + 1,
                    "movement": movement,
                    "attack": "DOWN",
                    "unitId": my_units[unitId].id
                }
            )
            unitId += 1
        return decision

    def take_threat(self, elem):
        return elem[0]

    def flatten_2d_array(self, arr2d):
        arr1d = []
        for arr in arr2d:
            for element in arr:
                arr1d.append(element)
        return arr1d

    def get_blocks(self):
        tiles_to_avoid = []
        for i in range(12):
            for j in range(12):
                tile = self.get_tile((i, j))
                if tile.type != 'BLANK':
                    tiles_to_avoid.append((i, j))
        return tiles_to_avoid

    """
    Returns a 2d int array showing how close to the edge of a single unit's "offensive range" each tile is.
    Does not account for attack patterns or obstacles.
    """

    def gen_atk_tileset_single(self, unit):

        tileset = []                                        # the 2d tileset returned
        # a temp storage for each row of tileset
        tilesetRow = []
        # the range the unit can theoretically attack on their turn
        atkRange = 4 + unit.speed

        for i in range(12):
            for j in range(12):

                x = j                                       # x is left to right
                # y is bottom to top
                y = (11 - i)

                xDist = abs(unit.pos.x - x)
                yDist = abs(unit.pos.y - y)

                dist = xDist + yDist

                # if the tile can be attacked by the unit in the next turn, it is nonzero
                tilesetRow.append((max(0, atkRange - dist), x, y))

            tileset.append(tilesetRow)

        return tileset

    """
    Returns a 2d int array showing how close to the edge of all enemy units' "offensive range" each tile is.
    Does not account for attack patterns or obstacles.
    """

    def gen_atk_tileset_all(self):
        tileset3D = []

        for unit in self.get_enemy_units():
            if unit.hp > 0:
                tileset3D.append(self.gen_atk_tileset_single(unit))

        tilesetFinal = []
        tilesetRowFinal = []

        for i in range(12):
            for j in range(12):
                x = j                                       # x is left to right
                # y is bottom to top
                y = (11 - i)
                maxThreat = 0
                for k in range(len(tileset3D)):
                    maxThreat = max(maxThreat, tileset3D[k][x][y][0])

                tilesetRowFinal.append((maxThreat, x, y))
            tilesetFinal.append(tilesetRowFinal)

        return tilesetFinal
