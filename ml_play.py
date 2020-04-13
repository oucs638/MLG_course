"""
The template of the main script of the machine learning process
"""
import pickle
from os import path

import numpy as np
import games.arkanoid.communication as comm
from games.arkanoid.communication import (
    SceneInfo, GameStatus, PlatformAction
)

x_axis_max, y_axis_max = 200, 500
bal_siz, bal_spd = 5, 7
plt_xsz, ply_ysz, plt_spd, plt_xin, plt_yin = 40, 5, 5, 75, 400
hit_sam_spd, hit_opp_spd = 10, 7
hit_rng_max = x_axis_max - bal_siz
brk_xsz, brk_ysz = 25, 10


def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False
    bal_xrc, bal_yrc, bal_xsp, bal_ysp = -1, -1, bal_spd, -bal_spd
    res_pos = plt_xin + 20
    filename = path.join(path.dirname(__file__), 'save',
                         'clf_KMeans_BallAndDirection.pickle')
    with open(filename, 'rb') as file:
        clf = pickle.load(file)
    s = [93, 93]

    def get_direction(ball_x, ball_y, ball_pre_x, ball_pre_y):
        VectorX = ball_x - ball_pre_x
        VectorY = ball_y - ball_pre_y
        if (VectorX >= 0 and VectorY >= 0):
            return 0
        elif (VectorX > 0 and VectorY < 0):
            return 1
        elif (VectorX < 0 and VectorY > 0):
            return 2
        elif (VectorX < 0 and VectorY < 0):
            return 3

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
                scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        if (bal_xrc < 0 and bal_yrc < 0) or (not ball_served):
            bal_xrc, bal_yrc = scene_info.ball
            bal_xsp, bal_ysp = -7, -7
        else:
            bal_xsp = scene_info.ball[0] - bal_xrc
            bal_ysp = scene_info.ball[1] - bal_yrc
            bal_xrc, bal_yrc = scene_info.ball
        # calculate the ball landing pos
        if ball_served and bal_ysp > 0:
            tp_time = (plt_yin - bal_siz - scene_info.ball[1]) // bal_ysp
            res_pos = abs(scene_info.ball[0] + bal_xsp * tp_time)
            if res_pos > hit_rng_max:
                if (res_pos // hit_rng_max) % 2 == 0:
                    res_pos -= (res_pos // hit_rng_max) * hit_rng_max
                else:
                    res_pos -= (res_pos // hit_rng_max) * hit_rng_max
                    res_pos = hit_rng_max - res_pos
        else:
            res_pos = scene_info.platform[0] + plt_xsz//2

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(
                scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            if res_pos < scene_info.platform[0] + bal_siz:
                comm.send_instruction(
                    scene_info.frame, PlatformAction.MOVE_LEFT)
            elif res_pos > (scene_info.platform[0] + plt_xsz - bal_siz*2):
                comm.send_instruction(
                    scene_info.frame, PlatformAction.MOVE_RIGHT)
            else:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
