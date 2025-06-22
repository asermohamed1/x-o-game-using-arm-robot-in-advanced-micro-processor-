import cv2
import numpy as np
import time
import SerialCom

# === ROI SETTINGS ===
ROI_TOP_LEFT = (100, 100)
ROI_BOTTOM_RIGHT = (900, 900)
ROI_WIDTH = ROI_BOTTOM_RIGHT[0] - ROI_TOP_LEFT[0]
ROI_HEIGHT = ROI_BOTTOM_RIGHT[1] - ROI_TOP_LEFT[1]

# Initialize serial communication
serial_com = SerialCom.SerialCom()

def send_command_to_arduino(command):
    """Sends a command to Arduino and waits for 'DONE' response."""
    serial_com.write(command + "\n")
    print(f"📡 Sent to Arduino: {command}")

    while True:
        response = serial_com.recieve().strip()
        if response == "done":
            print(f"✅ Arduino completed: {command}")
            break
        time.sleep(0.1)



Robot_moves = [
    "top-left", "top-center", "top-right",
    "middle-left", "middle-center", "middle-right",
    "bottom-left", "bottom-center", "bottom-right"
]

board = [' '] * 9

win_combos = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],
    [0, 3, 6], [1, 4, 7], [2, 5, 8],
    [0, 4, 8], [2, 4, 6]
]

def is_winner(brd, player):
    return any(all(brd[i] == player for i in combo) for combo in win_combos)

def get_available_moves(brd):
    return [i for i, cell in enumerate(brd) if cell == ' ']

def minimax(brd, is_maximizing, ai_symbol, player_symbol):
    if is_winner(brd, ai_symbol):
        return 1
    elif is_winner(brd, player_symbol):
        return -1
    elif ' ' not in brd:
        return 0

    scores = []
    for move in get_available_moves(brd):
        brd[move] = ai_symbol if is_maximizing else player_symbol
        score = minimax(brd, not is_maximizing, ai_symbol, player_symbol)
        brd[move] = ' '
        scores.append(score)

    return max(scores) if is_maximizing else min(scores)

def best_move(brd, ai_symbol, player_symbol):
    best_score = -float('inf')
    move = None
    for i in get_available_moves(brd):
        brd[i] = ai_symbol
        score = minimax(brd, False, ai_symbol, player_symbol)
        brd[i] = ' '
        if score > best_score:
            best_score = score
            move = i
    return move

