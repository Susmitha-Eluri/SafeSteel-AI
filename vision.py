import cv2
import numpy as np
from ultralytics import YOLO

# Load YOLO model
model = YOLO('yolov8n.pt')

# Define a static hazard polygon (approximate center/bottom of a 640x480 frame)
# This can be adjusted based on the actual camera feed.
HAZARD_POLYGON = np.array([
    [150, 480],
    [250, 200],
    [390, 200],
    [490, 480]
], np.int32)

def process_frame(frame, casting_sequence_active):
    """
    Processes a single frame:
    1. Runs YOLO detection for all classes.
    2. Pillar 1: Detects cup (41). If cup is found, checks if any other object (excluding person) overlaps it to act as a lid.
    3. Pillar 3: Checks if any person's (Class 0) bounding box corners are in the hazard polygon.
    4. Annotates the frame.
    
    Returns:
        annotated_frame (numpy array)
        breach_detected (bool)
        cover_missing (bool)
    """
    breach_detected = False
    
    # Run inference for all classes
    results = model(frame, verbose=False)
    
    # Draw hazard polygon
    poly_color = (0, 255, 0)
    if casting_sequence_active:
        poly_color = (0, 255, 255)
    cv2.polylines(frame, [HAZARD_POLYGON], isClosed=True, color=poly_color, thickness=3)
    
    # Variables for Pillar 1
    cup_boxes = []
    other_boxes = []
    
    for r in results:
        boxes = r.boxes
        for box in boxes:
            x1, y1, x2, y2 = box.xyxy[0].cpu().numpy().astype(int)
            cls_id = int(box.cls[0].cpu().numpy())
            
            # Draw all bounding boxes faintly for debug/demo
            cv2.rectangle(frame, (x1, y1), (x2, y2), (200, 200, 200), 1)
            
            if cls_id == 41: # Cup
                cup_boxes.append((x1, y1, x2, y2))
                cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 165, 0), 2)
                cv2.putText(frame, "LADLE", (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 165, 0), 1)
            elif cls_id != 0: # Not a person
                other_boxes.append((x1, y1, x2, y2))
            
            if cls_id == 0: # Person
                # Pillar 3: 4-Corner check
                corners = [
                    (int(x1), int(y1)), (int(x2), int(y1)),
                    (int(x1), int(y2)), (int(x2), int(y2))
                ]
                
                person_breached = False
                for corner in corners:
                    dist = cv2.pointPolygonTest(HAZARD_POLYGON, corner, False)
                    if dist >= 0:
                        person_breached = True
                        break
                        
                if person_breached:
                    breach_detected = True
                    print(f"[YOLOv8] Person detected at corners: {corners} -> PointPolygonTest = 1 (BREACH!) -> EXECUTING EMERGENCY HARDWARE LOCK...")
                else:
                    print(f"[YOLOv8] Person detected at corners: {corners} -> PointPolygonTest = -1 (SAFE)")

    # Evaluate Pillar 1 logic: Is the cup covered?
    cover_status = 'IDLE'
    if cup_boxes:
        cover_status = 'COVERED'
        for cx1, cy1, cx2, cy2 in cup_boxes:
            is_covered = False
            for ox1, oy1, ox2, oy2 in other_boxes:
                # Check intersection
                if not (ox2 < cx1 or ox1 > cx2 or oy2 < cy1 or oy1 > cy2):
                    is_covered = True
                    break
            
            if not is_covered:
                cover_status = 'MISSING'
                break

    # If breach while casting, draw red border and banner
    if breach_detected and casting_sequence_active:
        cv2.rectangle(frame, (0, 0), (frame.shape[1], frame.shape[0]), (0, 0, 255), 15)
        cv2.putText(frame, "CRITICAL ALERT: BLAST ZONE BREACHED!", (10, 50), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 0, 255), 2, cv2.LINE_AA)
        
    return frame, breach_detected, cover_status
