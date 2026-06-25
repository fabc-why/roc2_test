import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String
import numpy as np
import cv2
import json
from command_decision import decide_keyboard_command, load_keyboard_model

class OperationSide(Node):
    def __init__(self):
        super().__init__('operation_side')
        self.sub = self.create_subscription(
            CompressedImage,
            'camera/image/compressed',
            self.listener_callback,
            10)
        self.key_pub = self.create_publisher(String, 'keyboard/keys', 10)
        self.model = load_keyboard_model('yolov8n.pt')
        if self.model is None:
            self.get_logger().error('ultralytics is not installed; keyboard detection is disabled')
        self.last_output = None
        self.get_logger().info('OperationSide started')

    # send the command to the robot side
    def publish_command(self, command):
        msg = String()
        msg.data = json.dumps([command])
        self.key_pub.publish(msg)

    def listener_callback(self, msg):
        try:
            arr = np.frombuffer(msg.data, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                self.get_logger().error('Failed to decode image')
                return

            if self.model is None:
                cv2.putText(
                    frame,
                    'ultralytics missing',
                    (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.0,
                    (0, 0, 255),
                    2,
                )
                cv2.imshow('camera_sub', frame)
                cv2.waitKey(1)
                return

            output, box = decide_keyboard_command(frame, self.model)

            if output != self.last_output:
                self.publish_command(output) # Publish(send) the command only if it has changed
                self.last_output = output
                self.get_logger().info(f'Sent command: {output}')

            if box is not None:
                x1, y1, x2, y2 = box
                cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 2)

            cv2.putText(
                frame,
                f'keyboard: {output}',
                (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX,
                1.0,
                (0, 255, 0),
                2,
            )
            cv2.imshow('camera_sub', frame)
            cv2.waitKey(1)
        except Exception as e:
            self.get_logger().error(f'Error decoding/displaying image: {e}')

def main(args=None):
    rclpy.init(args=args)
    node = OperationSide()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
