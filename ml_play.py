class MLPlay:
    def __init__(self, player):
        self.player = player
        if self.player == "player1":
            self.player_no = 0
        elif self.player == "player2":
            self.player_no = 1
        elif self.player == "player3":
            self.player_no = 2
        elif self.player == "player4":
            self.player_no = 3
        self.car_vel = 0                            # speed initial
        self.car_pos = (0, 0)                        # pos initial
        self.car_lane = self.car_pos[0] // 70       # lanes 0 ~ 8
        self.lanes = [35, 105, 175, 245, 315,
                      385, 455, 525, 595]  # lanes center
        pass

    def update(self, scene_info):
        """
        9 grid relative position
        |    |    |    |
        |  1 |  2 |  3 |
        |    |  5 |    |
        |  4 |  c |  6 |
        |    |    |    |
        |  7 |  8 |  9 |
        9 grid relative position
        |    |    |    |    |    |    |    |    |    |
        | 31 | 21 | 11 |  1 |  2 |  3 | 13 | 23 | 33 |
        |    |    |    |    |  5 |    |    |    |    |
        | 34 | 24 | 14 |  4 |  c |  6 | 16 | 26 | 36 |
        |    |    |    |    |    |    |    |    |    |
        | 37 | 27 | 17 |  7 |  8 |  9 | 19 | 29 | 39 |
        """
        def check_grid():
            grid = set()
            speed_ahead = 100
            if self.car_pos[0] <= 245:  # left bound
                grid.add(31)
                grid.add(34)
                grid.add(37)
                if self.car_pos[0] <= 175:
                    grid.add(21)
                    grid.add(24)
                    grid.add(27)
                if self.car_pos[0] <= 105:
                    grid.add(11)
                    grid.add(14)
                    grid.add(17)
                if self.car_pos[0] <= 35:
                    grid.add(1)
                    grid.add(4)
                    grid.add(7)
            elif self.car_pos[0] >= 385:  # right bound
                grid.add(33)
                grid.add(36)
                grid.add(39)
                if self.car_pos[0] >= 455:
                    grid.add(23)
                    grid.add(26)
                    grid.add(29)
                if self.car_pos[0] >= 525:
                    grid.add(13)
                    grid.add(16)
                    grid.add(19)
                if self.car_pos[0] >= 595:
                    grid.add(3)
                    grid.add(6)
                    grid.add(9)

            for car in scene_info["cars_info"]:
                if car["id"] != self.player_no:
                    x = self.car_pos[0] - car["pos"][0]  # x relative position
                    y = self.car_pos[1] - car["pos"][1]  # y relative position

                    if x >= -40 and x <= 40:
                        if y > 0 and y < 300:
                            grid.add(2)
                            if y < 200:
                                speed_ahead = car["velocity"]
                                grid.add(5)
                        elif y < 0 and y > -200:
                            grid.add(8)

                    if x >= -110 and x < -40:
                        if y > 80 and y < 250:
                            grid.add(3)
                        elif y > -200 and y < -80:
                            grid.add(9)
                        elif y >= -80 and y <= 80:
                            grid.add(6)
                    if x >= -180 and x < -110:
                        if y > 80 and y < 250:
                            grid.add(13)
                        elif y > -200 and y < -80:
                            grid.add(19)
                        elif y >= -80 and y <= 80:
                            grid.add(16)
                    if x >= -250 and x < -180:
                        if y > 80 and y < 250:
                            grid.add(23)
                        elif y > -200 and y < -80:
                            grid.add(29)
                        elif y >= -80 and y <= 80:
                            grid.add(26)
                    if x >= -320 and x < -250:
                        if y > 80 and y < 250:
                            grid.add(33)
                        elif y > -200 and y < -80:
                            grid.add(39)
                        elif y >= -80 and y <= 80:
                            grid.add(36)

                    if x > 40 and x <= 110:
                        if y > 80 and y < 250:
                            grid.add(1)
                        elif y > -200 and y < -80:
                            grid.add(7)
                        elif y >= -80 and y <= 80:
                            grid.add(4)
                    if x > 110 and x <= 180:
                        if y > 80 and y < 250:
                            grid.add(11)
                        elif y > -200 and y < -80:
                            grid.add(17)
                        elif y >= -80 and y <= 80:
                            grid.add(14)
                    if x > 180 and x <= 250:
                        if y > 80 and y < 250:
                            grid.add(21)
                        elif y > -200 and y < -80:
                            grid.add(27)
                        elif y >= -80 and y <= 80:
                            grid.add(24)
                    if x > 250 and x <= 320:
                        if y > 80 and y < 250:
                            grid.add(31)
                        elif y > -200 and y < -80:
                            grid.add(37)
                        elif y >= -80 and y <= 80:
                            grid.add(34)

            return move(grid=grid, speed_ahead=speed_ahead)

        def move(grid, speed_ahead):
            # if self.player_no == 0:
            #     print(grid)
            if len(grid) == 0:
                return ["SPEED"]
            else:
                if (2 not in grid):  # Check forward
                    # Back to lane center
                    # return ["SPEED"]
                    if self.car_pos[0] > self.lanes[self.car_lane]:
                        if (1 not in grid):
                            return ["SPEED", "MOVE_LEFT"]
                        else:
                            return ["SPEED", "MOVE_RIGHT"]
                    elif self.car_pos[0] < self.lanes[self.car_lane]:
                        if (3 not in grid):
                            return ["SPEED", "MOVE_RIGHT"]
                        else:
                            return ["SPEED", "MOVE_LEFT"]
                    else:
                        return ["SPEED"]
                else:
                    if (5 in grid):  # NEED to BRAKE
                        if (4 not in grid) and (6 not in grid):
                            if (1 not in grid) and (3 not in grid):
                                L, R = 0, 0
                                if (11 in grid):
                                    L += 1
                                if (21 in grid):
                                    L += 1
                                if (31 in grid):
                                    L += 1
                                if (13 in grid):
                                    R += 1
                                if (23 in grid):
                                    R += 1
                                if (33 in grid):
                                    R += 1
                                if L < R:
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                elif L > R:
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]
                                else:
                                    if (self.car_pos[0] // 70) < 4:
                                        if self.car_vel < speed_ahead:
                                            return ["SPEED", "MOVE_RIGHT"]
                                        else:
                                            return ["BRAKE", "MOVE_RIGHT"]
                                    else:
                                        if self.car_vel < speed_ahead:
                                            return ["SPEED", "MOVE_LEFT"]
                                        else:
                                            return ["BRAKE", "MOVE_LEFT"]
                            elif (1 not in grid):
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif (3 not in grid):
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            elif (11 not in grid) and (13 not in grid):
                                L, R = 0, 0
                                if (21 in grid):
                                    L += 1
                                if (31 in grid):
                                    L += 1
                                if (23 in grid):
                                    R += 1
                                if (33 in grid):
                                    R += 1
                                if L < R:
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                elif L > R:
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]
                                else:
                                    if (self.car_pos[0] // 70) < 4:
                                        if self.car_vel < speed_ahead:
                                            return ["SPEED", "MOVE_RIGHT"]
                                        else:
                                            return ["BRAKE", "MOVE_RIGHT"]
                                    else:
                                        if self.car_vel < speed_ahead:
                                            return ["SPEED", "MOVE_LEFT"]
                                        else:
                                            return ["BRAKE", "MOVE_LEFT"]
                            elif (11 not in grid):
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif (13 not in grid):
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                            elif (21 not in grid) and (23 not in grid):
                                L, R = 0, 0
                                if (31 in grid):
                                    L += 1
                                if (33 in grid):
                                    R += 1
                                if L < R:
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_LEFT"]
                                    else:
                                        return ["BRAKE", "MOVE_LEFT"]
                                elif L > R:
                                    if self.car_vel < speed_ahead:
                                        return ["SPEED", "MOVE_RIGHT"]
                                    else:
                                        return ["BRAKE", "MOVE_RIGHT"]
                                else:
                                    if (self.car_pos[0] // 70) < 4:
                                        if self.car_vel < speed_ahead:
                                            return ["SPEED", "MOVE_RIGHT"]
                                        else:
                                            return ["BRAKE", "MOVE_RIGHT"]
                                    else:
                                        if self.car_vel < speed_ahead:
                                            return ["SPEED", "MOVE_LEFT"]
                                        else:
                                            return ["BRAKE", "MOVE_LEFT"]
                            elif (21 not in grid):
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_LEFT"]
                                else:
                                    return ["BRAKE", "MOVE_LEFT"]
                            elif (23 not in grid):
                                if self.car_vel < speed_ahead:
                                    return ["SPEED", "MOVE_RIGHT"]
                                else:
                                    return ["BRAKE", "MOVE_RIGHT"]
                        elif (4 not in grid):  # turn left
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_LEFT"]
                            else:
                                return ["BRAKE", "MOVE_LEFT"]
                        elif (6 not in grid):  # turn right
                            if self.car_vel < speed_ahead:
                                return ["SPEED", "MOVE_RIGHT"]
                            else:
                                return ["BRAKE", "MOVE_RIGHT"]
                        else:
                            if self.car_vel < speed_ahead:  # BRAKE
                                return ["SPEED"]
                            else:
                                return ["BRAKE"]

                    # if (self.car_pos[0] < 60):
                    #     return ["SPEED", "MOVE_RIGHT"]

                    # if (1 not in grid) and (4 not in grid) and (7 not in grid):  # turn left
                    #     return ["SPEED", "MOVE_LEFT"]
                    # if (3 not in grid) and (6 not in grid) and (9 not in grid):  # turn right
                    #     return ["SPEED", "MOVE_RIGHT"]
                    # if (1 not in grid) and (4 not in grid):  # turn left
                    #     return ["SPEED", "MOVE_LEFT"]
                    # if (3 not in grid) and (6 not in grid):  # turn right
                    #     return ["SPEED", "MOVE_RIGHT"]
                    # if (4 not in grid) and (7 not in grid):  # turn left
                    #     return ["MOVE_LEFT"]
                    # if (6 not in grid) and (9 not in grid):  # turn right
                    #     return ["MOVE_RIGHT"]

        if len(scene_info[self.player]) != 0:
            self.car_pos = scene_info[self.player]

        for car in scene_info["cars_info"]:
            if car["id"] == self.player_no:
                self.car_vel = car["velocity"]

        if scene_info["status"] != "ALIVE":
            return "RESET"
        self.car_lane = self.car_pos[0] // 70
        return check_grid()

    def reset(self):
        """
        Reset the status
        """
        pass
