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
    filename = path.join(path.dirname(__file__), 'save',
                         'clf_KNN_BallAndDirection.pickle')
    with open(filename, 'rb') as file:
        clf = pickle.load(file)
    bal_lst = [93, 395]

    def get_vector(bal_now, bal_pre, plt_pos):
        bal_xsp = bal_now[0] - bal_pre[0]
        bal_ysp = bal_now[1] - bal_pre[1]
        bal_siz, hit_max = 5, 195
        res_pos = bal_now[0]
        if bal_ysp > 0:
            tp_time = (plt_pos[1] - bal_siz - bal_now[1]) // bal_ysp
            res_pos = abs(bal_now[0] + bal_xsp * tp_time)
            if res_pos > hit_max:
                if (res_pos // hit_max) % 2 == 0:
                    res_pos -= (res_pos // hit_max) * hit_max
                else:
                    res_pos -= (res_pos // hit_max) * hit_max
                    res_pos = hit_max - res_pos
        else:
            res_pos = bal_now[0]
        return res_pos

    def data_preprocess(bal, plt, bal_pre):
        cmd = 0
        plt_xsz, bal_siz = 40, 5
        res_pos = get_vector(bal, bal_pre, plt)
        if res_pos < (plt[0] + bal_siz):
            cmd = -1
        elif res_pos > (plt[0] + plt_xsz - bal_siz * 2):
            cmd = 1
        else:
            cmd = 0
        return bal, [cmd, cmd]

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()
        bal_lst, frm_info = data_preprocess(
            scene_info.ball, scene_info.platform, bal_lst)
        bal_lst = scene_info.ball
        frm_info = np.array(frm_info).reshape(1, -1)
        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
                scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False
            bal_lst = [93, 395]

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information

        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(
                scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:

            y = clf.predict(frm_info)

            if y == 0:
                comm.send_instruction(scene_info.frame, PlatformAction.NONE)
                print('NONE')
            elif y == -1:
                comm.send_instruction(
                    scene_info.frame, PlatformAction.MOVE_LEFT)
                print('LEFT')
            elif y == 1:
                comm.send_instruction(
                    scene_info.frame, PlatformAction.MOVE_RIGHT)
                print('RIGHT')
