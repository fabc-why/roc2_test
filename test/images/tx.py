import rclpy
from rclpy.node import Node
from sensor_msgs.msg import CompressedImage
import cv2
import numpy as np

class CameraPublisher(Node):
    def __init__(self, cam_index=0, fps=10):
        super().__init__('camera_publisher')
        self.pub = self.create_publisher(CompressedImage, 'camera/image/compressed', 10)
        self.cap = cv2.VideoCapture(cam_index)
        self.timer = self.create_timer(1.0 / fps, self.timer_callback)
        self.get_logger().info('CameraPublisher started')

    def timer_callback(self):
        ret, frame = self.cap.read()
        if not ret:
            self.get_logger().error('Failed to read from camera')
            return
        # JPEG 圧縮して送信
        ok, buf = cv2.imencode('.jpg', frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
        if not ok:
            self.get_logger().error('Failed to encode frame')
            return
        msg = CompressedImage()
        msg.format = 'jpeg'
        msg.data = np.array(buf).tobytes()
        self.pub.publish(msg)
        self.get_logger().debug('Published compressed camera frame')

    def destroy_node(self):
        try:
            if self.cap.isOpened():
                self.cap.release()
        except Exception:
            pass
        super().destroy_node()

def main(args=None):
    rclpy.init(args=args)
    node = CameraPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
