#!/usr/bin/env python3
import curses
import time
import random

PADDLE_H = 5
FRAME_TIME = 0.03  # ~33 FPS


def clamp(value, low, high):
    return max(low, min(value, high))


def reset_ball(w, h, direction):
    return {
        "x": w / 2,
        "y": h / 2,
        "dx": direction * 1.0,
        "dy": random.choice([-0.5, -0.3, 0.3, 0.5]),
    }


def main(stdscr):
    curses.curs_set(0)      # hide cursor
    stdscr.nodelay(True)    # don't block waiting for keys
    stdscr.keypad(True)

    h, w = stdscr.getmaxyx()
    if h < 15 or w < 40:
        raise SystemExit("Terminal too small. Resize to at least 40x15.")

    left_y = h // 2 - PADDLE_H // 2
    right_y = left_y
    score_l = score_r = 0
    ball = reset_ball(w, h, random.choice([-1, 1]))
    paused = False

    while True:
        # ---- input ----
        key = stdscr.getch()
        if key == ord("q"):
            break
        if key == ord("p"):
            paused = not paused
        if not paused:
            if key == ord("w"):
                left_y -= 2
            elif key == ord("s"):
                left_y += 2
            if key == curses.KEY_UP:
                right_y -= 2
            elif key == curses.KEY_DOWN:
                right_y += 2

        left_y = clamp(left_y, 1, h - PADDLE_H - 1)
        right_y = clamp(right_y, 1, h - PADDLE_H - 1)

        # ---- update ----
        if not paused:
            ball["x"] += ball["dx"]
            ball["y"] += ball["dy"]

            # bounce off top and bottom walls
            if ball["y"] <= 1 or ball["y"] >= h - 2:
                ball["dy"] = -ball["dy"]
                ball["y"] = clamp(ball["y"], 1, h - 2)

            # left paddle collision
            if int(ball["x"]) <= 2 and left_y <= ball["y"] < left_y + PADDLE_H:
                ball["dx"] = abs(ball["dx"]) * 1.05
                offset = (ball["y"] - (left_y + PADDLE_H / 2)) / (PADDLE_H / 2)
                ball["dy"] = offset * 0.8

            # right paddle collision
            if int(ball["x"]) >= w - 3 and right_y <= ball["y"] < right_y + PADDLE_H:
                ball["dx"] = -abs(ball["dx"]) * 1.05
                offset = (ball["y"] - (right_y + PADDLE_H / 2)) / (PADDLE_H / 2)
                ball["dy"] = offset * 0.8

            # cap speed so the game stays playable
            ball["dx"] = clamp(ball["dx"], -2.0, 2.0)

            # scoring
            if ball["x"] < 0:
                score_r += 1
                ball = reset_ball(w, h, 1)
            elif ball["x"] > w - 1:
                score_l += 1
                ball = reset_ball(w, h, -1)

        # ---- draw ----
        stdscr.erase()
        stdscr.border()
        for y in range(1, h - 1, 2):
            stdscr.addch(y, w // 2, "|")  # center line
        for i in range(PADDLE_H):
            stdscr.addch(left_y + i, 2, "#")
            stdscr.addch(right_y + i, w - 3, "#")
        stdscr.addch(int(ball["y"]), int(ball["x"]), "O")
        score_text = f" {score_l}   {score_r} "
        stdscr.addstr(0, w // 2 - len(score_text) // 2, score_text)
        if paused:
            stdscr.addstr(h // 2, w // 2 - 3, "PAUSED")
        stdscr.refresh()

        time.sleep(FRAME_TIME)


if __name__ == "__main__":
    curses.wrapper(main)
