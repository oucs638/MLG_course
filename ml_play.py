"""
The template of the script for the machine learning process in game pingpong
"""

# Import the necessary modules and classes
from mlgame.communication import ml as comm

bal_siz = 5
plt_xsz, plt_ysz, plt_spd = 40, 30, 5
plt_1ps, plt_2ps = 420, 50 + plt_ysz
blk_xsz, blk_ysz = 30, 20
plk_pos, plt_spd = 180, 5
hit_rng = 195


def ml_loop(side: str):
    # 1. Put the initialization code here
    ball_served = False
    blk_est = False
    blk_old = -1

    def correct_pred(pos):
        new_pos = pos
        bound = new_pos // hit_rng  # Determine if it is beyond the boundary
        if (bound > 0):  # pred > 200 # fix landing position
            if (bound % 2 == 0):
                new_pos = new_pos - bound*hit_rng
            else:
                new_pos = hit_rng - (new_pos - hit_rng*bound)
        elif (bound < 0):  # pred < 0
            if (bound % 2 == 1):
                new_pos = abs(new_pos - (bound+1) * hit_rng)
            else:
                new_pos = new_pos + (abs(bound) * hit_rng)
        return new_pos

    def pred_flex(player, pos, spd, t, mode):
        if mode == 'p':
            pos_p = correct_pred(pos + abs(spd * t))
            pos_n = correct_pred(pos - abs(spd * t))
            new_pos = (pos_p + pos_n) // 2
            return new_pos
        else:
            return 100

    def move_to(player, pred):  # move platform to predicted position to catch ball
        if player == '1P':
            if pred > (scene_info["platform_1P"][0] + plt_xsz - bal_siz * 3):
                return 1
            elif pred < (scene_info["platform_1P"][0] + bal_siz * 2):
                return - 1
            else:
                return 0
        else:
            if pred > (scene_info["platform_2P"][0] + plt_xsz - bal_siz * 3):
                return 1
            elif pred < (scene_info["platform_2P"][0] + bal_siz * 2):
                return - 1
            else:
                return 0

    def ml_loop_for_1P(bk_est, bk_old):
        if scene_info["ball_speed"][1] > 0:  # 球正在向下 # ball goes down
            # x means how many frames before catch the ball
            x = (scene_info["platform_1P"][1]-bal_siz-scene_info["ball"]
                 [1]) // scene_info["ball_speed"][1]
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)
            if bk_est:
                if bk_old == -1:
                    pass
                elif (scene_info["ball"][1] + bal_siz) < scene_info["blocker"][1]:
                    if (scene_info["ball_speed"][0] > 0)\
                            and ((scene_info["ball"][0] + bal_siz) < scene_info["blocker"][0]):
                        blk_spd = 5 if (
                            scene_info["blocker"][0] > bk_old) else -5
                        y = (scene_info["blocker"][0] -
                             (scene_info["ball"][0] + bal_siz)) // (scene_info["ball_speed"][0] - blk_spd)
                        tmp_bal_y = scene_info["ball"][1] + \
                            scene_info["ball_speed"][1] * y
                        if (tmp_bal_y > (scene_info["blocker"][1] - bal_siz)) and (tmp_bal_y < (scene_info["blocker"][1] + blk_ysz)):
                            tmp_bal_x = scene_info["ball"][0] + \
                                scene_info["ball_speed"][0] * y
                            pred = tmp_bal_x - \
                                (scene_info["ball_speed"][0]*(x-y))
                    elif (scene_info["ball_speed"][0] < 0)\
                            and (scene_info["ball"][0] > (scene_info["blocker"][0] + blk_xsz)):
                        blk_spd = 5 if (
                            scene_info["blocker"][0] > bk_old) else -5
                        y = (scene_info["ball"][0] -
                             (scene_info["blocker"][0] + blk_xsz)) // (-(scene_info["ball_speed"][0] - blk_spd))
                        tmp_bal_y = scene_info["ball"][1] + \
                            scene_info["ball_speed"][1] * y
                        if (tmp_bal_y > (scene_info["blocker"][1] - bal_siz)) and (tmp_bal_y < (scene_info["blocker"][1] + blk_ysz)):
                            tmp_bal_x = scene_info["ball"][0] + \
                                scene_info["ball_speed"][0] * y
                            pred = tmp_bal_x - \
                                (scene_info["ball_speed"][0]*(x-y))
            # 預測最終位置 # pred means predict ball landing site
            bound = pred // hit_rng  # Determine if it is beyond the boundary
            if (bound > 0):  # pred > 200 # fix landing position
                if (bound % 2 == 0):
                    pred = pred - bound*hit_rng
                else:
                    pred = hit_rng - (pred - hit_rng*bound)
            elif (bound < 0):  # pred < 0
                if (bound % 2 == 1):
                    pred = abs(pred - (bound+1) * hit_rng)
                else:
                    pred = pred + (abs(bound) * hit_rng)
            return move_to(player='1P', pred=pred)
        else:  # 球正在向上 # ball goes up
            x = (scene_info["platform_2P"][1]+30 -
                 scene_info["ball"][1]) // scene_info["ball_speed"][1]
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)
            bound = pred // hit_rng
            if (bound > 0):
                if (bound % 2 == 0):
                    pred = pred - bound*hit_rng
                else:
                    pred = hit_rng - (pred - hit_rng*bound)
            elif (bound < 0):
                if bound % 2 == 1:
                    pred = abs(pred - (bound+1) * hit_rng)
                else:
                    pred = pred + (abs(bound) * hit_rng)
            new_pred = pred_flex(player='1P', pos=pred,
                                 spd=scene_info["ball_speed"][0],
                                 t=x, mode='p')
            if bk_est:
                if bk_old == -1:
                    pass
                elif scene_info["ball"][1] > (scene_info["blocker"][1] + blk_ysz):
                    blk_spd = 5 if (
                        scene_info["blocker"][0] > bk_old) else - 5
                    y = (scene_info["ball"][1] -
                         (scene_info["blocker"][1] +
                          blk_ysz)) // (-scene_info["ball_speed"][1])
                    flg = 0
                    tmp_bal_x = scene_info["ball"][0] + \
                        scene_info["ball_speed"][0] * y
                    if tmp_bal_x < 0:
                        flg = -1
                    elif tmp_bal_x > hit_rng:
                        flg = 1
                    tmp_bal_x = correct_pred(tmp_bal_x)
                    tmp_blk_x = scene_info["blocker"][0] + blk_spd * y
                    if tmp_blk_x < 0:
                        tmp_blk_x = -tmp_blk_x
                    elif tmp_blk_x > 160:
                        tmp_blk_x = 160 - (tmp_blk_x - 160)
                    if tmp_bal_x > (tmp_blk_x - bal_siz) and tmp_bal_x < (tmp_blk_x + blk_xsz):
                        if flg == 0:
                            new_pred = correct_pred(
                                tmp_bal_x + scene_info["ball_speed"][0] * y)
                        elif flg == 1:
                            new_pred = correct_pred(
                                tmp_bal_x + (-abs(scene_info["ball_speed"][0]) * y))
                        elif flg == -1:
                            new_pred = correct_pred(
                                tmp_bal_x + abs(scene_info["ball_speed"][0]) * y)
            return move_to(player='1P', pred=new_pred)

    def ml_loop_for_2P(bk_est, bk_old):  # as same as 1P
        if scene_info["ball_speed"][1] > 0:
            x = (scene_info["platform_1P"][1]-bal_siz-scene_info["ball"]
                 [1]) // scene_info["ball_speed"][1]
            # 預測最終位置 # pred means predict ball landing site
            pred = scene_info["ball"][0]+(scene_info["ball_speed"][0]*x)
            bound = pred // hit_rng  # Determine if it is beyond the boundary
            if (bound > 0):  # pred > 200 # fix landing position
                if (bound % 2 == 0):
                    pred = pred - bound*hit_rng
                else:
                    pred = hit_rng - (pred - hit_rng*bound)
            elif (bound < 0):  # pred < 0
                if (bound % 2 == 1):
                    pred = abs(pred - (bound+1) * hit_rng)
                else:
                    pred = pred + (abs(bound) * hit_rng)
            new_pred = pred_flex(player='2P', pos=pred,
                                 spd=scene_info["ball_speed"][0],
                                 t=x, mode='p')
            if bk_est:
                if bk_old == -1:
                    pass
                elif (scene_info["ball"][1] + bal_siz) < scene_info["blocker"][1]:
                    blk_spd = 5 if (
                        scene_info["blocker"][0] > bk_old) else - 5
                    y = (scene_info["blocker"][1] -
                         (scene_info["ball"][1] + bal_siz)) // scene_info["ball_speed"][1]
                    flg = 0
                    tmp_bal_x = scene_info["ball"][0] + \
                        scene_info["ball_speed"][0] * y
                    if tmp_bal_x < 0:
                        flg = -1
                    elif tmp_bal_x > hit_rng:
                        flg = 1
                    tmp_bal_x = correct_pred(tmp_bal_x)
                    tmp_blk_x = scene_info["blocker"][0] + blk_spd * y
                    if tmp_blk_x < 0:
                        tmp_blk_x = -tmp_blk_x
                    elif tmp_blk_x > 160:
                        tmp_blk_x = 160 - (tmp_blk_x - 160)
                    if tmp_bal_x > (tmp_blk_x - bal_siz) and tmp_bal_x < (tmp_blk_x + blk_xsz):
                        if flg == 0:
                            new_pred = correct_pred(
                                tmp_bal_x + scene_info["ball_speed"][0] * y)
                        elif flg == 1:
                            new_pred = correct_pred(
                                tmp_bal_x + (-abs(scene_info["ball_speed"][0]) * y))
                        elif flg == -1:
                            new_pred = correct_pred(
                                tmp_bal_x + abs(scene_info["ball_speed"][0]) * y)
            return move_to(player='2P', pred=new_pred)
        else:
            x = (scene_info["platform_2P"][1]+30 -
                 scene_info["ball"][1]) // scene_info["ball_speed"][1]
            pred = scene_info["ball"][0] + (scene_info["ball_speed"][0] * x)
            if bk_est:
                if bk_old == -1:
                    pass
                elif scene_info["ball"][1] > (scene_info["blocker"][1] + blk_ysz):
                    if (scene_info["ball_speed"][0] > 0)\
                            and ((scene_info["ball"][0] + bal_siz) < scene_info["blocker"][0]):
                        blk_spd = 5 if (
                            scene_info["blocker"][0] > bk_old) else -5
                        y = (scene_info["blocker"][0] -
                             (scene_info["ball"][0] + bal_siz)) // (scene_info["ball_speed"][0] - blk_spd)
                        tmp_bal_y = scene_info["ball"][1] + \
                            scene_info["ball_speed"][1] * y
                        if (tmp_bal_y > (scene_info["blocker"][1] - bal_siz)) and (tmp_bal_y < (scene_info["blocker"][1] + blk_ysz)):
                            tmp_bal_x = scene_info["ball"][0] + \
                                scene_info["ball_speed"][0] * y
                            pred = tmp_bal_x - \
                                (scene_info["ball_speed"][0]*(x-y))
                    elif (scene_info["ball_speed"][0] < 0)\
                            and (scene_info["ball"][0] > (scene_info["blocker"][0] + blk_xsz)):
                        blk_spd = 5 if (
                            scene_info["blocker"][0] > bk_old) else -5
                        y = (scene_info["ball"][0] -
                             (scene_info["blocker"][0] + blk_xsz)) // (-(scene_info["ball_speed"][0] - blk_spd))
                        tmp_bal_y = scene_info["ball"][1] + \
                            scene_info["ball_speed"][1] * y
                        if (tmp_bal_y > (scene_info["blocker"][1] - bal_siz)) and (tmp_bal_y < (scene_info["blocker"][1] + blk_ysz)):
                            tmp_bal_x = scene_info["ball"][0] + \
                                scene_info["ball_speed"][0] * y
                            pred = tmp_bal_x - \
                                (scene_info["ball_speed"][0]*(x-y))
            bound = pred // hit_rng
            if (bound > 0):
                if (bound % 2 == 0):
                    pred = pred - bound*hit_rng
                else:
                    pred = hit_rng - (pred - hit_rng*bound)
            elif (bound < 0):
                if bound % 2 == 1:
                    pred = abs(pred - (bound+1) * hit_rng)
                else:
                    pred = pred + (abs(bound) * hit_rng)
            return move_to(player='2P', pred=pred)

    # 2. Inform the game process that ml process is ready
    comm.ml_ready()

    # 3. Start an endless loop
    while True:
        # 3.1. Receive the scene information sent from the game process
        scene_info = comm.recv_from_game()
        if "blocker" in scene_info:
            blk_est = True
        else:
            blk_est = False

        # 3.2. If either of two sides wins the game, do the updating or
        #      resetting stuff and inform the game process when the ml process
        #      is ready.
        if scene_info["status"] != "GAME_ALIVE":
            # Do some updating or resetting stuff
            ball_served = False

            # 3.2.1 Inform the game process that
            #       the ml process is ready for the next round
            comm.ml_ready()
            continue

        # 3.3 Put the code here to handle the scene information

        # 3.4 Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_to_game(
                {"frame": scene_info["frame"], "command": "SERVE_TO_LEFT"})
            ball_served = True
        else:
            if side == "1P":
                command = ml_loop_for_1P(blk_est, blk_old)
            else:
                command = ml_loop_for_2P(blk_est, blk_old)

            if blk_est:
                blk_old = scene_info["blocker"][0]

            if command == 1:
                comm.send_to_game(
                    {"frame": scene_info["frame"], "command": "MOVE_RIGHT"})
            elif command == -1:
                comm.send_to_game(
                    {"frame": scene_info["frame"], "command": "MOVE_LEFT"})
            else:  # command == 0
                comm.send_to_game(
                    {"frame": scene_info["frame"], "command": "NONE"})
