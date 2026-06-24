import rclpy
from rclpy.node import Node
from std_msgs.msg import String
import random as rd

class AsyncPublisher(Node):
    def __init__(self):
        super().__init__('async_publisher')
        # 'async_topic' という名前でString型の通信口を開設
        self.publisher_ = self.create_publisher(String, 'async_topic', 10)
        # 1.0秒ごとにタイマーを叩く（非同期ループ）
        self.timer = self.create_timer(1.0, self.timer_callback)
        self.count = 0

    def timer_callback(self):
        msg = String()
        msg.data = f'Async Message ID: {self.count}'
        self.publisher_.publish(msg)
        # 送信したら、受信側の返事を待たずに即座にログを出力して終了する
        self.get_logger().info(f'Sent: "{msg.data}" (Not waiting for anyone)')
        self.count += rd.uniform(1, 10) # 次のメッセージIDをランダムに増加させる

def main(args=None):
    rclpy.init(args=args)
    node = AsyncPublisher()
    rclpy.spin(node) # イベントループを回す
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()
