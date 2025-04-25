import cv2
import mediapipe as mp
import tensorflow
import pygame
import time

# Initialize Mediapipe pose detection
mp_pose = mp.solutions.pose
pose = mp_pose.Pose()

# Initialize PyGame
pygame.init()
width, height = 800, 600
win = pygame.display.set_mode((width, height))
pygame.display.set_caption("Virtual Boxing Game")

# Colors and fonts
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
font = pygame.font.SysFont("Arial", 30)

# Health bars
player_health = 100
opponent_health = 100

# Timer for round logic
ROUND_TIME = 30
start_time = time.time()

# Start video capture for real-time body detection
cap = cv2.VideoCapture(0)

def draw_health_bars():
    pygame.draw.rect(win, RED, (50, 50, 200, 20))  # Player health bar (background)
    pygame.draw.rect(win, GREEN, (50, 50, 2 * player_health, 20))  # Player health (foreground)

    pygame.draw.rect(win, RED, (550, 50, 200, 20))  # Opponent health bar (background)
    pygame.draw.rect(win, GREEN, (550, 50, 2 * opponent_health, 20))  # Opponent health (foreground)

def display_winner():
    if player_health <= 0:
        text = font.render("You Lost! Opponent Wins!", True, RED)
        win.blit(text, (200, 300))
    elif opponent_health <= 0:
        text = font.render("You Win!", True, GREEN)
        win.blit(text, (350, 300))

    pygame.display.update()
    pygame.time.wait(3000)  # Pause for 3 seconds before exiting

# Game loop
running = True
while running:
    ret, frame = cap.read()
    if not ret:
        print("Failed to capture frame.")
        break

    # Flip and convert the frame to RGB for Mediapipe
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = pose.process(rgb_frame)

    # Handle PyGame events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Detect body landmarks and game logic
    punch_detected = False
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark

        # Extract relevant landmarks (wrists and elbows)
        left_wrist = landmarks[mp_pose.PoseLandmark.LEFT_WRIST]
        left_elbow = landmarks[mp_pose.PoseLandmark.LEFT_ELBOW]
        right_wrist = landmarks[mp_pose.PoseLandmark.RIGHT_WRIST]
        right_elbow = landmarks[mp_pose.PoseLandmark.RIGHT_ELBOW]

        # Detect punches (if wrist moves significantly forward compared to the elbow)
        if left_wrist.x > left_elbow.x + 0.1:
            punch_detected = True
            opponent_health -= 10  # Decrease opponent health on punch
            print("Left punch detected!")

        if right_wrist.x < right_elbow.x - 0.1:
            punch_detected = True
            opponent_health -= 10
            print("Right punch detected!")

        # Simple opponent response (random punch)
        if punch_detected and player_health > 0:
            player_health -= 5

    # Check if any player has won
    if player_health <= 0 or opponent_health <= 0:
        win.fill(WHITE)
        display_winner()
        break

    # Draw background, health bars, and round timer
    win.fill(WHITE)
    draw_health_bars()
    
    # Display remaining time
    time_left = max(0, ROUND_TIME - int(time.time() - start_time))
    timer_text = font.render(f"Time Left: {time_left}s", True, (0, 0, 0))
    win.blit(timer_text, (300, 10))

    # End the round when time runs out
    if time_left <= 0:
        win.fill(WHITE)
        display_winner()
        break

    # Update PyGame window
    pygame.display.update()

    # Display the frame in OpenCV window (optional)
    cv2.imshow("Virtual Boxing Detection", frame)

    # Exit on pressing 'q'
    if cv2.waitKey(10) & 0xFF == ord('q'):
        break

# Clean up
cap.release()
cv2.destroyAllWindows()
pygame.quit()
