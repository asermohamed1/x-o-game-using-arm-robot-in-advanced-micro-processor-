import cv2
import numpy as np
import time


def detect_colored_objects(frame, color_ranges):
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    red_positions = []
    blue_positions = []
    white_positions = []

    for color_name, ranges in color_ranges.items():
        mask = None
        for lower, upper in ranges:
            lower_np = np.array(lower)
            upper_np = np.array(upper)
            color_mask = cv2.inRange(hsv, lower_np, upper_np)
            mask = color_mask if mask is None else mask | color_mask

        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area > 500:
                x, y, w, h = cv2.boundingRect(cnt)
                cx, cy = x + w // 2, y + h // 2

                if color_name == "red":
                    red_positions.append((cx, cy))
                    color = (0, 0, 255)
                elif color_name == "blue":
                    blue_positions.append((cx, cy))
                    color = (255, 0, 0)
                elif color_name == "white":
                    white_positions.append((cx, cy))
                    color = (255, 255, 255)

                cv2.rectangle(frame, (x, y), (x+w, y+h), color, 2)
                cv2.putText(frame, color_name, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)

    return red_positions, blue_positions, white_positions, frame


def main():
    color_ranges = {
        "red": [([0, 120, 70], [10, 255, 255]), ([170, 120, 70], [180, 255, 255])],
        "blue": [([100, 150, 0], [140, 255, 255])],
        "white": [([0, 0, 200], [180, 30, 255])]
    }

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Failed to open camera.")
        return

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        red_pos, blue_pos, white_pos, processed_frame = detect_colored_objects(frame, color_ranges)

        # Optional: print positions if you want to see output
        print("Red:", red_pos)
        print("Blue:", blue_pos)
        print("White:", white_pos)

        cv2.imshow("Color Detection", processed_frame)
        

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
