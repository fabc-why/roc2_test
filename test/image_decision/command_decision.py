import importlib


# Load the YOLOv8 model for keyboard detection
def load_keyboard_model(model_path='yolov8n.pt'):
	try:
		ultralytics = importlib.import_module('ultralytics')
	except ImportError:
		return None

	return ultralytics.YOLO(model_path)


# Decide the keyboard command based on the detected position of the keyboard in the frame
# input: frame (numpy array), model (YOLOv8 model)
# output: command (str), detected_box (tuple of int)
def decide_keyboard_command(frame, model):
	if model is None:
		return 'not_found', None

	height, width = frame.shape[:2]
	results = model(frame, verbose=False)[0]

	best_conf = 0.0
	best_box = None

	for box in results.boxes:
		class_id = int(box.cls[0])
		label = model.names[class_id]
		if label != 'keyboard':
			continue

		confidence = float(box.conf[0])
		if confidence > best_conf:
			best_conf = confidence
			best_box = box

	if best_box is None:
		return 'not_found', None

	x1, y1, x2, y2 = map(int, best_box.xyxy[0])
	center_x = (x1 + x2) // 2

	if center_x < width / 3:
		position = 'left'
	elif center_x > 2 * width / 3:
		position = 'right'
	else:
		position = 'center'

	return position, (x1, y1, x2, y2)
