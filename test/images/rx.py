import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import numpy as np
import cv2

class CameraSubscriber(Node):
    def __init__(self):
        super().__init__('camera_subscriber')
        self.sub = self.create_subscription(
            CompressedImage,
            'camera/image/compressed',
            self.listener_callback,
            10)
        self.get_logger().info('CameraSubscriber started')

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
    node = CameraSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