def detect_colored_objects(frame, color_ranges):
    # Draw and extract ROI
    cv2.rectangle(frame, ROI_TOP_LEFT, ROI_BOTTOM_RIGHT, (255, 255, 255), 2)
    cv2.putText(frame, "ROI", (ROI_TOP_LEFT[0] + 5, ROI_TOP_LEFT[1] - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    x1, y1 = ROI_TOP_LEFT
    x2, y2 = ROI_BOTTOM_RIGHT
    roi = frame[y1:y2, x1:x2]

    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)
    detected_positions = {color: [] for color in color_ranges}

    for color, ranges in color_ranges.items():
        mask = None
        for lower, upper in ranges:
            lower_np = np.array(lower, dtype=np.uint8)
            upper_np = np.array(upper, dtype=np.uint8)
            partial_mask = cv2.inRange(hsv, lower_np, upper_np)
            mask = partial_mask if mask is None else cv2.bitwise_or(mask, partial_mask)

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                M = cv2.moments(cnt)
                if M["m00"] != 0:
                    cx = int(M["m10"] / M["m00"])
                    cy = int(M["m01"] / M["m00"])
                    # Convert to global frame coordinates
                    global_cx = cx + x1
                    global_cy = cy + y1
                    detected_positions[color].append((global_cx, global_cy))
                    cv2.circle(frame, (global_cx, global_cy), 10, (0, 255, 0), 2)
                    cv2.putText(frame, color, (global_cx - 20, global_cy - 20),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    return detected_positions["red"], detected_positions["blue"], frame

def map_position_to_cell(cx, cy):
    # Convert coordinates to ROI-relative
    rel_x = cx - ROI_TOP_LEFT[0]
    rel_y = cy - ROI_TOP_LEFT[1]

    col = min(max(rel_x * 3 // ROI_WIDTH, 0), 2)
    row = min(max(rel_y * 3 // ROI_HEIGHT, 0), 2)
    return row * 3 + col

def update_board_with_detection(cap, player_symbol):
    global board
    ret, frame = cap.read()
    if not ret:
        print("Failed to read frame.")
        return frame

    # Draw 3x3 Grid inside ROI
    for i in range(1, 3):
        # Vertical lines
        cv2.line(frame, (ROI_TOP_LEFT[0] + i * ROI_WIDTH // 3, ROI_TOP_LEFT[1]),
                        (ROI_TOP_LEFT[0] + i * ROI_WIDTH // 3, ROI_BOTTOM_RIGHT[1]), (255, 255, 255), 2)
        # Horizontal lines
        cv2.line(frame, (ROI_TOP_LEFT[0], ROI_TOP_LEFT[1] + i * ROI_HEIGHT // 3),
                        (ROI_BOTTOM_RIGHT[0], ROI_TOP_LEFT[1] + i * ROI_HEIGHT // 3), (255, 255, 255), 2)

    # Number each cell
    for row in range(3):
        for col in range(3):
            index = row * 3 + col
            cx = ROI_TOP_LEFT[0] + col * ROI_WIDTH // 3 + ROI_WIDTH // 6
            cy = ROI_TOP_LEFT[1] + row * ROI_HEIGHT // 3 + ROI_HEIGHT // 6
            cv2.putText(frame, str(index), (cx - 10, cy + 10), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    color_ranges = {
       "red": [([0, 150, 50], [10, 255, 255]), ([170, 150, 50], [180, 255, 255])],
        "blue": [([100, 150, 0], [140, 255, 255])]
    }

    red_pos, blue_pos, processed_frame = detect_colored_objects(frame, color_ranges)

    temp_board = [' '] * 9

    for cx, cy in red_pos:
        idx = map_position_to_cell(cx, cy)
        if 0 <= idx < 9:
            temp_board[idx] = 'O' 

    for cx, cy in blue_pos:
        idx = map_position_to_cell(cx, cy)
        if 0 <= idx < 9 and temp_board[idx] == ' ':
            temp_board[idx] = 'X'

    board[:] = temp_board
    print_board(board)

    resized_frame = cv2.resize(processed_frame, (640, 480))
    cv2.imshow("Tic-Tac-Toe Camera Feed", resized_frame)
    cv2.waitKey(1)

    return processed_frame

def print_board(brd):
    for i in range(3):
        print(brd[i*3], '|', brd[i*3+1], '|', brd[i*3+2])
        if i < 2:
            print('--+---+--')

def myturn(brd, ai_symbol):
    moves_played = sum(1 for cell in brd if cell != ' ')
    return (ai_symbol == 'X' and moves_played % 2 == 0) or (ai_symbol == 'O' and moves_played % 2 == 1)

def play_game():
    global board
    cap = cv2.VideoCapture("http://192.168.70.17:8080/video")
    if not cap.isOpened():
        print("Failed to open video stream.")
        return

    player_symbol = input("Choose your symbol (X or O): ").strip().upper()
    if player_symbol not in ['X', 'O']:
        print("Invalid choice. Defaulting to X.")
        player_symbol = 'X'
    ai_symbol = 'O' if player_symbol == 'X' else 'X'

    print(f"You are {player_symbol} (blue), Robot is {ai_symbol} (red).")
    count = 0
    while True:
        try:
            update_board_with_detection(cap, player_symbol)
        except Exception as e:
            print(f"⚠️ Error while updating board: {e}")
            break

        if is_winner(board, player_symbol):
            print("🎉 Human wins!")
            send_command_to_arduino("Reset")
            break
        elif is_winner(board, ai_symbol):
            print("🤖 Robot wins!")
            send_command_to_arduino("Reset")
            break
        elif ' ' not in board:
            print("🤝 It's a draw!")
            send_command_to_arduino("Reset")
            break
        
        if (count != 300):
            count+=1
            continue

        count = 0

        if not myturn(board, ai_symbol):
            continue

        cap.release()
        move = best_move(board, ai_symbol, player_symbol)
        if move is not None and board[move] == ' ':
            board[move] = ai_symbol
            command = Robot_moves[move]
            send_command_to_arduino(command)
            print(f"Robot move: {command}")
            cap = cv2.VideoCapture("http://192.168.70.17:8080/video")
        else:
            print("No valid moves.")
            break

        print_board(board)
        time.sleep(2)

    cap.release()
    cv2.destroyAllWindows()

# === Run the game ===
play_game()
