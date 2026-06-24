import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
from std_msgs.msg import String
import numpy as np
import cv2
import json
import threading
import ast

class OperationSide(Node):
    def __init__(self):
        super().__init__('operation_side')
        self.sub = self.create_subscription(
            CompressedImage,
            'camera/image/compressed',
            self.listener_callback,
            10)
        self.key_pub = self.create_publisher(String, 'keyboard/keys', 10)
        self.input_thread = threading.Thread(target=self.stdin_loop, daemon=True)
        self.input_thread.start()
        self.get_logger().info('OperationSide started')

    def stdin_loop(self):
        self.get_logger().info('Type a list like ["w", "a"] or w,a and press Enter to send')
        while rclpy.ok():
            try:
                line = input('keys> ').strip()
            except EOFError:
                break
            except KeyboardInterrupt:
                break
            if not line:
                continue
            keys = self.parse_keys(line)
            msg = String()
            msg.data = json.dumps(keys)
            self.key_pub.publish(msg)
            self.get_logger().info(f'Sent keys: {keys}')

    def parse_keys(self, line):
        try:
            value = ast.literal_eval(line)
            if isinstance(value, list):
                return [str(item) for item in value]
        except (ValueError, SyntaxError):
            pass
        return [item.strip() for item in line.split(',') if item.strip()]

    def listener_callback(self, msg):
        try:
            arr = np.frombuffer(msg.data, dtype=np.uint8)
            frame = cv2.imdecode(arr, cv2.IMREAD_COLOR)
            if frame is None:
                self.get_logger().error('Failed to decode image')
                return
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
